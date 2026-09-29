#!/usr/bin/env python3
"""opus-paper-04 — 04 구리 태극기 45초판을 기존 모듈 없이 만드는 실험 렌더러.

모든 그림을 코드로 그린다(이미지 생성 없음): 절차적 종이 결(섬유·요철) + 가위로 오린 가장자리 +
층마다 떨어지는 그림자. 태극기는 국기 규격(3:2, 태극 지름 = 세로/2, 괘 규격)대로 조각을 오려 붙이고,
땅에 떨어지는 그림자는 깃발 실루엣을 광원 방향으로 투영한 단색 그림자다.

재사용: 확정된 나레이션 음성·단어 타이밍(autoShorts/episodes/guri-flags-45-visit) — 비교를 위해 소리는 동일.
  .venv/bin/python render.py                 # → out/final.mp4
  .venv/bin/python render.py --still 1.2,9   # → out/still_<t>.png (확인용)
"""
import json, math, subprocess, sys, wave
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent
EP = ROOT.parents[1] / "autoShorts/episodes/guri-flags-45-visit"
OUT = ROOT / "out"
W, H, FPS = 1080, 1920, 30
FONT = "/System/Library/Fonts/AppleSDGothicNeo.ttc"
_fonts = {}


def font(sz, bold=True):
    k = (sz, bold)
    if k not in _fonts:
        _fonts[k] = ImageFont.truetype(FONT, sz, index=6 if bold else 4)
    return _fonts[k]


INK = (40, 35, 31)
RED = (205, 46, 58)      # 태극기 빨강
BLUE = (0, 71, 160)      # 태극기 파랑
BLACK = (26, 24, 24)
WHITE = (251, 248, 241)
GOLD = (206, 164, 74)

# ── 종이 결 ─────────────────────────────────────────────────
TEXN = 2400


def _smooth(n, cell, rng):
    k = n // cell + 3
    small = (rng.random((k, k)) * 255).astype(np.uint8)
    big = Image.fromarray(small).resize((k * cell, k * cell), Image.BICUBIC)
    return np.asarray(big, np.float32)[:n, :n] / 255


def _make_tex():
    rng = np.random.default_rng(11)
    t = 0.45 * _smooth(TEXN, 2, rng) + 0.35 * _smooth(TEXN, 9, rng) + 0.2 * _smooth(TEXN, 80, rng)
    t -= t.mean()
    fib = Image.new("L", (TEXN, TEXN), 128)
    d = ImageDraw.Draw(fib)
    for _ in range(14000):
        x, y = rng.random(2) * TEXN
        a = rng.random() * math.pi
        ln = 5 + rng.random() * 24
        d.line([(x, y), (x + math.cos(a) * ln, y + math.sin(a) * ln)], fill=int(128 + (rng.random() - 0.5) * 60))
    fib = np.asarray(fib.filter(ImageFilter.GaussianBlur(0.7)), np.float32) / 255 - 0.5
    return 1 + 0.09 * t + 0.09 * fib


TEX = _make_tex()


def paper(mask, color, seed=0, bevel=2):
    """마스크(L) 모양으로 오린 종이 한 장 (RGBA)."""
    w, h = mask.size
    r = np.random.default_rng(seed)
    ox, oy = int(r.integers(0, TEXN - w + 1)), int(r.integers(0, TEXN - h + 1))
    f = TEX[oy:oy + h, ox:ox + w]
    rgb = np.array(color, np.float32)[None, None, :] * f[..., None]
    m = np.asarray(mask, np.float32) / 255
    if bevel:
        hi = np.clip(m - np.roll(np.roll(m, bevel, 0), bevel, 1), 0, 1)
        lo = np.clip(m - np.roll(np.roll(m, -bevel, 0), -bevel, 1), 0, 1)
        rgb = rgb + hi[..., None] * 26 - lo[..., None] * 24
    out = np.dstack([np.clip(rgb, 0, 255), m * 255]).astype(np.uint8)
    return Image.fromarray(out, "RGBA")


class Sprite:
    def __init__(self, img, ox=0, oy=0):
        self.img, self.ox, self.oy = img, ox, oy

    @property
    def w(self):
        return self.img.width - 2 * self.ox

    @property
    def h(self):
        return self.img.height - 2 * self.oy


def lift(img, elev, opacity=0.34):
    """종이를 바닥에서 elev 만큼 띄운다 — 빛은 왼쪽 위, 그림자는 오른쪽 아래."""
    if elev <= 0:
        return Sprite(img)
    pad = int(elev * 3) + 4
    cv = Image.new("RGBA", (img.width + pad * 2, img.height + pad * 2), (0, 0, 0, 0))
    sa = Image.new("L", cv.size, 0)
    sa.paste(img.getchannel("A"), (pad + int(elev * 0.6), pad + int(elev)))
    sa = sa.filter(ImageFilter.GaussianBlur(max(1, elev * 0.8))).point(lambda v: int(v * opacity))
    sh = Image.new("RGBA", cv.size, (45, 32, 20, 0))
    sh.putalpha(sa)
    cv.alpha_composite(sh)
    cv.alpha_composite(img, (pad, pad))
    return Sprite(cv, pad, pad)


def _paste(frame, img, px, py):
    px, py = int(round(px)), int(round(py))
    x0, y0 = max(0, px), max(0, py)
    x1, y1 = min(W, px + img.width), min(H, py + img.height)
    if x1 <= x0 or y1 <= y0:
        return
    frame.alpha_composite(img.crop((x0 - px, y0 - py, x1 - px, y1 - py)), (x0, y0))


def blit(frame, spr, x, y, s=1.0, sx=None, sy=None, anchor=(0.5, 0.5), rot=0.0, alpha=1.0):
    """spr 의 종이 좌상단을 (x, y) 에 — 크기·회전은 anchor(종이 기준 비율) 중심."""
    sx = s if sx is None else sx
    sy = s if sy is None else sy
    img = spr.img
    cx, cy = x + anchor[0] * spr.w, y + anchor[1] * spr.h
    if sx != 1 or sy != 1:
        nw, nh = max(1, int(img.width * sx)), max(1, int(img.height * sy))
        img = img.resize((nw, nh), Image.BILINEAR)
    px = cx - (spr.ox + anchor[0] * spr.w) * sx
    py = cy - (spr.oy + anchor[1] * spr.h) * sy
    if rot:
        c = (px + img.width / 2, py + img.height / 2)
        img = img.rotate(rot, Image.BICUBIC, expand=True)
        px, py = c[0] - img.width / 2, c[1] - img.height / 2
    if alpha < 1:
        img = img.copy()
        img.putalpha(img.getchannel("A").point(lambda v: int(v * alpha)))
    _paste(frame, img, px, py)


# ── 오리기 도구 ──────────────────────────────────────────────
SS = 3


def mask(w, h, fn):
    m = Image.new("L", (w * SS, h * SS), 0)
    fn(ImageDraw.Draw(m), SS)
    return m.resize((w, h), Image.LANCZOS)


def poly(d, s, pts, fill=255):
    d.polygon([(x * s, y * s) for x, y in pts], fill=fill)


def deckle(pts, amp=1.3, step=7, seed=0):
    """가위로 오린 듯 살짝 삐뚤한 외곽선."""
    r = np.random.default_rng(seed)
    out = []
    n = len(pts)
    for i in range(n):
        a, b = np.array(pts[i], float), np.array(pts[(i + 1) % n], float)
        L = float(np.linalg.norm(b - a)) or 1.0
        k = max(1, int(L / step))
        nrm = np.array([-(b - a)[1], (b - a)[0]]) / L
        for j in range(k):
            p = a + (b - a) * j / k
            out.append(tuple(p + nrm * (r.normal() * amp if j else 0)))
    return out


def rrect(x0, y0, x1, y1, rad, n=6):
    pts = []
    for cx, cy, a0 in ((x1 - rad, y0 + rad, -90), (x1 - rad, y1 - rad, 0), (x0 + rad, y1 - rad, 90), (x0 + rad, y0 + rad, 180)):
        for i in range(n + 1):
            a = math.radians(a0 + 90 * i / n)
            pts.append((cx + rad * math.cos(a), cy + rad * math.sin(a)))
    return pts


def circle_pts(cx, cy, r, n=48):
    return [(cx + r * math.cos(2 * math.pi * i / n), cy + r * math.sin(2 * math.pi * i / n)) for i in range(n)]


def piece(w, h, pts, color, seed=0, elev=4, amp=1.2, bevel=2):
    m = mask(w, h, lambda d, s: poly(d, s, deckle(pts, amp, 7, seed) if amp else pts))
    return lift(paper(m, color, seed, bevel), elev)


def stack(w, h, parts):
    """여러 종이 조각을 한 장의 RGBA 로 붙인다. parts: (Sprite, x, y)"""
    cv = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    for spr, x, y in parts:
        _paste_into(cv, spr, x, y)
    return cv


def _paste_into(cv, spr, x, y):
    img = spr.img
    px, py = int(round(x - spr.ox)), int(round(y - spr.oy))
    x0, y0 = max(0, px), max(0, py)
    x1, y1 = min(cv.width, px + img.width), min(cv.height, py + img.height)
    if x1 > x0 and y1 > y0:
        cv.alpha_composite(img.crop((x0 - px, y0 - py, x1 - px, y1 - py)), (x0, y0))


# ── 태극기 (국기 규격) ───────────────────────────────────────
def flag_art(fw, seed=0):
    """가로 fw 의 태극기. 3:2, 태극 지름 = 세로/2, 괘: 길이 세로/4 · 두께 세로/24 · 간격 세로/48,
    태극에서 세로/8 떨어짐. 건(☰) 왼쪽 위 · 곤(☷) 오른쪽 아래 · 감(☵) 오른쪽 위 · 리(☲) 왼쪽 아래."""
    fh = round(fw * 2 / 3)
    small = fw < 160
    bev = 1 if small else 2
    base = paper(mask(fw, fh, lambda d, s: poly(d, s, deckle([(0, 0), (fw, 0), (fw, fh), (0, fh)], 0.5 if small else 0.9, 9, seed))), WHITE, seed, bev)
    cx, cy, R = fw / 2, fh / 2, fh / 4
    diag = np.array([fw, fh], float) / math.hypot(fw, fh)       # 왼쪽 위 → 오른쪽 아래
    nrm = np.array([fh, -fw], float) / math.hypot(fw, fh)       # 오른쪽 위를 향함
    # 태극: 대각선 위쪽이 빨강, 왼쪽 위 작은 원은 빨강 · 오른쪽 아래 작은 원은 파랑
    ys, xs = np.mgrid[0:fh * SS, 0:fw * SS].astype(np.float32)
    px, py = (xs + 0.5) / SS - cx, (ys + 0.5) / SS - cy
    disc = px * px + py * py < R * R
    ax, ay = -diag * R / 2
    bx, by = diag * R / 2
    in_a = (px - ax) ** 2 + (py - ay) ** 2 < (R / 2) ** 2
    in_b = (px - bx) ** 2 + (py - by) ** 2 < (R / 2) ** 2
    upper = px * nrm[0] + py * nrm[1] > 0
    red = in_a | (upper & ~in_b)
    rgb = np.where(red[..., None], np.array(RED, np.float32), np.array(BLUE, np.float32))
    col = Image.fromarray(rgb.astype(np.uint8), "RGB").resize((fw, fh), Image.LANCZOS)
    dm = Image.fromarray((disc * 255).astype(np.uint8)).resize((fw, fh), Image.LANCZOS)
    disc_img = paper(dm, (255, 255, 255), seed + 1, bev)
    tint = np.asarray(col, np.float32) / 255
    arr = np.asarray(disc_img, np.float32)
    arr[..., :3] *= tint
    disc_img = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGBA")

    u = fh / 48  # 기본 단위
    trig = {(-1, -1): (0, 0, 0), (1, 1): (1, 1, 1), (1, -1): (1, 0, 1), (-1, 1): (0, 1, 0)}  # 1 = 끊긴 막대

    def draw_trig(d, s):
        for (sx_, sy_), bars in trig.items():
            v = np.array([sx_ * fw, sy_ * fh], float) / math.hypot(fw, fh)
            w_ = np.array([-v[1], v[0]])
            for k, broken in enumerate(bars):
                dist = 18 * u + 1 * u + k * 3 * u  # 안쪽 가장자리 3H/8 + 막대 반두께
                c = np.array([cx, cy]) + v * dist
                segs = [(-6 * u, -0.5 * u), (0.5 * u, 6 * u)] if broken else [(-6 * u, 6 * u)]
                for a, b in segs:
                    pts = [c + v * (-u) + w_ * a, c + v * u + w_ * a, c + v * u + w_ * b, c + v * (-u) + w_ * b]
                    poly(d, s, [tuple(p) for p in pts])

    tm = mask(fw, fh, draw_trig)
    trig_img = paper(tm, BLACK, seed + 2, 1 if small else 1)
    cv = base.copy()
    for part, el in ((disc_img, 1 if small else 2), (trig_img, 1 if small else 1.5)):
        sa = Image.new("L", cv.size, 0)
        sa.paste(part.getchannel("A"), (int(round(el * 0.6)), int(round(el))))
        sa = sa.filter(ImageFilter.GaussianBlur(el)).point(lambda v: int(v * 0.35))
        sh = Image.new("RGBA", cv.size, (40, 30, 20, 0))
        sh.putalpha(sa)
        cv.alpha_composite(sh)
        cv.alpha_composite(part)
    return cv


def taeguk_art(d_, seed=0):
    fw = int(d_ * 3)
    f = flag_art(fw, seed)
    fh = f.height
    r = d_ / 2
    return f.crop((int(fw / 2 - r - 2), int(fh / 2 - r - 2), int(fw / 2 + r + 3), int(fh / 2 + r + 3)))


# ── 글자 라벨 ────────────────────────────────────────────────
def _segments(line, hl):
    segs, i = [], 0
    while i < len(line):
        hit = min(((line.find(h, i), h) for h in hl if line.find(h, i) >= 0), default=None)
        if not hit:
            segs.append((line[i:], None))
            break
        j, h = hit
        if j > i:
            segs.append((line[i:j], None))
        segs.append((h, True))
        i = j + len(h)
    return segs


def label(text, size, fg=INK, bg=WHITE, hl=(), hlc=RED, pad=(30, 16), seed=0, elev=6, tilt=0.0, lh=1.2, align="left", amp=1.6):
    f = font(size)
    lines = text.split("\n")
    widths = [f.getlength(l) for l in lines]
    tw, lhp = max(widths), size * lh
    asc, desc = f.getmetrics()
    w = int(tw + pad[0] * 2)
    h = int(lhp * (len(lines) - 1) + asc + desc * 0.4 + pad[1] * 2)
    img = paper(mask(w, h, lambda d, s: poly(d, s, deckle([(0, 0), (w, 0), (w, h), (0, h)], amp, 8, seed))), bg, seed)
    d = ImageDraw.Draw(img)
    for i, line in enumerate(lines):
        x = pad[0] + (0 if align == "left" else (tw - widths[i]) / 2)
        y = pad[1] + i * lhp
        for seg, is_hl in _segments(line, hl):
            d.text((x, y), seg, font=f, fill=hlc if is_hl else fg)
            x += f.getlength(seg)
    if tilt:
        img = img.rotate(tilt, Image.BICUBIC, expand=True)
    return lift(img, elev)


# ── 애니메이션 ───────────────────────────────────────────────
def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def prog(lt, t0, d):
    return clamp((lt - t0) / d)


def out_cubic(p):
    return 1 - (1 - p) ** 3


def out_back(p, k=1.6):
    p -= 1
    return 1 + (k + 1) * p ** 3 + k * p ** 2


def in_out(p):
    return p * p * (3 - 2 * p)


def pop(frame, spr, x, y, lt, t0, dur=0.42, anchor=(0.5, 1.0)):
    """종이가 탁 붙는 등장: 아래서 올라오며 살짝 튕김."""
    if lt < t0:
        return
    p = prog(lt, t0, dur)
    if p >= 1:
        blit(frame, spr, x, y)
        return
    s = 0.9 + 0.1 * out_back(p)
    blit(frame, spr, x, y + (1 - out_cubic(p)) * 46, s=s, anchor=anchor, alpha=clamp((lt - t0) / 0.1))


# ── 타이밍 ──────────────────────────────────────────────────
EPJ = json.loads((EP / "episode.json").read_text())
SC = [s["timing"] for s in EPJ["scenes"]]
TOTAL = SC[-1]["start"] + SC[-1]["duration"]


def wt(i, k):
    return SC[i]["words"][k]["start"]


# 자막: (문구, 시작 단어 번호) — 숫자는 화면에서 아라비아 숫자로
CAPS = [
    [("강변북로에서 구리로 넘어가면,", 0), ("하늘을 덮는 거대한 태극기를 만납니다.", 3)],
    [("시작은 2000년대 초.", 0), ("국경일에도 태극기를 다는 집이", 4), ("점점 사라졌죠.", 8)],
    [("그래서 구리시는 발상을 뒤집습니다.", 0), ("시민이 안 달면,", 4), ("시가 365일 달자.", 7)],
    [("2007년 한강시민공원에 50m,", 0), ("2013년 아차산엔 75m 게양대.", 5)],
    [("아차산 태극기는 가로 18,", 0), ("세로 12m.", 4), ("배구 코트보다 큰 천이에요.", 7)],
    [("태극기의 도시를 선언하고,", 0), ("2010년엔 대통령 표창까지 받았죠.", 3)],
    [("하늘을 덮는 그 태극기,", 0), ("직접 보고 싶다면", 4), ("구리시에 방문해 보세요.", 7)],
]
CAP_TL = sorted((SC[i]["start"] + wt(i, k), txt) for i, pages in enumerate(CAPS) for txt, k in pages)


def wrap(text, f, maxw):
    lines, cur = [], ""
    for wd in text.split(" "):
        t = (cur + " " + wd).strip()
        if cur and f.getlength(t) > maxw:
            lines.append(cur)
            cur = wd
        else:
            cur = t
    return "\n".join(lines + [cur])


_cap_cache = {}


def draw_caption(frame, t):
    cur = None
    for i, (st, txt) in enumerate(CAP_TL):
        if t >= st:
            cur = (i, st, txt)
    if not cur:
        return
    i, st, txt = cur
    if i not in _cap_cache:
        _cap_cache[i] = label(wrap(txt, font(70), 880), 70, pad=(34, 14), seed=900 + i, elev=5, align="center", amp=2.2)
    spr = _cap_cache[i]
    x, y = (W - spr.w) / 2, 1570 - spr.h  # 자막 하단 여백 350px
    p = prog(t, st, 0.16)
    blit(frame, spr, x, y + (1 - out_cubic(p)) * 14, alpha=clamp(p * 1.6))


# ── 공용 소품 ────────────────────────────────────────────────
def full_bg(color, seed):
    return paper(Image.new("L", (W, H), 255), color, seed, bevel=0)


def hill(pts_ctrl, ybase, color, seed, elev=6, x0=-30, x1=W + 30):
    xs = np.arange(x0, x1 + 1, 6)
    cx, cy = zip(*pts_ctrl)
    ys = np.interp(xs, cx, cy)
    ys = np.convolve(np.pad(ys, 6, mode="edge"), np.ones(13) / 13, mode="valid")
    top = list(zip(xs, ys))
    return full_layer([(p[0], p[1]) for p in top] + [(x1, ybase), (x0, ybase)], color, seed, elev, amp=1.0)


def full_layer(pts, color, seed, elev, amp=1.2):
    return piece(W, H, pts, color, seed, elev, amp)


def building(w, h, color, seed, rows_gap=64):
    parts = [(piece(w, h, [(0, 0), (w, 0), (w, h), (0, h)], color, seed, 0, 1.0), 0, 0)]
    r = np.random.default_rng(seed)
    win = tuple(min(255, c + 22) for c in color)
    y = 18
    while y + 26 < h - 10:
        for x in range(12, w - 24, 30):
            if r.random() < 0.85:
                parts.append((piece(16, 22, [(0, 0), (16, 0), (16, 22), (0, 22)], win, seed + x + y, 1, 0.4, 1), x, y))
        y += rows_gap if h > 300 else 34
    return lift(stack(w, h, parts), 4)


def pole(h, w=12):
    parts = [(piece(w, h, [(0, 0), (w, 0), (w, h), (0, h)], (224, 221, 214), 77, 0, 0.3), 0, 12)]
    parts.append((piece(26, 26, circle_pts(13, 13, 12, 20), GOLD, 78, 0, 0.3), (w - 26) / 2, 0))
    return lift(stack(max(w, 26), h + 12, [(s, x + (13 - w / 2 if w < 26 else 0), y) for s, x, y in parts]), 5)


def car():
    body = [(0, 18), (8, 12), (112, 12), (120, 20), (120, 40), (0, 40)]
    cab = [(26, 12), (36, 0), (82, 0), (96, 12)]
    parts = [
        (piece(122, 44, cab, (220, 92, 78), 31, 1, 0.6), 0, 0),
        (piece(122, 44, body, (206, 66, 58), 32, 1, 0.6), 0, 0),
        (piece(20, 12, [(0, 12), (6, 2), (20, 2), (20, 12)], (196, 222, 236), 33, 0, 0.3), 36, 1),
        (piece(20, 12, [(0, 2), (14, 2), (20, 12), (0, 12)], (196, 222, 236), 34, 0, 0.3), 60, 1),
        (piece(22, 22, circle_pts(11, 11, 10, 18), (48, 44, 44), 35, 1, 0.3), 16, 32),
        (piece(22, 22, circle_pts(11, 11, 10, 18), (48, 44, 44), 36, 1, 0.3), 84, 32),
    ]
    return lift(stack(124, 56, parts), 4)


def cloud(w, seed):
    r = np.random.default_rng(seed)
    h = int(w * 0.45)

    def fn(d, s):
        for i in range(5):
            cx = w * (0.18 + 0.16 * i)
            rr = h * (0.3 + 0.2 * r.random()) + (h * 0.12 if i in (1, 2, 3) else 0)
            d.ellipse([(cx - rr) * s, (h - rr - 4) * s - (rr * 0.3 * s), (cx + rr) * s, (h - 4) * s], fill=255)
        d.rectangle([w * 0.12 * s, (h - 26) * s, w * 0.88 * s, (h - 4) * s], fill=255)
    return lift(paper(mask(w, h, fn), (253, 251, 246), seed), 5, 0.22)


def tag(text, size=44, bg=RED, fg=(255, 255, 255), seed=0, tilt=0.0):
    return label(text, size, fg=fg, bg=bg, pad=(22, 8), seed=seed, elev=4, tilt=tilt, amp=1.0)


def measure(frame, x0, y0, x1, y1, p, color=INK, tick=16):
    """치수선 — p(0~1) 만큼 그려진다."""
    if p <= 0:
        return
    d = ImageDraw.Draw(frame)
    xe, ye = x0 + (x1 - x0) * p, y0 + (y1 - y0) * p
    d.line([(x0, y0), (xe, ye)], fill=color + (255,), width=4)
    vert = abs(x1 - x0) < abs(y1 - y0)
    for (x, y), show in (((x0, y0), True), ((x1, y1), p >= 1)):
        if show:
            if vert:
                d.line([(x - tick, y), (x + tick, y)], fill=color + (255,), width=4)
            else:
                d.line([(x, y - tick), (x, y + tick)], fill=color + (255,), width=4)


# ── 장면 ────────────────────────────────────────────────────
class Scene:
    def draw(self, frame, lt):
        raise NotImplementedError


class Riverside(Scene):
    """s01 · s07 — 강변북로·한강시민공원·아차산 디오라마 + 게양대."""

    POLE_X, BASE_Y, TOP_Y = 160, 1470, 660
    FW = 400

    def __init__(self, ending=False):
        self.ending = ending
        self.sky = full_bg((244, 234, 215), 1)
        sun = piece(140, 140, circle_pts(70, 70, 62), (241, 196, 128), 2, 3, 0.8)
        _paste_into(self.sky, sun, 820, 820)
        self.clouds = [(cloud(260, 3), 560, 560, 9), (cloud(200, 4), 80, 900, 6), (cloud(170, 5), 820, 700, 12)]
        L = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        for s in (hill([(-30, 1140), (90, 1040), (220, 975), (330, 1010), (450, 930), (580, 1000), (720, 1050), (880, 1010), (1110, 1080)], 1310, (160, 190, 132), 6),
                  hill([(-30, 1190), (160, 1125), (340, 1160), (540, 1105), (770, 1165), (960, 1120), (1110, 1150)], 1310, (126, 166, 108), 7)):
            _paste_into(L, s, 0, 0)
        r = np.random.default_rng(8)
        pal = [(236, 202, 164), (222, 166, 146), (245, 226, 192), (204, 193, 214), (231, 216, 172), (212, 226, 232)]
        x = 8
        while x < W:
            bw, bh = int(r.integers(62, 104)), int(r.integers(70, 190))
            _paste_into(L, building(bw, bh, pal[int(r.integers(0, len(pal)))], int(x)), x, 1302 - bh)
            x += bw + int(r.integers(6, 16))
        _paste_into(L, full_layer([(-20, 1294), (W + 20, 1290), (W + 20, 1354), (-20, 1356)], (141, 182, 214), 9, 3), 0, 0)
        for i in range(9):
            wx = 40 + i * 120 + (i % 2) * 30
            _paste_into(L, piece(60, 6, [(0, 0), (60, 0), (60, 6), (0, 6)], (186, 213, 233), 40 + i, 0, 0.3, 1), wx, 1312 + (i % 3) * 12)
        _paste_into(L, full_layer([(-20, 1352), (W + 20, 1350), (W + 20, 1404), (-20, 1404)], (152, 147, 140), 10, 3), 0, 0)
        for i in range(0, W, 70):
            _paste_into(L, piece(34, 5, [(0, 0), (34, 0), (34, 5), (0, 5)], (246, 242, 232), 60 + i, 0, 0.3, 1), i + 10, 1375)
        self.mid = L
        G = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        _paste_into(G, full_layer([(-20, 1404), (W + 20, 1398), (W + 20, H + 20), (-20, H + 20)], (171, 200, 136), 11, 10, amp=2.4), 0, 0)
        for i in range(14):
            tx, ty = int(r.integers(20, W - 40)), int(r.integers(1440, 1880))
            _paste_into(G, piece(30, 22, [(0, 22), (6, 4), (12, 16), (16, 0), (21, 15), (27, 6), (30, 22)], (142, 178, 110), 120 + i, 1, 0.5), tx, ty)
        self.ground = G
        self.car = car()
        self.pole = pole(self.BASE_Y - self.TOP_Y)
        self.flag = lift(flag_art(self.FW, 5), 5)
        if ending:
            self.kicker = tag("구리시", seed=21)
            self.head = label("구리시에\n방문해 보세요", 100, hl=("방문해",), seed=22, elev=7)
            self.act = tag("한강시민공원 · 아차산", 48, seed=23)
            self.pin = self._pin()
        else:
            self.kicker = tag("구리시", seed=11)
            self.head = label("하늘을 덮는\n태극기", 100, hl=("태극기",), seed=12, elev=7)

    def _pin(self):
        w, h = 90, 124
        drop = [(45 + 42 * math.cos(math.radians(a)), 44 + 42 * math.sin(math.radians(a))) for a in range(150, 391, 8)] + [(45, 122)]
        parts = [(piece(w, h, drop, RED, 51, 0, 0.8), 0, 0), (piece(40, 40, circle_pts(20, 20, 17), WHITE, 52, 1, 0.4), 25, 24)]
        return lift(stack(w, h, parts), 7)

    def flag_top(self, lt):
        if self.ending:
            return self.TOP_Y + 12
        p = in_out(prog(lt, 0.3, 2.4))
        return 1180 + (self.TOP_Y + 12 - 1180) * p

    def shadow(self, frame, fy):
        """광원(왼쪽 위)에서 땅(한강공원 잔디)으로 떨어지는 게양대·깃발 그림자 — 무늬 없는 단색 실루엣."""
        bx, by = self.POLE_X + 6, self.BASE_Y

        def proj(x, y):
            h = by - y
            return (x + h * 0.30, by + h * 0.28)
        fx0, fx1 = bx + 6, bx + 6 + self.FW
        fb = fy + self.FW * 2 / 3
        poly_flag = [proj(fx0, fy), proj(fx1, fy), proj(fx1, fb), proj(fx0, fb)]
        top = proj(bx, self.TOP_Y)
        m = Image.new("L", (W, H), 0)
        d = ImageDraw.Draw(m)
        d.polygon(poly_flag, fill=255)
        d.line([(bx, by), top], fill=255, width=9)
        m = m.crop((0, 1400, W, H)).filter(ImageFilter.GaussianBlur(3)).point(lambda v: int(v * 0.26))
        sh = Image.new("RGBA", m.size, (46, 60, 30, 0))
        sh.putalpha(m)
        frame.alpha_composite(sh, (0, 1400))

    def draw(self, frame, lt):
        frame.paste(self.sky)
        for spr, x, y, v in self.clouds:
            blit(frame, spr, x + lt * v - 20, y)
        frame.alpha_composite(self.mid)
        cx = -140 + ((lt + (2.2 if self.ending else 0)) * 230) % (W + 280)
        blit(frame, self.car, cx, 1352)
        frame.alpha_composite(self.ground)
        fy = self.flag_top(lt)
        self.shadow(frame, fy)
        blit(frame, self.pole, self.POLE_X, self.TOP_Y - 12)
        sway = 1 - 0.025 * (0.5 + 0.5 * math.sin(lt * 4.2))
        blit(frame, self.flag, self.POLE_X + 12, fy, sx=sway, anchor=(0, 0.5))
        if self.ending:
            pop(frame, self.kicker, 70, 290, lt, 0.1)
            pop(frame, self.head, 70, 360, lt, wt(6, 7) - 0.1)
            if lt >= wt(6, 4):
                p = prog(lt, wt(6, 4), 0.5)
                blit(frame, self.pin, 640, 1318 - (1 - out_back(p, 1.2)) * 380, alpha=clamp(p * 3))
            pop(frame, self.act, W - self.act.w - 60, 1000, lt, wt(6, 8))
        else:
            pop(frame, self.kicker, 70, 290, lt, 0.1)
            pop(frame, self.head, 70, 360, lt, 0.35)


class Homes(Scene):
    """s02 — 집집마다 걸렸던 태극기가 하나씩 사라진다."""

    def __init__(self):
        B = full_bg((240, 230, 212), 101)
        r = np.random.default_rng(102)
        x = -10
        while x < W:
            bw, bh = int(r.integers(80, 150)), int(r.integers(220, 420))
            _paste_into(B, piece(bw, bh, [(0, 0), (bw, 0), (bw, bh), (0, bh)], (226, 214, 194), int(x) + 300, 3, 1.0), x, 1390 - bh)
            x += bw + 6
        _paste_into(B, full_layer([(-20, 1392), (W + 20, 1386), (W + 20, H + 20), (-20, H + 20)], (214, 196, 166), 103, 9, 2.2), 0, 0)
        cols = [(233, 191, 152), (206, 182, 204), (240, 216, 172), (190, 206, 216)]
        spans = [(50, 280, 470), (300, 520, 400), (540, 780, 520), (800, 1030, 440)]
        self.flags = []
        stick = piece(6, 60, [(0, 0), (6, 0), (6, 60), (0, 60)], (210, 205, 196), 150, 2, 0.2, 1)
        mini = lift(flag_art(66, 7), 3)
        self.mini = mini
        for i, (x0, x1, bh) in enumerate(spans):
            top = 1392 - bh
            _paste_into(B, building(x1 - x0, bh, cols[i], 110 + i, 110), x0, top)
            for k, fy in enumerate(range(top + 40, 1330, 110)):
                if (i + k) % 2 == 0:
                    sx = x0 + (x1 - x0) * (0.3 if k % 2 else 0.62)
                    _paste_into(B, stick, sx, fy)
                    self.flags.append((sx + 6, fy + 2))
        self.base = B
        order = [3, 7, 0, 5, 9, 2, 8, 1, 6, 4]
        order = [o for o in order if o < len(self.flags)] + [i for i in range(len(self.flags)) if i not in order]
        t0, t1 = wt(1, 5), wt(1, 9) + 0.2
        self.leave = {fi: t0 + (t1 - t0) * n / max(1, len(order) - 1) for n, fi in enumerate(order)}
        self.kicker = tag("2000년대 초", seed=111)
        self.head = label("태극기 다는 집이\n사라졌다", 92, hl=("사라졌다",), seed=112, elev=7)
        self.sub = tag("국경일에도 빈 게양대", 50, bg=INK, seed=113)

    def draw(self, frame, lt):
        frame.paste(self.base)
        for i, (x, y) in enumerate(self.flags):
            t0 = self.leave[i]
            if lt < t0:
                blit(frame, self.mini, x, y)
            else:
                p = prog(lt, t0, 0.7)
                if p < 1:
                    blit(frame, self.mini, x + out_cubic(p) * 90, y - out_cubic(p) * 260, rot=-40 * p, alpha=1 - p)
        pop(frame, self.kicker, 70, 290, lt, wt(1, 1) - 0.1)
        pop(frame, self.head, 70, 360, lt, 0.25)
        pop(frame, self.sub, 70, 650, lt, wt(1, 9))


class Flip(Scene):
    """s03 — 달력 365장마다 태극기, 카드가 뒤집힌다: 시민이 안 달면 → 시가 365일 달자."""

    def __init__(self):
        B = full_bg((237, 227, 206), 201)
        pw, ph = 520, 560
        self.pw, self.ph = pw, ph
        fl = lift(flag_art(300, 9), 3)
        ring = piece(22, 44, rrect(0, 0, 22, 44, 10), (60, 56, 54), 205, 2, 0.3)

        def page(seed):
            parts = [(piece(pw, ph, [(0, 0), (pw, 0), (pw, ph), (0, ph)], WHITE, seed, 0, 1.0), 0, 0),
                     (piece(pw, 74, [(0, 0), (pw, 0), (pw, 74), (0, 74)], RED, seed + 1, 1, 0.8), 0, 0),
                     (fl, (pw - 300) / 2, 170)]
            for rx in (120, pw - 142):
                parts.append((ring, rx, -18))
            return lift(stack(pw, ph + 10, [(s, x, y + 10) for s, x, y in parts]), 6)
        self.page = page(210)
        for k in (3, 2, 1):
            _paste_into(B, page(220 + k), 280 + k * 8, 820 + k * 8)
        self.base = B
        self.stamp = self._stamp()
        self.kicker = tag("발상의 전환", seed=211)
        self.card_a = label("시민이 안 달면", 92, fg=(120, 112, 104), seed=212, elev=8, pad=(40, 26))
        self.card_b = label("시가 365일 달자", 92, hl=("365일",), seed=213, elev=8, pad=(40, 26))
        t0, t1 = wt(2, 3), wt(2, 7)
        n = 10
        self.tears = [t0 + (t1 - t0) * i / n for i in range(n)]

    def _stamp(self):
        w = h = 300
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        d.ellipse([10, 10, w - 10, h - 10], outline=RED + (230,), width=12)
        d.ellipse([34, 34, w - 34, h - 34], outline=RED + (200,), width=4)
        f = font(96)
        tw = f.getlength("365")
        d.text(((w - tw) / 2, 70), "365", font=f, fill=RED + (235,))
        f2 = font(54)
        d.text(((w - f2.getlength("일")) / 2, 178), "일", font=f2, fill=RED + (235,))
        arr = np.asarray(img, np.float32)
        arr[..., 3] *= np.clip(TEX[:h, :w] * 1.4 - 0.5, 0, 1)  # 도장 잉크 얼룩
        return Sprite(Image.fromarray(arr.astype(np.uint8), "RGBA").rotate(-12, Image.BICUBIC, expand=True))

    def draw(self, frame, lt):
        frame.paste(self.base)
        blit(frame, self.page, 280, 820)
        for t0 in self.tears:
            if lt >= t0:
                p = prog(lt, t0, 0.55)
                if p < 1:
                    blit(frame, self.page, 280 + out_cubic(p) * 420, 820 - out_cubic(p) * 520, rot=-30 * p, alpha=1 - p * p, anchor=(0.5, 0))
        if lt >= wt(2, 8):
            p = prog(lt, wt(2, 8), 0.3)
            blit(frame, self.stamp, 640, 1080, s=1.4 - 0.4 * out_cubic(p), alpha=clamp(p * 2.5), anchor=(0.5, 0.5))
        pop(frame, self.kicker, 70, 290, lt, 0.1)
        flip_t = wt(2, 7) - 0.1
        if lt < flip_t:
            pop(frame, self.card_a, (W - self.card_a.w) / 2, 420, lt, wt(2, 4) - 0.15)
        else:
            p = prog(lt, flip_t, 0.34)
            if p < 0.5:
                blit(frame, self.card_a, (W - self.card_a.w) / 2, 420, sx=max(0.02, 1 - p * 2), sy=1)
            else:
                blit(frame, self.card_b, (W - self.card_b.w) / 2, 420, sx=max(0.02, (p - 0.5) * 2), sy=1)


class TwoPoles(Scene):
    """s04 — 2007 한강시민공원 50m · 2013 아차산 75m (1m = 10px, 같은 축척)."""
    GROUND = 1400
    PX_M = 10

    def __init__(self):
        B = full_bg((238, 230, 213), 301)
        _paste_into(B, hill([(360, 1400), (520, 1150), (700, 1000), (860, 960), (1000, 1030), (1110, 1110)], 1400, (150, 184, 124), 302, 6, x0=360), 0, 0)
        _paste_into(B, hill([(520, 1400), (700, 1190), (900, 1130), (1110, 1200)], 1400, (124, 164, 106), 303, 6, x0=520), 0, 0)
        _paste_into(B, full_layer([(-20, 1336), (470, 1340), (470, 1392), (-20, 1392)], (141, 182, 214), 304, 3), 0, 0)
        _paste_into(B, full_layer([(-20, 1400), (W + 20, 1396), (W + 20, H + 20), (-20, H + 20)], (171, 200, 136), 305, 9, 2.2), 0, 0)
        self.base = B
        self.L = dict(x=220, m=50, flag=150, t=(wt(3, 0) - 0.1, wt(3, 2)), tag_t=wt(3, 3))
        self.R = dict(x=600, m=75, flag=190, t=(wt(3, 7) - 0.2, wt(3, 8)), tag_t=wt(3, 8))
        for P, sd in ((self.L, 311), (self.R, 321)):
            hpx = P["m"] * self.PX_M
            P["pole"] = pole(hpx)
            P["flag"] = lift(flag_art(P["flag"], sd), 4)
            P["tag"] = tag(f"{P['m']}m", 56, seed=sd + 1)
        self.L["yr"] = label("2007\n한강시민공원", 40, seed=331, elev=4, pad=(18, 10))
        self.R["yr"] = label("2013 · 아차산\n25층 높이", 40, seed=332, elev=4, pad=(18, 10))
        self.kicker = tag("게양대 두 개", seed=341)
        self.head = label("50m · 75m", 92, hl=("75m",), seed=342, elev=7)

    def one(self, frame, lt, P):
        t_grow, t_flag = P["t"]
        if lt < t_grow:
            return
        hpx = P["m"] * self.PX_M
        top = self.GROUND - hpx
        g = out_cubic(prog(lt, t_grow, 0.8))
        vis = int((hpx + 12) * g)
        if vis > 2:
            img = P["pole"].img
            cut = img.crop((0, 0, img.width, P["pole"].oy + vis + P["pole"].oy))
            _paste(frame, cut, P["x"] - P["pole"].ox, self.GROUND - vis - P["pole"].oy)
        if g >= 1:
            f = in_out(prog(lt, t_flag, 0.8))
            fh = P["flag"].h
            fy = self.GROUND - fh - 20 + (top + 14 - (self.GROUND - fh - 20)) * f
            blit(frame, P["flag"], P["x"] + 12, fy)
        mx = P["x"] - 48
        measure(frame, mx, self.GROUND, mx, top + 12, out_cubic(prog(lt, P["tag_t"] - 0.35, 0.5)))
        pop(frame, P["tag"], mx - P["tag"].w / 2, (self.GROUND + top) / 2 - P["tag"].h / 2, lt, P["tag_t"], anchor=(0.5, 0.5))
        pop(frame, P["yr"], P["x"] + 22, top + 14 + P["flag"].h + 18, lt, t_flag + 0.3)

    def draw(self, frame, lt):
        frame.paste(self.base)
        pop(frame, self.kicker, 70, 290, lt, 0.1)
        pop(frame, self.head, 70, 360, lt, 0.3)
        self.one(frame, lt, self.L)
        self.one(frame, lt, self.R)


class BigFlag(Scene):
    """s05 — 아차산 태극기 18 × 12m 와 배구 코트 18 × 9m (같은 축척 50px/m)."""
    X, Y, PX_M = 90, 610, 50

    def __init__(self):
        self.base = full_bg((239, 229, 210), 401)
        self.flag = lift(flag_art(18 * self.PX_M, 13), 8)
        self.court = self._court()
        self.kicker = tag("아차산 태극기", seed=411)
        self.head = label("18 × 12m", 110, hl=("18", "12m"), seed=412, elev=7)
        self.t18 = tag("18m", 48, bg=INK, seed=413)
        self.t12 = tag("12m", 48, bg=INK, seed=414)
        self.t3 = tag("+3m", 44, seed=415)
        self.sub = tag("배구 코트보다 큰 천", 54, bg=INK, seed=416)

    def _court(self):
        cw, ch = 18 * self.PX_M, 9 * self.PX_M
        line = (250, 246, 236)
        parts = [(piece(cw, ch, [(0, 0), (cw, 0), (cw, ch), (0, ch)], (226, 134, 76), 420, 0, 1.0), 0, 0)]
        for (x0, y0, x1, y1), sd in (((0, 0, cw, 7), 1), ((0, ch - 7, cw, ch), 2), ((0, 0, 7, ch), 3), ((cw - 7, 0, cw, ch), 4),
                                     ((cw / 2 - 4, 0, cw / 2 + 4, ch), 5), ((cw / 2 - 150 - 3, 0, cw / 2 - 150 + 3, ch), 6),
                                     ((cw / 2 + 150 - 3, 0, cw / 2 + 150 + 3, ch), 7)):
            w_, h_ = int(x1 - x0), int(y1 - y0)
            parts.append((piece(w_, h_, [(0, 0), (w_, 0), (w_, h_), (0, h_)], line, 430 + sd, 1, 0.3, 1), x0, y0))
        cv = stack(cw, ch, parts)
        d = ImageDraw.Draw(cv)
        f = font(46)
        txt = "배구 코트 18 × 9m"
        tw = f.getlength(txt)
        d.rounded_rectangle([(cw - tw) / 2 - 20, ch / 2 - 44, (cw + tw) / 2 + 20, ch / 2 + 30], 10, fill=WHITE + (235,))
        d.text(((cw - tw) / 2, ch / 2 - 38), txt, font=f, fill=INK)
        return lift(cv, 10)

    def draw(self, frame, lt):
        frame.paste(self.base)
        fh = 12 * self.PX_M
        p = out_cubic(prog(lt, 0.05, 0.55))
        if p > 0:
            blit(frame, self.flag, self.X, self.Y, sx=1, sy=max(0.02, p), anchor=(0.5, 0))
        pop(frame, self.kicker, 70, 290, lt, 0.05)
        pop(frame, self.head, 70, 360, lt, wt(4, 2))
        x0, x1, y0, y1 = self.X, self.X + 18 * self.PX_M, self.Y, self.Y + fh
        measure(frame, x0, y0 - 34, x1, y0 - 34, out_cubic(prog(lt, wt(4, 2), 0.6)))
        pop(frame, self.t18, (x0 + x1) / 2 - self.t18.w / 2, y0 - 34 - self.t18.h / 2, lt, wt(4, 3), anchor=(0.5, 0.5))
        mx = x1 + 34
        measure(frame, mx, y0, mx, y1, out_cubic(prog(lt, wt(4, 4), 0.6)))
        if lt >= wt(4, 7):
            q = out_cubic(prog(lt, wt(4, 7), 0.5))
            cy = y1 - 9 * self.PX_M
            blit(frame, self.court, x0, cy + (1 - q) * 900)
            if q >= 1:
                pop(frame, self.t3, mx - self.t3.w / 2, y0 + 75 - self.t3.h / 2, lt, wt(4, 8), anchor=(0.5, 0.5))
        pop(frame, self.t12, mx - self.t12.w / 2, y0 + fh * 0.72 - self.t12.h / 2, lt, wt(4, 5), anchor=(0.5, 0.5))
        pop(frame, self.sub, 70, 1260, lt, wt(4, 7) + 0.1)


class Award(Scene):
    """s06 — 태극기의 도시 선언, 2010 대통령 표창 (상장 글씨는 읽히지 않는 끄적임)."""

    def __init__(self):
        B = full_bg((240, 230, 210), 501)
        self.base = B
        self.cert = self._cert()
        self.rosette = self._rosette()
        self.kicker = tag("태극기의 도시 선언", 52, seed=511)
        self.head = label("2010\n대통령 표창", 100, hl=("대통령 표창",), seed=512, elev=7)

    def _cert(self):
        w, h = 780, 640
        parts = [(piece(w, h, [(0, 0), (w, 0), (w, h), (0, h)], (251, 245, 229), 520, 0, 1.0), 0, 0)]
        for i, ins in enumerate((22, 34)):
            th = 6 if i == 0 else 3
            for (x0, y0, x1, y1) in ((ins, ins, w - ins, ins + th), (ins, h - ins - th, w - ins, h - ins), (ins, ins, ins + th, h - ins), (w - ins - th, ins, w - ins, h - ins)):
                ww, hh = int(x1 - x0), int(y1 - y0)
                parts.append((piece(ww, hh, [(0, 0), (ww, 0), (ww, hh), (0, hh)], GOLD, 530 + i * 10 + x0, 0, 0.2, 1), x0, y0))
        tg = Sprite(taeguk_art(96, 17))
        parts.append((lift(tg.img, 2), (w - tg.img.width) / 2, 70))
        cv = stack(w, h, parts)
        d = ImageDraw.Draw(cv)
        r = np.random.default_rng(533)
        for row, y in enumerate(range(230, 520, 46)):
            x = 90 + (40 if row == 0 else 0)
            xe = w - 90 - (160 if row == 5 else 0)
            pts = []
            while x < xe:
                pts.append((x, y + r.normal() * 3.5))
                x += 9 + r.random() * 5
            d.line(pts, fill=(120, 110, 100, 170), width=3)
        return lift(cv, 10)

    def _rosette(self):
        s_ = 240
        c = s_ / 2
        star = []
        for i in range(48):
            a = 2 * math.pi * i / 48
            rr = 96 if i % 2 == 0 else 84
            star.append((c + rr * math.cos(a), c - 10 + rr * math.sin(a)))
        parts = [
            (piece(s_, s_, [(c - 64, c), (c - 14, c), (c - 34, s_ - 2), (c - 52, s_ - 22), (c - 72, s_ - 4)], RED, 541, 2, 0.6), 0, 0),
            (piece(s_, s_, [(c + 14, c), (c + 64, c), (c + 72, s_ - 4), (c + 52, s_ - 22), (c + 34, s_ - 2)], RED, 542, 2, 0.6), 0, 0),
            (piece(s_, s_, star, GOLD, 543, 3, 0.4), 0, 0),
            (piece(s_, s_, circle_pts(c, c - 10, 62), RED, 544, 2, 0.4), 0, 0),
            (piece(s_, s_, circle_pts(c, c - 10, 44), (236, 200, 110), 545, 2, 0.4), 0, 0),
        ]
        return lift(stack(s_, s_, parts), 8)

    def draw(self, frame, lt):
        frame.paste(self.base)
        pop(frame, self.kicker, 70, 290, lt, 0.1)
        pop(frame, self.cert, 150, 690, lt, 0.3, dur=0.5)
        pop(frame, self.head, 70, 370, lt, wt(5, 3))
        if lt >= wt(5, 5):
            p = prog(lt, wt(5, 5), 0.45)
            blit(frame, self.rosette, 700, 1120, s=0.2 + 0.8 * out_back(p, 2.2), rot=(1 - p) * 40, alpha=clamp(p * 4), anchor=(0.5, 0.5))


SCENES = [Riverside(), Homes(), Flip(), TwoPoles(), BigFlag(), Award(), Riverside(ending=True)]

# ── 전환: 찢긴 종이가 아래에서 위로 넘어간다 ────────────────
TR = 0.42
_j = np.random.default_rng(606)
JAG = np.convolve(_j.normal(0, 9, W + 40), np.ones(5) / 5, "same")[20:W + 20] + np.sin(np.arange(W) / 70) * 12
YS = np.arange(H)[:, None]


def scene_frame(i, lt):
    fr = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    SCENES[i].draw(fr, lt)
    return fr


def frame_at(t):
    i = max(k for k in range(len(SC)) if t >= SC[k]["start"] - 1e-6)
    lt = t - SC[i]["start"]
    fr = scene_frame(i, lt)
    if i > 0 and lt < TR:
        old = scene_frame(i - 1, t - SC[i - 1]["start"])
        p = in_out(lt / TR)
        edge = (H + 60) * (1 - p) - 30 + JAG[None, :]
        a_new, a_old = np.asarray(fr), np.asarray(old)
        out = np.where((YS > edge)[..., None], a_new, a_old).copy()
        fringe = (YS > edge - 8) & (YS <= edge)
        out[fringe] = (247, 242, 232, 255)
        shade = (YS > edge) & (YS < edge + 22)
        out[shade, :3] = (out[shade, :3] * 0.86).astype(np.uint8)
        fr = Image.fromarray(out, "RGBA")
    draw_caption(fr, t)
    return fr


# ── 효과음: 종이 넘기는 소리(합성) ───────────────────────────
def make_sfx(path):
    sr = 44100
    n = int(TOTAL * sr) + sr
    out = np.zeros(n, np.float32)
    r = np.random.default_rng(700)
    for i in range(1, len(SC)):
        st = int(SC[i]["start"] * sr)
        L = int(0.45 * sr)
        x = r.normal(0, 1, L).astype(np.float32)
        x = np.convolve(x, np.ones(3) / 3, "same") - np.convolve(x, np.ones(40) / 40, "same")  # 대역 통과 느낌
        tt = np.linspace(0, 1, L)
        env = np.sin(np.pi * tt) ** 1.5 * (1 + 0.5 * np.sin(tt * 60))
        out[st:st + L] += x * env * 0.08
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
            print("still", ts)
        return
    sfx = OUT / "sfx.wav"
    make_sfx(sfx)
    nfr = int(math.ceil(TOTAL * FPS))
    dst = OUT / "final.mp4"
    cmd = ["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-i", str(EP / "audio/narration.mp3"), "-i", str(sfx),
           "-filter_complex", "[1:a][2:a]amix=inputs=2:normalize=0:duration=first[a]",
           "-map", "0:v", "-map", "[a]", "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "-t", f"{TOTAL:.3f}", str(dst)]
    ff = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for f in range(nfr):
        ff.stdin.write(frame_at(f / FPS).convert("RGB").tobytes())
        if f % 150 == 0:
            print(f"  {f}/{nfr}", flush=True)
    ff.stdin.close()
    ff.wait()
    print("✓", dst.relative_to(ROOT), f"({TOTAL:.1f}s)")


if __name__ == "__main__":
    main()
