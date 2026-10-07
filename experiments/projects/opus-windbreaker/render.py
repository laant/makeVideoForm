#!/usr/bin/env python3
"""opus-windbreaker — 가을 러닝 바람막이 고르는 법 (쇼핑커넥트 글 기반 · 데카트론 런 100).

쌀쌀한 질감: 회청색 마분지 · 서리 낀 트레이싱지 띠 · 바람 줄무늬 · 바람에 날리는 마른 잎 · 슬레이트/네이비/아이스 블루, 포인트 러닝 오렌지.
전부 코드로 그린다(도구: ../paperkit.py, 소리: ../audiokit.py). 상품 사진만 판매 페이지 대표 이미지(media/).
  ../opus-paper-04/.venv/bin/python render.py [--still 1,9]
"""
import json, math, subprocess, sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parents[1]))  # experiments/ (paperkit·audiokit)
from paperkit import (W, H, FPS, font, paper, Sprite, lift, blit, _paste, mask, poly, deckle, rrect, circle_pts,  # noqa: E402
                      piece, stack, _paste_into, label, clamp, prog, out_cubic, out_back, in_out, pop, wrap, full_bg, measure)
from audiokit import make_bgm, wind_sfx  # noqa: E402
import importlib.util  # noqa: E402

_spec = importlib.util.spec_from_file_location("autumn", ROOT.parent / "opus-autumn-handcream/render.py")
A = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(A)  # leaf() 재사용

OUT = ROOT / "out"
S = json.loads((ROOT / "script.json").read_text())
TIM = json.loads((ROOT / "audio/timing.json").read_text())
SC = TIM["scenes"]
HOLD = S.get("hold_last", 2.0)
TOTAL = TIM["total"] + HOLD

SKY = (198, 209, 217)
FROST = (240, 245, 248)
SLATE = (74, 100, 128)
SLATE_D = (56, 78, 104)
NAVY = (34, 48, 70)
ICE = (36, 108, 168)
MINT = (140, 186, 184)
ORANGE = (232, 110, 48)
INK = (30, 38, 50)
GREYLEAF = [(150, 128, 104), (128, 120, 108), (170, 150, 120)]


def wt(i, k):
    return SC[i]["words"][k]["start"]


def tag(text, size=42, bg=SLATE_D, fg=FROST, seed=0):
    return label(text, size, fg=fg, bg=bg, pad=(22, 8), seed=seed, elev=4, amp=1.0)


def title(text, hl=(), seed=0, size=88):
    return label(text, size, fg=INK, bg=FROST, hl=hl, hlc=ICE, seed=seed, elev=7)


# ── 배경: 회청색 마분지 + 서리 트레이싱지 띠 ─────────────────
def make_bg(seed):
    B = full_bg(SKY, seed)
    for k, (x, y, w) in enumerate(((60, 1080, 520), (520, 1180, 600), (-80, 1260, 700))):  # 먼 언덕(차가운 회색)
        pts = [(x, y + 260)] + [(x + w * i / 20, y + 60 * math.sin(i / 3 + k) - 40 * math.sin(i / 7)) for i in range(21)] + [(x + w, y + 260)]
        _paste_into(B, piece(W, H, pts, tuple(int(c * (0.9 - 0.05 * k)) for c in SKY), seed + k, 3, 1.0), 0, 0)
    fm = mask(W, 300, lambda d, s: poly(d, s, deckle([(0, 18), (W, 0), (W, 300), (0, 300)], 2.5, 7, seed)))
    frost = paper(fm, FROST, seed + 9, 0)
    frost.putalpha(frost.getchannel("A").point(lambda v: int(v * 0.62)))
    B.alpha_composite(frost.filter(ImageFilter.GaussianBlur(0.6)), (0, 1660))
    return B


BG = make_bg(3)

# 바람 줄무늬 · 날리는 잎
_r = np.random.default_rng(31)
STREAKS = [dict(y=float(_r.uniform(250, 1650)), L=float(_r.uniform(160, 420)), v=float(_r.uniform(500, 900)), ph=float(_r.uniform(0, 3000)),
                a=int(_r.uniform(70, 150)), amp=float(_r.uniform(6, 22))) for _ in range(12)]
BLOWN = [dict(spr=A.leaf(int(_r.integers(40, 64)), GREYLEAF[i % 3], 3100 + i, "maple" if i % 2 else "ginkgo", 3),
              y=float(_r.uniform(300, 1600)), v=float(_r.uniform(260, 420)), ph=float(_r.uniform(0, 2000)), rs=float(_r.uniform(120, 300))) for i in range(5)]


def wind(frame, t, strength=1.0):
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    for k, s in enumerate(STREAKS):
        if k / len(STREAKS) > strength:
            continue
        x0 = (s["ph"] + s["v"] * t) % (W + 600) - 400
        pts = [(x0 + s["L"] * i / 12, s["y"] + s["amp"] * math.sin((x0 + s["L"] * i / 12) / 140 + k)) for i in range(13)]
        d.line(pts, fill=(255, 255, 255, s["a"]), width=3)
    frame.alpha_composite(ov)
    for k, L in enumerate(BLOWN):
        if k / len(BLOWN) > strength:
            continue
        x = (L["ph"] + L["v"] * t) % (W + 400) - 200
        blit(frame, L["spr"], x, L["y"] + 40 * math.sin(t * 2 + k), rot=L["rs"] * t, alpha=0.9)


# ── 바람막이 (조각 종이) ─────────────────────────────────────
JW, JH = 560, 600
SH_L, SH_R = (122, 112), (438, 112)  # 어깨(소매 회전축)


def sleeve(side):
    w, h = 150, 380
    pts = [(55, 0), (115, 0), (130, 340), (60, 352)] if side > 0 else [(35, 0), (95, 0), (90, 352), (20, 340)]
    cuff = [(60, 330), (130, 322), (132, 352), (62, 360)] if side > 0 else [(20, 322), (90, 330), (88, 360), (18, 352)]
    img = stack(w, h, [(piece(w, h, pts, SLATE, 3200 + side, 0, 0.8), 0, 0), (piece(w, h, cuff, NAVY, 3210 + side, 0, 0.5), 0, 0)])
    stripe = [(118, 120), (124, 120), (126, 210), (120, 210)] if side > 0 else [(26, 120), (32, 120), (30, 210), (24, 210)]
    _paste_into(img, piece(w, h, stripe, (214, 222, 228), 3220 + side, 0, 0.2, 1), 0, 0)
    pivot = (85, 12) if side > 0 else (65, 12)
    return img, pivot


def jacket_body():
    parts = [
        (piece(JW, JH, [(205, 92), (215, 22), (280, 0), (345, 22), (355, 92)], SLATE_D, 3301, 0, 0.6), 0, 0),
        (piece(JW, JH, [(240, 30), (280, 16), (320, 30), (316, 84), (244, 84)], NAVY, 3302, 0, 0.4), 0, 0),
        (piece(JW, JH, [(232, 74), (328, 74), (440, 112), (452, 560), (108, 560), (120, 112)], SLATE, 3303, 0, 0.9), 0, 0),
        (piece(JW, JH, [(108, 530), (452, 530), (452, 562), (108, 562)], NAVY, 3304, 0, 0.5), 0, 0),
        (piece(JW, JH, [(277, 84), (283, 84), (283, 560), (277, 560)], ORANGE, 3305, 0, 0.2, 1), 0, 0),
        (piece(JW, JH, [(272, 120), (288, 120), (288, 146), (272, 146)], (230, 230, 228), 3306, 0, 0.2, 1), 0, 0),
        (piece(JW, JH, [(170, 380), (176, 380), (190, 460), (184, 460)], NAVY, 3307, 0, 0.2, 1), 0, 0),
        (piece(JW, JH, [(384, 380), (390, 380), (376, 460), (370, 460)], NAVY, 3308, 0, 0.2, 1), 0, 0),
    ]
    return stack(JW, JH, parts)


SLV_R, PIV_R = sleeve(1)
SLV_L, PIV_L = sleeve(-1)
BODY = jacket_body()


def rot_about(img, pivot, ang):
    R = int(math.hypot(img.width, img.height)) + 4
    cv = Image.new("RGBA", (2 * R, 2 * R), (0, 0, 0, 0))
    cv.alpha_composite(img, (R - pivot[0], R - pivot[1]))
    return cv.rotate(ang, Image.BICUBIC), R


def jacket_img(arm_r=0.0, arm_l=0.0, lift_y=0):
    """arm: 0 = 내림, 양수 = 바깥·위로 든 각도(도)."""
    cv = Image.new("RGBA", (JW + 400, JH + 420), (0, 0, 0, 0))
    ox, oy = 200, 260
    for img, piv, sh, ang in ((SLV_R, PIV_R, SH_R, arm_r), (SLV_L, PIV_L, SH_L, -arm_l)):
        rimg, R = rot_about(img, piv, ang)
        cv.alpha_composite(rimg, (int(ox + sh[0] - R), int(oy + sh[1] - R - lift_y)))
    cv.alpha_composite(BODY, (ox, oy - lift_y))
    return lift(cv, 9), ox, oy


JK, JOX, JOY = jacket_img()
JX, JY = 260, 760  # 재킷 종이 좌상단(화면)


def draw_jacket(frame, x=JX, y=JY, spr=None, s=1.0, alpha=1.0):
    spr = spr or JK
    blit(frame, spr, x - JOX, y - JOY, s=s, alpha=alpha, anchor=((JOX + JW / 2) / spr.w, (JOY + JH / 2) / spr.h))


# ── 소품 ────────────────────────────────────────────────────
def thermometer():
    w, h = 130, 640
    tube = rrect(40, 0, 90, 560, 25)
    parts = [(piece(w, h, tube, FROST, 3401, 0, 0.6), 0, 0), (piece(w, h, circle_pts(65, 580, 56), FROST, 3402, 0, 0.5), 0, 0),
             (piece(w, h, circle_pts(65, 580, 40), ORANGE, 3403, 0, 0.4), 0, 0)]
    img = stack(w, h, parts)
    d = ImageDraw.Draw(img)
    for k, tc in enumerate(range(-5, 21, 5)):
        y = temp_y(tc)
        d.line([(92, y), (110, y)], fill=INK + (255,), width=3)
        d.text((112, y - 14), f"{tc}", font=font(24), fill=INK)
    return img


def temp_y(tc):  # 온도 → 온도계 안 y (−5 ~ 20)
    return 520 - (tc + 5) / 25 * 470


THERMO = thermometer()


def draw_thermo(frame, x, y, tc):
    img = THERMO.copy()
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([54, temp_y(tc), 76, 560], 10, fill=ORANGE + (255,))
    spr = lift(img, 8)
    blit(frame, spr, x, y)


def arrow_spr(color, seed, L=170):
    pts = [(0, 18), (L - 46, 18), (L - 46, 0), (L, 30), (L - 46, 60), (L - 46, 42), (0, 42)]
    return piece(L, 60, pts, color, seed, 4, 0.6)


ARROW = arrow_spr(ICE, 3501)
DROP = lift(paper(mask(26, 38, lambda d, s: poly(d, s, [(13, 0)] + [(13 + 13 * math.cos(a), 25 + 13 * math.sin(a)) for a in np.linspace(-0.3, math.pi + 0.3, 16)])), (120, 170, 214), 3502, 1), 2)


def magnifier(seed):
    r = 175
    w = h = 2 * r + 120
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    lens = paper(mask(2 * r, 2 * r, lambda d, s: poly(d, s, circle_pts(r, r, r - 2, 64))), SLATE, seed, 0)
    d = ImageDraw.Draw(lens)
    d.rectangle([r - 28, 0, r + 28, 2 * r], fill=(214, 220, 226, 255))  # 심실링 테이프
    for y in range(10, 2 * r, 26):
        d.line([(r - 50, y), (r - 50, y + 14)], fill=FROST + (255,), width=5)
        d.line([(r + 50, y), (r + 50, y + 14)], fill=FROST + (255,), width=5)
    d.line([(r, 0), (r, 2 * r)], fill=NAVY + (255,), width=3)
    lens.putalpha(Image.fromarray(np.minimum(np.asarray(lens.getchannel("A")), np.asarray(mask(2 * r, 2 * r, lambda dd, s: dd.ellipse([2 * s, 2 * s, (2 * r - 2) * s, (2 * r - 2) * s], fill=255))))))
    img.alpha_composite(lens, (10, 10))
    d2 = ImageDraw.Draw(img)
    d2.ellipse([6, 6, 2 * r + 14, 2 * r + 14], outline=NAVY + (255,), width=14)
    d2.line([(2 * r - 20, 2 * r - 20), (w - 10, h - 10)], fill=NAVY + (255,), width=30)
    return lift(img, 9)


MAG = magnifier(3601)


def size_chart(seed):
    w, h = 380, 300
    cv = stack(w, h, [(piece(w, h, [(0, 0), (w, 0), (w, h), (0, h)], FROST, seed, 0, 1.0), 0, 0)])
    d = ImageDraw.Draw(cv)
    d.text((22, 16), "상품 사이즈표", font=font(34), fill=INK)
    cols = ["", "S", "M", "L", "XL"]
    rows = ["가슴", "소매", "총장"]
    for c, name in enumerate(cols):
        d.text((24 + c * 70, 76), name, font=font(28), fill=SLATE_D)
    r = np.random.default_rng(seed)
    for k, name in enumerate(rows):
        y = 130 + k * 52
        d.text((24, y), name, font=font(28), fill=INK)
        for c in range(1, 5):
            x = 24 + c * 70
            d.line([(x, y + 18), (x + 18 + r.random() * 16, y + 14 + r.random() * 8)], fill=(120, 130, 140, 200), width=3)  # 끄적임(숫자 아님)
    d.line([(20, 120), (w - 20, 120)], fill=SLATE + (255,), width=2)
    return lift(cv, 7)


CHART = size_chart(3701)


def wash_card(seed):
    w, h = 520, 260
    cv = stack(w, h, [(piece(w, h, [(0, 0), (w, 0), (w, h), (0, h)], FROST, seed, 0, 1.0), 0, 0)])
    d = ImageDraw.Draw(cv)
    d.text((22, 14), "세탁 표시 확인 (기호는 예시)", font=font(30), fill=INK)
    # 물세탁 통
    d.polygon([(40, 100), (150, 100), (138, 180), (52, 180)], outline=INK, width=5)
    d.arc([40, 80, 150, 120], 200, 340, fill=INK, width=5)
    d.text((76, 122), "30", font=font(36), fill=INK)
    # 표백 금지 삼각형
    d.polygon([(260, 92), (310, 182), (210, 182)], outline=INK, width=5)
    d.line([(215, 95), (305, 182)], fill=INK, width=5)
    d.line([(305, 95), (215, 182)], fill=INK, width=5)
    # 다림질
    d.polygon([(370, 170), (390, 110), (470, 110), (490, 170)], outline=INK, width=5)
    d.text((26, 206), "실제 옷의 표시를 따르세요", font=font(28, bold=False), fill=SLATE_D)
    return lift(cv, 7)


WASH = wash_card(3801)


def pouch(seed):
    w, h = 300, 240
    parts = [(piece(w, h, rrect(0, 40, w, h, 30), NAVY, seed, 0, 0.8), 0, 0), (piece(w, h, [(20, 40), (w - 20, 40), (w - 20, 60), (20, 60)], ORANGE, seed + 1, 0, 0.3, 1), 0, 0)]
    cv = stack(w, h, parts)
    ImageDraw.Draw(cv).arc([80, 0, 220, 90], 180, 360, fill=SLATE_D + (255,), width=12)
    return lift(cv, 7)


POUCH = pouch(3901)


def photo(path, seed, tilt, w=300):
    im = Image.open(path).convert("RGB")
    s_ = (w - 24) / im.width
    im = im.resize((w - 24, int(im.height * s_)), Image.LANCZOS)
    im = im.crop((0, int(im.height * 0.02), w - 24, int(im.height * 0.02) + int((w - 24) * 1.2)))
    h = im.height + 24 + 10
    cv = stack(w, h, [(piece(w, h, [(0, 0), (w, 0), (w, h), (0, h)], (252, 252, 250), seed, 0, 0.6), 0, 0)])
    cv.paste(im, (12, 12))
    cv.alpha_composite(Image.new("RGBA", (110, 34), (226, 232, 236, 180)), (w // 2 - 55, 0))
    return lift(cv.rotate(tilt, Image.BICUBIC, expand=True), 9)


# ── 장면 ────────────────────────────────────────────────────
class Scene:
    kicker, head, hl = "", "", ()

    def setup(self, i):
        self.i = i
        self.k = tag(self.kicker, 38, bg=NAVY, seed=4000 + i) if self.kicker else None
        self.h = title(self.head, self.hl, 4100 + i) if self.head else None

    def bg(self, frame, wind_s=0.7):
        frame.paste(BG)
        wind(frame, CUR[0], wind_s)

    def chrome(self, frame, lt, head_t=0.25):
        if self.k:
            pop(frame, self.k, 70, 330, lt, 0.05)
        if self.h:
            pop(frame, self.h, 70, 392, lt, head_t)


class Chill(Scene):
    kicker = "체감온도"
    head = "같은 10도,\n바람 불면 7.6도"
    hl = ("7.6도",)

    def setup(self, i):
        super().setup(i)
        self.t1 = tag("기온 10°C", 46, bg=SLATE_D, seed=4201)
        self.t2 = tag("바람 초속 5m", 46, bg=SLATE_D, seed=4202)
        self.big = label("체감 7.6°C", 110, fg=FROST, bg=ICE, seed=4203, elev=8, pad=(36, 14))
        self.src = tag("기상청 체감온도 식 · 기온 10°C 이하, 풍속 1.3m/s 이상에 적용", 26, bg=INK, seed=4204)

    def draw(self, frame, lt):
        self.bg(frame, 0.4 + 0.6 * clamp((lt - wt(0, 3)) / 1.5))
        self.chrome(frame, lt, 0.2)
        tc = 10 - 2.4 * in_out(prog(lt, wt(0, 7), 1.2))
        draw_thermo(frame, 120, 700, tc)
        pop(frame, self.t1, 330, 760, lt, wt(0, 0))
        pop(frame, self.t2, 330, 860, lt, wt(0, 3))
        pop(frame, self.big, 330, 990, lt, wt(0, 7), dur=0.5)
        pop(frame, self.src, 70, 1340, lt, wt(0, 8))


class Three(Scene):
    kicker = "고르는 기준"
    head = "이름보다\n세 가지 먼저"
    hl = ("세 가지",)

    def setup(self, i):
        super().setup(i)
        self.tags = [tag(t, 40, bg=c, seed=4300 + k) for k, (t, c) in enumerate((("① 방풍·방수", ICE), ("② 사이즈", SLATE_D), ("③ 보관·세탁", NAVY)))]

    def draw(self, frame, lt):
        self.bg(frame)
        self.chrome(frame, lt)
        draw_jacket(frame, JX + 120, JY + 20)
        for k in range(3):
            pop(frame, self.tags[k], 70, 760 + k * 100, lt, wt(1, 3) + k * 0.25)


class WindRain(Scene):
    kicker = "① 방풍·방수"
    head = "방풍 ≠ 방수"
    hl = ("≠",)

    def setup(self, i):
        super().setup(i)
        self.t1 = tag("방풍 — 바람", 42, bg=ICE, seed=4401)
        self.t2 = tag("방수 — 물", 42, bg=NAVY, seed=4402)

    def draw(self, frame, lt):
        self.bg(frame, 1.0)
        self.chrome(frame, lt, 0.1)
        draw_jacket(frame)
        for k in range(3):  # 바람 화살표: 날아와서 튕겨 나감
            ph = (lt * 0.9 + k * 0.33) % 1.0
            y = 900 + k * 110
            if ph < 0.6:
                x = -180 + ph / 0.6 * (JX + 40)
                blit(frame, ARROW, x, y)
            else:
                q = (ph - 0.6) / 0.4
                blit(frame, ARROW, JX - 140 - q * 260, y - q * 220, rot=150, alpha=1 - q)
        if lt > wt(2, 4) - 0.3:  # 비: 이음새(지퍼선)로 스며드는 방울
            for k in range(6):
                ph = (lt * 1.1 + k / 6) % 1.0
                x = JX + 200 + (k % 3) * 60
                y = 640 + ph * 700
                blit(frame, DROP, x, y, alpha=1 - max(0, ph - 0.8) * 5)
            wet = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            ImageDraw.Draw(wet).ellipse([JX + 262, JY + 260, JX + 300, JY + 340], fill=(20, 40, 70, int(110 * clamp((lt - wt(2, 5)) / 1.0))))
            frame.alpha_composite(wet.filter(ImageFilter.GaussianBlur(6)))
        pop(frame, self.t1, 70, 1250, lt, wt(2, 1))
        pop(frame, self.t2, 600, 1250, lt, wt(2, 2))


class Seam(Scene):
    kicker = "① 방수 확인"
    head = "방수 성능 ·\n봉제선 처리"
    hl = ("봉제선 처리",)

    def setup(self, i):
        super().setup(i)
        self.t1 = tag("방수 성능 표기", 40, bg=ICE, seed=4501)
        self.t2 = tag("봉제선(심실링) 처리", 40, bg=NAVY, seed=4502)

    def draw(self, frame, lt):
        self.bg(frame)
        self.chrome(frame, lt)
        draw_jacket(frame, JX - 120, JY + 30)
        if lt > 0.4:
            p = out_back(prog(lt, 0.4, 0.5), 1.2)
            blit(frame, MAG, 520, 720, s=0.3 + 0.7 * p, anchor=(0.4, 0.4), alpha=clamp(p * 3))
        pop(frame, self.t1, 600, 1210, lt, wt(3, 5))
        pop(frame, self.t2, 600, 1300, lt, wt(3, 7))


class Size(Scene):
    kicker = "② 사이즈"
    head = "가슴 · 소매 · 총장"

    def setup(self, i):
        super().setup(i)
        self.tags = [tag(t, 38, bg=ICE, seed=4600 + k) for k, t in enumerate(("가슴", "소매", "총장"))]

    def draw(self, frame, lt):
        self.bg(frame)
        self.chrome(frame, lt, 0.1)
        x0, y0 = JX - 150, JY + 30
        draw_jacket(frame, x0, y0)
        lines = [((x0 + 122, y0 + 210), (x0 + 438, y0 + 210)),
                 ((x0 + 470, y0 + 120), (x0 + 560, y0 + 455)),
                 ((x0 + 60, y0 + 74), (x0 + 60, y0 + 560))]
        for k, ((a, b), (c, e)) in enumerate(lines):
            t0 = wt(4, 4 + k)
            measure(frame, a, b, c, e, out_cubic(prog(lt, t0 - 0.1, 0.5)), color=ORANGE)
            mx, my = (a + c) / 2, (b + e) / 2
            pop(frame, self.tags[k], mx - self.tags[k].w / 2 + (40 if k == 1 else 0), my - self.tags[k].h / 2, lt, t0 + 0.2, anchor=(0.5, 0.5))
        pop(frame, CHART, 680, 560, lt, wt(4, 8))


class Arms(Scene):
    kicker = "② 움직임"
    head = "팔 뻗고 올릴 때\n여유"
    hl = ("여유",)

    def setup(self, i):
        super().setup(i)
        self.frames = {}
        self.t1 = tag("밑단이 딸려 올라가는지도", 38, bg=NAVY, seed=4701)

    def jk(self, a):
        key = int(a // 6) * 6
        if key not in self.frames:
            self.frames[key] = jacket_img(arm_r=key, arm_l=key, lift_y=int(30 * key / 150))
        return self.frames[key]

    def draw(self, frame, lt):
        self.bg(frame)
        self.chrome(frame, lt, 0.1)
        a = 90 * in_out(prog(lt, wt(5, 1), 0.6)) + 60 * in_out(prog(lt, wt(5, 3), 0.6))
        spr, ox, oy = self.jk(a)
        blit(frame, spr, JX - ox, JY + 60 - oy, s=0.8, anchor=((ox + JW / 2) / spr.w, (oy + JH + 40) / spr.h))  # 든 팔이 제목을 가리지 않게
        pop(frame, self.t1, 70, 1330, lt, wt(5, 5))


class Pack(Scene):
    kicker = "③ 보관·세탁"
    head = "벗은 뒤 부피,\n세탁 표시"
    hl = ("세탁 표시",)

    def draw(self, frame, lt):
        self.bg(frame)
        self.chrome(frame, lt, 0.1)
        p = in_out(prog(lt, wt(6, 3), 1.0))
        if p < 1:
            blit(frame, JK, JX - JOX - 120 + p * 140, JY - JOY + p * 260, sx=1 - 0.7 * p, sy=1 - 0.75 * p,
                 anchor=((JOX + JW / 2) / JK.w, (JOY + JH / 2) / JK.h), alpha=1 - 0.6 * p)
        pop(frame, POUCH, 130, 1060, lt, wt(6, 3) - 0.3)
        pop(frame, WASH, 480, 960, lt, wt(6, 6))


class Product(Scene):
    kicker = "쇼핑 노트"
    head = "데카트론\n러닝 바람막이 런 100"
    hl = ("런 100",)

    def setup(self, i):
        super().setup(i)
        self.ph = [photo(ROOT / f"media/w{k}.jpg", 4800 + k, t) for k, t in ((1, 4), (2, 0), (3, -4))]
        R = S["rating"]
        self.info = label("주원단 폴리에스터 100%\n겨드랑이 폴리에스터 90% · 엘라스테인 10%", 34, fg=INK, bg=FROST, seed=4811, elev=5, pad=(24, 12))
        self.rate = tag(f"★ {R['score']} · 리뷰 {R['reviews']}건 · 4점 이상 {R['ge4']} ({R['asof'][5:]} 기준)", 34, bg=SLATE_D, seed=4812)
        self.link = tag("옵션과 가격은 링크에서", 46, bg=ORANGE, seed=4813)
        self.disc = tag(S["disclosure"], 28, bg=INK, seed=4814)

    def draw(self, frame, lt):
        self.bg(frame, 0.4)
        blit(frame, self.disc, 70, 272)
        self.chrome(frame, lt, 0.1)
        for k, (x, y) in enumerate(((40, 640), (370, 620), (700, 640))):
            pop(frame, self.ph[k], x, y, lt, wt(7, 4) - 0.2 + k * 0.15)
        pop(frame, self.info, 70, 1110, lt, wt(7, 6))
        pop(frame, self.rate, 70, 1235, lt, wt(7, 7))
        pop(frame, self.link, 70, 1310, lt, wt(7, 9))


SCENES = [Chill(), Three(), WindRain(), Seam(), Size(), Arms(), Pack(), Product()]
for _i, _s in enumerate(SCENES):
    _s.setup(_i)
CUR = [0.0]

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
        _cap[i] = label(wrap(txt, font(70), 880), 70, fg=NAVY, bg=FROST, pad=(34, 14), seed=4900 + i, elev=5, align="center", amp=2.2)
    spr = _cap[i]
    p = prog(t, st, 0.16)
    blit(frame, spr, (W - spr.w) / 2, 1570 - spr.h + (1 - out_cubic(p)) * 14, alpha=clamp(p * 1.6))


# ── 전환: 바람이 쓸고 지나간다 ──────────────────────────────
TR = 0.45
YS = np.arange(H)[:, None]
XS = np.arange(W)[None, :]


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
        edge = p * (W + 300) - 150 + 40 * np.sin(YS / 90.0)
        out = np.where((XS < edge)[..., None], np.asarray(fr), np.asarray(old))
        fr = Image.fromarray(out.astype(np.uint8), "RGBA")
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(ov)
        ex = p * (W + 300) - 150
        for k in range(26):
            y = 40 + k * 72
            x = ex + 40 * math.sin(y / 90.0)
            d.line([(x - 260 - (k % 3) * 60, y), (x + 10, y)], fill=(255, 255, 255, 170), width=4 + k % 3)
        fr.alpha_composite(ov.filter(ImageFilter.GaussianBlur(1.2)))
    draw_caption(fr, t)
    return fr


def main():
    OUT.mkdir(exist_ok=True)
    if "--still" in sys.argv:
        for ts in sys.argv[sys.argv.index("--still") + 1].split(","):
            frame_at(float(ts)).convert("RGB").save(OUT / f"still_{ts}.png")
        print("stills ok")
        return
    bgm, wnd = OUT / "bgm.wav", OUT / "wind.wav"
    make_bgm(bgm, TOTAL, [[57, 60, 64, 67], [53, 57, 60, 64], [48, 52, 55, 59], [52, 55, 59, 62]], bpm=72, seed=9, bright=0.9)
    wind_sfx(wnd, TOTAL, [s["start"] for s in SC[1:]], base=0.12)
    nfr = int(math.ceil(TOTAL * FPS))
    dst = OUT / "final.mp4"
    fc = ("[1:a]apad,asplit=2[n1][n2];[2:a]volume=0.30[b];[b][n1]sidechaincompress=threshold=0.02:ratio=6:attack=30:release=400[bd];"
          "[3:a]volume=0.35[w];[n2][bd][w]amix=inputs=3:normalize=0:duration=longest[a]")
    cmd = ["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-i", str(ROOT / "audio/narration.mp3"), "-i", str(bgm), "-i", str(wnd), "-filter_complex", fc,
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
