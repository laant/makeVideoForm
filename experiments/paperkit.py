"""paperkit — 종이 공작 절차적 렌더 도구 (opus-paper-04 에서 분리). 종이 결·오린 외곽·층 그림자·라벨·애니메이션·태극기."""
import json, math, subprocess, sys, wave
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

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


