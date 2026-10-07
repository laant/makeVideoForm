#!/usr/bin/env python3
"""나레이션 생성 — Gemini TTS(Aoede) → 앞뒤 무음 정리 → whisper.cpp 로 단어 시작 시각.

  .venv/bin/python tts.py            # 바뀐 컷만 (문장 해시 캐시)
  .venv/bin/python tts.py --force
결과: audio/sNN.mp3 · audio/timing.json · audio/narration.mp3 (컷 사이 GAP 초 무음)
"""
import base64, hashlib, json, os, re, subprocess, sys, tempfile, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[2]
AUD = ROOT / "audio"
MODEL = "gemini-3.1-flash-tts-preview"
VOICE = "Aoede"
GAP = 0.3
WHISPER_MODEL = REPO / "autoShorts/.cache/whisper/ggml-small.bin"
SCRIPT = json.loads((ROOT / "script.json").read_text())["scenes"]


def api_key():
    for line in (REPO / "autoShorts/.env").read_text().splitlines():
        if line.startswith("GEMINI_API_KEY="):
            return line.split("=", 1)[1].strip().strip('"')
    sys.exit("GEMINI_API_KEY 없음 (autoShorts/.env)")


def sh(*cmd):
    subprocess.run(cmd, check=True, capture_output=True)


def dur(p):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)],
                                capture_output=True, text=True).stdout)


def synth(text, mp3):
    body = {"contents": [{"parts": [{"text": text}]}],
            "generationConfig": {"responseModalities": ["AUDIO"],
                                 "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": VOICE}}}}}
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={api_key()}"
    req = urllib.request.Request(url, json.dumps(body).encode(), {"Content-Type": "application/json"})
    data = json.loads(urllib.request.urlopen(req, timeout=120).read())
    part = next(p for p in data["candidates"][0]["content"]["parts"] if "inlineData" in p)
    rate = int(re.search(r"rate=(\d+)", part["inlineData"]["mimeType"]).group(1))
    with tempfile.TemporaryDirectory() as td:
        pcm, wav = Path(td) / "a.pcm", Path(td) / "a.wav"
        pcm.write_bytes(base64.b64decode(part["inlineData"]["data"]))
        trim = ("silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.05,"
                "areverse,silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.05,areverse")
        sh("ffmpeg", "-y", "-v", "error", "-f", "s16le", "-ar", str(rate), "-ac", "1", "-i", str(pcm), "-af", trim, str(wav))
        sh("ffmpeg", "-y", "-v", "error", "-i", str(wav), "-ar", "44100", "-ac", "1", "-b:a", "160k", str(mp3))


def word_times(text, mp3):
    """whisper 토큰을 글자 비율로 대본 단어에 맞춘다(단어 시작 시각만 필요)."""
    with tempfile.TemporaryDirectory() as td:
        w16, of = Path(td) / "a.wav", Path(td) / "a"
        sh("ffmpeg", "-y", "-v", "error", "-i", str(mp3), "-ar", "16000", "-ac", "1", str(w16))
        sh("whisper-cli", "-m", str(WHISPER_MODEL), "-l", "ko", "-f", str(w16), "-ojf", "-of", str(of), "-np")
        out = json.loads((Path(td) / "a.json").read_text())
    toks = [t for seg in out["transcription"] for t in seg["tokens"] if not t["text"].strip().startswith("[")]
    rc = []  # 인식된 글자별 시각
    for t in toks:
        chars = re.sub(r"[^\w]", "", t["text"])
        a, b = t["offsets"]["from"] / 1000, t["offsets"]["to"] / 1000
        for i, _ in enumerate(chars):
            rc.append(a + (b - a) * i / max(1, len(chars)))
    recognized = "".join(re.sub(r"[^\w]", "", t["text"]) for t in toks)
    words = text.split(" ")
    total = sum(len(re.sub(r"[^\w]", "", w)) for w in words)
    res, pos = [], 0
    for w in words:
        k = min(len(rc) - 1, round(pos * len(rc) / max(1, total))) if rc else 0
        res.append({"text": w, "start": round(rc[k] if rc else 0, 3)})
        pos += len(re.sub(r"[^\w]", "", w))
    return res, recognized


def main():
    AUD.mkdir(exist_ok=True)
    tf = AUD / "timing.json"
    old = json.loads(tf.read_text()) if tf.exists() else {}
    force = "--force" in sys.argv
    scenes, t = [], 0.0
    for i, s in enumerate(SCRIPT):
        sid = f"s{i + 1:02d}"
        h = hashlib.sha1(f"{VOICE}|{MODEL}|{s['narration']}".encode()).hexdigest()[:12]
        mp3 = AUD / f"{sid}.mp3"
        prev = next((x for x in old.get("scenes", []) if x["id"] == sid), None)
        if force or not prev or prev["hash"] != h or not mp3.exists():
            print(f"▶ {sid} {s['narration']}")
            synth(s["narration"], mp3)
            words, rec = word_times(s["narration"], mp3)
            print(f"   인식: {rec}")
        else:
            words = prev["words"]
        d = dur(mp3)
        scenes.append({"id": sid, "hash": h, "start": round(t, 3), "speech": round(d, 3), "duration": round(d + GAP, 3), "words": words})
        t += d + GAP
    tf.write_text(json.dumps({"total": round(t, 3), "scenes": scenes}, ensure_ascii=False, indent=1))
    lst = AUD / "concat.txt"
    lst.write_text("".join(f"file '{AUD / (s['id'] + '.mp3')}'\nfile '{AUD / 'gap.mp3'}'\n" for s in scenes))
    sh("ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono", "-t", str(GAP), "-b:a", "160k", str(AUD / "gap.mp3"))
    sh("ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(lst), "-ar", "44100", "-ac", "1", "-b:a", "160k", str(AUD / "narration.mp3"))
    print(f"✓ 총 {t:.2f}s → audio/narration.mp3")


if __name__ == "__main__":
    main()
