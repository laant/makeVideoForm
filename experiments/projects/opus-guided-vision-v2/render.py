#!/usr/bin/env python3
"""23-v2 제미나이 라이브 가이드 비전 — MOTION-RULES v1.0 샘플 (treatment.md).

23번 opus판의 대본·나레이션(../opus-guided-vision/audio)을 그대로 쓰고 화면만 새로 만든다.
- 연결 모티프: 뷰파인더 괄호 4개가 장면마다 대상을 '포착'(전환도 괄호가 초점을 옮기는 것으로)
- 하단 자막 없음: 포착 대상 + 음성 말풍선 문구가 나레이션 순서대로
- 박자: BGM 86 BPM 격자 — 장면 전환은 첫 단어 직전 박, 포착·등장은 단어 뒤 0.15초 안의 박
- 모션 블러: 최종 렌더 서브프레임 4장(셔터 0.2) / --still·--fast 는 1장
  ../opus-paper-04/.venv/bin/python render.py [--still 3.0,20.5] [--fast]
"""
import importlib.util, json, math, subprocess, sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent
V1DIR = ROOT.parent / "opus-guided-vision"
sys.path.insert(0, str(ROOT.parents[1]))  # experiments/ (paperkit·audiokit)
from paperkit import (W, H, FPS, font, lift, blit, rrect, piece, stack, label, clamp, prog, out_cubic, out_back, in_out, pop)  # noqa: E402
from audiokit import make_bgm, wind_sfx  # noqa: E402

_s = importlib.util.spec_from_file_location("gv1", V1DIR / "render.py")
V1 = importlib.util.module_from_spec(_s)
_s.loader.exec_module(V1)
BG, NAVY, NAVY2, MINT, PAPER, CORAL, GREY, INK = V1.BG, V1.NAVY, V1.NAVY2, V1.MINT, V1.PAPER, V1.CORAL, V1.GREY, V1.INK
tag, title, rings = V1.tag, V1.title, V1.rings

OUT = ROOT / "out"
TIM = json.loads((V1DIR / "audio/timing.json").read_text())
SC = TIM["scenes"]
TAIL = 1.0
TOTAL = TIM["total"] + TAIL
BPM = 86
BEAT = 60 / BPM
SHUTTER = 0.2
SUBS = 1 if ("--fast" in sys.argv or "--still" in sys.argv) else 4


def wt(i, k):
    return SC[i]["words"][k]["start"]


# ── 박자 ────────────────────────────────────────────────────
def beat_floor(t):
    return math.floor(t / BEAT + 1e-6) * BEAT


def snap(i, k, win=0.15):
    """장면 i 단어 k 의 시각(장면 로컬) → 단어 뒤 win 초 안에 박이 있으면 그 박, 없으면 단어 시각."""
    g = SC[i]["start"] + wt(i, k)
    b = math.ceil(g / BEAT - 1e-6) * BEAT
    return (b if b - g <= win else g) - SC[i]["start"]


# 장면 전환: 앞 장면 나레이션이 끝난 뒤 ~ 다음 첫 단어(+0.15초) 사이의 박. 그 구간에 박이 없으면 첫 단어 시각.
def cut_at(i):
    lo = SC[i - 1]["start"] + SC[i - 1]["speech"]
    hi = SC[i]["start"]
    bs = [k * BEAT for k in range(int(lo / BEAT), int((hi + 0.15) / BEAT) + 2) if lo <= k * BEAT <= hi + 0.15]
    before = [b for b in bs if b <= hi]
    return before[-1] if before else (bs[0] if bs else hi)


CUTS = [0.0] + [cut_at(i) for i in range(1, len(SC))]
XF = 0.3  # 장면 내용 크로스페이드

# ── 나레이션 엔벨로프(말풍선 파형) ─────────────────────────
_pcm = subprocess.run(["ffmpeg", "-v", "error", "-i", str(V1DIR / "audio/narration.mp3"), "-f", "s16le", "-ac", "1", "-ar", "16000", "-"],
                      capture_output=True, check=True).stdout
_x = np.frombuffer(_pcm, np.int16).astype(np.float32) / 32768
_hop = 16000 // 60
_env = np.sqrt(np.convolve(_x ** 2, np.ones(_hop) / _hop, "same"))[::_hop]
_env = np.clip(_env / (np.percentile(_env, 98) + 1e-6), 0, 1)


def env(t):
    k = int(t * 60)
    return float(_env[k]) if 0 <= k < len(_env) else 0.0


# ── 뷰파인더 괄호 (전역 상태: 시각 → 상자) ──────────────────
# 키프레임: (전역 시각, (x0,y0,x1,y1), style)  style: ok / dim / fail
KEYS = []


def key(i, lt, box, style="ok"):
    KEYS.append((SC[i]["start"] + lt, box, style))


MOVE = 0.38


def bracket_state(t):
    if not KEYS or t < KEYS[0][0]:
        return KEYS[0][1], KEYS[0][2], 1.0, 0.0
    k = max(j for j in range(len(KEYS)) if KEYS[j][0] <= t)
    t0, box, st = KEYS[k]
    prev = KEYS[k - 1][1] if k > 0 else box
    p = out_cubic(clamp((t - t0) / MOVE))
    b = tuple(a + (c - a) * p for a, c in zip(prev, box))
    # 도착 순간 '툭 조임': 18px 부풀었다가 out_back 으로 제자리
    q = clamp((t - t0 - MOVE * 0.7) / 0.28)
    infl = 18 * (1 - out_back(q)) if q > 0 else 18 * p
    return b, st, p, infl


def draw_bracket(frame, t):
    box, st, p, infl = bracket_state(t)
    x0, y0, x1, y1 = box
    x0 -= infl; y0 -= infl; x1 += infl; y1 += infl
    if st == "fail":
        sh = 10 * math.sin(t * 46) * math.exp(-3 * max(0, t - KEYS[[k for k in range(len(KEYS)) if KEYS[k][0] <= t][-1]][0]))
        x0 += sh; x1 += sh
    col = {"ok": MINT + (240,), "dim": MINT + (110,), "fail": GREY + (230,)}[st]
    d = ImageDraw.Draw(frame)
    L = max(28, min(70, (x1 - x0) / 4, (y1 - y0) / 4))
    for (cx, cy, sx, sy) in ((x0, y0, 1, 1), (x1, y0, -1, 1), (x0, y1, 1, -1), (x1, y1, -1, -1)):
        if st == "fail":  # 점선 괄호
            for a, b in (((cx, cy), (cx, cy + sy * L)), ((cx, cy), (cx + sx * L, cy))):
                n = 4
                for j in range(n):
                    if j % 2 == 0:
                        pa = (a[0] + (b[0] - a[0]) * j / n, a[1] + (b[1] - a[1]) * j / n)
                        pb = (a[0] + (b[0] - a[0]) * (j + 1) / n, a[1] + (b[1] - a[1]) * (j + 1) / n)
                        d.line([pa, pb], fill=col, width=7)
        else:
            d.line([(cx, cy + sy * L), (cx, cy), (cx + sx * L, cy)], fill=col, width=8)


# ── 말풍선 (파형 + 문구) ─────────────────────────────────────
BUB_Y = 1300
_bub = {}


def bubble_sprite(text, fg):
    k = (text, fg)
    if k not in _bub:
        _bub[k] = label(text, 52, fg=fg, bg=NAVY2, pad=(28, 14), seed=abs(hash(k)) % 9973, elev=6, amp=1.0)
    return _bub[k]


def draw_bubble(frame, t, lt, items):
    """items: [(로컬 시각, 문구, 색)] — 가장 최근 것 하나를 보여준다."""
    cur = None
    for k, (t0, txt, fg) in enumerate(items):
        if lt >= t0:
            cur = (k, t0, txt, fg)
    if not cur:
        return
    k, t0, txt, fg = cur
    spr = bubble_sprite(txt, fg)
    p = prog(lt, t0, 0.22)
    x = 70 + 150
    blit(frame, spr, x, BUB_Y + (1 - out_cubic(p)) * 20, alpha=clamp(p * 1.6))
    # 파형: 실제 나레이션 음량
    d = ImageDraw.Draw(frame)
    cy = BUB_Y + spr.h / 2
    d.rounded_rectangle([70, cy - 50, 200, cy + 50], 26, fill=NAVY2 + (255,))
    for j in range(7):
        e = env(t - j * 0.035)
        h = 8 + 70 * e * (0.6 + 0.4 * math.sin(j * 1.7 + 1))
        bx = 86 + j * 16
        d.rounded_rectangle([bx, cy - h / 2, bx + 9, cy + h / 2], 4, fill=MINT + (230,))


def src_note(frame, lt, t0, text, seed):
    spr = _note(text, seed)
    pop(frame, spr, 70, 1430, lt, t0)


_notes = {}


def _note(text, seed):
    if text not in _notes:
        _notes[text] = label(text, 28, fg=GREY, bg=BG.getpixel((70, 1440))[:3], pad=(0, 4), seed=seed, elev=0, amp=0.2)
    return _notes[text]


LIVE = label("● LIVE  카메라 공유", 28, fg=MINT, bg=NAVY, pad=(16, 6), seed=9301, elev=0, amp=0.3)


def photo(path, w, seed):
    im = Image.open(path).convert("RGB")
    h = int(im.height * w / im.width)
    im = im.resize((w, h), Image.LANCZOS)
    b = 12
    cv = stack(w + 2 * b, h + 2 * b, [(piece(w + 2 * b, h + 2 * b, [(0, 0), (w + 2 * b, 0), (w + 2 * b, h + 2 * b), (0, h + 2 * b)], (250, 250, 247), seed, 0, 1.0), 0, 0)])
    cv.paste(im, (b, b))
    return lift(cv, 9)


def box_of(x, y, spr, s=1.0, m=24):
    return (x - m, y - m, x + spr.w * s + m, y + spr.h * s + m)


# ── 장면 ────────────────────────────────────────────────────
class Scene:
    kicker, head, hl = "", "", ()

    def setup(self, i):
        self.i = i
        self.k = label(self.kicker, 34, fg=MINT, bg=NAVY, pad=(18, 6), seed=9400 + i, elev=0, amp=0.6) if self.kicker else None
        self.h = title(self.head, self.hl, 9500 + i) if self.head else None
        self.keys()

    def keys(self):
        pass

    def chrome(self, frame, lt):
        if self.k:
            pop(frame, self.k, 70, 300, lt, -0.6)
        if self.h:
            pop(frame, self.h, 70, 366, lt, -0.5)


class Hook(Scene):
    kicker = "10월 1일 구글 발표"
    head = "제미나이 라이브\n가이드 비전"
    hl = ("가이드 비전",)
    HX, HY = 190, 590

    def keys(self):
        self.hero = photo(V1DIR / "media/thumbnail.png", 680, 9601)
        self.lab = V1.LABEL
        self.sw = snap(0, 6) - 0.45  # '카메라로' 직전: 이미지 속 포장으로 줌인 → 그린 라벨
        key(0, -1, box_of(self.HX, self.HY, self.hero, m=10), "dim")
        key(0, snap(0, 3), box_of(self.HX, self.HY, self.hero, m=10), "ok")
        self.LS = 2.2
        lx, ly = 540 - self.lab.w * self.LS / 2, 900 - self.lab.h * self.LS / 2
        key(0, self.sw + 0.15, box_of(lx, ly, self.lab, self.LS, 30), "ok")
        self.lpos = (lx, ly)
        self.bub = [(snap(0, 6), "카메라로 보여주고", PAPER), (snap(0, 8), "말로 물어보기", MINT)]

    def draw(self, frame, lt):
        self.chrome(frame, lt)
        if lt < self.sw + 0.45:
            z = 1 + 0.9 * in_out(clamp((lt - self.sw) / 0.45))
            a = clamp((lt + 0.6) / 0.3) * (1 - clamp((lt - self.sw) / 0.45))
            blit(frame, self.hero, self.HX, self.HY, s=z, anchor=(0.62, 0.66), alpha=a)
        if lt > self.sw:
            q = clamp((lt - self.sw - 0.15) / 0.35)
            blit(frame, self.lab, *self.lpos, s=self.LS, anchor=(0, 0), alpha=q)
        draw_bubble(frame, SC[0]["start"] + lt, lt, self.bub)


class Uses(Scene):
    kicker = "이럴 때"
    head = "보여주고 물어보기"

    def keys(self):
        self.items = [(V1.LABEL, 120, 640, 1.3, 2), (V1.CARDS[1][1], 700, 640, 1.3, 5), (V1.CARDS[2][1], 400, 960, 1.3, 9)]
        self.bub = []
        for spr, x, y, s, k in self.items:
            key(1, snap(1, k), box_of(x, y, spr, s, 44))
        self.bub = [(snap(1, 2), "작은 라벨 읽기", MINT), (snap(1, 5), "떨어진 물건 찾기", MINT), (snap(1, 9), "옷 색·무늬 확인", MINT)]

    def draw(self, frame, lt):
        self.chrome(frame, lt)
        if not hasattr(self, "cards"):
            self.cards = [piece(int(spr.w * s) + 60, int(spr.h * s) + 60, rrect(0, 0, int(spr.w * s) + 60, int(spr.h * s) + 60, 26), PAPER, 9620 + j, 6, 1.0)
                          for j, (spr, x, y, s, k) in enumerate(self.items)]
        for j, (spr, x, y, s, k) in enumerate(self.items):
            t0 = 0.15 * j  # 세 물건은 처음부터 놓여 있고 괄호가 차례로 포착
            pop(frame, self.cards[j], x - 30, y - 30, lt, t0)
            if lt >= t0 + 0.1:
                blit(frame, spr, x, y, s=s, anchor=(0, 0), alpha=clamp((lt - t0 - 0.1) / 0.2))
        src_note(frame, lt, snap(1, 9) + 0.4, "구글 발표 속 활용 예", 9611)
        draw_bubble(frame, SC[1]["start"] + lt, lt, self.bub)


class Reframe(Scene):
    kicker = "말로 방향 안내"
    head = "비켜 있으면\n알려준다"
    hl = ("알려준다",)
    BOX = (540 - 200 - 30, 900 - 150 - 30, 540 + 200 + 30, 900 + 150 + 30)

    def keys(self):
        key(2, 0.0, self.BOX, "dim")
        self.fit = snap(2, 7) + 0.9
        key(2, self.fit, (self.BOX[0] + 20, self.BOX[1] + 20, self.BOX[2] - 20, self.BOX[3] - 20), "ok")
        self.bub = [(snap(2, 3), "카메라가 비켜 있어요", PAPER), (snap(2, 5), "“오른쪽으로 천천히”", MINT),
                    (snap(2, 7), "“조금 뒤로”", MINT), (snap(2, 9), "말로 방향을 알려줘요", PAPER)]

    def draw(self, frame, lt):
        self.chrome(frame, lt)
        p1 = in_out(prog(lt, snap(2, 5) + 0.2, 1.0))
        p2 = in_out(prog(lt, snap(2, 7) + 0.2, 0.7))
        s = 3.2 - 1.2 * p2
        lab = V1.LABEL
        cx = 980 + (540 - 980) * p1
        blit(frame, lab, cx - lab.w * s / 2, 900 - lab.h * s / 2, s=s, anchor=(0, 0))
        if snap(2, 5) - 0.1 <= lt < snap(2, 5) + 1.3:
            d = ImageDraw.Draw(frame)
            ax = 120 + 18 * math.sin(lt * 8)
            d.polygon([(ax + 70, 900), (ax, 865), (ax, 935)], fill=MINT + (255,))  # 오른쪽으로 → 화면이 따라감
        draw_bubble(frame, SC[2]["start"] + lt, lt, self.bub)


class Cond(Scene):
    kicker = "이용 조건"
    head = "내 폰에 있을까?"

    def keys(self):
        self.rows = [label(r, 50, fg=INK, bg=PAPER, seed=9700 + k, elev=6, pad=(24, 12)) for k, r in
                     enumerate(("Android 9 이상", "Gemini Live 지원 지역·언어", "순차 배포 중"))]
        self.wk = (1, 4, 10)
        key(3, -0.3, box_of(70, 640, self.rows[0], 1, 16), "dim")
        for k, r in enumerate(self.rows):
            key(3, snap(3, self.wk[k]), box_of(70, 640 + k * 150, r, 1, 16))
        self.tt = snap(3, 13) - 0.2
        self.tip = photo(V1DIR / "media/summary-01.png", 560, 9710)
        self.tx = (W - self.tip.w) / 2
        key(3, self.tt + 0.1, box_of(self.tx, 600, self.tip, 1, 14))
        self.bub = [(snap(3, 1), "Android 9 이상", MINT), (snap(3, 4), "지원 지역·언어", MINT),
                    (snap(3, 10), "천천히 배포 중", PAPER), (snap(3, 13), "아직 메뉴가 없을 수도", PAPER)]

    def draw(self, frame, lt):
        self.chrome(frame, lt)
        fade = 1 - clamp((lt - self.tt) / 0.3)
        if fade > 0:
            layer = Image.new("RGBA", frame.size, (0, 0, 0, 0))
            d = ImageDraw.Draw(layer)
            for k, r in enumerate(self.rows):
                y = 640 + k * 150
                pop(layer, r, 70, y, lt, snap(3, self.wk[k]) - 0.1)
                if lt > snap(3, self.wk[k]) + MOVE:
                    mx = 70 + r.w + 30
                    if k < 2:
                        d.line([(mx, y + 40), (mx + 18, y + 60), (mx + 50, y + 18)], fill=MINT + (255,), width=9)
                    else:
                        for j in range(3):
                            a = 0.3 + 0.7 * (0.5 + 0.5 * math.sin(lt * 6 - j))
                            d.ellipse([mx + j * 26, y + 34, mx + j * 26 + 14, y + 48], fill=GREY + (int(255 * a),))
            if fade < 1:
                layer.putalpha(layer.getchannel("A").point(lambda v, f=fade: int(v * f)))
            frame.alpha_composite(layer)
        if lt > self.tt:
            q = clamp((lt - self.tt) / 0.35)
            blit(frame, self.tip, self.tx, 600 + (1 - out_cubic(q)) * 30, alpha=q)
        draw_bubble(frame, SC[3]["start"] + lt, lt, self.bub)


class Setup(Scene):
    kicker = "켜는 법"
    head = "프로필 설정 → 켜기"
    hl = ("켜기",)
    PX0, PY0, PX1, PY1 = 150, 600, 930, 1130

    def keys(self):
        self.hdr = label("프로필 설정", 40, fg=PAPER, bg=(30, 40, 60), seed=9801, elev=0, pad=(18, 8), amp=0.4)
        self.menu = label("Use Guided Vision in Live", 34, fg=PAPER, bg=(36, 48, 70), seed=9802, elev=0, pad=(10, 6), amp=0.3)
        self.ty = self.PY0 + 140
        key(4, -0.2, (self.PX0 - 10, self.PY0 - 10, self.PX1 + 10, self.PY1 + 10), "dim")
        key(4, snap(4, 3), (self.PX0 + 10, self.PY0 + 10, self.PX0 + 330, self.PY0 + 110))
        key(4, snap(4, 6), (self.PX0 + 10, self.ty - 14, self.PX1 - 10, self.ty + 110))
        self.on_t = snap(4, 6) + BEAT
        self.cam = (540, 1215)
        key(4, snap(4, 8), (self.cam[0] - 110, self.cam[1] - 80, self.cam[0] + 110, self.cam[1] + 80))
        self.bub = [(snap(4, 3), "프로필 설정에서", PAPER), (snap(4, 6), "가이드 비전 켜기", MINT), (snap(4, 8), "라이브에서 카메라 공유", MINT)]

    def draw(self, frame, lt):
        self.chrome(frame, lt)
        d = ImageDraw.Draw(frame)
        d.rounded_rectangle([self.PX0, self.PY0, self.PX1, self.PY1], 36, fill=(22, 30, 46, 255))
        blit(frame, self.hdr, self.PX0 + 30, self.PY0 + 30)
        for k in range(3):
            y = self.ty + k * 125
            d.rounded_rectangle([self.PX0 + 26, y, self.PX1 - 26, y + 100], 18, fill=(36, 48, 70, 255))
        blit(frame, self.menu, self.PX0 + 44, self.ty + 26)
        on = in_out(prog(lt, self.on_t, 0.25))
        V1.toggle(frame, self.PX1 - 170, self.ty + 20, on)
        if lt > snap(4, 8):
            rings(frame, *self.cam, lt, 150, n=3, speed=1.1)
        V1.cam_icon(ImageDraw.Draw(frame), self.cam[0] + 6, self.cam[1], s=1.0, color=MINT if lt > snap(4, 8) else GREY)
        src_note(frame, lt, snap(4, 9), "Gemini 앱 → 프로필 설정 → Use Guided Vision in Live → Live에서 카메라 공유", 9811)
        draw_bubble(frame, SC[4]["start"] + lt, lt, self.bub)


class Mute(Scene):
    kicker = "주의"
    head = "음소거 ≠ 카메라 끄기"
    hl = ("≠",)
    MIC, CAM = (330, 860), (750, 860)

    def keys(self):
        r = 150
        key(5, -0.2, (self.MIC[0] - r, self.MIC[1] - r, self.CAM[0] + r, self.CAM[1] + r), "dim")
        key(5, snap(5, 2), (self.MIC[0] - r, self.MIC[1] - r, self.MIC[0] + r, self.MIC[1] + r))
        key(5, snap(5, 4), (self.CAM[0] - r, self.CAM[1] - r, self.CAM[0] + r, self.CAM[1] + r))
        self.off_t = snap(5, 9) + 0.9
        self.bub = [(snap(5, 2), "음소거를 눌러도", PAPER), (snap(5, 4), "카메라 공유는 계속될 수 있어요", CORAL),
                    (snap(5, 9), "끝나면 카메라 버튼 끄기", MINT)]

    def draw(self, frame, lt):
        self.chrome(frame, lt)
        d = ImageDraw.Draw(frame)
        muted = lt > snap(5, 3)
        camoff = lt > self.off_t
        for (cx, cy), kind in ((self.MIC, "mic"), (self.CAM, "cam")):
            d.ellipse([cx - 120, cy - 120, cx + 120, cy + 120], fill=(36, 48, 70, 255))
            if kind == "mic":
                V1.mic_icon(d, cx, cy + 6, s=1.4, crossed=muted)
            else:
                V1.cam_icon(d, cx, cy, s=1.3, crossed=camoff)
        d.text((self.MIC[0] - 50, 1000), "음소거", font=font(40), fill=PAPER)
        d.text((self.CAM[0] - 50, 1000), "카메라", font=font(40), fill=PAPER)
        if snap(5, 4) <= lt < self.off_t and (lt * 2) % 1 < 0.6:  # 예외색 코랄: 이 장면 '공유 중'에서만
            d.ellipse([self.CAM[0] + 78, self.CAM[1] - 112, self.CAM[0] + 112, self.CAM[1] - 78], fill=CORAL + (255,))
            d.text((self.CAM[0] + 30, self.CAM[1] - 170), "공유 중", font=font(36), fill=CORAL)
        src_note(frame, lt, snap(5, 4) + 0.5, "Gemini 도움말: 음소거해도 카메라 공유는 계속될 수 있음", 9821)
        draw_bubble(frame, SC[5]["start"] + lt, lt, self.bub)


def route_icon(seed):
    w, h = 260, 200
    cv = stack(w, h, [(piece(w, h, rrect(0, 0, w, h, 26), (36, 48, 70), seed, 0, 0.6), 0, 0)])
    d = ImageDraw.Draw(cv)
    d.line([(30, 160), (90, 110), (150, 130), (220, 50)], fill=PAPER + (255,), width=10, joint="curve")
    d.ellipse([205, 30, 240, 65], fill=PAPER + (255,))
    return lift(cv, 5)


def cone_icon(seed):
    w, h = 260, 200
    cv = stack(w, h, [(piece(w, h, rrect(0, 0, w, h, 26), (36, 48, 70), seed, 0, 0.6), 0, 0)])
    d = ImageDraw.Draw(cv)
    d.polygon([(130, 30), (180, 160), (80, 160)], fill=PAPER + (255,))
    d.rectangle([60, 160, 200, 176], fill=PAPER + (255,))
    d.line([(100, 105), (160, 105)], fill=(36, 48, 70, 255), width=12)
    return lift(cv, 5)


class Limit(Scene):
    kicker = "용도의 선"
    head = "길 안내·장애물\n감지용 아님"
    hl = ("아님",)
    R1, R2 = (100, 650), (520, 650)

    def keys(self):
        self.route, self.cone = route_icon(9901), cone_icon(9902)
        key(6, -0.2, (60, 600, 1020, 920), "dim")
        key(6, snap(6, 1), box_of(*self.R1, self.route, 1, 20), "fail")
        key(6, snap(6, 3), box_of(*self.R2, self.cone, 1, 20), "fail")
        key(6, snap(6, 6), (840, 600, 1000, 1250), "dim")
        self.x1 = label("× 길 안내", 44, fg=PAPER, bg=(80, 88, 104), seed=9903, elev=4, pad=(20, 8))
        self.x2 = label("× 장애물 감지", 44, fg=PAPER, bg=(80, 88, 104), seed=9904, elev=4, pad=(20, 8))
        self.bub = [(snap(6, 1), "길 안내용이 아니에요", PAPER), (snap(6, 3), "장애물 감지용도 아니에요", PAPER),
                    (snap(6, 6), "흰지팡이를 대신하지 않아요", MINT)]

    def draw(self, frame, lt):
        self.chrome(frame, lt)
        t6 = snap(6, 6) - 0.2
        a = 1 - 0.55 * clamp((lt - t6) / 0.3)
        blit(frame, self.route, *self.R1, alpha=a)
        blit(frame, self.cone, *self.R2, alpha=a)
        pop(frame, self.x1, self.R1[0], self.R1[1] + 230, lt, snap(6, 1) + MOVE)
        pop(frame, self.x2, self.R2[0], self.R2[1] + 230, lt, snap(6, 3) + MOVE)
        if lt > t6:
            blit(frame, V1.CANE, 860, 620, alpha=clamp((lt - t6) / 0.3))
        src_note(frame, lt, snap(6, 7), "구글: 의료기기·이동 보조수단 아님 · 오류가 있을 수 있음", 9911)
        draw_bubble(frame, SC[6]["start"] + lt, lt, self.bub)


def app_icon(seed):
    w, h = 300, 330
    cv = stack(w, h, [(piece(w, 240, rrect(30, 0, 270, 240, 56), (36, 48, 70), seed, 0, 0.6), 0, 0)])
    d = ImageDraw.Draw(cv)
    d.ellipse([90, 70, 210, 170], outline=MINT + (255,), width=10)
    d.ellipse([132, 102, 168, 138], fill=MINT + (255,))
    d.text((40, 262), "Guided Vision", font=font(36), fill=PAPER)
    return lift(cv, 6)


class Close(Scene):
    kicker = "접근성을 위해"
    head = "작은 글씨가\n어려울 때"
    hl = ("작은 글씨",)

    def keys(self):
        self.t1 = label("시각장애인·저시력 커뮤니티와 함께 개발", 40, fg=PAPER, bg=(18, 110, 92), seed=9921, elev=5, pad=(22, 10))
        self.t2 = label("Aira 테스터 1,000명+", 36, fg=MINT, bg=NAVY2, seed=9922, elev=4, pad=(18, 8))
        self.icon = app_icon(9923)
        self.ix, self.iy = 390, 860
        key(7, snap(7, 0), box_of(70, 640, self.t1, 1, 16), "dim")
        key(7, snap(7, 9), box_of(self.ix, self.iy, self.icon, 1, 24), "ok")
        self.bub = [(snap(7, 0), "커뮤니티와 함께 만든 기능", PAPER), (snap(7, 5), "작은 글씨가 어려울 때", PAPER),
                    (snap(7, 9), "내 앱에 메뉴가 있는지 확인", MINT)]

    def draw(self, frame, lt):
        self.chrome(frame, lt)
        pop(frame, self.t1, 70, 640, lt, snap(7, 0))
        pop(frame, self.t2, 70, 740, lt, snap(7, 1))
        pop(frame, self.icon, self.ix, self.iy, lt, snap(7, 9) - 0.15)
        src_note(frame, lt, snap(7, 12), "출처: Google 블로그(2026.10.01) · Gemini 도움말 · 실사용 후기 아님", 9931)
        draw_bubble(frame, SC[7]["start"] + lt, lt, self.bub)


SCENES = [Hook(), Uses(), Reframe(), Cond(), Setup(), Mute(), Limit(), Close()]
for _i, _s in enumerate(SCENES):
    _s.setup(_i)
KEYS.sort(key=lambda k: k[0])


def scene_layer(i, t):
    fr = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    SCENES[i].draw(fr, t - SC[i]["start"])
    return fr


def frame1(t):
    i = max(k for k in range(len(CUTS)) if t >= CUTS[k] - 1e-6)
    fr = BG.copy()
    lay = scene_layer(i, t)
    if i > 0 and t - CUTS[i] < XF:  # 괄호가 초점을 옮기는 동안: 앞 절반은 이전 장면이 빠지고 뒤 절반에 새 장면(글자 겹침 없음)
        p = (t - CUTS[i]) / XF
        if p < 0.5:
            lay = scene_layer(i - 1, t)
            a = 1 - in_out(p * 2)
        else:
            a = in_out(p * 2 - 1)
        lay.putalpha(lay.getchannel("A").point(lambda v, a=a: int(v * a)))
    fr.alpha_composite(lay)
    blit(fr, LIVE, W - 70 - LIVE.w, 300)
    draw_bracket(fr, t)
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
    make_bgm(bgm, TOTAL, [[60, 64, 67, 71], [57, 60, 64, 67], [62, 65, 69, 72], [55, 59, 62, 65]], bpm=BPM, seed=41, bright=1.15)
    wind_sfx(sfx, TOTAL, CUTS[1:], length=0.3)
    nfr = int(math.ceil(TOTAL * FPS))
    dst = OUT / ("final_fast.mp4" if "--fast" in sys.argv else "final.mp4")
    fc = ("[1:a]apad,asplit=2[n1][n2];[2:a]volume=0.28[b];[b][n1]sidechaincompress=threshold=0.02:ratio=6:attack=30:release=400[bd];"
          "[3:a]volume=0.16[w];[n2][bd][w]amix=inputs=3:normalize=0:duration=longest[a]")
    cmd = ["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-i", str(V1DIR / "audio/narration.mp3"), "-i", str(bgm), "-i", str(sfx), "-filter_complex", fc,
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
