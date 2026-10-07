#!/usr/bin/env python3
"""opus-autumn-handcream — 가을 핸드크림 고르는 법 (쇼핑커넥트 글 기반 구매 가이드).

가을 질감: 크라프트지 바탕 · 말린 단풍/은행잎 종이 콜라주 · 니트 띠 · 벽돌·머스터드·버건디·올리브.
이미지 생성 없이 전부 코드로 그린다 (도구: ../paperkit.py). 음성·단어 시각: tts.py → audio/.
  ../opus-paper-04/.venv/bin/python render.py              # → out/final.mp4
  ../opus-paper-04/.venv/bin/python render.py --still 1,9  # → out/still_<t>.png
"""
import json, math, subprocess, sys, wave
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # experiments/
from paperkit import (W, H, FPS, font, paper, Sprite, lift, blit, _paste, mask, poly, deckle, rrect, circle_pts,  # noqa: E402
                      piece, stack, _paste_into, label, clamp, prog, out_cubic, out_back, in_out, pop, wrap, full_bg, TEX)

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "out"
SCRIPT = json.loads((ROOT / "script.json").read_text())
TIM = json.loads((ROOT / "audio/timing.json").read_text())
SC = TIM["scenes"]
TOTAL = TIM["total"]

KRAFT = (203, 167, 121)
CREAM = (247, 238, 220)
BRICK = (188, 84, 44)
MUST = (214, 158, 60)
BURG = (120, 40, 46)
OLIVE = (108, 114, 64)
BROWN = (104, 70, 46)
INK = (56, 38, 28)
LEAFC = [BRICK, MUST, BURG, (200, 120, 50), OLIVE, (226, 186, 80)]


def wt(i, k):
    return SC[i]["words"][k]["start"]


# ── 가을 소품 ───────────────────────────────────────────────
MAPLE = [(0.5, 0.0), (0.56, 0.16), (0.66, 0.1), (0.63, 0.3), (0.82, 0.18), (0.78, 0.3), (0.98, 0.33), (0.86, 0.45),
         (0.92, 0.55), (0.72, 0.6), (0.76, 0.72), (0.58, 0.66), (0.54, 0.8), (0.46, 0.8), (0.42, 0.66), (0.24, 0.72),
         (0.28, 0.6), (0.08, 0.55), (0.14, 0.45), (0.02, 0.33), (0.22, 0.3), (0.18, 0.18), (0.37, 0.3), (0.34, 0.1), (0.44, 0.16)]


def _veins(d, s, sz, lines, color, width):
    for (x0, y0), (x1, y1) in lines:
        d.line([(x0 * sz * s, y0 * sz * s), (x1 * sz * s, y1 * sz * s)], fill=color, width=max(1, int(width * s)))


def leaf(sz, color, seed, kind="maple", elev=4):
    def shape(d, s):
        if kind == "maple":
            poly(d, s, deckle([(x * sz, y * sz) for x, y in MAPLE], sz * 0.006, 5, seed))
            d.line([(0.5 * sz * s, 0.78 * sz * s), (0.52 * sz * s, 1.0 * sz * s)], fill=255, width=max(2, int(sz * 0.035 * s)))
        else:  # 은행잎: 부채꼴 + 가운데 홈
            cx, cy, r = 0.5 * sz, 0.66 * sz, 0.5 * sz
            pts = [(cx, cy)]
            for i in range(41):
                a = math.radians(205 + 130 * i / 40)
                rr = r * (1 + 0.03 * math.sin(i * 1.7)) * (0.82 if 19 <= i <= 21 else 1)
                pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
            poly(d, s, pts)
            d.line([(cx * s, cy * s), (cx * s, sz * s)], fill=255, width=max(2, int(sz * 0.03 * s)))
    m = mask(sz, sz, shape)
    img = paper(m, color, seed, 1 if sz < 90 else 2)
    dr = ImageDraw.Draw(img)
    dark = tuple(int(c * 0.72) for c in color) + (150,)
    if kind == "maple":
        tips = [(0.5, 0.06), (0.9, 0.34), (0.1, 0.34), (0.72, 0.62), (0.28, 0.62)]
        _veins(dr, 1, sz, [((0.5, 0.74), t) for t in tips], dark, sz * 0.012)
    else:
        _veins(dr, 1, sz, [((0.5, 0.66), (0.5 + 0.44 * math.cos(math.radians(a)), 0.66 + 0.44 * math.sin(math.radians(a))))
                            for a in range(212, 334, 12)], dark, sz * 0.006)
    return lift(img, elev)


def knit_band(w, h, color, seed):
    """니트 띠 — 코마다 기울어진 두 가닥(V)이 세로로 이어진 메리야스 뜨기. 가닥별 입체 음영."""
    cw, ch, ang = 34, 30, math.radians(32)
    ys, xs = np.mgrid[0:h, 0:w].astype(np.float32)
    lx, ly = xs % cw, ys % ch
    bright = np.zeros((h, w), np.float32)
    for dy in (-ch, 0, ch):
        for side in (-1, 1):
            cx, cy = cw / 2 + side * cw * 0.2, ch / 2 + dy
            upx, upy = side * math.sin(ang), -math.cos(ang)
            dx_, dy_ = lx - cx, ly - cy
            v = dx_ * upx + dy_ * upy
            u = dx_ * -upy + dy_ * upx
            e = (u / (cw * 0.19)) ** 2 + (v / (ch * 0.62)) ** 2
            bright = np.maximum(bright, np.sqrt(np.clip(1 - e, 0, 1)))
    f = TEX[:h, :w]
    shade = np.where(bright > 0, 0.5 + 0.62 * bright, 0.32) * f
    rgb = np.array(color, np.float32)[None, None, :] * shade[..., None]
    img = Image.fromarray(np.dstack([np.clip(rgb, 0, 255), np.full((h, w), 255, np.float32)]).astype(np.uint8), "RGBA")
    top = mask(w, h, lambda d, s: poly(d, s, deckle([(0, 6), (w, 0), (w, h), (0, h)], 3, 6, seed)))
    img.putalpha(top)
    return lift(img, 8)


def tube(w=150, h=420, body=CREAM, band=MUST, cap=BRICK, seed=0, text="hand cream"):
    cr = 26
    parts = [
        (piece(w, h, [(w * 0.2, h - 78), (w * 0.8, h - 78), (w * 0.8, h), (w * 0.2, h)], cap, seed + 1, 2, 0.4), 0, 0),
        (piece(w, h, [(0, cr), (w, cr), (w * 0.84, h - 76), (w * 0.16, h - 76)], body, seed + 2, 2, 0.8), 0, 0),
        (piece(w, cr + 2, [(0, 0), (w, 0), (w, cr + 2), (0, cr + 2)], tuple(int(c * 0.93) for c in body), seed + 3, 1, 0.5), 0, 0),
        (piece(w, 120, [(8, 0), (w - 8, 0), (w - 16, 120), (16, 120)], band, seed + 4, 1, 0.6), 0, 130),
    ]
    cv = stack(w, h, parts)
    d = ImageDraw.Draw(cv)
    for x in range(8, w - 6, 10):
        d.line([(x, 4), (x, cr - 4)], fill=(150, 140, 125, 160), width=2)
    f = font(int(w * 0.15))
    for i, word in enumerate(text.split(" ")):
        d.text(((w - f.getlength(word)) / 2, 150 + i * w * 0.18), word, font=f, fill=CREAM if band != CREAM else INK)
    return lift(cv, 7)


def pump(w=230, h=560, body=CREAM, band=BURG, seed=0, text="hand cream"):
    parts = [
        (piece(w, h, rrect(0, 170, w, h, 36), body, seed + 1, 2, 0.8), 0, 0),
        (piece(w, h, [(w * 0.38, 118), (w * 0.62, 118), (w * 0.62, 176), (w * 0.38, 176)], (170, 160, 150), seed + 2, 1, 0.3), 0, 0),
        (piece(w, h, [(w * 0.46, 80), (w * 0.54, 80), (w * 0.54, 122), (w * 0.46, 122)], (230, 226, 218), seed + 3, 1, 0.2), 0, 0),
        (piece(w, h, [(w * 0.02, 44), (w * 0.62, 44), (w * 0.62, 86), (w * 0.3, 86), (w * 0.3, 66), (w * 0.02, 66)], (240, 236, 228), seed + 4, 2, 0.3), 0, 0),
        (piece(w, 170, [(0, 0), (w, 0), (w, 170), (0, 170)], band, seed + 5, 1, 0.6), 0, 300),
    ]
    cv = stack(w, h, parts)
    d = ImageDraw.Draw(cv)
    f = font(int(w * 0.13))
    for i, word in enumerate(text.split(" ")):
        d.text(((w - f.getlength(word)) / 2, 330 + i * w * 0.16), word, font=f, fill=CREAM)
    return lift(cv, 8)


def tag(text, size=44, bg=BRICK, fg=CREAM, seed=0, tilt=0.0):
    return label(text, size, fg=fg, bg=bg, pad=(22, 8), seed=seed, elev=4, tilt=tilt, amp=1.0)


def title(text, size=88, hl=(), seed=0):
    return label(text, size, fg=INK, bg=CREAM, hl=hl, hlc=BRICK, seed=seed, elev=7)


def hang_tag(lines, sub, color, seed, w=380, h=300):
    """끈 구멍 있는 크라프트 택."""
    pts = [(40, 0), (w, 0), (w, h), (40, h), (0, h * 0.62), (0, h * 0.38)]
    cv = stack(w, h, [(piece(w, h, pts, color, seed, 0, 1.0), 0, 0)])
    d = ImageDraw.Draw(cv)
    d.ellipse([22, h / 2 - 14, 50, h / 2 + 14], fill=(0, 0, 0, 0))
    d.ellipse([22, h / 2 - 14, 50, h / 2 + 14], outline=(120, 90, 60, 255), width=3)
    f1, f2 = font(64), font(38, bold=False)
    y = 70
    for ln in lines:
        d.text((80, y), ln, font=f1, fill=INK)
        y += 78
    d.text((80, y + 6), sub, font=f2, fill=(110, 84, 62))
    return lift(cv, 7)


def full_bg_kraft(seed):
    return full_bg(KRAFT, seed)


# ── 공통 배경 · 낙엽 ────────────────────────────────────────
BG = full_bg_kraft(1)
KNIT = knit_band(W + 40, 250, MUST, 7)
_paste_into(BG, KNIT, -20, 1690)
DISC = tag(SCRIPT["disclosure"], 30, bg=INK, fg=CREAM, seed=3)


def corner_leaves(seed, spots):
    r = np.random.default_rng(seed)
    out = []
    for i, (x, y, sz) in enumerate(spots):
        kind = "ginkgo" if r.random() < 0.35 else "maple"
        col = LEAFC[int(r.integers(0, len(LEAFC)))] if kind == "maple" else (226, 186, 80)
        spr = leaf(sz, col, seed * 10 + i, kind)
        out.append((spr, x, y, float(r.uniform(-60, 60))))
    return out


def bake(base, items):
    img = base.copy()
    for spr, x, y, rot in items:
        tmp = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        blit(tmp, spr, x, y, rot=rot)
        img.alpha_composite(tmp)
    return img


FALL = []
_r = np.random.default_rng(99)
for i in range(9):
    kind = "ginkgo" if i % 3 == 0 else "maple"
    col = (226, 186, 80) if kind == "ginkgo" else LEAFC[i % len(LEAFC)]
    FALL.append(dict(spr=leaf(int(_r.integers(46, 78)), col, 500 + i, kind, 3), x=float(_r.uniform(0, W)), y=float(_r.uniform(0, H)),
                     v=float(_r.uniform(55, 95)), a=float(_r.uniform(25, 60)), w=float(_r.uniform(0.6, 1.3)), rs=float(_r.uniform(-50, 50))))


def falling(frame, t, extra=1.0):
    for k, L in enumerate(FALL):
        if extra < 1 and k % 2:
            continue
        y = (L["y"] + L["v"] * t) % (H + 240) - 120
        x = L["x"] + L["a"] * math.sin(t * L["w"] + k)
        blit(frame, L["spr"], x, y, rot=L["rs"] * t + k * 40, alpha=0.92)


# ── 장면 ────────────────────────────────────────────────────
class Scene:
    kicker = ""
    head = ""
    hl = ()
    decor = []

    def setup(self, i):
        self.i = i
        self.base = bake(BG, corner_leaves(40 + i, self.decor))
        self.k = tag(self.kicker, 40, seed=100 + i) if self.kicker else None
        self.h = title(self.head, hl=self.hl, seed=200 + i) if self.head else None

    def bg(self, frame):
        frame.paste(self.base)
        falling(frame, CUR[0], 1.0 if self.i in (0, 8) else 0.5)

    def chrome(self, frame, lt, head_t=0.3):
        if isinstance(self, Products):  # 광고 고지는 제품이 나오는 컷에만
            blit(frame, DISC, 70, 272)
        if self.k:
            pop(frame, self.k, 70, 336, lt, 0.05)
        if self.h:
            pop(frame, self.h, 70, 400, lt, head_t)


class Hook(Scene):
    decor = [(900, 300, 150), (960, 560, 110), (-40, 1180, 170), (860, 1260, 190), (120, 1330, 140), (620, 1330, 160), (380, 1250, 150)]
    head = "가을 핸드크림,\n향만 보고 고르세요?"
    hl = ("향만",)
    kicker = "구매 가이드"

    def setup(self, i):
        super().setup(i)
        self.tube = tube(170, 470, seed=11)

    def draw(self, frame, lt):
        self.bg(frame)
        p = out_back(prog(lt, 0.1, 0.6), 1.2)
        blit(frame, self.tube, 450, 820 - (1 - p) * 500, rot=-18, anchor=(0.5, 0.5), alpha=clamp(p * 3))
        self.chrome(frame, lt, 0.2)


class Scent(Scene):
    decor = [(940, 700, 130), (-50, 1300, 150), (930, 1330, 140)]
    kicker = "① 향"
    head = "'무향' 표시만\n믿지 마세요"
    hl = ("'무향'",)

    def setup(self, i):
        super().setup(i)
        self.a = hang_tag(["무향"], "unscented", (232, 214, 184), 21, 380, 250)
        self.b = hang_tag(["향료 무첨가"], "fragrance-free", (236, 222, 190), 22, 480, 250)
        self.neq = label("≠", 110, fg=BRICK, bg=CREAM, seed=23, elev=5, pad=(22, 0))
        self.note = tag("냄새를 가리는 성분이 들 수 있어요", 40, bg=BURG, seed=24)
        self.aad = tag("미국피부과학회(AAD)는 '향료 무첨가'를 권해요", 34, bg=OLIVE, seed=25)

    def draw(self, frame, lt):
        self.bg(frame)
        self.chrome(frame, lt)
        pop(frame, self.a, 70, 720, lt, wt(1, 1) - 0.1, anchor=(0.5, 0.5))
        pop(frame, self.neq, 470, 740, lt, wt(1, 3), anchor=(0.5, 0.5))
        pop(frame, self.b, 530, 990, lt, wt(1, 3) + 0.2, anchor=(0.5, 0.5))
        pop(frame, self.note, 70, 1000, lt, wt(1, 5))
        pop(frame, self.aad, 70, 1290, lt, wt(1, 9))


class Ingredients(Scene):
    decor = [(960, 380, 120), (-40, 1350, 140)]
    kicker = "① 향 — 전성분 확인"
    head = "전성분에서\n이 이름 찾기"

    LINES = ["정제수, 글리세린, 시어버터,", "세테아릴알코올, 디메치콘,", "향료, 리날룰, 리모넨, ..."]

    def setup(self, i):
        super().setup(i)
        w, h = 900, 480
        cv = stack(w, h, [(piece(w, h, [(0, 0), (w, 0), (w, h), (0, h)], CREAM, 31, 0, 1.0), 0, 0)])
        d = ImageDraw.Draw(cv)
        d.text((40, 30), "전성분 (예시)", font=font(40), fill=(130, 100, 76))
        d.line([(40, 92), (w - 40, 92)], fill=(180, 150, 120, 255), width=2)
        f = font(52)
        self.hits = {}
        for r, ln in enumerate(self.LINES):
            y = 130 + r * 88
            x = 40
            for tok in ln.split(" "):
                word = tok.strip(",")
                is_hit = word in ("향료", "리날룰", "리모넨")
                d.text((x, y), tok, font=f, fill=BRICK if is_hit else INK)
                if is_hit:
                    self.hits[word] = (x, y, f.getlength(word))
                x += f.getlength(tok + " ")
        self.card = lift(cv, 8)
        self.cx, self.cy = 90, 700
        self.rule = tag("알레르기 유발 향료 성분 25종 — 전성분 표시 의무", 36, bg=OLIVE, seed=32)
        self.src = tag("씻어내지 않는 제품 0.001% 초과 시 (2020~)", 30, bg=INK, seed=33)

    def ring(self, frame, word, p):
        if p <= 0:
            return
        x, y, w = self.hits[word]
        x += self.cx + self.card.ox * 0 + 0
        y += self.cy
        d = ImageDraw.Draw(frame)
        box = [x - 16, y - 6, x + w + 16, y + 70]
        d.arc(box, -200, -200 + 360 * out_cubic(p), fill=BRICK + (255,), width=6)

    def draw(self, frame, lt):
        self.bg(frame)
        self.chrome(frame, lt)
        pop(frame, self.card, self.cx, self.cy, lt, 0.2, dur=0.5)
        for word, k in (("향료", 1), ("리날룰", 2), ("리모넨", 3)):
            self.ring(frame, word, prog(lt, wt(2, k), 0.35))
        pop(frame, self.rule, 70, 1230, lt, wt(2, 5))
        pop(frame, self.src, 70, 1310, lt, wt(2, 6))


class Place(Scene):
    decor = [(-40, 640, 120), (960, 1330, 140)]
    kicker = "② 둘 곳"
    head = "둘 곳부터\n정하세요"

    def setup(self, i):
        super().setup(i)
        bw, bh = 420, 470
        bag_pts = [(20, 130), (bw - 20, 130), (bw, bh), (0, bh)]
        handle = mask(bw, bh, lambda d, s: d.arc([110 * s, 20 * s, (bw - 110) * s, 240 * s], 180, 360, fill=255, width=int(22 * s)))
        hsp = lift(paper(handle, (150, 64, 34), 41, 1), 3)
        t = tube(120, 330, band=OLIVE, seed=42)
        self.bag = lift(stack(bw, bh, [(hsp, 0, 0), (t, 150, 20), (piece(bw, bh, bag_pts, BRICK, 43, 0, 1.2), 0, 0)]), 8)
        dw, dh = 440, 520
        desk = piece(dw, 70, [(0, 0), (dw, 0), (dw, 70), (0, 70)], BROWN, 44, 0, 0.8)
        mug = piece(120, 130, rrect(0, 0, 100, 130, 14) + [(100, 30), (120, 40), (120, 90), (100, 100)], OLIVE, 45, 0, 0.6)
        pm = pump(190, 450, seed=46)
        self.desk = lift(stack(dw, dh, [(pm, 40, 0), (mug, 280, 320), (desk, 0, 450)]), 6)
        self.t1 = tag("가방 → 뚜껑 있는 튜브", 40, seed=47)
        self.t2 = tag("책상 → 펌프", 40, bg=BURG, seed=48)

    def draw(self, frame, lt):
        self.bg(frame)
        self.chrome(frame, lt)
        pop(frame, self.bag, 60, 760, lt, wt(3, 4) - 0.15)
        pop(frame, self.t1, 60, 1260, lt, wt(3, 5))
        pop(frame, self.desk, 580, 700, lt, wt(3, 8) - 0.15)
        pop(frame, self.t2, 620, 1260, lt, wt(3, 9))


class Texture(Scene):
    decor = [(960, 700, 120), (-40, 1330, 130)]
    kicker = "② 제형"
    head = "로션보다 크림"
    hl = ("크림",)

    def setup(self, i):
        super().setup(i)
        lw, lh_ = 380, 200
        lot = [(20 + 170 * (1 + math.cos(a)) + 6 * math.sin(a * 5), 110 + 60 * math.sin(a) + 4 * math.cos(a * 7)) for a in np.linspace(0, 2 * math.pi, 60)]
        lotion = stack(lw, lh_, [(piece(lw, lh_, lot, (252, 249, 242), 51, 2, 0.4), 0, 0),
                                (piece(lw, lh_, circle_pts(120, 95, 18, 20), (255, 255, 255), 52, 0, 0.2, 1), 0, 0)])
        self.lotion = lift(lotion, 3)
        cw, ch = 300, 280
        layers = []
        for k, (rx, ry, yc) in enumerate(((140, 44, 230), (112, 40, 186), (84, 36, 146), (56, 32, 110))):
            layers.append((piece(cw, ch, [(150 + rx * math.cos(a), yc + ry * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 48)],
                                 (250, 246, 238) if k % 2 else (244, 238, 226), 53 + k, 3, 0.4), 0, 0))
        tip = [(150 + 30 * math.cos(a), 92 + 24 * math.sin(a)) for a in np.linspace(0.2, math.pi - 0.2, 20)] + [(150, 40)]
        layers.append((piece(cw, ch, tip, (250, 246, 238), 58, 3, 0.4), 0, 0))
        self.cream = lift(stack(cw, ch, layers), 5)
        self.l1 = tag("로션 — 묽다", 42, bg=INK, seed=59)
        self.l2 = tag("크림 ✓ 보습에 더 효과적", 42, bg=BRICK, seed=60)
        self.pm = tag("펌프형이라면 제형부터 확인", 42, bg=BURG, seed=61)
        self.src = tag("출처: 미국피부과학회(AAD) 건조 피부 관리 안내", 30, bg=OLIVE, seed=62)

    def draw(self, frame, lt):
        self.bg(frame)
        self.chrome(frame, lt)
        pop(frame, self.lotion, 60, 820, lt, wt(4, 1) - 0.1)
        pop(frame, self.l1, 90, 1050, lt, wt(4, 1))
        pop(frame, self.cream, 640, 740, lt, wt(4, 2) - 0.1)
        pop(frame, self.l2, 520, 1050, lt, wt(4, 3))
        pop(frame, self.pm, 70, 1180, lt, wt(4, 4))
        pop(frame, self.src, 70, 1290, lt, wt(4, 5))


class Size(Scene):
    decor = [(960, 420, 120), (-40, 1330, 140), (930, 1320, 120)]
    kicker = "② 용량"
    head = "처음이면\n작은 용량부터"
    hl = ("작은 용량",)

    def setup(self, i):
        super().setup(i)
        self.small = tube(130, 360, band=OLIVE, seed=71)
        self.big = pump(260, 600, seed=72)
        self.t1 = tag("✓ 먼저 사용감 확인", 40, bg=OLIVE, seed=73)
        self.t2 = tag("대용량 — 자주 바르는 사람에게", 36, bg=INK, seed=74)

    def draw(self, frame, lt):
        self.bg(frame)
        self.chrome(frame, lt)
        pop(frame, self.big, 640, 690, lt, wt(5, 3) - 0.2)
        pop(frame, self.t2, 470, 1320, lt, wt(5, 3))
        pop(frame, self.small, 230, 930, lt, wt(5, 4) - 0.1)
        pop(frame, self.t1, 90, 1320, lt, wt(5, 5))


class Sink(Scene):
    decor = [(960, 380, 120), (-40, 1330, 130)]
    kicker = "③ 바르는 때"
    head = "손 씻은 직후,\n손끝까지"

    def setup(self, i):
        super().setup(i)
        cw, ch = 760, 330
        counter = piece(cw, ch, [(0, 60), (cw, 60), (cw, ch), (0, ch)], (228, 214, 190), 81, 0, 0.8)
        basin = piece(cw, ch, [(380 + 230 * math.cos(a), 150 + 70 * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 60)], (250, 248, 244), 82, 0, 0.4)
        inner = piece(cw, ch, [(380 + 190 * math.cos(a), 156 + 52 * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 60)], (214, 222, 226), 83, 0, 0.4, 1)
        tap = piece(cw, ch, [(360, 0), (400, 0), (400, 30), (470, 30), (470, 58), (440, 58), (440, 52), (360, 52)], (170, 170, 172), 84, 3, 0.2)
        self.sink = lift(stack(cw, ch, [(counter, 0, 0), (basin, 0, 0), (inner, 0, 0), (tap, 0, -20)]), 7)
        self.drop = lift(paper(mask(18, 26, lambda d, s: poly(d, s, [(9, 0)] + [(9 + 9 * math.cos(a), 17 + 9 * math.sin(a)) for a in np.linspace(-0.3, math.pi + 0.3, 16)])), (160, 200, 222), 85, 1), 2)
        self.tube = tube(110, 300, band=BRICK, cap=OLIVE, seed=86)
        self.steps = [tag(t, 42, bg=c, seed=87 + k) for k, (t, c) in enumerate((("① 손 씻은 직후", BRICK), ("② 물기가 살짝 남았을 때", BURG), ("③ 손끝·손톱까지", OLIVE)))]
        self.src = tag("출처: 미국피부과학회(AAD)", 30, bg=INK, seed=90)

    def draw(self, frame, lt):
        self.bg(frame)
        self.chrome(frame, lt)
        pop(frame, self.sink, 160, 700, lt, 0.2, dur=0.5)
        for k in range(4):
            ph = (lt * 1.6 + k * 0.25) % 1.0
            if lt > 0.6:
                blit(frame, self.drop, 160 + 450, 760 + ph * 150, alpha=1 - ph)
        pop(frame, self.tube, 830, 760, lt, 0.5)
        for k, wi in enumerate((1, 4, 7)):
            pop(frame, self.steps[k], 70, 1080 + k * 80, lt, wt(6, wi) - 0.05)
        pop(frame, self.src, 700, 1320, lt, wt(6, 8))


class Products(Scene):
    """상품 대표 이미지(판매 페이지 공개 이미지, media/)를 테이프로 붙인 인화지로."""
    decor = [(960, 330, 110), (-40, 1340, 120)]
    kicker = "쇼핑 노트"
    head = "무향으로 판매되는\n두 가지 선택지"
    hl = ("두 가지",)

    def photo(self, path, crop_h, top, name, seed, tilt):
        w, ph = 470, 430
        im = Image.open(path).convert("RGB")
        im = im.crop((0, 0, im.width, int(im.height * crop_h)))  # 판매처 홍보 띠 제외
        s_ = max(ph / im.height, (w - 36) / im.width)
        im = im.resize((int(im.width * s_), int(im.height * s_)), Image.LANCZOS)
        ox = (im.width - (w - 36)) // 2
        im = im.crop((ox, 0, ox + w - 36, ph))
        h = ph + 36 + 170
        cv = stack(w, h, [(piece(w, h, [(0, 0), (w, 0), (w, h), (0, h)], (252, 249, 242), seed, 0, 0.8), 0, 0)])
        cv.paste(im, (18, 18))
        d = ImageDraw.Draw(cv)
        d.text((24, ph + 42), top, font=font(36), fill=BRICK)
        d.text((24, ph + 96), wrap(name, font(30, bold=False), w - 48), font=font(30, bold=False), fill=INK, spacing=8)
        tape = Image.new("RGBA", (150, 44), (236, 222, 180, 170))
        cv.alpha_composite(tape, (w // 2 - 75, 0))
        return lift(cv.rotate(tilt, Image.BICUBIC, expand=True), 9)

    def setup(self, i):
        super().setup(i)
        self.c1 = self.photo(ROOT / "media/p1.jpg", 1.0, "가방용 · 튜브형 60ml", "동구밭 시어버터 무향 핸드크림", 92, 2.0)
        self.c2 = self.photo(ROOT / "media/p2.jpg", 0.8, "책상용 · 펌프형 300g", "엠디스픽 드 바리스타 무향 핸드크림", 94, -2.0)
        self.link = tag("구성·가격은 설명란 링크 · 전성분은 구매 전 확인", 36, bg=INK, seed=95)
        self.credit = tag("이미지: 각 판매 페이지 대표 이미지", 26, bg=BROWN, seed=96)

    def draw(self, frame, lt):
        self.bg(frame)
        self.chrome(frame, lt, 0.1)
        pop(frame, self.c1, 40, 655, lt, wt(7, 2) - 0.1)
        pop(frame, self.c2, 560, 665, lt, wt(7, 4) - 0.1)
        pop(frame, self.link, 70, 1318, lt, wt(7, 6))
        pop(frame, self.credit, 70, 1380, lt, wt(7, 6) + 0.2)


class Close(Scene):
    decor = [(900, 300, 150), (-40, 760, 140), (860, 1250, 190), (100, 1320, 150), (560, 1300, 170), (330, 1250, 130)]
    kicker = "이번 가을의 기준"

    def setup(self, i):
        super().setup(i)
        self.warn = tag("따갑거나 붉어지면 사용 중지 · 계속되면 피부과 상담", 34, bg=BURG, seed=101)
        self.big = label("비싼 한 통보다,\n꾸준히 쓰는 한 통", 96, fg=INK, bg=CREAM, hl=("꾸준히",), hlc=BRICK, seed=102, elev=8, pad=(40, 26))
        self.tube = tube(150, 420, seed=103)

    def draw(self, frame, lt):
        self.bg(frame)
        self.chrome(frame, lt)
        pop(frame, self.warn, 70, 400, lt, 0.1)
        pop(frame, self.big, 70, 560, lt, wt(8, 3) - 0.1, dur=0.5)
        pop(frame, self.tube, 620, 930, lt, wt(8, 5), anchor=(0.5, 0.5))


SCENES = [Hook(), Scent(), Ingredients(), Place(), Texture(), Size(), Sink(), Products(), Close()]
for _i, _s in enumerate(SCENES):
    _s.setup(_i)

# ── 자막 ────────────────────────────────────────────────────
CAP_TL = sorted((SC[i]["start"] + wt(i, k), txt) for i, s in enumerate(SCRIPT["scenes"]) for txt, k in s["caps"])
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
        _cap[i] = label(wrap(txt, font(70), 880), 70, fg=INK, bg=CREAM, pad=(34, 14), seed=900 + i, elev=5, align="center", amp=2.2)
    spr = _cap[i]
    p = prog(t, st, 0.16)
    blit(frame, spr, (W - spr.w) / 2, 1570 - spr.h + (1 - out_cubic(p)) * 14, alpha=clamp(p * 1.6))


# ── 전환: 낙엽이 쓸고 지나간다 ──────────────────────────────
TR = 0.5
SWEEP = [leaf(int(150 + 40 * (k % 3)), LEAFC[k % len(LEAFC)], 700 + k, "ginkgo" if k % 4 == 1 else "maple", 6) for k in range(9)]
YS = np.arange(H)[:, None]
XS = np.arange(W)[None, :]


CUR = [0.0]


def frame_at(t):
    CUR[0] = t
    i = max(k for k in range(len(SC)) if t >= SC[k]["start"] - 1e-6)
    lt = t - SC[i]["start"]
    fr = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    SCENES[i].draw(fr, lt)
    if i > 0 and lt < TR:
        old = Image.new("RGBA", (W, H), (0, 0, 0, 255))
        SCENES[i - 1].draw(old, t - SC[i - 1]["start"])
        p = in_out(lt / TR)
        edge = p * (W + 400) - 200 + 60 * np.sin(YS / 160.0)
        out = np.where((XS < edge)[..., None], np.asarray(fr), np.asarray(old))
        fr = Image.fromarray(out.astype(np.uint8), "RGBA")
        for k, spr in enumerate(SWEEP):
            y = -120 + k * (H + 200) / len(SWEEP)
            x = p * (W + 400) - 200 + 60 * math.sin(y / 160.0) - spr.w / 2 + (k % 2) * 50
            blit(fr, spr, x, y, rot=k * 47 + p * 160)
    draw_caption(fr, t)
    return fr


def make_sfx(path):
    sr = 44100
    out = np.zeros(int(TOTAL * sr) + sr, np.float32)
    r = np.random.default_rng(700)
    for i in range(1, len(SC)):
        st, L = int(SC[i]["start"] * sr), int(0.5 * sr)
        x = r.normal(0, 1, L).astype(np.float32)
        x = np.convolve(x, np.ones(2) / 2, "same") - np.convolve(x, np.ones(30) / 30, "same")
        tt = np.linspace(0, 1, L)
        crackle = (r.random(L) < 0.004).astype(np.float32) * r.normal(0, 2.5, L).astype(np.float32)  # 마른 잎 바스락
        out[st:st + L] += (x * np.sin(np.pi * tt) ** 1.5 * 0.06 + np.convolve(crackle, np.ones(4) / 4, "same") * np.sin(np.pi * tt) * 0.12)
    pcm = (np.clip(out, -1, 1) * 32767).astype(np.int16)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(pcm.tobytes())


def main():
    OUT.mkdir(exist_ok=True)
    if "--still" in sys.argv:
        for ts in sys.argv[sys.argv.index("--still") + 1].split(","):
            frame_at(float(ts)).convert("RGB").save(OUT / f"still_{ts}.png")
        print("stills ok")
        return
    sfx = OUT / "sfx.wav"
    make_sfx(sfx)
    nfr = int(math.ceil(TOTAL * FPS))
    dst = OUT / "final.mp4"
    cmd = ["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-i", str(ROOT / "audio/narration.mp3"), "-i", str(sfx),
           "-filter_complex", "[1:a][2:a]amix=inputs=2:normalize=0:duration=first[a]",
           "-map", "0:v", "-map", "[a]", "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "-t", f"{TOTAL:.3f}", str(dst)]
    ff = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for f in range(nfr):
        ff.stdin.write(frame_at(f / FPS).convert("RGB").tobytes())
        if f % 300 == 0:
            print(f"  {f}/{nfr}", flush=True)
    ff.stdin.close()
    ff.wait()
    print("✓", dst.relative_to(ROOT), f"({TOTAL:.1f}s)")


if __name__ == "__main__":
    main()
