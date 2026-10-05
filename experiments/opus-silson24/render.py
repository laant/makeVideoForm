#!/usr/bin/env python3
"""27 실손24, 10월 7일 네이버·토스 앱 안에서 청구 — MOTION-RULES v1.0 (treatment.md).

크림 감열지 바탕 · 잉크 · 신호색 그린 · 예외색 레드(5장면 도장만). 연결 모티프 = 종이 영수증.
하단 자막 없음(화면 문구가 나레이션 순서대로) · 박자 맞춤(84 BPM 합성 BGM) · 최종 모션 블러 4장.
사실: 금융위 2026-09-30 보도자료 · 실손24 이용안내(보험개발원).
  ../opus-paper-04/.venv/bin/python render.py [--still 3,12] [--fast]
"""
import json, math, subprocess, sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent))
from paperkit import (W, H, FPS, font, lift, blit, rrect, circle_pts, piece, stack, full_bg, label,  # noqa: E402
                      clamp, prog, out_cubic, out_back, in_out, pop)
from audiokit import make_bgm, wind_sfx  # noqa: E402

CREAM = (244, 238, 226)
PAPER = (253, 252, 248)
INK = (31, 42, 58)
GREEN = (30, 138, 99)
GREEN_L = (214, 238, 226)
RED = (200, 69, 46)
GREY = (128, 132, 140)
LINE = (210, 202, 188)

OUT = ROOT / "out"
TIM = json.loads((ROOT / "audio/timing.json").read_text())
SC = TIM["scenes"]
TAIL = 1.2
TOTAL = TIM["total"] + TAIL
BPM = 84
BEAT = 60 / BPM
SHUTTER = 0.2
SUBS = 1 if ("--fast" in sys.argv or "--still" in sys.argv) else 4


def wt(i, k):
    return SC[i]["words"][k]["start"]


def snap(i, k, win=0.15):
    g = SC[i]["start"] + wt(i, k)
    b = math.ceil(g / BEAT - 1e-6) * BEAT
    return (b if b - g <= win else g) - SC[i]["start"]


def cut_at(i):
    lo = SC[i - 1]["start"] + SC[i - 1]["speech"]
    hi = SC[i]["start"]
    bs = [k * BEAT for k in range(int(lo / BEAT), int((hi + 0.15) / BEAT) + 2) if lo <= k * BEAT <= hi + 0.15]
    before = [b for b in bs if b <= hi]
    return before[-1] if before else (bs[0] if bs else hi)


CUTS = [0.0] + [cut_at(i) for i in range(1, len(SC))]
XF = 0.36


# ── 바탕 · 공통 ──────────────────────────────────────────────
def make_bg():
    B = full_bg(CREAM, 27)
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    for y in range(0, H, 60):  # 감열지 점선 결
        for x in range(0, W, 24):
            d.point((x, y), fill=INK + (26,))
    B.alpha_composite(ov)
    return B


BG = make_bg()


def kicker(text, seed):
    return label(text, 34, fg=GREEN, bg=CREAM, pad=(0, 6), seed=seed, elev=0, amp=0.3)


def title(text, hl=(), seed=0):
    return label(text, 86, fg=INK, bg=PAPER, hl=hl, hlc=GREEN, seed=seed, elev=7)


def chip(text, seed, size=40, fg=INK, bg=PAPER, elev=5):
    return label(text, size, fg=fg, bg=bg, pad=(22, 10), seed=seed, elev=elev, amp=0.9)


def note(text, seed, size=28):
    return label(text, size, fg=GREY, bg=CREAM, pad=(0, 4), seed=seed, elev=0, amp=0.2)


def receipt(w=240, h=320, seed=0, head="영수증", lines=5, check=False):
    zz = [(0, 0), (w, 0), (w, h - 14)]
    n = 12
    for j in range(n, -1, -1):  # 아래 절취선 톱니
        zz.append((w * j / n, h - (0 if j % 2 else 14)))
    zz.append((0, h - 14))
    cv = stack(w, h, [(piece(w, h, zz, PAPER, seed, 0, 0.6), 0, 0)])
    d = ImageDraw.Draw(cv)
    f = font(int(w * 0.13))
    d.text((w * 0.1, h * 0.07), head, font=f, fill=INK)
    for k in range(lines):
        y = h * 0.28 + k * h * 0.1
        d.line([(w * 0.1, y), (w * (0.62 if k % 2 else 0.8), y)], fill=LINE + (255,), width=max(3, w // 60))
        d.line([(w * 0.72, y), (w * 0.9, y)], fill=LINE + (255,), width=max(3, w // 60))
    d.line([(w * 0.1, h * 0.8), (w * 0.9, h * 0.8)], fill=INK + (255,), width=max(3, w // 70))
    if check:
        cx, cy, r = w * 0.78, h * 0.12, w * 0.1
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=GREEN + (255,))
        d.line([(cx - r * 0.5, cy), (cx - r * 0.1, cy + r * 0.4), (cx + r * 0.55, cy - r * 0.45)], fill=PAPER + (255,), width=max(3, w // 50))
    return lift(cv, 6)


RC = receipt(240, 320, 2701)
RC_OK = receipt(240, 320, 2701, check=True)
RC_S = receipt(130, 170, 2702)


def photo(path, w, seed):
    im = Image.open(path).convert("RGB")
    h = int(im.height * w / im.width)
    im = im.resize((w, h), Image.LANCZOS)
    b = 12
    cv = stack(w + 2 * b, h + 2 * b, [(piece(w + 2 * b, h + 2 * b, [(0, 0), (w + 2 * b, 0), (w + 2 * b, h + 2 * b), (0, h + 2 * b)], PAPER, seed, 0, 1.0), 0, 0)])
    cv.paste(im, (b, b))
    return lift(cv, 9)


def box(w, h, seed, color=PAPER, r=26, elev=5):
    return lift(stack(w, h, [(piece(w, h, rrect(0, 0, w, h, r), color, seed, 0, 0.8), 0, 0)]), elev)


def check_mark(d, cx, cy, s=1.0, color=GREEN):
    d.ellipse([cx - 26 * s, cy - 26 * s, cx + 26 * s, cy + 26 * s], fill=color + (255,))
    d.line([(cx - 12 * s, cy), (cx - 3 * s, cy + 10 * s), (cx + 14 * s, cy - 10 * s)], fill=PAPER + (255,), width=int(6 * s))


def arrow(d, x0, y, x1, p, color=INK, w=6):
    if p <= 0:
        return
    xe = x0 + (x1 - x0) * p
    d.line([(x0, y), (xe, y)], fill=color + (255,), width=w)
    if p > 0.9:
        d.polygon([(xe + 4, y), (xe - 18, y - 13), (xe - 18, y + 13)], fill=color + (255,))


def fade_layer(frame, lay, a):
    if a < 1:
        lay.putalpha(lay.getchannel("A").point(lambda v, a=a: int(v * a)))
    frame.alpha_composite(lay)


# ── 장면 ────────────────────────────────────────────────────
class Scene:
    kick, head, hl = "", "", ()

    def setup(self, i):
        self.i = i
        self.k = kicker(self.kick, 2800 + i) if self.kick else None
        self.h = title(self.head, self.hl, 2900 + i) if self.head else None
        self.prep()

    def prep(self):
        pass

    def s(self, k):
        return snap(self.i, k)

    def chrome(self, frame, lt):
        if self.k:
            pop(frame, self.k, 70, 292, lt, -0.6)
        if self.h:
            pop(frame, self.h, 70, 350, lt, -0.5)


class Hook(Scene):
    kick = "금융위 9월 30일 발표 · 10월 7일부터"
    head = "네이버·토스 앱 안에서\n실손 청구 끝까지"
    hl = ("끝까지",)

    def prep(self):
        self.hero = photo(ROOT / "media/thumbnail.png", 620, 2710)
        self.chips = [chip(t, 2711 + j) for j, t in enumerate(("네이버 지도", "네이버페이", "토스"))]
        self.phone = box(340, 560, 2714, color=INK, r=50, elev=8)
        self.n = note("AI 제작 설명용 이미지 · 실제 앱 화면 아님", 2715)
        self.sw = self.s(8) - 0.3  # '실손보험' 직전에 대표 이미지 → 폰 속 영수증

    def draw(self, frame, lt):
        self.chrome(frame, lt)
        if lt < self.sw + 0.4:
            a = clamp((lt + 0.5) / 0.3) * (1 - clamp((lt - self.sw) / 0.4))
            lay = Image.new("RGBA", frame.size, (0, 0, 0, 0))
            blit(lay, self.hero, (W - self.hero.w) / 2, 600, s=1 + 0.03 * clamp(lt / 5))
            blit(lay, self.n, (W - self.n.w) / 2, 600 + self.hero.h + 6)
            fade_layer(frame, lay, a)
        if lt > self.sw:
            q = out_cubic(clamp((lt - self.sw) / 0.4))
            px, py = (W - self.phone.w) / 2, 620
            blit(frame, self.phone, px, py + (1 - q) * 60, alpha=q)
            d = ImageDraw.Draw(frame)
            d.rounded_rectangle([px + 18, py + 60, px + self.phone.w - 18, py + self.phone.h - 40], 30, fill=(250, 248, 242, int(255 * q)))
            p = out_back(clamp((lt - self.s(9)) / 0.45))
            if lt > self.s(9):
                rc = RC_OK if lt > self.s(10) else RC
                blit(frame, rc, W / 2 - rc.w / 2, py + 120 + (1 - p) * 500)
        for j, k in enumerate((2, 4, 5)):
            pop(frame, self.chips[j], 110 + j * 300, 1290, lt, self.s(k))


class Flow(Scene):
    kick = "지금 vs 10월 7일"
    head = "건너가던 단계가\n줄어요"
    hl = ("줄어요",)

    def prep(self):
        self.now = chip("지금", 2720, 34, fg=GREY, bg=CREAM, elev=0)
        self.new = chip("10월 7일", 2721, 34, fg=GREEN, bg=CREAM, elev=0)
        self.a1 = chip("앱", 2722, 40)
        self.a2 = chip("실손24 사이트", 2723, 40)
        self.a3 = chip("보험사", 2724, 40)
        self.b1 = chip("네이버·토스 앱 안에서", 2725, 40, fg=PAPER, bg=GREEN)
        self.b3 = chip("보험사", 2726, 40)
        self.form = box(940, 420, 2727)
        self.fields = ["병원", "진료일", "보험사", "계좌번호"]
        self.fk = [self.s(11), self.s(12), (self.s(12) + self.s(13)) / 2, self.s(13)]
        self.md = chip("마이데이터 동의 시 입력 생략", 2728, 34, fg=GREEN, bg=GREEN_L, elev=0)
        self.n = note("실제 이용 때 동의 항목은 직접 읽어보기", 2729)

    def draw(self, frame, lt):
        self.chrome(frame, lt)
        d = ImageDraw.Draw(frame)
        y1, y2 = 600, 760
        t1 = self.s(4)
        dim = 0.45 if lt > self.s(8) else 1.0
        lay = Image.new("RGBA", frame.size, (0, 0, 0, 0))
        pop(lay, self.now, 70, y1 - 46, lt, 0.0)
        pop(lay, self.a1, 70, y1, lt, 0.1)
        pop(lay, self.a2, 330, y1, lt, t1)
        pop(lay, self.a3, 800, y1, lt, t1 + 0.35)
        ld = ImageDraw.Draw(lay)
        arrow(ld, 180, y1 + 38, 318, out_cubic(prog(lt, t1 - 0.2, 0.3)))
        arrow(ld, 650, y1 + 38, 788, out_cubic(prog(lt, t1 + 0.15, 0.3)))
        if lt > self.s(8):
            ld.line([(70, y1 + 40), (980, y1 + 40)], fill=GREY + (200,), width=4)
        fade_layer(frame, lay, dim)
        if lt > self.s(8) - 0.1:
            pop(frame, self.new, 70, y2 - 46, lt, self.s(8) - 0.1)
            pop(frame, self.b1, 70, y2, lt, self.s(8))
            pop(frame, self.b3, 800, y2, lt, self.s(8) + 0.25)
            arrow(d, 560, y2 + 38, 788, out_cubic(prog(lt, self.s(8) + 0.1, 0.35)), color=GREEN, w=8)
            if lt > self.s(8) + 0.2:
                p = in_out(clamp((lt - self.s(8) - 0.2) / 0.8))
                blit(frame, RC_S, 560 + 160 * p, y2 - 50, s=0.55, anchor=(0, 0))
        if lt > self.s(9) - 0.1:
            fy = 930
            pop(frame, self.form, 70, fy, lt, self.s(9) - 0.1)
            pop(frame, self.md, 100, fy + 30, lt, self.s(10))
            for j, f in enumerate(self.fields):
                x, y = 100 + (j % 2) * 450, fy + 120 + (j // 2) * 130
                if lt > self.s(9) + 0.1:
                    d.text((x, y), f, font=font(36), fill=GREY)
                    d.rounded_rectangle([x, y + 48, x + 400, y + 100], 12, outline=LINE + (255,), width=3, fill=PAPER + (255,))
                    if lt > self.fk[j]:
                        pp = clamp((lt - self.fk[j]) / 0.25)
                        d.rounded_rectangle([x + 4, y + 52, x + 4 + 392 * pp, y + 96], 10, fill=GREEN_L + (255,))
                        check_mark(d, x + 360, y + 74, 0.75)
            pop(frame, self.n, 80, 1380, lt, self.s(14))


class Linked(Scene):
    kick = "① 연계 병원 확인"
    head = "내 병원,\n연계됐을까?"
    hl = ("연계",)

    def prep(self):
        self.where = chip("실손24 홈페이지 ‘참여병원·약국’에서 확인", 2730, 34, fg=INK, bg=PAPER)
        self.big = label("47.7%", 120, fg=GREEN, bg=PAPER, pad=(0, 0), seed=2731, elev=0, amp=0.1)
        self.base = chip("연계 5만340곳 · 9월 28일 기준", 2732, 34, fg=INK, bg=GREEN_L, elev=0)
        self.half = chip("아직 절반이 안 돼요", 2733, 40, fg=PAPER, bg=INK)

    def draw(self, frame, lt):
        self.chrome(frame, lt)
        pop(frame, self.where, 70, 590, lt, self.s(3))
        cx, cy, r = 540, 960, 220
        d = ImageDraw.Draw(frame)
        if lt > self.s(5) - 0.2:
            a = clamp((lt - self.s(5) + 0.2) / 0.3)
            d.ellipse([cx - r - 14, cy - r - 14, cx + r + 14, cy + r + 14], fill=PAPER + (int(255 * a),))
            d.arc([cx - r, cy - r, cx + r, cy + r], 0, 360, fill=LINE + (int(255 * a),), width=46)
        if lt > self.s(9):  # 원호는 쓸리듯 그려지되 숫자는 완성값으로만
            p = out_cubic(clamp((lt - self.s(9)) / 0.7))
            d.arc([cx - r, cy - r, cx + r, cy + r], -90, -90 + 360 * 0.477 * p, fill=GREEN + (255,), width=46)
            blit(frame, self.big, cx - self.big.w / 2, cy - self.big.h / 2, alpha=clamp((lt - self.s(9)) / 0.2))
        if lt > self.s(14):
            for y0 in (cy - r - 40, cy + r - 40):  # 절반 선: 고리 위·아래에만(숫자 가리지 않게)
                for k in range(0, 80, 20):
                    d.line([(cx, y0 + k), (cx, y0 + k + 10)], fill=INK + (220,), width=5)
            pop(frame, self.half, cx - self.half.w / 2, cy + r + 50 + 70, lt, self.s(14))
        pop(frame, self.base, cx - self.base.w / 2, cy + r + 50, lt, self.s(5))
        pop(frame, note("출처: 금융위원회 2026.9.30 보도자료", 2734), 70, 1480, lt, self.s(9))


class Docs(Scene):
    kick = "② 전자로 가는 서류"
    head = "자동 전송 3종 +\n사진 첨부"
    hl = ("3종", "사진")

    def prep(self):
        self.docs = [receipt(220, 290, 2740 + j, head=h) for j, h in enumerate(("영수증", "세부내역", "처방전"))]
        self.names = [chip(t, 2745 + j, 32) for j, t in enumerate(("진료비 계산서·영수증", "세부산정내역서", "처방전"))]
        self.extra = receipt(220, 290, 2748, head="진단서")
        self.photo = chip("사진으로 별도 첨부", 2749, 40, fg=PAPER, bg=GREEN)
        self.rail = chip("전자 전송 → 보험사", 2750, 34, fg=GREEN, bg=GREEN_L, elev=0)
        self.ex2 = note("진단서·입퇴원확인서 등 추가서류", 2751, 30)

    def draw(self, frame, lt):
        self.chrome(frame, lt)
        d = ImageDraw.Draw(frame)
        ks = (4, 5, 6)
        for j in range(3):
            t0 = self.s(ks[j]) - 0.05
            x = 80 + j * 320
            if lt > t0:
                p = out_back(clamp((lt - t0) / 0.4))
                blit(frame, self.docs[j], x + 20, 600 + (1 - p) * 120, alpha=clamp((lt - t0) / 0.15))
            pop(frame, self.names[j], x, 910, lt, t0 + 0.1)
        if lt > self.s(4) + 0.3:
            p = out_cubic(clamp((lt - self.s(4) - 0.3) / 1.6))
            d.line([(80, 1000), (80 + 900 * p, 1000)], fill=GREEN + (255,), width=8)
        pop(frame, self.rail, 640, 1020, lt, self.s(6) + 0.3)
        if lt > self.s(7) - 0.1:
            p = out_back(clamp((lt - self.s(7) + 0.1) / 0.4))
            blit(frame, self.extra, 90, 1110 + (1 - p) * 100, s=0.8, anchor=(0, 0), alpha=clamp((lt - self.s(7)) / 0.15))
            pop(frame, self.ex2, 300, 1130, lt, self.s(8))
        if lt > self.s(10):
            # 카메라 아이콘 + 사진 첨부
            cx, cy = 360, 1250
            d.rounded_rectangle([cx - 40, cy - 26, cx + 40, cy + 30], 10, fill=INK + (255,))
            d.ellipse([cx - 16, cy - 14, cx + 16, cy + 18], fill=PAPER + (255,))
            pop(frame, self.photo, 430, 1220, lt, self.s(10))
        pop(frame, note("출처: 실손24 이용안내(보험개발원)", 2752), 70, 1480, lt, self.s(6))


class Sent(Scene):
    kick = "③ 전송 뒤 확인"
    head = "전송했다고\n지급이 끝난 건 아니에요"
    hl = ("아니에요",)

    def prep(self):
        self.done = chip("전송 완료", 2760, 40, fg=PAPER, bg=GREEN)
        st = label("지급 확정 아님", 64, fg=RED, bg=PAPER, pad=(26, 12), seed=2761, elev=0, amp=1.4)
        cv = Image.new("RGBA", (st.w + 30, st.h + 30), (0, 0, 0, 0))
        cv.alpha_composite(st.img, (15 - st.ox, 15 - st.oy) if False else (15, 15))
        dd = ImageDraw.Draw(cv)
        dd.rounded_rectangle([6, 6, cv.width - 6, cv.height - 6], 16, outline=RED + (255,), width=8)
        self.stamp = cv.rotate(-8, Image.BICUBIC, expand=True)
        self.steps = [chip(t, 2762 + j, 40) for j, t in enumerate(("접수", "심사", "결과 확인"))]

    def draw(self, frame, lt):
        self.chrome(frame, lt)
        d = ImageDraw.Draw(frame)
        rc = RC_OK if lt > self.s(1) else RC
        pop(frame, rc, 110, 640, lt, -0.2)
        pop(frame, self.done, 400, 700, lt, self.s(1))
        if lt > self.s(3):  # 예외색 레드: 이 도장에서만
            p = clamp((lt - self.s(3)) / 0.18)
            s = 1.6 - 0.6 * out_cubic(p)
            im = self.stamp.resize((int(self.stamp.width * s), int(self.stamp.height * s)), Image.BICUBIC)
            if p < 1:
                im.putalpha(im.getchannel("A").point(lambda v, p=p: int(v * p)))
            frame.alpha_composite(im, (int(660 - im.width / 2), int(860 - im.height / 2)))
        ks = (7, 8, 10)
        for j in range(3):
            x = 70 + j * 330
            t0 = self.s(ks[j])
            pop(frame, self.steps[j], x, 1150, lt, t0)
            if j < 2:
                arrow(d, x + self.steps[j].w + 12, 1188, x + 318, out_cubic(prog(lt, t0 + 0.2, 0.3)))
        pop(frame, note("보험금은 보험사 심사 뒤 확정 · 보완 요청도 확인", 2766, 30), 70, 1300, lt, self.s(10))


class Fork(Scene):
    kick = "연계 안 됐다면"
    head = "청구 길은\n여전히 있어요"
    hl = ("여전히",)

    def prep(self):
        self.l1 = chip("연계 안 된 병원", 2770, 36, fg=GREY, bg=PAPER)
        self.l2 = chip("보험사 기존 청구 방법", 2771, 40, fg=PAPER, bg=INK)
        self.r1 = chip("실손24 앱·홈페이지", 2772, 36, fg=INK, bg=PAPER)
        self.r2 = chip("지금도 청구 가능", 2773, 40, fg=PAPER, bg=GREEN)

    def draw(self, frame, lt):
        self.chrome(frame, lt)
        d = ImageDraw.Draw(frame)
        pop(frame, RC_S, W / 2 - RC_S.w / 2, 600, lt, -0.2)
        sx, sy = W / 2, 790
        pl = out_cubic(prog(lt, self.s(0), 0.5))
        pr = out_cubic(prog(lt, self.s(10), 0.5))
        if pl > 0:
            d.line([(sx, sy), (sx - (sx - 260) * pl, sy + 180 * pl)], fill=INK + (255,), width=7)
        if pr > 0:
            d.line([(sx, sy), (sx + (820 - sx) * pr, sy + 180 * pr)], fill=GREEN + (255,), width=7)
        pop(frame, self.l1, 70, 990, lt, self.s(0) + 0.2)
        pop(frame, self.l2, 70, 1080, lt, self.s(5))
        pop(frame, self.r1, 560, 990, lt, self.s(10))
        pop(frame, self.r2, 560, 1080, lt, self.s(13))


class Close(Scene):
    kick = "앞으로"
    head = "연말 연계율\n80~90% 목표"
    hl = ("80~90%",)

    def prep(self):
        self.c1 = chip("실손24 가입 약 521만 명", 2780, 46, fg=INK, bg=PAPER)
        self.c2 = chip("누적 청구 461만 건", 2781, 36, fg=GREY, bg=PAPER)
        self.c3 = chip("연말 목표 연계율 80~90%", 2782, 46, fg=PAPER, bg=GREEN)
        self.pile = [receipt(200, 260, 2790 + j) for j in range(4)]
        self.go = chip("미뤄둔 진료 영수증부터", 2795, 42, fg=INK, bg=GREEN_L, elev=0)
        self.src = note("출처: 금융위원회 2026.9.30 · 실손24 이용안내 · 일반 안내이며 지급을 보장하지 않음", 2796, 26)

    def draw(self, frame, lt):
        self.chrome(frame, lt)
        pop(frame, self.c1, 70, 600, lt, self.s(3))
        pop(frame, self.c2, 70, 700, lt, self.s(3) + 0.4)
        pop(frame, self.c3, 70, 790, lt, self.s(8))
        t0 = self.s(11)
        for j, rc in enumerate(self.pile):
            if lt > t0 + 0.08 * j:
                p = out_back(clamp((lt - t0 - 0.08 * j) / 0.4))
                blit(frame, rc, 560 + j * 70, 960 + (1 - p) * 160 + j * 12, rot=(-10 + j * 7), alpha=clamp((lt - t0 - 0.08 * j) / 0.15))
        if lt > self.s(13):
            check_mark(ImageDraw.Draw(frame), 870, 960, 1.6)
        pop(frame, self.go, 70, 1000, lt, t0)
        pop(frame, self.src, 70, 1480, lt, self.s(14))


SCENES = [Hook(), Flow(), Linked(), Docs(), Sent(), Fork(), Close()]
for _i, _s in enumerate(SCENES):
    _s.setup(_i)


def scene_layer(i, t):
    fr = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    SCENES[i].draw(fr, t - SC[i]["start"])
    return fr


def frame1(t):
    i = max(k for k in range(len(CUTS)) if t >= CUTS[k] - 1e-6)
    fr = BG.copy()
    if i > 0 and t - CUTS[i] < XF:  # 영수증이 화면을 가로질러 미끄러지는 동안 장면 교체(겹침 없음)
        p = (t - CUTS[i]) / XF
        lay = scene_layer(i - 1 if p < 0.5 else i, t)
        a = 1 - in_out(p * 2) if p < 0.5 else in_out(p * 2 - 1)
        fade_layer(fr, lay, a)
        blit(fr, RC_S, W + 40 - (W + 260) * in_out(p), 1000, rot=-6)
    else:
        fr.alpha_composite(scene_layer(i, t))
    return fr


def frame_at(t):
    if SUBS == 1:
        return frame1(t).convert("RGB")
    acc = None
    for k in range(SUBS):
        tk = t + ((k + 0.5) / SUBS - 0.5) * SHUTTER / FPS
        a = np.asarray(frame1(max(0.0, tk)).convert("RGB"), np.float32)
        acc = a if acc is None else acc + a
    return Image.fromarray((acc / SUBS + 0.5).astype(np.uint8))


def main():
    OUT.mkdir(exist_ok=True)
    if "--still" in sys.argv:
        for ts in sys.argv[sys.argv.index("--still") + 1].split(","):
            frame_at(float(ts)).save(OUT / f"still_{ts}.png")
        print("stills ok · cuts", [round(c, 2) for c in CUTS])
        return
    bgm, sfx = OUT / "bgm.wav", OUT / "sfx.wav"
    make_bgm(bgm, TOTAL, [[60, 64, 67, 72], [57, 60, 64, 69], [53, 57, 60, 65], [55, 59, 62, 67]], bpm=BPM, seed=27, bright=1.0)
    wind_sfx(sfx, TOTAL, CUTS[1:], length=0.3)
    nfr = int(math.ceil(TOTAL * FPS))
    dst = OUT / ("final_fast.mp4" if "--fast" in sys.argv else "final.mp4")
    fc = ("[1:a]apad,asplit=2[n1][n2];[2:a]volume=0.3[b];[b][n1]sidechaincompress=threshold=0.02:ratio=6:attack=30:release=400[bd];"
          "[3:a]volume=0.14[w];[n2][bd][w]amix=inputs=3:normalize=0:duration=longest[a]")
    cmd = ["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-i", str(ROOT / "audio/narration.mp3"), "-i", str(bgm), "-i", str(sfx), "-filter_complex", fc,
           "-map", "0:v", "-map", "[a]", "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "-t", f"{TOTAL:.3f}", str(dst)]
    ff = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for f in range(nfr):
        ff.stdin.write(frame_at(f / FPS).tobytes())
    ff.stdin.close()
    ff.wait()
    print("✓", dst.relative_to(ROOT), f"({TOTAL:.1f}s, 서브프레임 {SUBS})")


if __name__ == "__main__":
    main()
