#!/usr/bin/env python3
"""opus-buds-on — 갤럭시 버즈 온, 지하철보다 산책에 맞을까요? (22번 · 테크)

19번(opus-smarttag3)의 테크 결(네이비 방안지 · 민트 선)에, 종이로 오린 귀와 클립형 이어폰 · 음파로 구성.
수치는 삼성전자 뉴스룸(2026-10-01) 기준. 상품 컷의 사진은 삼성전자 뉴스룸 공식 이미지(media/, 뉴스룸 자유 이용 안내).
  ../opus-paper-04/.venv/bin/python render.py [--still 1,9]
"""
import importlib.util, json, math, subprocess, sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent))
from paperkit import (W, H, FPS, font, paper, lift, blit, mask, poly, rrect, circle_pts, piece, stack, _paste_into,  # noqa: E402
                      label, clamp, prog, out_cubic, out_back, in_out, pop, wrap)
from audiokit import make_bgm, wind_sfx  # noqa: E402

_s = importlib.util.spec_from_file_location("st3", ROOT.parent / "opus-smarttag3/render.py")
ST = importlib.util.module_from_spec(_s)
_s.loader.exec_module(ST)  # 테크 배경·색·태그 재사용
BG, NAVY, NAVY2, MINT, SKY, PAPER, CORAL, GREY, INK = ST.BG, ST.NAVY, ST.NAVY2, ST.MINT, ST.SKY, ST.PAPER, ST.CORAL, ST.GREY, ST.INK
tag, title, rings = ST.tag, ST.title, ST.rings

OUT = ROOT / "out"
S = json.loads((ROOT / "script.json").read_text())
TIM = json.loads((ROOT / "audio/timing.json").read_text())
SC = TIM["scenes"]
TAIL = 1.0
TOTAL = TIM["total"] + TAIL
SKIN = (238, 200, 176)
SKIN_D = (206, 160, 134)
BUD = (46, 48, 54)
BUD_L = (84, 88, 98)


def wt(i, k):
    return SC[i]["words"][k]["start"]


# ── 귀 + 클립형 이어폰 (옆모습, 종이) ───────────────────────
EW, EH = 520, 640


def ear():
    outer = [(260 + 200 * math.cos(a) * (1 - 0.18 * max(0, math.sin(a))), 250 + 250 * math.sin(a)) for a in np.linspace(-math.pi, math.pi, 64)]
    lobe = [(150, 420), (330, 430), (300, 600), (220, 630), (150, 560)]
    helix = [(260 + 165 * math.cos(a), 245 + 205 * math.sin(a)) for a in np.linspace(-math.pi * 0.95, math.pi * 0.35, 40)] + \
            [(260 + 120 * math.cos(a), 245 + 160 * math.sin(a)) for a in np.linspace(math.pi * 0.35, -math.pi * 0.95, 40)]
    concha = [(250 + 95 * math.cos(a), 320 + 85 * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 40)]
    canal = circle_pts(205, 330, 30, 28)
    parts = [(piece(EW, EH, lobe, SKIN, 6001, 0, 1.0), 0, 0), (piece(EW, EH, outer, SKIN, 6002, 0, 1.0), 0, 0),
             (piece(EW, EH, helix, SKIN_D, 6003, 1, 0.8), 0, 0), (piece(EW, EH, concha, (222, 178, 152), 6004, 1, 0.8), 0, 0),
             (piece(EW, EH, canal, (90, 50, 46), 6005, 1, 0.4), 0, 0)]
    return lift(stack(EW, EH, parts), 8)


def _bez(p0, p1, p2, p3, n=40):
    return [tuple((1 - t) ** 3 * np.array(p0) + 3 * (1 - t) ** 2 * t * np.array(p1) + 3 * (1 - t) * t * t * np.array(p2) + t ** 3 * np.array(p3))
            for t in np.linspace(0, 1, n)]


def _strap(path, width, seed, color=BUD):
    w, h = EW + 60, EH
    m = mask(w, h, lambda d, s: d.line([(x * s, y * s) for x, y in path], fill=255, width=int(width * s), joint="curve"))
    img = paper(m, color, seed, 2)
    d = ImageDraw.Draw(img)
    d.line([(x, y - width * 0.28) for x, y in path], fill=BUD_L + (200,), width=max(2, int(width * 0.18)), joint="curve")  # 띠 윗면 하이라이트
    return img


def _ball(cx, cy, r, seed, color=BUD, grille=False):
    w, h = EW + 60, EH
    img = paper(mask(w, h, lambda d, s: poly(d, s, circle_pts(cx, cy, r, 48))), color, seed, 2)
    ys, xs = np.mgrid[0:h, 0:w].astype(np.float32)
    shade = np.clip(1.25 - np.hypot(xs - (cx - r * 0.35), ys - (cy - r * 0.4)) / (r * 1.6), 0.55, 1.25)  # 구 입체감
    arr = np.asarray(img, np.float32)
    arr[..., :3] *= shade[..., None]
    img = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGBA")
    if grille:
        d = ImageDraw.Draw(img)
        gr = r * 0.55
        d.ellipse([cx - gr, cy - gr, cx + gr, cy + gr], fill=(70, 72, 80, 255))
        for gx in np.arange(cx - gr + 5, cx + gr, 7):
            for gy in np.arange(cy - gr + 5, cy + gr, 7):
                if (gx - cx) ** 2 + (gy - cy) ** 2 < (gr - 4) ** 2:
                    d.ellipse([gx - 1.6, gy - 1.6, gx + 1.6, gy + 1.6], fill=(30, 31, 36, 255))
    return img


CANAL = (205, 330)  # 귀 그림 안 귓구멍 위치


def _smooth_strap(path, width, size):
    """제품 띠처럼 매끈한 검은 띠(종이 결 없이) — 어두운 바탕 + 윗면 하이라이트."""
    SSx = 3
    w, h = size

    def line(img, pts, col, wd):
        ImageDraw.Draw(img).line([(x * SSx, y * SSx) for x, y in pts], fill=col, width=int(wd * SSx), joint="curve")
    big = Image.new("RGBA", (w * SSx, h * SSx), (0, 0, 0, 0))
    line(big, path, (34, 35, 40, 255), width)
    line(big, [(x, y - width * 0.18) for x, y in path], (72, 75, 84, 255), width * 0.38)
    for (x, y) in (path[0], path[-1]):  # 둥근 끝
        r = width / 2 * SSx
        ImageDraw.Draw(big).ellipse([x * SSx - r, y * SSx - r, x * SSx + r, y * SSx + r], fill=(34, 35, 40, 255))
    return big.resize((w, h), Image.LANCZOS)


def buds_on_parts(ball_scale=0.78):
    """착용 모습(옆): 귓구멍 앞에 보이는 것은 그릴 달린 구형 스피커뿐(공식 사진에서 공 부분만 오림),
    C자 띠는 귓바퀴를 넘어가 귀 뒤로 사라지고, 본체는 귀 뒤에 가려져 테두리 너머로 가장자리만 보인다."""
    size = (EW + 80, EH)
    cut = Image.open(ROOT / "media/bud_cut.png").convert("RGBA")
    m = Image.new("L", cut.size, 0)
    ImageDraw.Draw(m).ellipse([30, 40, 230, 240], fill=255)
    ball = cut.copy()
    ball.putalpha(Image.fromarray(np.minimum(np.asarray(cut.getchannel("A")), np.asarray(m))))
    ball = ball.crop((30, 40, 230, 240))
    bs = int(200 * ball_scale)
    ball = ball.resize((bs, bs), Image.LANCZOS)
    bx, by = CANAL[0] - bs * 0.55, CANAL[1] - bs * 0.55  # 공 중심 ≈ 귓구멍 앞
    front = Image.new("RGBA", size, (0, 0, 0, 0))
    strap = _bez((bx + bs * 0.8, by + bs * 0.34), (300, 240), (400, 232), (452, 280))  # 공 뒤쪽 → 귓바퀴 테두리(여기서 귀 뒤로)
    front.alpha_composite(_smooth_strap(strap, 34, size))
    front.alpha_composite(ball, (int(bx), int(by)))
    back = Image.new("RGBA", size, (0, 0, 0, 0))  # 귀 뒤: 넘어간 띠와 본체(대부분 가려짐)
    back.alpha_composite(_smooth_strap(_bez((452, 280), (478, 290), (480, 318), (462, 336)), 34, size))
    back.alpha_composite(_ball(436, 352, 42, 6021, color=(44, 45, 50)))  # 귀 뒤 본체 — 테두리 너머로 가장자리만
    return lift(back, 4), lift(front, 6)


EAR = ear()
CLIP_BACK, CLIP = buds_on_parts()


def draw_ear(frame, x, y, s=1.0, with_bud=True):
    if with_bud:
        blit(frame, CLIP_BACK, x, y, s=s, anchor=(0, 0))   # 귀 뒤 — 귀 그림에 가려짐
    blit(frame, EAR, x, y, s=s, anchor=(0, 0))
    if with_bud:
        blit(frame, CLIP, x, y, s=s, anchor=(0, 0))


_WEAR = Image.open(ROOT / "media/wear_gem_1.png").convert("RGB")  # 사용자 제공 착용 사진 → Gemini 종이공작 변환
WEAR_BALL = (0.60, 0.54)  # 그림 안 스피커 공(귓구멍 앞) 위치 비율
_wear_cache = {}


def wear_card(w):
    """착용 그림을 흰 테두리 종이 인화지로 — (Sprite, 공 위치(px, 카드 기준))."""
    if w not in _wear_cache:
        h = int(w * _WEAR.height / _WEAR.width)
        im = _WEAR.resize((w, h), Image.LANCZOS)
        b = 14
        cv = stack(w + 2 * b, h + 2 * b, [(piece(w + 2 * b, h + 2 * b, [(0, 0), (w + 2 * b, 0), (w + 2 * b, h + 2 * b), (0, h + 2 * b)], (252, 251, 247), 6040 + w, 0, 1.2), 0, 0)])
        cv.paste(im, (b, b))
        _wear_cache[w] = (lift(cv, 9), (b + w * WEAR_BALL[0], b + h * WEAR_BALL[1]))
    return _wear_cache[w]


def draw_wear(frame, x, y, w):
    spr, (bx, by) = wear_card(w)
    blit(frame, spr, x, y)
    return x + bx, y + by


def waves(frame, cx, cy, t, color, direction=0.0, spread=55, n=4, r0=30, r1=260, alpha=220, speed=0.7, width=6, shrink=1.0):
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    for k in range(n):
        ph = (t * speed + k / n) % 1.0
        r = r0 + ph * (r1 - r0) * shrink
        a = int(alpha * (1 - ph))
        d.arc([cx - r, cy - r, cx + r, cy + r], direction - spread, direction + spread, fill=color + (a,), width=width)
    frame.alpha_composite(ov)


# ── 장면 ────────────────────────────────────────────────────
class Scene:
    kicker, head, hl = "", "", ()

    def setup(self, i):
        self.i = i
        self.k = tag(self.kicker, 38, bg=(20, 120, 200), seed=6100 + i) if self.kicker else None
        self.h = title(self.head, self.hl, 6200 + i) if self.head else None

    def chrome(self, frame, lt, head_t=0.2):
        if self.k:
            pop(frame, self.k, 70, 330, lt, 0.05)
        if self.h:
            pop(frame, self.h, 70, 392, lt, head_t)


class Hook(Scene):
    """첫 컷 = 출시 소개 페이지: 무슨 영상인지(신제품 출시 + 사용성 점검)부터 보여주고 질문을 띄운다."""
    kicker = "10월 27일 국내 출시"
    head = "갤럭시 버즈 첫 클립형\n갤럭시 버즈 온"
    hl = ("갤럭시 버즈 온",)

    def setup(self, i):
        super().setup(i)
        self.ph = [_photo(ROOT / f"media/p{k}.jpg", 6290 + k, t, w=320) for k, t in ((1, -3), (2, 2), (3, -2))]
        self.q = label("지하철보다 산책에 맞을까?", 64, fg=NAVY, bg=MINT, seed=6301, elev=7, pad=(28, 12))
        self.t = tag("귀를 막지 않는 클립형", 46, bg=NAVY2, seed=6302)
        self.cr = tag("사진: 삼성전자 뉴스룸", 26, bg=INK, seed=6303)

    def draw(self, frame, lt):
        frame.paste(BG)
        rings(frame, 540, 860, lt, 360, n=3)
        self.chrome(frame, lt, 0.1)
        for k, (x, y) in enumerate(((40, 690), (380, 670), (720, 690))):
            pop(frame, self.ph[k], x, y, lt, 0.15 + k * 0.12)
        pop(frame, self.cr, 70, 945, lt, 0.6)
        pop(frame, self.q, 70, 1030, lt, wt(0, 3) - 0.1)
        pop(frame, self.t, 70, 1170, lt, wt(0, 6))


class Open(Scene):
    kicker = "열린 귀"
    head = "주변 소리를\n함께 듣는다"
    hl = ("함께",)

    def setup(self, i):
        super().setup(i)
        self.t1 = tag("산책 · 운동", 46, bg=(18, 120, 100), seed=6401)
        self.t2 = tag("주변 소리 ✓  +  음악 ✓", 46, bg=NAVY2, seed=6402)
        self.src = tag("삼성 발표: 주변 상황을 살펴야 하는 야외 활동 용도", 28, bg=INK, seed=6403)

    def draw(self, frame, lt):
        frame.paste(BG)
        self.chrome(frame, lt)
        cx, cy = draw_wear(frame, 560, 600, 430)
        waves(frame, cx - 260, cy, lt, MINT, direction=0, spread=40, r0=20, r1=300, speed=0.6)  # 바깥에서 들어오는 주변 소리
        waves(frame, cx - 30, cy - 10, lt + 0.3, SKY, direction=0, spread=35, r0=10, r1=80, speed=1.1, width=5)  # 스피커 → 귀
        pop(frame, self.t1, 70, 1110, lt, wt(1, 3))
        pop(frame, self.t2, 70, 1200, lt, wt(1, 6))
        pop(frame, self.src, 70, 1290, lt, wt(1, 9))


class Subway(Scene):
    kicker = "몰입이 우선이라면"
    head = "시끄러운 지하철"

    def setup(self, i):
        super().setup(i)
        self.t1 = tag("음악보다 큰 소음 속에선?", 42, bg=(160, 60, 60), seed=6501)
        self.t2 = label("출시 후 비교 리뷰부터 확인", 50, fg=NAVY, bg=MINT, seed=6502, elev=6, pad=(24, 10))
        w, h = W + 200, 260
        car = [(0, 40), (w, 40), (w, 220), (0, 220)]
        parts = [(piece(w, h, car, (70, 84, 110), 6503, 0, 1.0), 0, 0)]
        for k in range(10):
            parts.append((piece(w, h, rrect(30 + k * 130, 70, 120 + k * 130, 150, 12), (160, 190, 220), 6510 + k, 1, 0.4), 0, 0))
        self.train = lift(stack(w, h, parts), 6)

    def draw(self, frame, lt):
        frame.paste(BG)
        self.chrome(frame, lt, 0.1)
        blit(frame, self.train, -100 - (lt * 260) % 130, 600)
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(ov)
        for k in range(14):  # 소음 막대
            hgt = 80 + 160 * abs(math.sin(lt * 7 + k * 1.3)) * (0.6 + 0.4 * math.sin(k))
            x = 90 + k * 64
            d.rounded_rectangle([x, 1150 - hgt, x + 40, 1150], 8, fill=CORAL + (210,))
        for k in range(14):  # 음악(작게)
            hgt = 20 + 40 * abs(math.sin(lt * 4 + k * 0.9))
            x = 90 + k * 64
            d.rounded_rectangle([x + 8, 1150 - hgt, x + 32, 1150], 6, fill=SKY + (255,))
        frame.alpha_composite(ov)
        pop(frame, self.t1, 70, 1180, lt, wt(2, 1))
        pop(frame, self.t2, 70, 1270, lt, wt(2, 6))


class Leak(Scene):
    kicker = "누음 저감"
    head = "옆 사람에겐\n얼마나 들릴까?"
    hl = ("얼마나",)

    def setup(self, i):
        super().setup(i)
        self.t1 = tag("소리 새는 걸 줄이는 기술 · 갤럭시 버즈 첫 적용", 34, bg=(18, 120, 100), seed=6601)
        self.t2 = label("얼마나 들리는지는 아직 몰라요", 48, fg=PAPER, bg=CORAL, seed=6602, elev=6, pad=(24, 10))
        self.q = label("?", 120, fg=CORAL, bg=PAPER, seed=6603, elev=6, pad=(30, 4))
        self.person = lift(stack(220, 360, [(piece(220, 360, circle_pts(110, 70, 60, 30), (150, 162, 178), 6610, 0, 0.6), 0, 0),
                                            (piece(220, 360, rrect(30, 140, 190, 360, 60), (120, 134, 152), 6611, 0, 0.6), 0, 0)]), 6)

    def draw(self, frame, lt):
        frame.paste(BG)
        self.chrome(frame, lt, 0.1)
        cx, cy = draw_wear(frame, 80, 640, 430)
        sh = 1 - 0.65 * out_cubic(prog(lt, wt(3, 4), 1.2))  # 저감: 새는 음파가 짧아짐
        waves(frame, cx, cy, lt, CORAL, direction=0, spread=60, r0=40, r1=420, shrink=sh, alpha=200)
        pop(frame, self.person, 820, 820, lt, wt(3, 9) - 0.3)
        pop(frame, self.q, 860, 700, lt, wt(3, 11))
        pop(frame, self.t1, 70, 1190, lt, wt(3, 4))
        pop(frame, self.t2, 70, 1270, lt, wt(3, 13))


class Memo(Scene):
    kicker = "퀵 보이스 메모"
    head = "쓰려면 필요한 것"

    def setup(self, i):
        super().setup(i)
        rows = ("갤럭시 AI 지원 기기", "삼성 음성 녹음 앱", "빅스비 앱", "길게 누르기 동작 따로 설정")
        self.rows = [label("· " + r, 50, fg=INK, bg=PAPER, seed=6700 + k, elev=6, pad=(24, 10)) for k, r in enumerate(rows)]
        self.ok = [label("✓ " + r, 50, fg=INK, bg=MINT, seed=6710 + k, elev=6, pad=(24, 10)) for k, r in enumerate(rows)]
        self.src = tag("삼성 발표 각주 기준 · 아이폰·구형 갤럭시는 지원 조건 확인", 28, bg=INK, seed=6720)

    def draw(self, frame, lt):
        frame.paste(BG)
        self.chrome(frame, lt)
        for k, wi in enumerate((3, 7, 9, 12)):
            t0 = wt(4, wi) - 0.1
            spr = self.ok[k] if lt > t0 + 0.6 else self.rows[k]
            pop(frame, spr, 70, 560 + k * 140, lt, t0)
        pop(frame, self.src, 70, 1150, lt, wt(4, 13))


class Good(Scene):
    kicker = "그래도 반가운 점"
    head = "최대 9.5시간 ·\n헤드 제스처"
    hl = ("9.5시간",)

    def setup(self, i):
        super().setup(i)
        self.t1 = tag("1회 충전 최대 9.5시간 연속 음악 재생", 38, bg=(18, 120, 100), seed=6801)
        self.t2 = tag("고개 끄덕임 = 전화 받기 · 가로젓기 = 끊기", 34, bg=NAVY2, seed=6802)
        self.head_spr = piece(300, 320, circle_pts(150, 160, 140, 48), SKIN, 6803, 6, 0.8)

    def draw(self, frame, lt):
        frame.paste(BG)
        self.chrome(frame, lt, 0.1)
        # 배터리
        bx, by, bw, bh = 110, 680, 360, 170
        f = out_cubic(prog(lt, wt(5, 3), 1.2))
        d = ImageDraw.Draw(frame)
        d.rounded_rectangle([bx, by, bx + bw, by + bh], 26, outline=PAPER + (255,), width=10)
        d.rounded_rectangle([bx + bw, by + 55, bx + bw + 26, by + bh - 55], 8, fill=PAPER + (255,))
        d.rounded_rectangle([bx + 20, by + 20, bx + 20 + (bw - 40) * f, by + bh - 20], 14, fill=MINT + (255,))
        d.text((bx + 90, by + 45), f"{9.5 * f:.1f}h", font=font(70), fill=NAVY)
        # 끄덕이는 머리
        if lt > wt(5, 8) - 0.3:  # 머리·귀·이어폰을 한 덩어리로 위아래 끄덕임
            dy = 22 * max(0, math.sin(max(0, lt - wt(5, 8)) * 6))
            draw_wear(frame, 600, 610 + dy, 300)
            ImageDraw.Draw(frame).arc([600, 560 + dy, 820, 600 + dy + 30], 200, 340, fill=MINT + (230,), width=6)
        pop(frame, self.t1, 70, 1150, lt, wt(5, 4))
        pop(frame, self.t2, 70, 1240, lt, wt(5, 12))


def _photo(path, seed, tilt, w=330):
    im = Image.open(path).convert("RGB")
    s_ = (w - 24) / im.width
    im = im.resize((w - 24, int(im.height * s_)), Image.LANCZOS)
    h = im.height + 24
    cv = stack(w, h, [(piece(w, h, [(0, 0), (w, 0), (w, h), (0, h)], (252, 252, 250), seed, 0, 0.6), 0, 0)])
    cv.paste(im, (12, 12))
    return lift(cv.rotate(tilt, Image.BICUBIC, expand=True), 9)


class Launch(Scene):
    kicker = "출시 정보"

    def setup(self, i):
        super().setup(i)
        self.ph = [_photo(ROOT / f"media/p{k}.jpg", 6900 + k, t) for k, t in ((1, 3), (2, -2), (3, 2))]
        self.date = label("10월 27일 국내 출시", 70, fg=INK, bg=PAPER, seed=6911, elev=8, pad=(28, 10))
        self.price = label("299,000원", 96, fg=NAVY, bg=MINT, seed=6912, elev=8, pad=(28, 6))
        self.color = tag("블랙 단일 · 발표 가격", 40, bg=NAVY2, seed=6913)
        self.cr = tag("사진: 삼성전자 뉴스룸", 26, bg=INK, seed=6914)

    def draw(self, frame, lt):
        frame.paste(BG)
        self.chrome(frame, lt)
        for k, (x, y) in enumerate(((40, 960), (375, 930), (710, 960))):
            pop(frame, self.ph[k], x, y, lt, 0.2 + k * 0.15)
        pop(frame, self.date, 70, 400, lt, wt(6, 2))
        pop(frame, self.color, 70, 560, lt, wt(6, 4))
        pop(frame, self.price, 70, 650, lt, wt(6, 7))
        pop(frame, self.cr, 70, 1270, lt, 0.6)


class Place(Scene):
    head = "내가 가장 자주\n듣는 곳은?"
    hl = ("가장 자주",)

    def setup(self, i):
        super().setup(i)
        self.cards = [label(t, 50, fg=INK, bg=c, seed=7000 + k, elev=7, pad=(30, 16)) for k, (t, c) in
                      enumerate((("산책길", MINT), ("지하철", (255, 196, 186)), ("도서관", SKY)))]
        self.src = tag("출처: 삼성전자 뉴스룸 2026.10.01 · 실사용 후기 아님", 28, bg=INK, seed=7010)

    def draw(self, frame, lt):
        frame.paste(BG)
        rings(frame, 540, 1000, lt, 300, n=3)
        self.chrome(frame, lt, 0.1)
        for k in range(3):
            pop(frame, self.cards[k], 70 + k * 330, 900 + (k % 2) * 60, lt, wt(7, 4) + k * 0.25)
        pop(frame, self.src, 70, 1300, lt, wt(7, 9))


SCENES = [Hook(), Open(), Subway(), Leak(), Memo(), Good(), Launch(), Place()]
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
        _cap[i] = label(wrap(txt, font(70), 880), 70, fg=INK, bg=PAPER, pad=(34, 14), seed=7100 + i, elev=5, align="center", amp=2.2)
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
    if i > 0 and lt < TR:  # 음파가 위로 훑으며 전환
        old = Image.new("RGBA", (W, H), (0, 0, 0, 255))
        SCENES[i - 1].draw(old, t - SC[i - 1]["start"])
        p = in_out(lt / TR)
        edge = p * (H + 160) - 80 + 30 * np.sin(np.arange(W)[None, :] / 40.0 + p * 8)
        fr = Image.fromarray(np.where((YS < edge)[..., None], np.asarray(fr), np.asarray(old)).astype(np.uint8), "RGBA")
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(ov)
        e0 = p * (H + 160) - 80
        d.line([(x, e0 + 30 * math.sin(x / 40.0 + p * 8)) for x in range(0, W + 10, 10)], fill=MINT + (230,), width=6)
        fr.alpha_composite(ov.filter(ImageFilter.GaussianBlur(1.5)))
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
    make_bgm(bgm, TOTAL, [[62, 66, 69, 73], [59, 62, 66, 69], [55, 59, 62, 66], [57, 61, 64, 68]], bpm=90, seed=31, bright=1.2)
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
