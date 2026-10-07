#!/usr/bin/env python3
"""29 Flow Music — 신스 아르페지오 BGM(90 BPM) 합성 + 나레이션 덕킹 믹스 + HTML 용 타이밍(timing.js).

장면 전환 = 앞 나레이션 끝 ~ 다음 첫 단어(+0.15) 사이의 박(없으면 첫 단어 시각) — MOTION-RULES.
  .venv/bin/python mix.py
"""
import json, math, subprocess, wave
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent
SC = json.loads((ROOT / "audio/timing.json").read_text())["scenes"]
TAIL = 1.2
TOTAL = json.loads((ROOT / "audio/timing.json").read_text())["total"] + TAIL
BPM = 90
BEAT = 60 / BPM
SR = 44100


def cut_at(i):
    lo = SC[i - 1]["start"] + SC[i - 1]["speech"]
    hi = SC[i]["start"]
    bs = [k * BEAT for k in range(int(lo / BEAT), int((hi + 0.15) / BEAT) + 2) if lo <= k * BEAT <= hi + 0.15]
    before = [b for b in bs if b <= hi]
    return before[-1] if before else (bs[0] if bs else hi)


CUTS = [0.0] + [round(cut_at(i), 3) for i in range(1, len(SC))]


def synth_bgm(path):
    n = int((TOTAL + 1) * SR)
    out = np.zeros(n, np.float32)
    nf = lambda m: 440 * 2 ** ((m - 69) / 12)  # noqa: E731
    chords = [[57, 60, 64, 69], [53, 57, 60, 65], [55, 59, 62, 67], [52, 55, 59, 64]]  # Am F G Em
    step = BEAT / 2  # 8분음표 아르페지오
    t = 0.0
    k = 0
    while t < TOTAL:
        ch = chords[int(t / (BEAT * 4)) % 4]
        m = ch[[0, 2, 1, 3, 2, 1, 3, 2][k % 8]] + 12
        L = int(step * 1.6 * SR)
        tt = np.arange(L) / SR
        f = nf(m)
        x = sum(((-1) ** (h + 1)) / h * np.sin(2 * np.pi * f * h * tt) for h in range(1, 6)) * 0.55  # 부드러운 톱니(배음 5개)
        env = np.minimum(1, tt * 200) * np.exp(-tt * 5.5)
        s0 = int(t * SR)
        seg = (x * env * 0.16).astype(np.float32)
        out[s0:s0 + L] += seg[: max(0, min(L, n - s0))]
        t += step
        k += 1
    # 패드: 코드 길게, 느린 트레몰로
    tt = np.arange(n) / SR
    pad = np.zeros(n, np.float32)
    for bar in range(int(TOTAL / (BEAT * 4)) + 2):
        ch = chords[bar % 4]
        a, b = int(bar * BEAT * 4 * SR), int((bar + 1) * BEAT * 4 * SR)
        if a >= n:
            break
        b = min(b, n)
        seg_t = tt[a:b] - tt[a]
        env = np.minimum(1, seg_t * 2) * np.minimum(1, (seg_t[::-1]) * 3)
        pad[a:b] += sum(np.sin(2 * np.pi * nf(m) * seg_t) for m in ch[:3]).astype(np.float32) * env.astype(np.float32) * 0.05
    out += pad * (0.85 + 0.15 * np.sin(2 * np.pi * 0.25 * tt)).astype(np.float32)
    # 끝 페이드
    fade = int(1.5 * SR)
    end = int(TOTAL * SR)
    out[end - fade:end] *= np.linspace(1, 0, fade)
    out[end:] = 0
    out /= max(1e-6, np.abs(out).max()) / 0.8
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((out[:end] * 32767).astype(np.int16).tobytes())


def main():
    bgm = ROOT / "audio/bgm.wav"
    synth_bgm(bgm)
    fc = ("[0:a]aresample=44100,apad[n0];[n0]asplit=2[n1][n2];[1:a]volume=0.22[b];"
          "[b][n1]sidechaincompress=threshold=0.02:ratio=6:attack=30:release=400[bd];"
          "[n2][bd]amix=inputs=2:normalize=0:duration=longest,alimiter=limit=0.9[a]")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(ROOT / "audio/narration.mp3"), "-i", str(bgm),
                    "-filter_complex", fc, "-map", "[a]", "-t", f"{TOTAL:.3f}", "-b:a", "192k", str(ROOT / "audio/mix.mp3")], check=True)
    tm = {"total": round(TOTAL, 3), "beat": BEAT, "cuts": CUTS,
          "scenes": [{"start": s["start"], "speech": s["speech"], "w": [round(w["start"], 3) for w in s["words"]]} for s in SC]}
    (ROOT / "timing.js").write_text("window.TM = " + json.dumps(tm) + ";\n")
    print("✓ mix.mp3", f"{TOTAL:.2f}s", "cuts", CUTS)


if __name__ == "__main__":
    main()
