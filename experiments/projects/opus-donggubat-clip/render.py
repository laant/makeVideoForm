#!/usr/bin/env python3
"""opus-donggubat-clip — Gemini 생성 16:9 제품 영상 → 9:16 쇼츠 (원 음성 제거 · 새 나레이션 · 자막 · 배경음 · 평점/엔드카드).

원본은 컷마다 가운데 9:16(405×720)을 잘라 1080×1920 으로 키운다. 나레이션이 원본 구간보다 길면
최대 1.4배까지 느리게(프레임 섞기) 재생한 뒤 마지막 프레임을 천천히 확대하며 유지한다.
평점 컷: 원본의 가로 평점 카드 대신 실제 스토어 평점(script.json rating, 확인일 표기)을 종이 카드로 새로 그린다.
배경음은 코드로 합성(피아노 아르페지오 + 패드 + 잔향) — 저작권 문제 없음. 나레이션이 나올 때 자동으로 줄어든다.
  ../opus-paper-04/.venv/bin/python render.py [--still 1,13]
"""
import importlib.util, json, math, subprocess, sys, wave
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parents[1]))  # experiments/ (paperkit·audiokit)
from paperkit import (W, H, font, Sprite, lift, blit, stack, piece, label, clamp, prog, out_cubic, out_back,  # noqa: E402
                      pop, wrap, full_bg, _paste_into, mask, poly)

_spec = importlib.util.spec_from_file_location("autumn", ROOT.parent / "opus-autumn-handcream/render.py")
A = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(A)  # 가을 소품(낙엽·니트·태그·색) 재사용

FPS = 30
OUT = ROOT / "out"
S = json.loads((ROOT / "script.json").read_text())
TIM = json.loads((ROOT / "audio/timing.json").read_text())
SC = TIM["scenes"]
TAIL = 1.2
TOTAL = TIM["total"] + TAIL
SRC = S["source_video"].split(" ")[0]
SRC_FPS, CW, CH, CX = 24, 404, 720, 438
MAX_SLOW = 1.4


def wt(i, k):
    return SC[i]["words"][k]["start"]


# ── 원본 프레임 (가운데 9:16 크롭) ───────────────────────────
def load_src():
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", SRC, "-vf", f"crop={CW}:{CH}:{CX}:0", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, CH, CW, 3)


FR = load_src()


def src_frame(t):
    f = clamp(t * SRC_FPS, 0, len(FR) - 1)
    a = int(f)
    b = min(a + 1, len(FR) - 1)
    w = f - a
    return FR[a] if w < 1e-3 else (FR[a] * (1 - w) + FR[b] * w).astype(np.uint8)


def video_bg(i, lt):
    s0, s1 = S["scenes"][i]["src"]
    dur = SC[i]["duration"] + (TAIL if i == len(SC) - 1 else 0)
    k = min(MAX_SLOW, dur / (s1 - s0))
    play = (s1 - s0) * k
    if lt <= play:
        img, zoom = Image.fromarray(src_frame(s0 + lt / k)), 1.0
    else:
        img, zoom = Image.fromarray(src_frame(s1 - 1e-3)), 1 + 0.06 * clamp((lt - play) / max(0.5, dur - play))
    if S["scenes"][i].get("blur"):
        img = img.filter(ImageFilter.GaussianBlur(7))
        img = Image.eval(img, lambda v: int(v * 0.82))
    big = img.resize((int(W * zoom), int(H * zoom)), Image.LANCZOS)
    ox, oy = (big.width - W) // 2, (big.height - H) // 2
    return big.crop((ox, oy, ox + W, oy + H)).convert("RGBA")


# ── 평점 카드 · 엔드카드 ────────────────────────────────────
R = S["rating"]


def star_pts(cx, cy, r):
    return [(cx + (r if k % 2 == 0 else r * 0.45) * math.sin(math.pi * k / 5), cy - (r if k % 2 == 0 else r * 0.45) * math.cos(math.pi * k / 5)) for k in range(10)]


def rating_card():
    w, h = 880, 600
    cv = stack(w, h, [(piece(w, h, [(0, 0), (w, 0), (w, h), (0, h)], A.CREAM, 1701, 0, 1.0), 0, 0)])
    d = ImageDraw.Draw(cv)
    f1, fb, f3, f4 = font(40), font(170), font(50), font(32, bold=False)
    t1 = f"{R['where']} 평점"
    d.text(((w - f1.getlength(t1)) / 2, 44), t1, font=f1, fill=(130, 100, 76))
    d.text(((w - fb.getlength(R["score"])) / 2, 100), R["score"], font=fb, fill=A.INK)
    # 별 5개 — 평점만큼 채움
    sc = float(R["score"])
    for k in range(5):
        cx = w / 2 + (k - 2) * 96
        star = star_pts(cx, 345, 40)
        d.polygon(star, fill=(222, 210, 188))
        fill = clamp(sc - k)
        if fill > 0:
            m = Image.new("L", (w, h), 0)
            ImageDraw.Draw(m).polygon(star, fill=255)
            clip = Image.new("L", (w, h), 0)
            ImageDraw.Draw(clip).rectangle([cx - 40, 300, cx - 40 + 80 * fill, 390], fill=255)
            m = Image.fromarray(np.minimum(np.asarray(m), np.asarray(clip)))
            cv.paste(Image.new("RGBA", (w, h), A.MUST + (255,)), (0, 0), m)
    t3 = f"리뷰 {R['reviews']}건 · 4점 이상 {R['ge4']}"
    d.text(((w - f3.getlength(t3)) / 2, 420), t3, font=f3, fill=A.BRICK)
    t4 = f"최근 6개월 {R['recent6m']} · {R['asof']} 기준"
    d.text(((w - f4.getlength(t4)) / 2, 510), t4, font=f4, fill=(120, 96, 76))
    return lift(cv, 10)


class EndCard:
    def __init__(self):
        B = full_bg(A.KRAFT, 1801)
        _paste_into(B, A.KNIT, -20, 1690)
        self.base = A.bake(B, A.corner_leaves(1802, [(930, 330, 130), (-40, 820, 140), (900, 1280, 150), (60, 1330, 120)]))
        self.photo = A.Products.photo(None, ROOT.parent / "opus-autumn-handcream/media/p1.jpg", 1.0, "가방용 · 튜브형 60ml", "동구밭 시어버터 무향 핸드크림", 1803, 1.5)
        self.disc = A.tag(S["disclosure"], 30, bg=A.INK, fg=A.CREAM, seed=1804)
        self.t1 = A.tag("구성·가격 → 설명란 링크", 46, bg=A.BRICK, seed=1805)
        self.t2 = A.tag("전성분은 구매 전 확인", 46, bg=A.OLIVE, seed=1806)

    def draw(self, frame, lt):
        frame.paste(self.base)
        A.CUR[0] = lt + 30
        A.falling(frame, lt + 30, 0.5)
        blit(frame, self.disc, 70, 272)
        pop(frame, self.photo, (W - self.photo.w) / 2, 380, lt, 0.05, dur=0.5)
        pop(frame, self.t1, 90, 1130, lt, wt(4, 2))
        pop(frame, self.t2, 90, 1225, lt, wt(4, 4))


RATING = rating_card()
END = EndCard()
TAG_AAD = A.tag("미국피부과학회(AAD) 보습 안내", 32, bg=A.OLIVE, seed=1807)


# ── 자막 ────────────────────────────────────────────────────
CAP_TL = sorted((SC[i]["start"] + wt(i, k), txt) for i, s in enumerate(S["scenes"]) for txt, k in s["caps"])
_cap = {}


def draw_caption(frame, t):
    cur = None
    for i, (st, txt) in enumerate(CAP_TL):
        if t >= st:
            cur = (i, st, txt)
    if not cur:
        return
    i, st, txt = cur
    if i not in _cap:
        _cap[i] = label(wrap(txt, font(70), 880), 70, fg=A.INK, bg=A.CREAM, pad=(34, 14), seed=1900 + i, elev=5, align="center", amp=2.2)
    spr = _cap[i]
    p = prog(t, st, 0.16)
    blit(frame, spr, (W - spr.w) / 2, 1570 - spr.h + (1 - out_cubic(p)) * 14, alpha=clamp(p * 1.6))


def scene_frame(i, lt):
    if S["scenes"][i]["src"] is None:
        fr = Image.new("RGBA", (W, H), (0, 0, 0, 255))
        END.draw(fr, lt)
        return fr
    fr = video_bg(i, lt)
    if i == 0:  # 처음부터 상품이 나오므로 첫 화면에 광고 고지
        blit(fr, END.disc, (W - END.disc.w) / 2, 335)
    if i == 2:
        pop(fr, TAG_AAD, 70, 300, lt, 0.2)
    if i == 3:
        pop(fr, RATING, (W - RATING.w) / 2, 560, lt, 0.1, dur=0.5, anchor=(0.5, 0.5))
    return fr


XF = 0.35


def frame_at(t):
    i = max(k for k in range(len(SC)) if t >= SC[k]["start"] - 1e-6)
    lt = t - SC[i]["start"]
    fr = scene_frame(i, lt)
    if i == len(SC) - 1 and lt < XF:  # 영상 → 엔드카드만 부드럽게
        old = scene_frame(i - 1, t - SC[i - 1]["start"])
        fr = Image.blend(old, fr, out_cubic(lt / XF))
    draw_caption(fr, t)
    return fr


# ── 배경음 합성 ─────────────────────────────────────────────
def make_bgm(path, dur):
    sr = 44100
    n = int(dur * sr)
    out = np.zeros(n + sr * 2, np.float32)
    bpm = 76
    beat = 60 / bpm
    nf = lambda m: 440 * 2 ** ((m - 69) / 12)  # noqa: E731
    chords = [[53, 57, 60, 64], [52, 55, 59, 62], [50, 53, 57, 60], [48, 52, 55, 59]]  # Fmaj7 Em7 Dm7 Cmaj7
    r = np.random.default_rng(5)

    def piano(f, L, amp):
        t = np.arange(int(L * sr)) / sr
        x = sum((1 / k ** 1.6) * np.sin(2 * np.pi * f * k * (1 + 0.0004 * k * k) * t) for k in range(1, 7))
        return (x * np.exp(-t * 2.6) * (1 - np.exp(-t * 300)) * amp).astype(np.float32)

    def add(sig, at):
        a = int(at * sr)
        if a < len(out):
            out[a:a + len(sig)] += sig[:len(out) - a]

    bar = beat * 4
    t0 = 0.0
    ci = 0
    while t0 < dur:
        ch = chords[ci % 4]
        add(piano(nf(ch[0] - 12), bar, 0.22), t0)  # 베이스
        pat = [0, 2, 1, 3, 2, 1, 3, 2]
        for k, p in enumerate(pat):  # 8분음표 아르페지오
            add(piano(nf(ch[p] + 12), beat * 1.5, 0.09 * (1.1 if k == 0 else 1) * (0.9 + 0.2 * r.random())), t0 + k * beat / 2)
        L = int(bar * sr)
        tt = np.arange(L) / sr
        env = np.minimum(1, tt / 0.8) * np.minimum(1, (bar - tt) / 0.6)
        pad = sum(np.sin(2 * np.pi * nf(m) * tt * (1 + 0.002 * np.sin(2 * np.pi * 0.3 * tt))) for m in ch) * 0.025 * env
        add(pad.astype(np.float32), t0)
        t0 += bar
        ci += 1
    ir_t = np.arange(int(1.2 * sr)) / sr  # 잔향
    ir = (r.normal(0, 1, len(ir_t)) * np.exp(-ir_t * 4)).astype(np.float32)
    ir[0] = 1
    wet = np.fft.irfft(np.fft.rfft(out, len(out) + len(ir)) * np.fft.rfft(ir, len(out) + len(ir)))[:len(out)]
    mix = out + 0.12 * wet / (np.abs(wet).max() + 1e-6) * np.abs(out).max()
    mix = mix[:n]
    fade = np.ones(n, np.float32)
    fi, fo = int(0.6 * sr), int(1.8 * sr)
    fade[:fi] = np.linspace(0, 1, fi)
    fade[-fo:] = np.linspace(1, 0, fo)
    mix = mix * fade
    mix = mix / (np.abs(mix).max() + 1e-6) * 0.8
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes((mix * 32767).astype(np.int16).tobytes())


def main():
    OUT.mkdir(exist_ok=True)
    if "--still" in sys.argv:
        for ts in sys.argv[sys.argv.index("--still") + 1].split(","):
            frame_at(float(ts)).convert("RGB").save(OUT / f"still_{ts}.png")
        print("stills ok")
        return
    bgm = OUT / "bgm.wav"
    make_bgm(bgm, TOTAL)
    nfr = int(math.ceil(TOTAL * FPS))
    dst = OUT / "final.mp4"
    fc = ("[1:a]apad,asplit=2[n1][n2];[2:a]volume=0.32[b];[b][n1]sidechaincompress=threshold=0.02:ratio=6:attack=30:release=400[bd];"
          "[n2][bd]amix=inputs=2:normalize=0:duration=longest[a]")
    cmd = ["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-i", str(ROOT / "audio/narration.mp3"), "-i", str(bgm), "-filter_complex", fc,
           "-map", "0:v", "-map", "[a]", "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "-t", f"{TOTAL:.3f}", str(dst)]
    ff = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for f in range(nfr):
        ff.stdin.write(frame_at(f / FPS).convert("RGB").tobytes())
    ff.stdin.close()
    ff.wait()
    print("✓", dst.relative_to(ROOT), f"({TOTAL:.1f}s)")


if __name__ == "__main__":
    main()
