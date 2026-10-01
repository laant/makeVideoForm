#!/usr/bin/env python3
"""opus-guri-cosmos — 2026 구리 코스모스 축제 (21번 · autoShorts/OpenMontage 판과 같은 나레이션).

종이공작: 복숭아빛 하늘 마분지 · 종이로 오린 분홍/자홍/흰 코스모스(8장 꽃잎)가 바람에 흔들리는 꽃밭 ·
한강 · 낮은 도시 실루엣 · 밤 무대와 종이 불꽃. 모든 사실은 구리시 공식 축제 사이트·포스터(2026-10-01 확인).
도구: ../paperkit.py · ../audiokit.py
  ../opus-paper-04/.venv/bin/python render.py [--still 1,9]
"""
import json, math, subprocess, sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent))
from paperkit import (W, H, FPS, font, paper, lift, blit, mask, poly, rrect, circle_pts, piece, stack, _paste_into,  # noqa: E402
                      label, clamp, prog, out_cubic, out_back, in_out, pop, wrap, full_bg, deckle)
from audiokit import make_bgm, wind_sfx  # noqa: E402

OUT = ROOT / "out"
TIM = json.loads((ROOT / "audio/timing.json").read_text())
SC = TIM["scenes"]
TAIL = 1.2
TOTAL = TIM["total"] + TAIL

SKY_T, SKY_B = (250, 214, 196), (226, 206, 236)
PINK, MAGENTA, WHITE_P, LPINK = (238, 120, 168), (200, 58, 128), (252, 244, 246), (246, 182, 206)
GREEN, GREEN_D = (110, 160, 92), (78, 128, 70)
RIVER = (150, 196, 226)
CREAM = (253, 247, 240)
INK = (60, 36, 48)
NAVY = (34, 36, 74)
GOLD = (246, 196, 90)


def wt(i, k):
    return SC[i]["words"][k]["start"]


def tag(text, size=42, bg=MAGENTA, fg=CREAM, seed=0):
    return label(text, size, fg=fg, bg=bg, pad=(22, 8), seed=seed, elev=5, amp=1.0)


def title(text, hl=(), seed=0, size=92):
    return label(text, size, fg=INK, bg=CREAM, hl=hl, hlc=MAGENTA, seed=seed, elev=8)


# ── 코스모스 한 송이 ────────────────────────────────────────
def cosmos(d_, color, seed):
    w = h = d_
    c = d_ / 2

    def fn(dr, s):
        for k in range(8):
            a = 2 * math.pi * k / 8 + seed * 0.3
            pts = []
            L, Wp = d_ * 0.47, d_ * 0.15
            for t in np.linspace(0, 1, 14):
                r = 0.12 * d_ + t * (L - 0.12 * d_)
                wdt = Wp * math.sin(math.pi * min(1, t * 1.15)) * (0.85 if t > 0.9 else 1)
                pts.append((r, wdt))
            tip = [(L, Wp * 0.35), (L - d_ * 0.03, 0), (L, -Wp * 0.35)]  # 끝이 톱니처럼 패인 꽃잎
            outline = pts + tip + [(x, -y) for x, y in reversed(pts)]
            poly(dr, s, [(c + x * math.cos(a) - y * math.sin(a), c + x * math.sin(a) + y * math.cos(a)) for x, y in outline])
    petals = paper(mask(w, h, fn), color, seed, 1 if d_ < 90 else 2)
    core = paper(mask(w, h, lambda dr, s: poly(dr, s, circle_pts(c, c, d_ * 0.11, 20))), GOLD, seed + 1, 1)
    petals.alpha_composite(core)
    return petals


FLOWERS = {}


def flower(d_, ci, seed):
    k = (d_, ci, seed % 6)
    if k not in FLOWERS:
        FLOWERS[k] = cosmos(d_, (PINK, MAGENTA, WHITE_P, LPINK)[ci], seed % 6 + 10 * ci)
    return FLOWERS[k]


def field_row(y_top, h_, n, size, seed, ground=True):
    """한 줄의 꽃밭(줄기+꽃) — 흔들림은 프레임마다 가로 기울이기로."""
    r = np.random.default_rng(seed)
    img = Image.new("RGBA", (W + 160, h_), (0, 0, 0, 0))
    if ground:
        g = piece(W + 160, h_, deckle([(0, h_ * 0.55), (W + 160, h_ * 0.5), (W + 160, h_), (0, h_)], 2, 8, seed), GREEN, seed, 0, 2.0)
        _paste_into(img, g, 0, 0)
    d = ImageDraw.Draw(img)
    items = []
    for _ in range(n):
        x = r.uniform(0, W + 160)
        top = r.uniform(0, h_ * 0.45)
        sz = int(size * r.uniform(0.75, 1.15))
        items.append((top, x, sz, int(r.integers(0, 4)), int(r.integers(0, 99))))
    for top, x, sz, ci, sd in sorted(items):
        d.line([(x, top + sz / 2), (x + r.uniform(-8, 8), h_)], fill=GREEN_D + (255,), width=max(2, sz // 22))
        f = flower(sz, ci, sd)
        img.alpha_composite(f, (int(x - sz / 2), int(top)))
    sh = Image.new("RGBA", img.size, (60, 30, 40, 0))
    sh.putalpha(img.getchannel("A").filter(ImageFilter.GaussianBlur(4)).point(lambda v: int(v * 0.25)))
    out = Image.new("RGBA", img.size, (0, 0, 0, 0))
    out.alpha_composite(sh, (3, 5))
    out.alpha_composite(img)
    return out, y_top


def sway(frame, row, t, amp, ph):
    img, y = row
    k = amp * math.sin(t * 1.4 + ph) / img.height
    tr = img.transform(img.size, Image.AFFINE, (1, k, -k * img.height, 0, 1, 0), Image.BICUBIC)
    frame.alpha_composite(tr.crop((80, 0, 80 + W, img.height)), (0, int(y)))


def sky(top, bot, seed):
    g = np.linspace(0, 1, H)[:, None, None]
    arr = (np.array(top, np.float32) * (1 - g) + np.array(bot, np.float32) * g) * np.ones((1, W, 1), np.float32)
    base = full_bg((255, 255, 255), seed)
    a = np.asarray(base, np.float32)
    a[..., :3] = a[..., :3] / 255 * arr
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGBA")


def landscape(night=False):
    B = sky((22, 26, 60), (60, 48, 100), 7) if night else sky(SKY_T, SKY_B, 7)
    mt = [(-20, 1000), (180, 880), (330, 930), (520, 820), (700, 900), (900, 860), (1100, 930), (1100, 1100), (-20, 1100)]
    _paste_into(B, piece(W, H, mt, (90, 80, 120) if night else (176, 160, 196), 8, 4, 1.0), 0, 0)
    r = np.random.default_rng(9)
    x = 0
    while x < W:
        bw, bh = int(r.integers(40, 90)), int(r.integers(60, 170))
        col = (70, 66, 104) if night else (214, 196, 214)
        _paste_into(B, piece(bw, bh, [(0, 0), (bw, 0), (bw, bh), (0, bh)], col, int(x) + 50, 2, 0.6), x, 1060 - bh)
        x += bw + int(r.integers(2, 10))
    _paste_into(B, piece(W, H, [(-20, 1058), (W + 20, 1050), (W + 20, 1130), (-20, 1140)], (70, 90, 140) if night else RIVER, 11, 3, 1.4), 0, 0)
    if night:
        d = ImageDraw.Draw(B)
        rr = np.random.default_rng(12)
        for _ in range(90):
            sx, sy = rr.uniform(0, W), rr.uniform(0, 800)
            d.ellipse([sx - 1.5, sy - 1.5, sx + 1.5, sy + 1.5], fill=(255, 250, 230, int(rr.uniform(120, 255))))
    return B


DAY, NIGHT = landscape(False), landscape(True)
ROWS = [field_row(1090, 260, 70, 70, 21), field_row(1220, 330, 46, 110, 22), field_row(1430, 520, 26, 170, 23)]

_rp = np.random.default_rng(41)
PETALS = [dict(spr=lift(cosmos(36, (PINK, MAGENTA, WHITE_P, LPINK)[int(_rp.integers(0, 4))], 70 + k), 2), x=float(_rp.uniform(0, W)), y=float(_rp.uniform(0, H)),
               vx=float(_rp.uniform(30, 80)), vy=float(_rp.uniform(40, 90)), rs=float(_rp.uniform(-90, 90))) for k in range(10)]


def petals(frame, t, n=10):
    for k, p in enumerate(PETALS[:n]):
        x = (p["x"] + p["vx"] * t) % (W + 100) - 50
        y = (p["y"] + p["vy"] * t + 30 * math.sin(t + k)) % (H + 100) - 50
        blit(frame, p["spr"], x, y, rot=p["rs"] * t, alpha=0.85)


def scene_bg(frame, t, night=False, field=True, n_petals=8):
    frame.paste(NIGHT if night else DAY)
    if field:
        for k, row in enumerate(ROWS):
            sway(frame, row, t, (10, 16, 26)[k], k)
    if not night:
        petals(frame, t, n_petals)


# ── 소품 ────────────────────────────────────────────────────
def day_card(dow, day, sub, color, seed):
    w, h = 270, 300
    cv = stack(w, h, [(piece(w, h, [(0, 0), (w, 0), (w, h), (0, h)], CREAM, seed, 0, 1.0), 0, 0),
                      (piece(w, 70, [(0, 0), (w, 0), (w, 70), (0, 70)], color, seed + 1, 1, 0.6), 0, 0)])
    d = ImageDraw.Draw(cv)
    d.text(((w - font(40).getlength(dow)) / 2, 12), dow, font=font(40), fill=CREAM)
    d.text(((w - font(130).getlength(day)) / 2, 82), day, font=font(130), fill=INK)
    d.text(((w - font(32).getlength(sub)) / 2, 245), sub, font=font(32, bold=False), fill=(130, 90, 110))
    return lift(cv, 8)


def pin(seed):
    w, h = 110, 150
    drop = [(55 + 50 * math.cos(math.radians(a)), 52 + 50 * math.sin(math.radians(a))) for a in range(150, 391, 8)] + [(55, 146)]
    return lift(stack(w, h, [(piece(w, h, drop, MAGENTA, seed, 0, 0.6), 0, 0), (piece(w, h, circle_pts(55, 52, 20), CREAM, seed + 1, 1, 0.3), 0, 0)]), 7)


def stage_spr(seed):
    w, h = 760, 420
    parts = [(piece(w, h, [(0, 120), (w, 120), (w, h), (0, h)], (52, 46, 86), seed, 0, 0.8), 0, 0),
             (piece(w, h, [(40, 150), (w - 40, 150), (w - 40, 330), (40, 330)], (24, 22, 48), seed + 1, 1, 0.6), 0, 0),
             (piece(w, h, [(0, 330), (w, 330), (w, h), (0, h)], (90, 70, 110), seed + 2, 1, 0.8), 0, 0),
             (piece(w, h, [(0, 90), (w, 90), (w, 126), (0, 126)], (60, 52, 96), seed + 3, 1, 0.5), 0, 0)]
    cv = stack(w, h, parts)
    d = ImageDraw.Draw(cv)
    for k in range(9):
        x = 60 + k * 80
        d.ellipse([x - 12, 96, x + 12, 120], fill=GOLD + (255,))
    return lift(cv, 8), cv


STAGE, _ = stage_spr(301)


def firework(frame, cx, cy, p, color):
    if p <= 0 or p >= 1:
        return
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    R = 40 + 200 * out_cubic(p)
    a = int(255 * (1 - p) ** 0.7)
    for k in range(16):
        ang = 2 * math.pi * k / 16
        x0, y0 = cx + math.cos(ang) * R * 0.55, cy + math.sin(ang) * R * 0.55
        x1, y1 = cx + math.cos(ang) * R, cy + math.sin(ang) * R + 30 * p * p
        d.line([(x0, y0), (x1, y1)], fill=color + (a,), width=7)
        d.ellipse([x1 - 7, y1 - 7, x1 + 7, y1 + 7], fill=color + (a,))
    frame.alpha_composite(ov.filter(ImageFilter.GaussianBlur(0.8)))


def mic(seed):
    w, h = 200, 520
    parts = [(piece(w, h, [(96, 150), (104, 150), (104, 470), (96, 470)], (70, 70, 80), seed, 2, 0.3), 0, 0),
             (piece(w, h, rrect(60, 20, 140, 170, 40), (90, 90, 104), seed + 1, 3, 0.4), 0, 0),
             (piece(w, h, [(40, 470), (160, 470), (170, 500), (30, 500)], (70, 70, 80), seed + 2, 2, 0.4), 0, 0)]
    cv = stack(w, h, parts)
    d = ImageDraw.Draw(cv)
    for y in range(40, 160, 18):
        d.line([(66, y), (134, y)], fill=(130, 130, 146, 255), width=3)
    return lift(cv, 8)


MIC = mic(401)


def bus(seed, color=(120, 170, 120)):
    w, h = 300, 150
    parts = [(piece(w, h, rrect(0, 10, w, 120, 24), color, seed, 0, 0.6), 0, 0),
             (piece(w, h, circle_pts(64, 122, 26, 20), (50, 50, 60), seed + 1, 1, 0.3), 0, 0),
             (piece(w, h, circle_pts(236, 122, 26, 20), (50, 50, 60), seed + 2, 1, 0.3), 0, 0)]
    for k in range(4):
        parts.append((piece(w, h, rrect(24 + k * 64, 26, 74 + k * 64, 64, 8), (210, 230, 244), seed + 3 + k, 1, 0.3, 1), 0, 0))
    return lift(stack(w, h, parts), 6)


BUS = bus(501)
SHUTTLE = bus(511, color=MAGENTA)


# ── 장면 ────────────────────────────────────────────────────
class Scene:
    kicker, head, hl = "", "", ()

    def setup(self, i):
        self.i = i
        self.k = tag(self.kicker, 38, bg=MAGENTA, seed=7000 + i) if self.kicker else None
        self.h = title(self.head, self.hl, 7100 + i) if self.head else None

    def chrome(self, frame, lt, head_t=0.2):
        if self.k:
            pop(frame, self.k, 70, 300, lt, 0.05)
        if self.h:
            pop(frame, self.h, 70, 362, lt, head_t)


class Hook(Scene):
    kicker = "2026 구리 코스모스 축제"
    head = "축구장 11개 꽃밭,\n딱 사흘만"
    hl = ("사흘만",)

    def setup(self, i):
        super().setup(i)
        self.area = tag("꽃단지 79,620㎡ ≈ 축구장 11개", 40, bg=(120, 80, 140), seed=7201)

    def draw(self, frame, lt):
        scene_bg(frame, lt)
        self.chrome(frame, lt, 0.15)
        pop(frame, self.area, 70, 660, lt, wt(0, 1))


class When(Scene):
    kicker = "꽃멍하러 구리로 ON"

    def setup(self, i):
        super().setup(i)
        self.cards = [day_card(d, n, s, c, 7300 + k) for k, (d, n, s, c) in
                      enumerate((("금", "9", "전야제", PINK), ("토", "10", "개막식", MAGENTA), ("일", "11", "폐막식", (150, 80, 160))))]
        self.place = tag("구리한강시민공원", 52, bg=INK, seed=7310)
        self.pin = pin(7311)
        self.yr = label("2026. 10월", 70, fg=INK, bg=CREAM, seed=7312, elev=7, pad=(26, 10))

    def draw(self, frame, lt):
        scene_bg(frame, lt)
        self.chrome(frame, lt)
        pop(frame, self.yr, 70, 380, lt, wt(1, 0))
        for k in range(3):
            pop(frame, self.cards[k], 70 + k * 320, 540, lt, wt(1, 4) + k * 0.25)
        pop(frame, self.pin, 470, 880, lt, wt(1, 7) - 0.2)
        pop(frame, self.place, (W - self.place.w) / 2, 1040, lt, wt(1, 7))


class Area(Scene):
    kicker = "더 넓어진 꽃단지"
    head = "+11,940㎡"
    hl = ("+11,940㎡",)

    def setup(self, i):
        super().setup(i)
        self.l1 = tag("작년 67,680㎡", 40, bg=(150, 120, 150), seed=7401)
        self.l2 = tag("올해 79,620㎡", 46, bg=MAGENTA, seed=7402)
        self.src = tag("구리시 발표 (일간경기 보도) · 작년 = 올해 − 늘어난 면적", 26, bg=INK, seed=7403)

    def draw(self, frame, lt):
        scene_bg(frame, lt, n_petals=4)
        self.chrome(frame, lt, 0.1)
        # 면적 비교 막대 (같은 축척: 79,620㎡ = 900px)
        x0, y0, hh = 90, 640, 90
        w_old = 900 * 67680 / 79620
        g = out_cubic(prog(lt, wt(2, 1), 0.7))
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(ov)
        if g > 0:
            d.rounded_rectangle([x0, y0, x0 + w_old * g, y0 + hh], 16, fill=(186, 160, 186, 255))
            grow = clamp((lt - wt(2, 2)) / 0.8)
            d.rounded_rectangle([x0, y0 + 150, x0 + (w_old + (900 - w_old) * out_cubic(grow)) * g, y0 + 150 + hh], 16, fill=PINK + (255,))
        frame.alpha_composite(ov)
        pop(frame, self.l1, x0, y0 + hh + 6, lt, wt(2, 1))
        pop(frame, self.l2, x0, y0 + 150 + hh + 6, lt, wt(2, 2))
        pop(frame, self.src, 70, 1010, lt, wt(2, 6))


class Night(Scene):
    kicker = "매일 밤 7시"
    head = "꽃밭 옆 무대"

    def setup(self, i):
        super().setup(i)
        self.sat = label("토 개막식\n양파 · 김다현 외", 46, fg=INK, bg=CREAM, seed=7501, elev=6, pad=(24, 10))
        self.sun = label("일 폐막식\n홍이삭 · 박혜신 외", 46, fg=INK, bg=CREAM, seed=7502, elev=6, pad=(24, 10))
        self.fire = tag("일요일 불꽃쇼", 50, bg=GOLD, fg=INK, seed=7503)
        self.src = tag("출연진: 구리시 공식 포스터", 26, bg=NAVY, seed=7504)

    def draw(self, frame, lt):
        scene_bg(frame, lt, night=True)
        t0 = wt(3, 13) - 0.2
        if lt > t0:  # 불꽃은 글자 카드 뒤
            for k, (cx, cy, c) in enumerate(((300, 420, PINK), (780, 380, GOLD), (540, 300, (180, 220, 255)), (200, 300, GOLD))):
                firework(frame, cx, cy, ((lt - t0 - k * 0.35) % 1.6) / 1.6 if lt - t0 - k * 0.35 > 0 else 0, c)
        self.chrome(frame, lt, 0.1)
        blit(frame, STAGE, 160, 760)
        if lt > wt(3, 4):
            ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            d = ImageDraw.Draw(ov)
            for k, cx in enumerate((300, 540, 780)):
                sw = 60 * math.sin(lt * 1.6 + k)
                d.polygon([(cx, 880), (cx - 120 + sw, 1180), (cx + 120 + sw, 1180)], fill=(255, 236, 190, 50))
            frame.alpha_composite(ov.filter(ImageFilter.GaussianBlur(6)))
        pop(frame, self.sat, 70, 500, lt, wt(3, 6))
        pop(frame, self.sun, 560, 500, lt, wt(3, 9))
        pop(frame, self.fire, 70, 700, lt, wt(3, 13))
        pop(frame, self.src, 70, 1330, lt, wt(3, 12))


class Song(Scene):
    kicker = "10월 10일(토) 오후 4시"
    head = "전국 코스모스\n가요제"
    hl = ("가요제",)

    def setup(self, i):
        super().setup(i)
        self.t1 = tag("축제장 메인무대", 44, bg=(120, 80, 140), seed=7601)

    def draw(self, frame, lt):
        scene_bg(frame, lt)
        self.chrome(frame, lt, 0.1)
        pop(frame, MIC, 440, 640, lt, 0.3)
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(ov)
        for k in range(3):  # 음표 대신 소리 물결
            ph = (lt * 0.8 + k / 3) % 1
            r = 80 + ph * 220
            d.arc([540 - r, 720 - r, 540 + r, 720 + r], -60, 60, fill=MAGENTA + (int(220 * (1 - ph)),), width=6)
            d.arc([540 - r, 720 - r, 540 + r, 720 + r], 120, 240, fill=MAGENTA + (int(220 * (1 - ph)),), width=6)
        frame.alpha_composite(ov)
        pop(frame, self.t1, 70, 1000, lt, wt(4, 4))


class Transit(Scene):
    kicker = "대중교통으로"
    head = "8호선 + 마을버스"
    hl = ("마을버스",)

    def setup(self, i):
        super().setup(i)
        self.st = tag("8호선 장자호수공원역 인근", 38, bg=(120, 80, 140), seed=7701)
        self.fe = tag("축제장", 44, bg=MAGENTA, seed=7702)
        self.sh = tag("공원 안 무료 셔틀 · 10~23시", 40, bg=INK, seed=7703)
        self.mb = tag("마을버스 연장 운행 · 09~23시", 34, bg=(90, 130, 90), seed=7704)

    def draw(self, frame, lt):
        scene_bg(frame, lt, n_petals=4)
        self.chrome(frame, lt, 0.1)
        x0, x1, y = 120, 900, 760
        p = in_out(prog(lt, wt(5, 6) - 0.3, 2.0))
        d = ImageDraw.Draw(frame)
        d.line([(x0, y), (x1, y)], fill=INK + (255,), width=8)
        for x in range(x0, x1, 40):
            d.line([(x, y), (x + 20, y)], fill=CREAM + (255,), width=4)
        pop(frame, self.st, 60, 640, lt, wt(5, 4))
        pop(frame, self.fe, 820, 640, lt, wt(5, 7))
        if lt > wt(5, 6) - 0.4:
            blit(frame, BUS, x0 - 40 + (x1 - x0 - 200) * p, y - 140)
            pop(frame, self.mb, 60, 820, lt, wt(5, 6))
        if lt > wt(5, 9) - 0.3:
            q = (lt - wt(5, 9)) * 120
            blit(frame, SHUTTLE, -300 + (q % (W + 600)), 960)
            pop(frame, self.sh, 60, 900, lt, wt(5, 11))


class Visit(Scene):
    head = "꽃멍하러\n구리로 ON"
    hl = ("ON",)

    def setup(self, i):
        super().setup(i)
        self.h = label(self.head, 120, fg=INK, bg=CREAM, hl=self.hl, hlc=MAGENTA, seed=7801, elev=9, pad=(40, 20))
        self.info = tag("10.9 금 ~ 10.11 일 · 구리한강시민공원", 42, bg=MAGENTA, seed=7802)
        self.src = tag("출처: 구리시 코스모스 축제 공식 사이트 (2026.10.01 확인)", 26, bg=INK, seed=7803)

    def draw(self, frame, lt):
        scene_bg(frame, lt, n_petals=10)
        pop(frame, self.h, 70, 380, lt, 0.1, dur=0.5)
        pop(frame, self.info, 70, 760, lt, wt(6, 3))
        pop(frame, self.src, 70, 850, lt, wt(6, 6))


SCENES = [Hook(), When(), Area(), Night(), Song(), Transit(), Visit()]
for _i, _s in enumerate(SCENES):
    _s.setup(_i)

CAPS = [
    [("한강변에 축구장 11개 크기 코스모스 꽃밭이,", 0), ("딱 사흘만 열려요.", 7)],
    [("2026 구리 코스모스 축제,", 0), ("10월 9일부터 11일까지,", 4), ("구리한강시민공원이에요.", 7)],
    [("꽃밭은 작년보다 1만2천㎡ 가까이", 0), ("더 넓어졌어요.", 6)],
    [("밤 7시엔 매일 무대가 열려요.", 0), ("토요일엔 양파, 김다현,", 6), ("일요일엔 홍이삭, 박혜신,", 9), ("그리고 불꽃쇼까지.", 12)],
    [("토요일 오후 4시엔", 0), ("전국 코스모스 가요제도 열려요.", 4)],
    [("대중교통도 편해요.", 0), ("8호선 장자호수공원역 근처에서", 2), ("마을버스가 축제장까지 다니고,", 6), ("공원 안엔 무료 셔틀도 있어요.", 9)],
    [("꽃멍하러 구리로.", 0), ("올가을, 구리 코스모스 축제에 방문해 보세요.", 2)],
]
CAP_TL = sorted((SC[i]["start"] + wt(i, k), txt) for i, pages in enumerate(CAPS) for txt, k in pages)
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
        _cap[i] = label(wrap(txt, font(70), 880), 70, fg=INK, bg=CREAM, pad=(34, 14), seed=7900 + i, elev=5, align="center", amp=2.2)
    spr = _cap[i]
    p = prog(t, st, 0.16)
    blit(frame, spr, (W - spr.w) / 2, 1570 - spr.h + (1 - out_cubic(p)) * 14, alpha=clamp(p * 1.6))


# ── 전환: 꽃잎이 흩날리며 넘어간다 ──────────────────────────
TR = 0.45
_rb = np.random.default_rng(55)
BURST = [(lift(cosmos(int(_rb.integers(90, 160)), (PINK, MAGENTA, WHITE_P, LPINK)[int(_rb.integers(0, 4))], 90 + k), 4), float(_rb.uniform(0, H))) for k in range(14)]
XS = np.arange(W)[None, :]
YS = np.arange(H)[:, None]


def frame_at(t):
    i = max(k for k in range(len(SC)) if t >= SC[k]["start"] - 1e-6)
    lt = t - SC[i]["start"]
    fr = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    SCENES[i].draw(fr, lt)
    if i > 0 and lt < TR:
        old = Image.new("RGBA", (W, H), (0, 0, 0, 255))
        SCENES[i - 1].draw(old, t - SC[i - 1]["start"])
        p = in_out(lt / TR)
        edge = p * (W + 400) - 200 + 70 * np.sin(YS / 120.0)
        fr = Image.fromarray(np.where((XS < edge)[..., None], np.asarray(fr), np.asarray(old)).astype(np.uint8), "RGBA")
        for k, (spr, y) in enumerate(BURST):
            x = p * (W + 400) - 200 + 70 * math.sin(y / 120.0) - spr.w / 2 + (k % 3) * 40
            blit(fr, spr, x, y - 60, rot=k * 37 + p * 200)
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
    make_bgm(bgm, TOTAL, [[60, 64, 67, 71], [65, 69, 72, 76], [62, 65, 69, 72], [67, 71, 74, 77]], bpm=84, seed=21, bright=1.1)
    wind_sfx(sfx, TOTAL, [s["start"] for s in SC[1:]], length=0.4)
    nfr = int(math.ceil(TOTAL * FPS))
    dst = OUT / "final.mp4"
    fc = ("[1:a]apad,asplit=2[n1][n2];[2:a]volume=0.30[b];[b][n1]sidechaincompress=threshold=0.02:ratio=6:attack=30:release=400[bd];"
          "[3:a]volume=0.18[w];[n2][bd][w]amix=inputs=3:normalize=0:duration=longest[a]")
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
