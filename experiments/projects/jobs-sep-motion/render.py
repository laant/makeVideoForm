#!/usr/bin/env python3
"""26번 2026년 9월 미국 고용보고서 — 사용자 모션그래픽 + Gemini Aoede 나레이션.

장면 길이 = max(원래 길이, 나레이션 + 여유). 각 장면 시작 0.3초 뒤에 나레이션.
배경음은 사용자 music-original.wav(36초)를 크로스페이드로 이어 붙이고, 키운 뒤 나레이션에 맞춰 덕킹.
  .venv/bin/python render.py [--still 2:3.5,5:4]
"""
import json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import motion as M  # noqa: E402

TIM = json.loads((ROOT / "audio/timing.json").read_text())["scenes"]
ORIG = [5, 8, 8, 8, 7]
LEAD = 0.3
SPEECH = [s["speech"] for s in TIM]
DURS = [round(max(o, LEAD + sp + 0.8), 2) for o, sp in zip(ORIG, SPEECH)]
DURS[-1] = round(max(ORIG[-1], LEAD + SPEECH[-1] + 1.6), 2)  # 마지막은 여운
M.DURS = DURS
STARTS = [sum(DURS[:i]) for i in range(len(DURS))]
TOTAL = sum(DURS)
OUT = ROOT / "out"
MUSIC_GAIN_DB = 12


def main():
    OUT.mkdir(exist_ok=True)
    if "--still" in sys.argv:
        for spec in sys.argv[sys.argv.index("--still") + 1].split(","):
            n, t = spec.split(":")
            M.frame(int(n), float(t)).save(OUT / f"still_{n}_{t}.png")
        print("stills ok", DURS)
        return
    silent = OUT / "silent.mp4"
    if "--audio-only" in sys.argv and silent.exists():
        ff = None
    else:
        ff = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{M.W}x{M.H}", "-r", str(M.FPS), "-i", "-",
                           "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", str(silent)], stdin=subprocess.PIPE)
    if ff:
        for n, d in enumerate(DURS, 1):
            for i in range(round(d * M.FPS)):
                ff.stdin.write(M.frame(n, i / M.FPS).convert("RGB").tobytes())
        ff.stdin.close()
        if ff.wait():
            raise RuntimeError("encode failed")
    ins, parts = [], []
    for k, s in enumerate(TIM):
        ins += ["-i", str(ROOT / "audio" / f"{s['id']}.mp3")]
        ms = int((STARTS[k] + LEAD) * 1000)
        parts.append(f"[{k + 1}:a]aresample=48000,adelay={ms}|{ms}[v{k}]")
    nv = len(TIM)
    mi = nv + 1
    fc = ";".join(parts) + ";" + "".join(f"[v{k}]" for k in range(nv)) + f"amix=inputs={nv}:normalize=0:duration=longest,apad,atrim=0:{TOTAL:.3f}[vo];"
    fc += (f"[{mi}:a]aresample=48000[m0];[{mi + 1}:a]aresample=48000[m1];[m0][m1]acrossfade=d=2[mm];"
           f"[mm]atrim=0:{TOTAL:.3f},volume={MUSIC_GAIN_DB}dB,afade=t=out:st={TOTAL - 1.5:.3f}:d=1.5[mu];"
           "[vo]asplit=2[vk][vm];[mu][vk]sidechaincompress=threshold=0.03:ratio=5:attack=40:release=500[md];"
           "[vm][md]amix=inputs=2:normalize=0,alimiter=limit=0.9[a]")
    music = str(ROOT / "music-original.wav")
    cmd = ["ffmpeg", "-y", "-v", "error", "-i", str(silent), *ins, "-i", music, "-i", music, "-filter_complex", fc,
           "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-t", f"{TOTAL:.3f}", "-movflags", "+faststart", str(OUT / "final.mp4")]
    subprocess.run(cmd, check=True)
    print("✓ out/final.mp4", f"{TOTAL:.2f}s", DURS)


if __name__ == "__main__":
    main()
