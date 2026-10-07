#!/usr/bin/env python3
"""opus-smarttag3 — 스마트태그3 아이폰 지원, 정밀 찾기도 똑같이 될까 (테크 · autoShorts판과 같은 나레이션).

테크 질감: 짙은 네이비 방안지 · 민트 형광 선 · 종이로 오린 태그/폰(실루엣, 로고 없음) · 레이더처럼 퍼지는 탐색 원.
수치는 삼성 뉴스룸 각주 기준(2026-10-01 확인). 도구: ../paperkit.py · ../audiokit.py
  ../opus-paper-04/.venv/bin/python render.py [--still 1,9]
"""
import json, math, subprocess, sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parents[1]))  # experiments/ (paperkit·audiokit)
from paperkit import (W, H, FPS, font, paper, lift, blit, mask, poly, rrect, circle_pts, piece, stack, _paste_into,  # noqa: E402
                      label, clamp, prog, out_cubic, out_back, in_out, pop, wrap, full_bg)
from audiokit import make_bgm, wind_sfx  # noqa: E402

OUT = ROOT / "out"
TIM = json.loads((ROOT / "audio/timing.json").read_text())
SC = TIM["scenes"]
TAIL = 1.0
TOTAL = TIM["total"] + TAIL

NAVY = (16, 26, 44)
NAVY2 = (28, 42, 66)
MINT = (92, 232, 196)
SKY = (124, 196, 255)
PAPER = (238, 242, 246)
CORAL = (255, 112, 96)
GREY = (120, 134, 152)
INK = (20, 28, 44)


def wt(i, k):
    return SC[i]["words"][k]["start"]


def tag(text, size=42, bg=NAVY2, fg=PAPER, seed=0):
    return label(text, size, fg=fg, bg=bg, pad=(22, 8), seed=seed, elev=5, amp=1.0)


def title(text, hl=(), seed=0, size=90):
    return label(text, size, fg=INK, bg=PAPER, hl=hl, hlc=(20, 120, 200), seed=seed, elev=8)


# ── 배경: 네이비 방안지 ─────────────────────────────────────
def make_bg():
    B = full_bg(NAVY, 5)
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    for x in range(0, W, 45):
        d.line([(x, 0), (x, H)], fill=MINT + ((34 if x % 225 == 0 else 14),), width=1)
    for y in range(0, H, 45):
        d.line([(0, y), (W, y)], fill=MINT + ((34 if y % 225 == 0 else 14),), width=1)
    B.alpha_composite(ov)
    vg = Image.new("L", (W, H), 0)
    ImageDraw.Draw(vg).ellipse([-300, 200, W + 300, H - 100], fill=255)
    vg = vg.filter(ImageFilter.GaussianBlur(220))
    dark = Image.new("RGBA", (W, H), (6, 10, 20, 150))
    dark.putalpha(Image.eval(vg, lambda v: int(150 * (1 - v / 255))))
    B.alpha_composite(dark)
    return B


BG = make_bg()


# ── 소품 ────────────────────────────────────────────────────
def tracker(d_=170, seed=0, color=PAPER):
    w = h = d_ + 20
    parts = [(piece(w, h, rrect(0, 0, d_, d_, d_ * 0.32), color, seed, 0, 0.6), 0, 0),
             (piece(w, h, circle_pts(d_ * 0.5, d_ * 0.5, d_ * 0.2, 36), (200, 208, 218), seed + 1, 1, 0.3), 0, 0)]
    img = stack(w, h, parts)
    d = ImageDraw.Draw(img)
    d.ellipse([d_ * 0.78, d_ * 0.08, d_ * 0.92, d_ * 0.22], fill=(0, 0, 0, 0), outline=GREY + (255,), width=4)  # 고리 구멍
    return lift(img, 8)


def phone(w=230, h=460, seed=0, body=(52, 62, 80), screen=(30, 44, 70), notch=True):
    parts = [(piece(w, h, rrect(0, 0, w, h, 36), body, seed, 0, 0.6), 0, 0),
             (piece(w, h, rrect(12, 14, w - 12, h - 14, 26), screen, seed + 1, 0, 0.4, 1), 0, 0)]
    img = stack(w, h, parts)
    d = ImageDraw.Draw(img)
    if notch:
        d.rounded_rectangle([w / 2 - 34, 24, w / 2 + 34, 44], 10, fill=(10, 12, 18, 255))
    else:
        d.ellipse([w / 2 - 9, 24, w / 2 + 9, 42], fill=(10, 12, 18, 255))
    return lift(img, 9), img


IPH, IPH_RAW = phone(seed=11, notch=True)
GAL, GAL_RAW = phone(seed=21, notch=False, body=(60, 66, 76))
SMALLPH = [phone(90, 170, 31 + k, notch=False)[0] for k in range(6)]
TAG_BIG = tracker(200, 41)
TAG_MID = tracker(130, 42)


def pin(seed):
    w, h = 90, 120
    drop = [(45 + 40 * math.cos(math.radians(a)), 42 + 40 * math.sin(math.radians(a))) for a in range(150, 391, 8)] + [(45, 118)]
    return lift(stack(w, h, [(piece(w, h, drop, MINT, seed, 0, 0.6), 0, 0), (piece(w, h, circle_pts(45, 42, 16), NAVY, seed + 1, 1, 0.3), 0, 0)]), 6)


PIN = pin(51)


def check_mark(ok, size=64):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    c = MINT if ok else CORAL
    if ok:
        d.line([(size * 0.18, size * 0.52), (size * 0.42, size * 0.76), (size * 0.84, size * 0.26)], fill=c + (255,), width=int(size * 0.14), joint="curve")
    else:
        d.line([(size * 0.22, size * 0.22), (size * 0.78, size * 0.78)], fill=c + (255,), width=int(size * 0.14))
        d.line([(size * 0.78, size * 0.22), (size * 0.22, size * 0.78)], fill=c + (255,), width=int(size * 0.14))
    return img


def table_card():
    w, h = 940, 520
    cv = stack(w, h, [(piece(w, h, [(0, 0), (w, 0), (w, h), (0, h)], PAPER, 61, 0, 1.0), 0, 0)])
    d = ImageDraw.Draw(cv)
    f, fb = font(44), font(46)
    d.text((40, 36), "기능", font=fb, fill=GREY)
    d.text((560, 36), "갤럭시", font=fb, fill=INK)
    d.text((760, 36), "아이폰", font=fb, fill=INK)
    d.line([(30, 110), (w - 30, 110)], fill=(190, 198, 208, 255), width=3)
    rows = ["컴퍼스 뷰 (방향·거리)", "폰 울리기", "두고 온 알림"]
    for k, r in enumerate(rows):
        y = 150 + k * 120
        d.text((40, y), r, font=f, fill=INK)
        cv.alpha_composite(check_mark(True, 70), (585, y - 6))
    return lift(cv, 9), [150 + k * 120 for k in range(3)]


TABLE, TROWS = table_card()
XMARK = check_mark(False, 70)


def chain_broken(seed):
    w, h = 520, 200
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for k, (x, ang) in enumerate(((40, -8), (150, 8), (300, -8), (410, 8))):
        link = Image.new("RGBA", (130, 80), (0, 0, 0, 0))
        ImageDraw.Draw(link).rounded_rectangle([6, 6, 124, 74], 34, outline=GREY + (255,), width=16)
        link = link.rotate(ang, Image.BICUBIC, expand=True)
        img.alpha_composite(link, (x + (30 if k >= 2 else -10), 60))
    return lift(img, 6)


CHAIN = chain_broken(71)


def wall(seed):
    w, h = 70, 520
    img = stack(w, h, [(piece(w, h, [(0, 0), (w, 0), (w, h), (0, h)], (96, 108, 126), seed, 0, 0.8), 0, 0)])
    d = ImageDraw.Draw(img)
    for y in range(0, h, 52):
        d.line([(0, y), (w, y)], fill=(70, 80, 96, 255), width=3)
        d.line([(w / 2 if (y // 52) % 2 else 0, y), (w / 2 if (y // 52) % 2 else 0, y + 52)], fill=(70, 80, 96, 255), width=3)
    return lift(img, 8)


WALL = wall(81)


def rings(frame, cx, cy, t, rmax, color=MINT, n=5, clip_x=None, speed=0.55):
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    for k in range(n):
        ph = (t * speed + k / n) % 1.0
        r = 30 + ph * rmax
        a = int(200 * (1 - ph))
        d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=color + (a,), width=5)
    if clip_x is not None:
        ImageDraw.Draw(ov).rectangle([clip_x, 0, W, H], fill=(0, 0, 0, 0))
    frame.alpha_composite(ov)


# ── 장면 ────────────────────────────────────────────────────
class Scene:
    kicker, head, hl = "", "", ()

    def setup(self, i):
        self.i = i
        self.k = tag(self.kicker, 38, bg=(20, 120, 200), seed=5000 + i) if self.kicker else None
        self.h = title(self.head, self.hl, 5100 + i) if self.head else None

    def chrome(self, frame, lt, head_t=0.2):
        if self.k:
            pop(frame, self.k, 70, 330, lt, 0.05)
        if self.h:
            pop(frame, self.h, 70, 392, lt, head_t)


class Hook(Scene):
    kicker = "갤럭시 스마트태그3"
    head = "아이폰에서도\n될까?"
    hl = ("아이폰에서도",)

    def setup(self, i):
        super().setup(i)
        self.li = tag("iPhone", 40, seed=5201)
        self.lg = tag("Galaxy", 40, seed=5202)
        self.sub = label("반은 맞고, 반은 달라요", 60, fg=NAVY, bg=MINT, seed=5203, elev=6, pad=(28, 10))

    def draw(self, frame, lt):
        frame.paste(BG)
        rings(frame, 540, 1110, lt, 330, n=4)
        self.chrome(frame, lt)
        pop(frame, IPH, 60, 860, lt, 0.4)
        pop(frame, GAL, 790, 860, lt, 0.6)
        pop(frame, self.li, 100, 1340, lt, 0.6)
        pop(frame, self.lg, 830, 1340, lt, 0.8)
        b = 0.5 + 0.5 * math.sin(lt * 3)
        blit(frame, TAG_BIG, 440, 1000 - 8 * b)
        pop(frame, self.sub, 70, 700, lt, wt(0, 5))


class Works(Scene):
    kicker = "SmartThings Find"
    head = "아이폰에서 되는 것"

    def setup(self, i):
        super().setup(i)
        self.t1 = tag("✓ 태그 위치 확인", 46, bg=(18, 120, 100), seed=5301)
        self.t2 = tag("✓ 가족과 위치 공유", 46, bg=(18, 120, 100), seed=5302)
        self.fam = [phone(110, 210, 5310 + k, notch=k % 2 == 0)[0] for k in range(2)]

    def draw(self, frame, lt):
        frame.paste(BG)
        self.chrome(frame, lt)
        blit(frame, IPH, 160, 700)
        p = out_back(prog(lt, wt(1, 2) - 0.2, 0.5), 1.4)
        if p > 0:
            blit(frame, PIN, 230, 770 - 30 * (1 - p), alpha=clamp(p * 3))
            rings(frame, 275, 900, lt, 120, n=3, speed=0.9)
        if lt > wt(1, 4) - 0.1:
            q = out_cubic(prog(lt, wt(1, 4) - 0.1, 0.6))
            ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            d = ImageDraw.Draw(ov)
            for k, (x, y) in enumerate(((700, 760), (760, 1040))):
                ex, ey = 400 + (x - 400) * q, 900 + (y + 90 - 900) * q
                d.line([(400, 900), (ex, ey)], fill=MINT + (220,), width=5)
            frame.alpha_composite(ov)
            for k, (x, y) in enumerate(((700, 760), (760, 1040))):
                blit(frame, self.fam[k], x, y, alpha=q)
        pop(frame, self.t1, 70, 1210, lt, wt(1, 3))
        pop(frame, self.t2, 70, 1300, lt, wt(1, 4))


NOT_SRC = tag("삼성 발표 각주: Compass View · Ring Phone · Left Behind Alert iOS 미제공", 26, bg=NAVY2, seed=5401)
SMALL_TAG = tracker(50, 5820)


class NotIOS(Scene):
    kicker = "iOS 미지원"
    head = "아이폰에선 안 되는 것"

    def draw(self, frame, lt):
        frame.paste(BG)
        self.chrome(frame, lt)
        pop(frame, TABLE, 70, 720, lt, 0.2, dur=0.5)
        if lt > 0.7:
            for k, y in enumerate(TROWS):
                t0 = wt(2, 8) + k * 0.18
                if lt >= t0:
                    p = out_back(prog(lt, t0, 0.35), 2.0)
                    img = XMARK.resize((max(1, int(70 * p)), max(1, int(70 * p))))
                    frame.alpha_composite(img, (int(70 + 9 + 785 + 35 - img.width / 2), int(720 + 9 + y - 6 + 35 - img.height / 2)))
        pop(frame, NOT_SRC, 70, 1290, lt, wt(2, 9))


class FindMy(Scene):
    kicker = "애플 '나의 찾기'"
    head = "연동도\n발표엔 없었어요"
    hl = ("없었어요",)

    def setup(self, i):
        super().setup(i)
        self.stamp = label("발표에 없음", 84, fg=PAPER, bg=CORAL, seed=5501, elev=8, pad=(30, 10), tilt=-6)
        self.note = tag("아이폰 등록·연동 방식은 이번 자료로 확인되지 않음", 32, seed=5502)

    def draw(self, frame, lt):
        frame.paste(BG)
        self.chrome(frame, lt, 0.1)
        blit(frame, IPH, 120, 820, s=0.8)
        blit(frame, TAG_MID, 800, 980)
        gap = 40 * out_cubic(prog(lt, wt(3, 3), 0.5))
        blit(frame, CHAIN, 330 - gap, 960, alpha=1)
        pop(frame, self.stamp, 360, 1120, lt, wt(3, 4), anchor=(0.5, 0.5))
        pop(frame, self.note, 70, 1310, lt, wt(3, 5))


class Range(Scene):
    kicker = "정밀 탐색 · Compass View"
    head = "최대 60m, 조건이 있어요"
    hl = ("60m",)

    def setup(self, i):
        super().setup(i)
        self.models = [tag(t, 34, bg=(20, 120, 200), seed=5600 + k) for k, t in enumerate(("S26 울트라", "S26 플러스", "Z 폴드8 울트라", "Z 폴드8"))]
        self.bt = tag("블루투스 6.0 채널 사운딩 지원 갤럭시", 32, seed=5610)
        self.cond = label("장애물 없는 조건 기준", 50, fg=NAVY, bg=MINT, seed=5611, elev=6, pad=(24, 8))

    def draw(self, frame, lt):
        frame.paste(BG)
        self.chrome(frame, lt, 0.1)
        wall_on = lt >= wt(4, 11) - 0.1
        rings(frame, 230, 1010, lt, 900, n=6, clip_x=(700 if wall_on else None))
        blit(frame, TAG_MID, 165, 945)
        # 60m 자
        p = out_cubic(prog(lt, 0.1, 0.8))
        d = ImageDraw.Draw(frame)
        d.line([(230, 1180), (230 + 780 * p, 1180)], fill=PAPER + (255,), width=5)
        for k in range(0, 7):
            x = 230 + 130 * k
            if x <= 230 + 780 * p:
                d.line([(x, 1166), (x, 1194)], fill=PAPER + (255,), width=4)
                d.text((x - 16, 1200), f"{k * 10}", font=font(26), fill=PAPER)
        if wall_on:
            pop(frame, WALL, 700, 760, lt, wt(4, 11) - 0.1)
            pop(frame, self.cond, 70, 1300, lt, wt(4, 11))
        for k, m in enumerate(self.models):
            pop(frame, m, 70 + (k % 2) * 330, 640 + (k // 2) * 72, lt, wt(4, 4) + k * 0.12)
        pop(frame, self.bt, 70, 800, lt, wt(4, 4) + 0.6)


class Network(Scene):
    kicker = "찾기 네트워크"
    head = "실시간 GPS와 달라요"
    hl = ("GPS",)

    def setup(self, i):
        super().setup(i)
        self.t1 = tag("주변 갤럭시 기기가 감지 → 위치 갱신", 38, bg=(18, 120, 100), seed=5701)
        self.t2 = tag("갱신 시점: 주변 기기·네트워크·설정·지역에 따라", 30, seed=5702)
        self.spots = [(150, 760), (470, 690), (820, 780), (880, 1120), (120, 1110), (520, 1220)]

    def draw(self, frame, lt):
        frame.paste(BG)
        self.chrome(frame, lt)
        cx, cy = 540, 1000
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(ov)
        for k, (x, y) in enumerate(self.spots):
            on = lt >= wt(5, 3) + k * 0.25
            if on:
                q = out_cubic(prog(lt, wt(5, 3) + k * 0.25, 0.4))
                d.line([(cx, cy), (cx + (x + 45 - cx) * q, cy + (y + 85 - cy) * q)], fill=MINT + (170,), width=4)
        frame.alpha_composite(ov)
        for k, (x, y) in enumerate(self.spots):
            on = lt >= wt(5, 3) + k * 0.25
            blit(frame, SMALLPH[k], x, y, alpha=1.0 if on else 0.45)
        rings(frame, cx, cy, lt, 160, n=3, speed=0.8)
        blit(frame, TAG_MID, cx - 65, cy - 65)
        pop(frame, self.t1, 70, 1300, lt, wt(5, 4))
        pop(frame, self.t2, 70, 1375, lt, wt(5, 6))


class Positive(Scene):
    kicker = "그래도 반가운 변화"
    head = "다음이 더 기대돼요"
    hl = ("기대돼요",)

    def setup(self, i):
        super().setup(i)
        self.rows = [label(t, 50, fg=NAVY, bg=c, seed=5800 + k, elev=6, pad=(26, 10)) for k, (t, c) in
                     enumerate((("스마트태그 첫 아이폰 위치 공유", MINT), ("탐색 거리 이전 세대의 약 3배", SKY), ("지원 기기 확대 가능", PAPER)))]
        self.src = tag("출처: 삼성전자 뉴스룸 (2026.09.30 발표)", 28, seed=5810)

    def draw(self, frame, lt):
        frame.paste(BG)
        self.chrome(frame, lt, 0.1)
        for k, (wi) in enumerate((1, 4, 9)):
            pop(frame, self.rows[k], 70, 700 + k * 120, lt, wt(6, wi) - 0.1)
        if lt >= wt(6, 4):  # 이전 세대 vs 3배 원
            q = out_cubic(prog(lt, wt(6, 4), 0.9))
            ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            d = ImageDraw.Draw(ov)
            cx, cy = 540, 1210
            d.ellipse([cx - 40, cy - 40, cx + 40, cy + 40], outline=GREY + (255,), width=4)
            r = 40 + 80 * q
            d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=MINT + (230,), width=6)
            frame.alpha_composite(ov)
            blit(frame, SMALL_TAG, cx - 35, cy - 35)
        pop(frame, self.src, 70, 1340, lt, wt(6, 14))


class Cta(Scene):
    kicker = "출시 정보"

    def setup(self, i):
        super().setup(i)
        self.date = label("10월 7일 국내 출시", 76, fg=INK, bg=PAPER, seed=5901, elev=8, pad=(30, 12))
        self.price = label("44,000원", 110, fg=NAVY, bg=MINT, seed=5902, elev=8, pad=(30, 8))
        self.c1 = tag("□ 내 폰 모델", 46, seed=5903)
        self.c2 = tag("□ 필요한 기능 (위치 공유 / 정밀 탐색)", 40, seed=5904)
        self.src = tag("삼성전자 뉴스룸 · 2026.10.01 확인", 28, bg=NAVY2, seed=5905)

    def draw(self, frame, lt):
        frame.paste(BG)
        self.chrome(frame, lt)
        rings(frame, 860, 1000, lt, 260, n=3)
        blit(frame, TAG_MID, 795, 935)
        pop(frame, self.date, 70, 420, lt, wt(7, 1))
        pop(frame, self.price, 70, 590, lt, wt(7, 3))
        pop(frame, self.c1, 70, 1020, lt, wt(7, 6))
        pop(frame, self.c2, 70, 1110, lt, wt(7, 8))
        pop(frame, self.src, 70, 1330, lt, wt(7, 10))


SCENES = [Hook(), Works(), NotIOS(), FindMy(), Range(), Network(), Positive(), Cta()]
for _i, _s in enumerate(SCENES):
    _s.setup(_i)

# 자막(숫자는 아라비아)
CAPS = [
    [("스마트태그3, 아이폰에서도 쓸 수 있을까요?", 0), ("반은 맞고 반은 달라요.", 5)],
    [("아이폰에서도 태그 위치를 확인하고", 0), ("공유할 수 있어요.", 4)],
    [("하지만 컴퍼스 뷰, 폰 울리기,", 0), ("두고 온 알림은 아이폰에선 안 돼요.", 5)],
    [("애플 '나의 찾기' 연동도", 0), ("발표엔 없었어요.", 4)],
    [("60m 정밀 탐색은", 0), ("S26, 폴드8 일부 모델만 되고,", 4), ("장애물이 없을 때 기준이에요.", 11)],
    [("멀리 있는 위치는 주변 갤럭시가 찾아줘서,", 0), ("실시간 GPS와는 달라요.", 6)],
    [("그래도 첫 아이폰 지원에,", 0), ("탐색 거리는 약 3배.", 4), ("지원 기기도 늘 수 있어 다음이 기대돼요.", 9)],
    [("출시는 10월 7일, 44,000원.", 0), ("내 폰과 필요한 기능부터 확인하세요.", 6)],
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
        _cap[i] = label(wrap(txt, font(70), 880), 70, fg=INK, bg=PAPER, pad=(34, 14), seed=6000 + i, elev=5, align="center", amp=2.2)
    spr = _cap[i]
    p = prog(t, st, 0.16)
    blit(frame, spr, (W - spr.w) / 2, 1570 - spr.h + (1 - out_cubic(p)) * 14, alpha=clamp(p * 1.6))


# ── 전환: 스캔 라인이 훑고 지나간다 ─────────────────────────
TR = 0.4
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
        edge = p * (H + 120) - 60
        out = np.where((YS < edge)[..., None], np.asarray(fr), np.asarray(old))
        fr = Image.fromarray(out.astype(np.uint8), "RGBA")
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(ov)
        d.rectangle([0, edge - 4, W, edge + 4], fill=MINT + (230,))
        d.rectangle([0, edge - 40, W, edge - 4], fill=MINT + (50,))
        fr.alpha_composite(ov.filter(ImageFilter.GaussianBlur(2)))
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
    make_bgm(bgm, TOTAL, [[60, 64, 67, 71], [57, 60, 64, 67], [53, 57, 60, 64], [55, 59, 62, 66]], bpm=88, seed=11, bright=1.2)
    wind_sfx(sfx, TOTAL, [s["start"] for s in SC[1:]], length=0.35)
    nfr = int(math.ceil(TOTAL * FPS))
    dst = OUT / "final.mp4"
    fc = ("[1:a]apad,asplit=2[n1][n2];[2:a]volume=0.28[b];[b][n1]sidechaincompress=threshold=0.02:ratio=6:attack=30:release=400[bd];"
          "[3:a]volume=0.22[w];[n2][bd][w]amix=inputs=3:normalize=0:duration=longest[a]")
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
