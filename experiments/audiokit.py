"""audiokit — 코드로 만드는 배경음·효과음 (저작권 걱정 없음). 17번 make_bgm 을 일반화."""
import wave

import numpy as np

SR = 44100


def _write(path, x):
    x = x / (np.abs(x).max() + 1e-6) * 0.8
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((x * 32767).astype(np.int16).tobytes())


def make_bgm(path, dur, chords, bpm=76, seed=5, bright=1.0):
    """피아노 아르페지오 + 패드 + 잔향. chords: MIDI 음 4개씩, 한 마디에 하나."""
    n = int(dur * SR)
    out = np.zeros(n + SR * 2, np.float32)
    beat = 60 / bpm
    nf = lambda m: 440 * 2 ** ((m - 69) / 12)  # noqa: E731
    r = np.random.default_rng(seed)

    def piano(f, L, amp):
        t = np.arange(int(L * SR)) / SR
        x = sum((1 / k ** (1.6 / bright)) * np.sin(2 * np.pi * f * k * (1 + 0.0004 * k * k) * t) for k in range(1, 7))
        return (x * np.exp(-t * 2.6) * (1 - np.exp(-t * 300)) * amp).astype(np.float32)

    def add(sig, at):
        a = int(at * SR)
        if a < len(out):
            out[a:a + len(sig)] += sig[:len(out) - a]

    bar, t0, ci = beat * 4, 0.0, 0
    while t0 < dur:
        ch = chords[ci % len(chords)]
        add(piano(nf(ch[0] - 12), bar, 0.22), t0)
        for k, p in enumerate([0, 2, 1, 3, 2, 1, 3, 2]):
            add(piano(nf(ch[p] + 12), beat * 1.5, 0.09 * (1.1 if k == 0 else 1) * (0.9 + 0.2 * r.random())), t0 + k * beat / 2)
        tt = np.arange(int(bar * SR)) / SR
        env = np.minimum(1, tt / 0.8) * np.minimum(1, (bar - tt) / 0.6)
        pad = sum(np.sin(2 * np.pi * nf(m) * tt * (1 + 0.002 * np.sin(2 * np.pi * 0.3 * tt))) for m in ch) * 0.025 * env
        add(pad.astype(np.float32), t0)
        t0 += bar
        ci += 1
    ir_t = np.arange(int(1.4 * SR)) / SR
    ir = (r.normal(0, 1, len(ir_t)) * np.exp(-ir_t * 3.5)).astype(np.float32)
    ir[0] = 1
    L = len(out) + len(ir)
    wet = np.fft.irfft(np.fft.rfft(out, L) * np.fft.rfft(ir, L))[:len(out)]
    mix = (out + 0.14 * wet / (np.abs(wet).max() + 1e-6) * np.abs(out).max())[:n]
    fade = np.ones(n, np.float32)
    fi, fo = int(0.6 * SR), int(1.8 * SR)
    fade[:fi] = np.linspace(0, 1, fi)
    fade[-fo:] = np.linspace(1, 0, fo)
    _write(path, mix * fade)


def wind_sfx(path, dur, at_times, length=0.6, seed=7, base=0.0):
    """바람 '쉭' (장면 전환) + 선택적으로 깔리는 약한 바람(base 0~1)."""
    n = int(dur * SR) + SR
    r = np.random.default_rng(seed)
    out = np.zeros(n, np.float32)
    if base > 0:  # 깔리는 바람: 저역 노이즈 + 느린 세기 변화
        x = r.normal(0, 1, n).astype(np.float32)
        x = np.convolve(x, np.ones(60) / 60, "same")
        t = np.arange(n) / SR
        out += x * (0.6 + 0.4 * np.sin(2 * np.pi * 0.11 * t) * np.sin(2 * np.pi * 0.037 * t + 1)) * base * 3
    for st in at_times:
        a, L = int(st * SR), int(length * SR)
        x = r.normal(0, 1, L).astype(np.float32)
        x = np.convolve(x, np.ones(6) / 6, "same") - np.convolve(x, np.ones(40) / 40, "same")
        tt = np.linspace(0, 1, L)
        out[a:a + L] += x * np.sin(np.pi * tt) ** 2 * 0.5
    _write(path, out)
