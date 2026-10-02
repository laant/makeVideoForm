#!/usr/bin/env python3
"""opus-jobs-report — 미국 9월 고용보고서 발표 전 체크 4가지 (24번 · 재테크).

크림 장부지 바탕 · 짙은 녹색/금색 종이공작. 숫자는 BLS 2026-09-04 발표문(8월분)만 쓴다.
막대·업종 그림은 설명용 도식이며 실제 통계가 아니다(화면에 표기).
  ../opus-paper-04/.venv/bin/python render.py [--still 1,9]
"""
import json, math, subprocess, sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent))
from paperkit import (W, H, FPS, font, lift, blit, rrect, circle_pts, piece, stack, full_bg,  # noqa: E402
                      label, clamp, prog, out_cubic, in_out, pop, wrap)
from audiokit import make_bgm, wind_sfx  # noqa: E402

CREAM = (244, 238, 224)
PAPER = (252, 250, 244)
GREEN = (28, 78, 62)
GREEN2 = (62, 120, 96)
GOLD = (196, 150, 60)
INK = (34, 36, 40)
GREY = (140, 136, 126)
RED = (190, 70, 56)

OUT = ROOT / "out"
S = json.loads((ROOT / "script.json").read_text())
TIM = json.loads((ROOT / "audio/timing.json").read_text())
SC = TIM["scenes"]
TAIL = 1.0
TOTAL = TIM["total"] + TAIL


def wt(i, k):
    return SC[i]["words"][k]["start"]


def tag(text, size=40, bg=GREEN, fg=PAPER, seed=0):
    return label(text, size, fg=fg, bg=bg, pad=(22, 8), seed=seed, elev=5, amp=1.0)


def title(text, hl=(), seed=0, size=88):
    return label(text, size, fg=INK, bg=PAPER, hl=hl, hlc=GREEN2, seed=seed, elev=8)


def note(text, seed, size=28):
    return label(text, size, fg=GREY, bg=CREAM, pad=(14, 6), seed=seed, elev=0, amp=0.4)


def make_bg():
    B = full_bg(CREAM, 24)
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    for y in range(0, H, 54):  # 장부 줄
        d.line([(0, y), (W, y)], fill=GREEN + (22,), width=2)
    d.line([(96, 0), (96, H)], fill=RED + (40,), width=3)  # 여백선
    B.alpha_composite(ov)
    return B


BG = make_bg()


def photo(path, w, seed):
    im = Image.open(path).convert("RGB")
    h = int(im.height * w / im.width)
    im = im.resize((w, h), Image.LANCZOS)
    b = 14
    cv = stack(w + 2 * b, h + 2 * b, [(piece(w + 2 * b, h + 2 * b, [(0, 0), (w + 2 * b, 0), (w + 2 * b, h + 2 * b), (0, h + 2 * b)], PAPER, seed, 0, 1.2), 0, 0)])
    cv.paste(im, (b, b))
    return lift(cv, 9)


def card(head, value, sub, seed, w=450, h=300, vc=GREEN):
    cv = stack(w, h, [(piece(w, h, rrect(0, 0, w, h, 26), PAPER, seed, 0, 1.0), 0, 0)])
    d = ImageDraw.Draw(cv)
    d.text((30, 26), head, font=font(38), fill=GREY)
    d.text((30, 92), value, font=font(96), fill=vc)
    d.text((30, 222), sub, font=font(30), fill=GREY)
    return lift(cv, 7)


def person(seed, color=GREEN):
    w, h = 120, 220
    parts = [(piece(w, h, circle_pts(60, 40, 34), (230, 196, 160), seed, 0, 0.5), 0, 0),
             (piece(w, h, rrect(14, 86, 106, 218, 36), color, seed + 1, 0, 0.6), 0, 0)]
    return lift(stack(w, h, parts), 6)


def office(seed, color):
    w, h = 200, 240
    cv = stack(w, h, [(piece(w, h, [(0, 30), (w, 0), (w, h), (0, h)], color, seed, 0, 0.8), 0, 0)])
    d = ImageDraw.Draw(cv)
    for r in range(4):
        for c in range(3):
            d.rectangle([26 + c * 56, 60 + r * 44, 56 + c * 56, 86 + r * 44], fill=(250, 236, 190, 255))
    return lift(cv, 6)


PERSON = person(2401)
OFF1, OFF2 = office(2402, GREEN2), office(2403, (120, 110, 150))


def bar(w, h, color, seed):
    return lift(stack(w, h, [(piece(w, h, [(0, 0), (w, 0), (w, h), (0, h)], color, seed, 0, 0.6), 0, 0)]), 4)


# ── 장면 ────────────────────────────────────────────────────
class Scene:
    kicker, head, hl = "", "", ()

    def setup(self, i):
        self.i = i
        self.k = tag(self.kicker, 38, bg=GOLD, fg=INK, seed=2500 + i) if self.kicker else None
        self.h = title(self.head, self.hl, 2600 + i) if self.head else None

    def chrome(self, frame, lt, head_t=0.1):
        frame.paste(BG)
        if self.k:
            pop(frame, self.k, 70, 300, lt, 0.05)
        if self.h:
            pop(frame, self.h, 70, 366, lt, head_t)


class Hook(Scene):
    kicker = "오늘 밤 9:30 (한국시간)"
    head = "미국 9월\n고용보고서"
    hl = ("고용보고서",)

    def setup(self, i):
        super().setup(i)
        self.cover = photo(ROOT / "media/01-employment-report-cover.png", 920, 2701)
        self.check = photo(ROOT / "media/03-reading-checklist.png", 920, 2702)
        self.n1 = note("AI 생성 이미지 · 화면 속 막대는 실제 통계 아님", 2703)
        self.t1 = tag("발표 전 체크 4가지", 46, bg=GREEN, seed=2704)

    def draw(self, frame, lt):
        self.chrome(frame, lt)
        sw = wt(0, 9) - 0.25  # '발표문은 이 네 가지' → 블로그 체크리스트 이미지
        y = 640
        if lt < sw + 0.35:
            a = clamp(lt / 0.25) * (1 - clamp((lt - sw) / 0.35))
            blit(frame, self.cover, 70, y, s=1 + 0.03 * clamp(lt / sw), alpha=a)
            pop(frame, self.n1, 80, y + self.cover.h + 6, lt, 0.4) if lt < sw else None
        if lt >= sw:
            q = clamp((lt - sw) / 0.35)
            blit(frame, self.check, 70, y + (1 - out_cubic(q)) * 40, alpha=q)
            pop(frame, self.t1, 70, y + self.check.h + 20, lt, sw + 0.3)


class Base(Scene):
    kicker = "비교 기준 · 8월분 (9월 4일 발표)"
    head = "지난달 숫자"

    def setup(self, i):
        super().setup(i)
        self.c = [card("일자리", "+16.2만", "비농업 · 전월 대비", 2711),
                  card("실업률", "4.1%", "변동 없음", 2712, vc=RED),
                  card("시간당 임금", "+0.3%", "전월 대비 · 전년 +3.1%", 2713),
                  card("주당 근로", "34.4h", "민간 비농업 평균", 2714)]
        self.n = tag("9월 예상치 아님 · BLS 발표 수치", 34, bg=INK, seed=2715)

    def draw(self, frame, lt):
        self.chrome(frame, lt)
        ts = (wt(1, 6), wt(1, 11), wt(1, 13) + 0.3, wt(1, 14) + 0.3)
        for k, c in enumerate(self.c):
            pop(frame, c, 70 + (k % 2) * 490, 560 + (k // 2) * 340, lt, ts[k] - 0.1)
        pop(frame, self.n, 70, 1250, lt, wt(1, 0) + 0.4)


class Payroll(Scene):
    kicker = "① 비농업 고용"
    head = "일자리 수 ≠\n취업한 사람 수"
    hl = ("≠",)

    def setup(self, i):
        super().setup(i)
        self.t1 = tag("두 곳에서 일하면 일자리 2개로 집계될 수 있어요", 32, bg=GREEN, seed=2721)
        self.t2 = tag("업종별 증감은 B-1 표", 34, bg=INK, seed=2722)
        self.n = note("설명용 도식 · 실제 통계 아님", 2723)
        self.inds = ["업종 A", "업종 B", "업종 C", "업종 D", "업종 E"]
        self.lens = [0.55, -0.3, 0.9, 0.2, 0.6]
        self.bars = [bar(int(380 * abs(v)), 54, GREEN2 if v > 0 else RED, 2730 + k) for k, v in enumerate(self.lens)]

    def draw(self, frame, lt):
        self.chrome(frame, lt)
        t2 = wt(2, 10) - 0.2
        if lt < t2 + 0.3:
            a = 1 - clamp((lt - t2) / 0.3)
            layer = Image.new("RGBA", frame.size, (0, 0, 0, 0))
            pop(layer, OFF1, 140, 640, lt, wt(2, 3))
            pop(layer, OFF2, 700, 640, lt, wt(2, 3) + 0.15)
            pop(layer, PERSON, 480, 680, lt, wt(2, 0) + 0.3)
            if lt > wt(2, 4):
                d = ImageDraw.Draw(layer)
                p = clamp((lt - wt(2, 4)) / 0.5)
                for x1 in (340, 700):
                    xm = 540 + (x1 - 540) * p
                    d.line([(540, 800), (xm, 760)], fill=GOLD + (255,), width=8)
            pop(layer, self.t1, 70, 960, lt, wt(2, 5))
            if a < 1:
                layer.putalpha(layer.getchannel("A").point(lambda v, a=a: int(v * a)))
            frame.alpha_composite(layer)
        if lt >= t2:
            d = ImageDraw.Draw(frame)
            for k, (nm, v) in enumerate(zip(self.inds, self.lens)):
                y = 640 + k * 90
                q = out_cubic(prog(lt, t2 + 0.1 * k, 0.5))
                d.text((90, y + 6), nm, font=font(40), fill=INK)
                d.line([(560, y - 10), (560, y + 64)], fill=GREY + (255,), width=3)
                b = self.bars[k]
                ww = max(1, b.w * q)
                bx = 560 if v > 0 else 560 - ww
                if q > 0.02:
                    blit(frame, b, bx, y, sx=q, sy=1, anchor=(0 if v > 0 else 1, 0.5))
            pop(frame, self.t2, 70, 1110, lt, t2 + 0.5)
            pop(frame, self.n, 80, 1200, lt, t2 + 0.6)


class Unemp(Scene):
    kicker = "② 실업률"
    head = "참가율과 같이"
    hl = ("참가율",)

    def setup(self, i):
        super().setup(i)
        self.f = label("실업률 = 실업자 ÷ 경제활동인구", 50, fg=INK, bg=PAPER, seed=2741, elev=6, pad=(26, 14))
        self.f2 = tag("일 안 하는 모든 사람의 비율이 아니에요", 34, bg=GREEN, seed=2742)
        self.img = photo(ROOT / "media/02-two-surveys.png", 920, 2743)
        self.t = tag("다른 조사라 방향이 엇갈릴 수 있어요", 38, bg=RED, seed=2744)

    def draw(self, frame, lt):
        self.chrome(frame, lt)
        sw = wt(3, 5) - 0.2
        if lt < sw + 0.3:
            a = 1 - clamp((lt - sw) / 0.3)
            layer = Image.new("RGBA", frame.size, (0, 0, 0, 0))
            pop(layer, self.f, 70, 640, lt, wt(3, 1))
            pop(layer, self.f2, 70, 780, lt, wt(3, 2) + 0.4)
            if a < 1:
                layer.putalpha(layer.getchannel("A").point(lambda v, a=a: int(v * a)))
            frame.alpha_composite(layer)
        if lt >= sw:
            q = clamp((lt - sw) / 0.35)
            blit(frame, self.img, 70, 560 + (1 - out_cubic(q)) * 40, alpha=q)
            pop(frame, self.t, 70, 560 + self.img.h + 24, lt, wt(3, 10))


class Wage(Scene):
    kicker = "③ 임금"
    head = "전월 대비 ≠\n전년 대비"
    hl = ("≠",)

    def setup(self, i):
        super().setup(i)
        self.c1 = card("전월 대비", "+0.3%", "최근 1달 변화 · 8월", 2751, w=440)
        self.c2 = card("전년 대비", "+3.1%", "1년 전과 비교 · 8월", 2752, w=440, vc=GOLD)
        self.n = tag("민간 비농업 전체 근로자 · B-3 표", 34, bg=INK, seed=2753)
        self.n2 = note("개인 연봉 인상률과도 달라요", 2754, 32)

    def draw(self, frame, lt):
        self.chrome(frame, lt)
        pop(frame, self.c1, 70, 640, lt, wt(4, 2) - 0.1)
        pop(frame, self.c2, 570, 640, lt, wt(4, 4) - 0.1)
        pop(frame, self.n, 70, 1000, lt, wt(4, 7))
        pop(frame, self.n2, 80, 1090, lt, wt(4, 9))


class Revise(Scene):
    kicker = "④ 과거치 수정"
    head = "지난 숫자도\n바뀐다"
    hl = ("바뀐다",)

    def setup(self, i):
        super().setup(i)
        self.t1 = tag("6·7월 합계 +5.5만 상향 (9월 4일 발표)", 36, bg=GREEN, seed=2761)
        self.t2 = label("오늘 밤 메모: 9월 신규 · 7·8월 수정치", 42, fg=INK, bg=PAPER, seed=2762, elev=6, pad=(24, 12))
        self.n = note("막대 높이는 설명용 도식", 2763)

    def draw(self, frame, lt):
        self.chrome(frame, lt)
        d = ImageDraw.Draw(frame)
        base = 1060
        up = in_out(prog(lt, wt(5, 7), 0.8))
        for k, (m, h0, dh) in enumerate((("6월", 170, 70), ("7월", 120, 60), ("8월", 220, 0))):
            x = 170 + k * 280
            if lt < wt(5, 3) + 0.15 * k - 0.2 and k < 2:
                continue
            h = h0 + (dh * up if k < 2 else 0)
            if k < 2 and up > 0:  # 처음 값 점선 테두리
                for yy in range(int(base - h0), base, 18):
                    d.line([(x - 4, yy), (x - 4, yy + 9)], fill=GREY + (255,), width=3)
                d.line([(x - 4, base - h0), (x + 164, base - h0)], fill=GREY + (255,), width=3)
            d.rectangle([x, base - h, x + 160, base], fill=(GREEN2 if k < 2 else GREY) + (255,))
            d.text((x + 50, base + 14), m, font=font(40), fill=INK)
            if k < 2 and up > 0.5:
                d.polygon([(x + 80, base - h - 70), (x + 50, base - h - 30), (x + 110, base - h - 30)], fill=GOLD + (255,))
        d.line([(120, base), (960, base)], fill=INK + (255,), width=4)
        pop(frame, self.n, 80, base + 70, lt, wt(5, 3))
        pop(frame, self.t1, 70, 640, lt, wt(5, 7) + 0.3)
        pop(frame, self.t2, 70, 1230, lt, wt(5, 11))


class Close(Scene):
    kicker = "읽기와 매매는 구분"
    head = "보고서 하나가\n금리를 정하진 않아요"
    hl = ("정하진 않아요",)

    def setup(self, i):
        super().setup(i)
        self.t1 = tag("연준 목표: 최대고용 · 물가안정", 38, bg=GREEN, seed=2771)
        self.x = label("× 출처 불분명한 예상치", 46, fg=PAPER, bg=RED, seed=2772, elev=6, pad=(24, 10))
        self.o = label("○ 공식 발표문 (BLS)", 46, fg=PAPER, bg=GREEN, seed=2773, elev=6, pad=(24, 10))
        self.src = tag("출처: BLS 2026.9.4 발표문 · 투자 권유 아님", 28, bg=INK, seed=2774)

    def draw(self, frame, lt):
        self.chrome(frame, lt)
        pop(frame, self.t1, 70, 700, lt, wt(6, 2))
        pop(frame, self.x, 70, 840, lt, wt(6, 7))
        pop(frame, self.o, 70, 960, lt, wt(6, 10))
        pop(frame, self.src, 70, 1100, lt, wt(6, 12))


SCENES = [Hook(), Base(), Payroll(), Unemp(), Wage(), Revise(), Close()]
for _i, _s in enumerate(SCENES):
    _s.setup(_i)

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
        _cap[i] = label(wrap(txt, font(70), 880), 70, fg=PAPER, bg=GREEN, pad=(34, 14), seed=2900 + i, elev=5, align="center", amp=2.2)
    spr = _cap[i]
    p = prog(t, st, 0.16)
    blit(frame, spr, (W - spr.w) / 2, 1570 - spr.h + (1 - out_cubic(p)) * 14, alpha=clamp(p * 1.6))


TR = 0.4
YS = np.arange(H)[:, None]


def frame_at(t):
    i = max(k for k in range(len(SC)) if t >= SC[k]["start"] - 1e-6)
    lt = t - SC[i]["start"]
    fr = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    SCENES[i].draw(fr, lt)
    if i > 0 and lt < TR:  # 장부를 넘기듯 위에서 아래로
        old = Image.new("RGBA", (W, H), (0, 0, 0, 255))
        SCENES[i - 1].draw(old, t - SC[i - 1]["start"])
        edge = in_out(lt / TR) * (H + 40)
        m = YS < edge
        fr = Image.fromarray(np.where(np.repeat(m, W, 1)[..., None], np.asarray(fr), np.asarray(old)).astype(np.uint8), "RGBA")
        ImageDraw.Draw(fr).line([(0, edge), (W, edge)], fill=GOLD + (230,), width=6)
    draw_caption(fr, t)
    return fr


def main():
    OUT.mkdir(exist_ok=True)
    if "--still" in sys.argv:
        for ts in sys.argv[sys.argv.index("--still") + 1].split(","):
            frame_at(float(ts)).convert("RGB").save(OUT / f"still_{ts}.png")
        print("stills ok")
        return
    bgm, sfx = OUT / "bgm.wav", OUT / "sfx.wav"
    make_bgm(bgm, TOTAL, [[57, 60, 64, 67], [53, 57, 60, 64], [55, 59, 62, 65], [52, 55, 59, 62]], bpm=80, seed=24, bright=0.95)
    wind_sfx(sfx, TOTAL, [s["start"] for s in SC[1:]], length=0.35)
    nfr = int(math.ceil(TOTAL * FPS))
    dst = OUT / "final.mp4"
    fc = ("[1:a]apad,asplit=2[n1][n2];[2:a]volume=0.28[b];[b][n1]sidechaincompress=threshold=0.02:ratio=6:attack=30:release=400[bd];"
          "[3:a]volume=0.2[w];[n2][bd][w]amix=inputs=3:normalize=0:duration=longest[a]")
    cmd = ["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-i", str(ROOT / "audio/narration.mp3"), "-i", str(bgm), "-i", str(sfx), "-filter_complex", fc,
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
