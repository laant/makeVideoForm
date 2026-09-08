#!/usr/bin/env python3
"""컷 조립: clips/cutNN.mp4 + audio/cutNN.mp3 → 자막 얹어 트림·연결 → out/final.mp4

사용: FLOW_PROJECT=<프로젝트명> python3 scripts/assemble.py
      (또는 cd projects/<이름> 후 실행 — projlib.find_project 규칙)
전제 (모두 프로젝트 디렉토리 기준):
  - clips/cut01.mp4 ... (Flow/Veo 생성 클립, 9:16)
  - audio/cut01.mp3 ... (dub.py 산출)
  - 자막 폰트: flow-pipeline/fonts/Pretendard-Bold.ttf
동작:
  - 각 컷을 나레이션 길이 + PAD 로 트림 (클립이 짧으면 마지막 프레임 홀드)
  - drawtext 자막 (나레이션 전체, 20자 단위 어절 줄바꿈)
  - concat → 최종 loudnorm
"""
import json, pathlib, subprocess, sys

from projlib import find_project, PIPELINE_ROOT

ROOT = find_project()
VENV_PY = PIPELINE_ROOT / "../OpenMontage/.venv/bin/python"  # PIL 자막 렌더용 (Pillow 보유 venv)
FONT = (PIPELINE_ROOT / "fonts/Pretendard-Bold.ttf").resolve()
PAD = 0.35          # 컷 사이 숨 고르기
# 화면비: cuts.json 최상위 "aspect"가 "16:9"면 가로, 기본 세로
import json as _json
_ASPECT = _json.load(open(ROOT / "cuts.json")).get("aspect", "9:16")
if _ASPECT == "16:9":
    W, H = 1920, 1080
    SUB_BOTTOM = 90     # 가로 자막 하단 여백
    WRAP_LIMIT = 24
else:
    W, H = 1080, 1920
    SUB_BOTTOM = 350    # 세로 자막 레드라인
    WRAP_LIMIT = 14


def dur(p):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                          "-of", "csv=p=0", str(p)], capture_output=True, text=True, check=True)
    return float(out.stdout.strip())


def render_sub_png(text, out_png):
    """homebrew ffmpeg 에 drawtext/libass 가 없어 자막은 PIL 로 PNG 렌더 후 overlay."""
    code = f"""
from PIL import Image, ImageDraw, ImageFont
font = ImageFont.truetype(r'{FONT}', 70)
lines = {wrap(text).splitlines()!r}
W = {W}
pad_y, ls = 10, 20
heights = []
widths = []
img0 = Image.new('RGBA', (10, 10))
d0 = ImageDraw.Draw(img0)
for ln in lines:
    box = d0.textbbox((0, 0), ln, font=font, stroke_width=4)
    widths.append(box[2] - box[0]); heights.append(box[3] - box[1])
H = sum(heights) + ls * (len(lines) - 1) + pad_y * 2
img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
d = ImageDraw.Draw(img)
y = pad_y
for ln, h in zip(lines, heights):
    d.text((W // 2, y), ln, font=font, fill='white', anchor='ma',
           stroke_width=4, stroke_fill=(0, 0, 0, 217))
    y += h + ls
img.save(r'{out_png}')
"""
    subprocess.run([str(VENV_PY), "-c", code], check=True)


def render_stat_png(stat, out_png):
    """수치 슬랩 (계측선 규칙의 숫자 담당 — AI 화면 내 텍스트 금지라 렌더러가 얹는다).
    stat = {"text": "50m", "caption": "한강시민공원 게양대 · 2007", "color": "#E5372F"(선택)}"""
    color = stat.get("color", "#E5372F")
    code = f"""
from PIL import Image, ImageDraw, ImageFont
big = ImageFont.truetype(r'{FONT}', 120)
small = ImageFont.truetype(r'{FONT}', 40)
text, caption = {stat['text']!r}, {stat.get('caption', '')!r}
img0 = Image.new('RGBA', (10, 10)); d0 = ImageDraw.Draw(img0)
tb = d0.textbbox((0, 0), text, font=big)
tw, th = tb[2] - tb[0], tb[3] - tb[1]
pad_x, pad_y, radius = 56, 34, 34
slab_w, slab_h = tw + pad_x * 2, th + pad_y * 2
cb = d0.textbbox((0, 0), caption, font=small, stroke_width=4) if caption else (0, 0, 0, 0)
cw, ch = cb[2] - cb[0], cb[3] - cb[1]
W = max(slab_w, cw) + 20
H = slab_h + (ch + 26 if caption else 0) + 16
img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
d = ImageDraw.Draw(img)
sx = (W - slab_w) // 2
d.rounded_rectangle([sx, 6, sx + slab_w, 6 + slab_h], radius=radius, fill={color!r},
                    outline=(0, 0, 0, 40), width=2)
d.text((W // 2, 6 + pad_y - tb[1]), text, font=big, fill='white', anchor='ma')
if caption:
    d.text((W // 2, 6 + slab_h + 18), caption, font=small, fill='white', anchor='ma',
           stroke_width=3, stroke_fill=(0, 0, 0, 200))
img.save(r'{out_png}')
"""
    subprocess.run([str(VENV_PY), "-c", code], check=True)


def wrap(text, limit=None):
    limit = limit or WRAP_LIMIT
    words, lines, cur = text.split(), [], ""
    for w in words:
        if cur and len(cur) + 1 + len(w) > limit:
            lines.append(cur); cur = w
        else:
            cur = f"{cur} {w}".strip()
    if cur: lines.append(cur)
    return "\n".join(lines)


def split_pages(text, max_chars=None):
    max_chars = max_chars or (WRAP_LIMIT * 2 - 2)
    """긴 나레이션을 순차 노출용 페이지로 분할 (페이지 ≤ 2줄).
    문장(.?!) → 쉼표 → 어절 순으로 쪼갠다."""
    import re
    pages = []
    for sent in re.split(r"(?<=[.?!])\s+", text.strip()):
        if not sent:
            continue
        if len(sent) <= max_chars:
            pages.append(sent)
            continue
        cur = ""
        for piece in re.split(r"(?<=,)\s+", sent):
            if cur and len(cur) + 1 + len(piece) > max_chars:
                pages.append(cur); cur = piece
            else:
                cur = f"{cur} {piece}".strip()
        if cur:
            pages.append(cur)
    final = []
    for p in pages:  # 그래도 긴 페이지는 어절 분할
        if len(p) <= max_chars + 4:
            final.append(p)
            continue
        cur = ""
        for w in p.split():
            if cur and len(cur) + 1 + len(w) > max_chars:
                final.append(cur); cur = w
            else:
                cur = f"{cur} {w}".strip()
        if cur:
            final.append(cur)
    return final


def main():
    (ROOT / "out").mkdir(exist_ok=True)
    (ROOT / "subs").mkdir(exist_ok=True)
    cuts = json.load(open(ROOT / "cuts.json"))["cuts"]
    missing = [c["id"] for c in cuts
               if not (ROOT / f"clips/cut{c['id']:02d}.mp4").exists()
               or not (ROOT / f"audio/cut{c['id']:02d}.mp3").exists()]
    if missing:
        sys.exit(f"누락된 컷 (clips/ 또는 audio/): {missing}")

    seg_paths = []
    for c in cuts:
        cid = f"cut{c['id']:02d}"
        clip, voice = ROOT / f"clips/{cid}.mp4", ROOT / f"audio/{cid}.mp3"
        seg = ROOT / f"out/seg{c['id']:02d}.mp4"
        seg_len = dur(voice) + PAD
        # 자막 페이징: 구절 단위 순차 노출 (페이지 ≤2줄), 글자수 비례 타이밍
        pages = split_pages(c["narration"])
        voice_len = dur(voice)
        weights = [len(p) for p in pages]
        total_w = sum(weights)
        inputs = ["-i", str(clip), "-i", str(voice)]
        vf = (
            f"[0:v]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},"
            f"tpad=stop_mode=clone:stop_duration=8[v0]"
        )
        t_cursor, label = 0.0, "v0"
        for pi, page in enumerate(pages):
            page_png = ROOT / f"subs/{cid}_p{pi}.png"
            render_sub_png(page, page_png)
            inputs += ["-i", str(page_png)]
            idx = len(inputs) // 2 - 1  # 방금 추가한 입력의 인덱스
            t0 = t_cursor
            t1 = seg_len if pi == len(pages) - 1 else t_cursor + voice_len * weights[pi] / total_w
            nxt = f"v{pi + 1}"
            vf += (f";[{label}][{idx}:v]overlay=(W-w)/2:H-{SUB_BOTTOM}-h:"
                   f"enable='between(t,{t0:.2f},{t1:.2f})'[{nxt}]")
            t_cursor, label = t1, nxt
        if c.get("stat"):
            stat_png = ROOT / f"subs/{cid}_stat.png"
            render_stat_png(c["stat"], stat_png)
            inputs += ["-i", str(stat_png)]
            idx = len(inputs) // 2 - 1
            vf += f";[{label}][{idx}:v]overlay=(W-w)/2:190:enable='gte(t,0.4)'[out]"
        else:
            vf += f";[{label}]null[out]"
        subprocess.run([
            "ffmpeg", "-y", "-v", "error", *inputs,
            "-t", f"{seg_len:.3f}",
            "-filter_complex", vf,
            "-map", "[out]", "-map", "1:a",
            "-af", f"apad=pad_dur={PAD}",
            "-r", "30", "-c:v", "libx264", "-preset", "medium", "-crf", "19",
            "-c:a", "aac", "-b:a", "192k", "-pix_fmt", "yuv420p",
            str(seg),
        ], check=True)
        seg_paths.append(seg)
        print(f"seg {cid}  {seg_len:.2f}s")

    lst = ROOT / "out/concat.txt"
    lst.write_text("".join(f"file '{p}'\n" for p in seg_paths))
    subprocess.run([
        "ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(lst),
        "-c:v", "copy", "-af", "loudnorm=I=-15:TP=-1.5:LRA=11",
        "-c:a", "aac", "-b:a", "192k", str(ROOT / "out/final.mp4"),
    ], check=True)
    print(f"final: {ROOT/'out/final.mp4'}  ({dur(ROOT/'out/final.mp4'):.1f}s)")


if __name__ == "__main__":
    main()
