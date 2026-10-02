#!/usr/bin/env python3
"""opus-guided-vision — 제미나이 라이브 가이드 비전 (23번 · 테크).

19·22번 테크 결(네이비 방안지 · 민트)에 종이로 그린 폰 카메라 뷰파인더 · 음성 말풍선 · 설정 토글 · 음소거/카메라 버튼.
구글 로고·실제 앱 화면은 쓰지 않는다. 사실은 Google 블로그(2026-10-01)·Gemini 도움말 기준.
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
_s.loader.exec_module(ST)
BG, NAVY, NAVY2, MINT, SKY, PAPER, CORAL, GREY, INK = ST.BG, ST.NAVY, ST.NAVY2, ST.MINT, ST.SKY, ST.PAPER, ST.CORAL, ST.GREY, ST.INK
tag, title, rings = ST.tag, ST.title, ST.rings
BLUE = (20, 120, 200)

OUT = ROOT / "out"
S = json.loads((ROOT / "script.json").read_text())
TIM = json.loads((ROOT / "audio/timing.json").read_text())
SC = TIM["scenes"]
TAIL = 1.0
TOTAL = TIM["total"] + TAIL


def wt(i, k):
    return SC[i]["words"][k]["start"]


# ── 소품 ────────────────────────────────────────────────────
def phone_frame(w=400, h=700, seed=0):
    parts = [(piece(w, h, rrect(0, 0, w, h, 54), (44, 52, 70), seed, 0, 0.6), 0, 0),
             (piece(w, h, rrect(16, 18, w - 16, h - 18, 42), (22, 30, 46), seed + 1, 0, 0.4, 1), 0, 0)]
    cv = stack(w, h, parts)
    ImageDraw.Draw(cv).ellipse([w / 2 - 9, 30, w / 2 + 9, 48], fill=(8, 10, 16, 255))
    return lift(cv, 9)


PHONE = phone_frame(seed=8001)
PX, PY, PW, PH = 600, 620, 400, 700  # 폰 위치(화면 오른쪽) — 왼쪽 열은 말풍선·태그
SCR = (PX + 16, PY + 60, PX + PW - 16, PY + PH - 70)  # 폰 안 '카메라 화면'


def viewfinder(frame, color=MINT, a=230):
    d = ImageDraw.Draw(frame)
    x0, y0, x1, y1 = SCR[0] + 30, SCR[1] + 40, SCR[2] - 30, SCR[3] - 120
    L = 50
    for (cx, cy, sx, sy) in ((x0, y0, 1, 1), (x1, y0, -1, 1), (x0, y1, 1, -1), (x1, y1, -1, -1)):
        d.line([(cx, cy + sy * L), (cx, cy), (cx + sx * L, cy)], fill=color + (a,), width=7)
    return x0, y0, x1, y1


def food_label(w=200, h=150, seed=0):
    cv = stack(w, h, [(piece(w, h, [(0, 0), (w, 0), (w, h), (0, h)], (250, 246, 236), seed, 0, 0.6), 0, 0)])
    d = ImageDraw.Draw(cv)
    d.rectangle([12, 12, w - 12, 34], fill=INK + (255,))
    r = np.random.default_rng(seed)
    for k in range(5):
        y = 48 + k * 19
        pts = []
        x = 14.0
        while x < w - 16 - (40 if k == 4 else 0):
            pts.append((x, y + r.normal() * 1.2))
            x += 5 + r.random() * 3
        d.line(pts, fill=(90, 90, 96, 230), width=3)  # 글자 대신 끄적임
    return lift(cv, 4)


LABEL = food_label(seed=8010)


def bubble(text, size=40, bg=PAPER, fg=INK, tail="left", seed=0):
    spr = label(text, size, fg=fg, bg=bg, pad=(26, 12), seed=seed, elev=6, amp=1.2)
    return spr


def earbud_icon(seed):
    w = h = 160
    parts = [(piece(w, h, circle_pts(70, 80, 48, 30), (40, 42, 48), seed, 3, 0.4), 0, 0),
             (piece(w, h, rrect(100, 60, 150, 100, 18), (54, 56, 64), seed + 1, 3, 0.4), 0, 0)]
    return lift(stack(w, h, parts), 5)


def shirt_icon(seed):
    w, h = 200, 190
    body = [(40, 20), (75, 8), (100, 26), (125, 8), (160, 20), (198, 60), (172, 84), (160, 74), (160, 186), (40, 186), (40, 74), (28, 84), (2, 60)]
    m = mask(w, h, lambda d, s: poly(d, s, body))
    img = paper(m, (226, 232, 240), seed, 2)
    d = ImageDraw.Draw(img)
    for y in range(30, 190, 22):
        d.line([(0, y), (w, y)], fill=(40, 90, 170, 255), width=8)
    img.putalpha(m)
    return lift(img, 5)


CARDS = [("작은 라벨 읽기", LABEL), ("떨어진 물건 찾기", earbud_icon(8020)), ("옷 색·무늬 확인", shirt_icon(8021))]


def toggle(frame, x, y, on):
    d = ImageDraw.Draw(frame)
    d.rounded_rectangle([x, y, x + 110, y + 60], 30, fill=(MINT if on > 0.5 else (90, 100, 116)) + (255,))
    cx = x + 30 + 50 * on
    d.ellipse([cx - 24, y + 6, cx + 24, y + 54], fill=PAPER + (255,))


def mic_icon(d, cx, cy, s=1.0, crossed=False, color=PAPER):
    d.rounded_rectangle([cx - 22 * s, cy - 50 * s, cx + 22 * s, cy + 14 * s], int(22 * s), fill=color + (255,))
    d.arc([cx - 40 * s, cy - 24 * s, cx + 40 * s, cy + 36 * s], 0, 180, fill=color + (255,), width=int(8 * s))
    d.line([(cx, cy + 36 * s), (cx, cy + 58 * s)], fill=color + (255,), width=int(8 * s))
    if crossed:
        d.line([(cx - 52 * s, cy - 56 * s), (cx + 52 * s, cy + 60 * s)], fill=CORAL + (255,), width=int(10 * s))


def cam_icon(d, cx, cy, s=1.0, crossed=False, color=PAPER):
    d.rounded_rectangle([cx - 54 * s, cy - 32 * s, cx + 26 * s, cy + 32 * s], int(12 * s), fill=color + (255,))
    d.polygon([(cx + 30 * s, cy - 6 * s), (cx + 58 * s, cy - 26 * s), (cx + 58 * s, cy + 26 * s), (cx + 30 * s, cy + 6 * s)], fill=color + (255,))
    if crossed:
        d.line([(cx - 64 * s, cy - 50 * s), (cx + 64 * s, cy + 50 * s)], fill=CORAL + (255,), width=int(10 * s))


def cane(seed):
    w, h = 80, 600
    parts = [(piece(w, h, [(34, 0), (46, 0), (46, h), (34, h)], (246, 246, 246), seed, 0, 0.2), 0, 0)]
    for y0 in (460, 500, 540):
        parts.append((piece(w, h, [(33, y0), (47, y0), (47, y0 + 24), (33, y0 + 24)], (220, 40, 50), seed + y0, 0, 0.2, 1), 0, 0))
    parts.append((piece(w, h, circle_pts(40, h - 12, 12), (40, 40, 44), seed + 9, 0, 0.2), 0, 0))
    return lift(stack(w, h, parts), 6)


CANE = cane(8030)


# ── 장면 ────────────────────────────────────────────────────
class Scene:
    kicker, head, hl = "", "", ()

    def setup(self, i):
        self.i = i
        self.k = tag(self.kicker, 38, bg=BLUE, seed=8100 + i) if self.kicker else None
        self.h = title(self.head, self.hl, 8200 + i) if self.head else None

    def chrome(self, frame, lt, head_t=0.2):
        if self.k:
            pop(frame, self.k, 70, 330, lt, 0.05)
        if self.h:
            pop(frame, self.h, 70, 392, lt, head_t)


class Hook(Scene):
    kicker = "10월 1일 구글 발표"
    head = "제미나이 라이브\n가이드 비전"
    hl = ("가이드 비전",)

    def setup(self, i):
        super().setup(i)
        self.b1 = bubble("이 포장 글자 읽어 줘", 40, seed=8301)
        im = Image.open(ROOT / "media/thumbnail.png").convert("RGB").resize((720, 720), Image.LANCZOS)  # 블로그 대표 이미지
        b = 16
        cv = stack(720 + 2 * b, 720 + 2 * b, [(piece(720 + 2 * b, 720 + 2 * b, [(0, 0), (752, 0), (752, 752), (0, 752)], (252, 251, 247), 8305, 0, 1.2), 0, 0)])
        cv.paste(im, (b, b))
        self.hero = lift(cv, 10)
        self.b2 = bubble("카메라로 보여주고\n말로 묻기", 44, bg=MINT, fg=NAVY, seed=8302)

    def draw(self, frame, lt):
        frame.paste(BG)
        self.chrome(frame, lt, 0.1)
        sw = wt(0, 6) - 0.35  # '카메라로 보여주고' 직전까지 블로그 대표 이미지 → 이후 뷰파인더 장면
        if lt < sw + 0.4:
            hero = Image.new("RGBA", frame.size, (0, 0, 0, 0))
            z = 1 + 0.04 * clamp(lt / max(sw, 0.1))
            blit(hero, self.hero, (W - self.hero.w) / 2, 650, s=z, anchor=(0.5, 0.5), alpha=clamp(lt / 0.25))
            if lt > sw:  # 0.4초 동안 사라짐
                hero.putalpha(hero.getchannel("A").point(lambda v, a=1 - (lt - sw) / 0.4: int(v * a)))
            frame.alpha_composite(hero)
            if lt < sw:
                return
        q = clamp((lt - sw) / 0.4)
        blit(frame, PHONE, PX, PY + (1 - out_cubic(q)) * 80, alpha=q)
        x0, y0, x1, y1 = viewfinder(frame, a=int(230 * q))
        blit(frame, LABEL, (x0 + x1) / 2 - LABEL.w / 2, (y0 + y1) / 2 - LABEL.h / 2, alpha=q)
        pop(frame, self.b1, 50, 800, lt, wt(0, 6) - 0.1)
        if lt > wt(0, 8):
            rings(frame, PX + PW / 2, PY + PH - 40, lt, 140, n=3, speed=1.0)
        pop(frame, self.b2, 50, 960, lt, wt(0, 8))


class Uses(Scene):
    kicker = "이럴 때"
    head = "보여주고 물어보기"

    def setup(self, i):
        super().setup(i)
        self.tags = [tag(t, 40, bg=NAVY2, seed=8400 + k) for k, (t, _) in enumerate(CARDS)]
        self.src = tag("구글 발표 속 활용 예", 28, bg=INK, seed=8410)
        self.cards = [piece(300, 330, rrect(0, 0, 300, 330, 28), PAPER, 8420 + k, 7, 1.0) for k in range(3)]

    def draw(self, frame, lt):
        frame.paste(BG)
        self.chrome(frame, lt, 0.1)
        for k, wi in enumerate((0, 4, 7)):
            x = 60 + k * 340
            t0 = wt(1, wi) - 0.1
            pop(frame, self.cards[k], x, 640, lt, t0)
            if lt >= t0:
                icon = CARDS[k][1]
                pop(frame, icon, x + 150 - icon.w / 2, 700, lt, t0 + 0.1)
                pop(frame, self.tags[k], x, 1000, lt, t0 + 0.2)
        pop(frame, self.src, 70, 1120, lt, wt(1, 9))


class Reframe(Scene):
    kicker = "말로 방향 안내"
    head = "비켜 있으면\n알려준다"
    hl = ("알려준다",)

    def setup(self, i):
        super().setup(i)
        self.c1 = bubble("오른쪽으로 천천히", 44, bg=MINT, fg=NAVY, seed=8501)
        self.c2 = bubble("조금 뒤로", 44, bg=MINT, fg=NAVY, seed=8502)

    def draw(self, frame, lt):
        frame.paste(BG)
        self.chrome(frame, lt, 0.1)
        blit(frame, PHONE, PX, PY)
        x0, y0, x1, y1 = viewfinder(frame)
        # 처음엔 라벨이 화면 오른쪽 밖으로 비켜 있고 너무 큼 → '오른쪽으로' 후 가운데로 → '뒤로' 후 작아짐
        p1 = in_out(prog(lt, wt(2, 5) + 0.3, 1.0))
        p2 = in_out(prog(lt, wt(2, 7) + 0.3, 0.9))
        s = 1.7 - 0.7 * p2
        cx = (x1 - 10) + ((x0 + x1) / 2 - (x1 - 10)) * p1
        cy = (y0 + y1) / 2
        tmp = Image.new("RGBA", frame.size, (0, 0, 0, 0))
        blit(tmp, LABEL, cx - LABEL.w / 2, cy - LABEL.h / 2, s=s)
        clipm = Image.new("L", frame.size, 0)
        ImageDraw.Draw(clipm).rounded_rectangle(SCR, 40, fill=255)  # 폰 화면 안만 보이게
        tmp.putalpha(Image.fromarray(np.minimum(np.asarray(tmp.getchannel("A")), np.asarray(clipm))))
        frame.alpha_composite(tmp)
        viewfinder(frame)
        if wt(2, 5) - 0.1 <= lt < wt(2, 5) + 1.4:
            d = ImageDraw.Draw(frame)
            ax = PX - 110 + 20 * math.sin(lt * 8)
            d.polygon([(ax, 1000), (ax + 70, 1035), (ax, 1070)], fill=MINT + (255,))
        pop(frame, self.c1, 50, 820, lt, wt(2, 5))
        pop(frame, self.c2, 50, 960, lt, wt(2, 7))


class Cond(Scene):
    kicker = "이용 조건"
    head = "내 폰에 있을까?"

    def setup(self, i):
        super().setup(i)
        rows = ("Android 9 이상", "Gemini Live 지원 지역·언어", "최신 앱·시스템 업데이트")
        self.rows = [label("✓ " + r, 50, fg=INK, bg=PAPER, seed=8600 + k, elev=6, pad=(24, 10)) for k, r in enumerate(rows)]
        self.roll = label("순차 배포 중 — 아직 메뉴가 없을 수 있어요", 42, fg=PAPER, bg=CORAL, seed=8610, elev=6, pad=(24, 10))
        im = Image.open(ROOT / "media/summary-01.png").convert("RGB").resize((440, 440), Image.LANCZOS)  # 블로그: 메뉴가 안 보인다면?
        b = 14
        cv = stack(440 + 2 * b, 440 + 2 * b, [(piece(468, 468, [(0, 0), (468, 0), (468, 468), (0, 468)], (252, 251, 247), 8611, 0, 1.2), 0, 0)])
        cv.paste(im, (b, b))
        self.tip = lift(cv, 9)

    def draw(self, frame, lt):
        frame.paste(BG)
        self.chrome(frame, lt, 0.1)
        tt = wt(3, 12) - 0.2  # '아직 메뉴가 없을 수도' → 블로그 이미지 '메뉴가 안 보인다면?' (조건 목록 자리를 이어받음)
        fade = 1 - clamp((lt - tt) / 0.3)
        if fade > 0:
            layer = Image.new("RGBA", frame.size, (0, 0, 0, 0))
            for k, wi in enumerate((1, 4, 7)):
                pop(layer, self.rows[k], 70, 600 + k * 140, lt, wt(3, wi) - 0.1)
            if fade < 1:
                layer.putalpha(layer.getchannel("A").point(lambda v, f=fade: int(v * f)))
            frame.alpha_composite(layer)
        pop(frame, self.roll, 70, 1080, lt, wt(3, 9))
        if lt > tt:
            pop(frame, self.tip, (W - self.tip.w) / 2, 580, lt, tt, dur=0.5)


class Setup(Scene):
    kicker = "켜는 법"
    head = "프로필 설정 → 켜기"
    hl = ("켜기",)

    def setup(self, i):
        super().setup(i)
        self.menu = label("Use Guided Vision in Live", 25, fg=PAPER, bg=(30, 40, 60), seed=8701, elev=0, pad=(18, 8), amp=0.4)
        self.hdr = label("프로필 설정", 36, fg=PAPER, bg=(30, 40, 60), seed=8702, elev=0, pad=(18, 8), amp=0.4)
        self.share = label("카메라 공유", 40, fg=NAVY, bg=MINT, seed=8703, elev=6, pad=(26, 10))
        self.path = tag("Gemini 앱 → 프로필 설정 → Use Guided Vision in Live → Live에서 카메라 공유", 26, bg=INK, seed=8704)

    def draw(self, frame, lt):
        frame.paste(BG)
        self.chrome(frame, lt, 0.1)
        blit(frame, PHONE, PX, PY)
        blit(frame, self.hdr, SCR[0] + 30, SCR[1] + 40)
        d = ImageDraw.Draw(frame)
        for k in range(4):
            y = SCR[1] + 140 + k * 110
            d.rounded_rectangle([SCR[0] + 24, y, SCR[2] - 24, y + 90], 18, fill=(36, 48, 70, 255))
        y = SCR[1] + 140
        blit(frame, self.menu, SCR[0] + 34, y + 22)
        on = in_out(prog(lt, wt(4, 6) - 0.2, 0.4))
        toggle(frame, SCR[2] - 150, y + 150, on)
        d.text((SCR[0] + 40, y + 160), "Guided Vision", font=font(32), fill=PAPER)
        if lt > wt(4, 8) - 0.2:
            rings(frame, PX + PW / 2, SCR[3] - 60, lt, 120, n=3, speed=1.1)
            cam_icon(ImageDraw.Draw(frame), PX + PW / 2, SCR[3] - 60, s=0.9, color=MINT)
        pop(frame, self.share, 50, 900, lt, wt(4, 8))
        pop(frame, self.path, 40, 1300, lt, wt(4, 9))


class Mute(Scene):
    kicker = "주의"
    head = "음소거 ≠ 카메라 끄기"
    hl = ("≠",)

    def setup(self, i):
        super().setup(i)
        self.t1 = tag("음소거해도 카메라 공유는 계속될 수 있어요", 36, bg=(160, 60, 60), seed=8801)
        self.t2 = label("끝나면 카메라 버튼 끄기", 50, fg=NAVY, bg=MINT, seed=8802, elev=6, pad=(24, 10))

    def draw(self, frame, lt):
        frame.paste(BG)
        self.chrome(frame, lt, 0.1)
        d = ImageDraw.Draw(frame)
        muted = lt > wt(5, 2)
        camoff = lt > wt(5, 11)
        for k, (cx, kind) in enumerate(((330, "mic"), (750, "cam"))):
            d.ellipse([cx - 140, 680, cx + 140, 960], fill=(36, 48, 70, 255), outline=(MINT if (kind == "cam" and not camoff) else GREY) + (255,), width=6)
            if kind == "mic":
                mic_icon(d, cx, 830, s=1.6, crossed=muted)
            else:
                cam_icon(d, cx, 820, s=1.5, crossed=camoff)
        d.text((260, 980), "음소거", font=font(40), fill=PAPER)
        d.text((680, 980), "카메라", font=font(40), fill=PAPER)
        if muted and not camoff and int(lt * 2) % 2 == 0:
            d.ellipse([850, 690, 880, 720], fill=(240, 60, 60, 255))
            d.text((800, 640), "공유 중", font=font(34), fill=(255, 140, 130))
        pop(frame, self.t1, 70, 1080, lt, wt(5, 4))
        pop(frame, self.t2, 70, 1170, lt, wt(5, 9))


class Limit(Scene):
    kicker = "용도의 선"
    head = "길 안내·장애물\n감지용 아님"
    hl = ("아님",)

    def setup(self, i):
        super().setup(i)
        self.n1 = label("× 길 안내", 50, fg=PAPER, bg=CORAL, seed=8901, elev=6, pad=(24, 10))
        self.n2 = label("× 장애물 감지", 50, fg=PAPER, bg=CORAL, seed=8902, elev=6, pad=(24, 10))
        self.n3 = label("흰지팡이를 대신하지 않아요", 44, fg=INK, bg=PAPER, seed=8903, elev=6, pad=(24, 10))
        self.src = tag("구글: 오류가 있을 수 있음 · 의료기기·이동 보조수단 아님", 28, bg=INK, seed=8904)

    def draw(self, frame, lt):
        frame.paste(BG)
        self.chrome(frame, lt, 0.1)
        pop(frame, self.n1, 70, 680, lt, wt(6, 1))
        pop(frame, self.n2, 70, 800, lt, wt(6, 3))
        pop(frame, CANE, 820, 620, lt, wt(6, 6) - 0.3)
        pop(frame, self.n3, 70, 960, lt, wt(6, 6))
        pop(frame, self.src, 70, 1080, lt, wt(6, 7))


class Close(Scene):
    kicker = "접근성을 위해"
    head = "작은 글씨가\n어려울 때"
    hl = ("작은 글씨",)

    def setup(self, i):
        super().setup(i)
        self.t1 = tag("시각장애인·저시력 커뮤니티와 함께 개발 · Aira 테스터 1,000명+", 32, bg=(18, 120, 100), seed=9001)
        self.t2 = label("내 앱에 메뉴가 있는지부터 확인", 50, fg=NAVY, bg=MINT, seed=9002, elev=6, pad=(24, 10))
        self.src = tag("출처: Google 블로그(2026.10.01) · Gemini 도움말 · 실사용 후기 아님", 26, bg=INK, seed=9003)

    def draw(self, frame, lt):
        frame.paste(BG)
        self.chrome(frame, lt, 0.1)
        blit(frame, PHONE, 640, 760, s=0.6, anchor=(0, 0))
        rings(frame, 640 + PW * 0.3, 760 + PH * 0.3, lt, 260, n=3)
        pop(frame, self.t1, 70, 660, lt, wt(7, 0))
        pop(frame, self.t2, 70, 1040, lt, wt(7, 9))
        pop(frame, self.src, 70, 1150, lt, wt(7, 12))


SCENES = [Hook(), Uses(), Reframe(), Cond(), Setup(), Mute(), Limit(), Close()]
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
        _cap[i] = label(wrap(txt, font(70), 880), 70, fg=INK, bg=PAPER, pad=(34, 14), seed=9100 + i, elev=5, align="center", amp=2.2)
    spr = _cap[i]
    p = prog(t, st, 0.16)
    blit(frame, spr, (W - spr.w) / 2, 1570 - spr.h + (1 - out_cubic(p)) * 14, alpha=clamp(p * 1.6))


TR = 0.4
XS = np.arange(W)[None, :]


def frame_at(t):
    i = max(k for k in range(len(SC)) if t >= SC[k]["start"] - 1e-6)
    lt = t - SC[i]["start"]
    fr = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    SCENES[i].draw(fr, lt)
    if i > 0 and lt < TR:  # 뷰파인더 셔터처럼 가운데서 열리며 전환
        old = Image.new("RGBA", (W, H), (0, 0, 0, 255))
        SCENES[i - 1].draw(old, t - SC[i - 1]["start"])
        p = in_out(lt / TR)
        half = p * (W / 2 + 20)
        m = np.abs(XS - W / 2) < half
        fr = Image.fromarray(np.where(np.repeat(m, H, 0)[..., None], np.asarray(fr), np.asarray(old)).astype(np.uint8), "RGBA")
        d = ImageDraw.Draw(fr)
        for x in (W / 2 - half, W / 2 + half):
            d.line([(x, 0), (x, H)], fill=MINT + (230,), width=6)
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
    make_bgm(bgm, TOTAL, [[60, 64, 67, 71], [57, 60, 64, 67], [62, 65, 69, 72], [55, 59, 62, 65]], bpm=86, seed=41, bright=1.15)
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
