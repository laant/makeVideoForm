#!/usr/bin/env python3
"""스타일 프리셋 5종 비교 — 27번 실손24 앞 3장면 (experiments/style-compare-silson24/plan.md).

같은 나레이션(opus-silson24 audio, 0~29.9초)·같은 화면 문구, 그림체만 프리셋별로.
이미지: gemini-3.1-flash-image 9:16, 장면당 2장(글자 없음). 합성: Remotion ExplainerVertical, playbook = 프리셋.
MOTION-RULES: 하단 자막 없음(captions 비움) — 문구는 컷마다 stat_card, 컷 경계는 단어 시각.
사용: .venv/bin/python projects/style-compare-silson24/produce.py [assets|props|render|all] [style ...]
"""
import json
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent.parent
PROJ = Path(__file__).resolve().parent
SRC = ROOT.parent / "experiments/opus-silson24"
sys.path.insert(0, str(ROOT))

from lib.env_loader import load_env  # noqa: E402

load_env(ROOT)

from tools.graphics.google_imagen import GoogleImagen  # noqa: E402
from tools.video.video_compose import VideoCompose  # noqa: E402

STYLES = ["anime-ghibli", "clean-professional", "flat-motion-graphics", "minimalist-diagram", "premium-minimalist"]
TIM = json.loads((SRC / "audio/timing.json").read_text())["scenes"][:3]
END = TIM[2]["start"] + TIM[2]["speech"] + 0.7

PROHIB = ("No text, no letters, no numbers, no labels, no logos, no brand marks, no app UI, "
          "no watermark, phone screens are blank light cards or abstract icons only.")

# (컷 이름, 그림 내용, 장면 번호, 경계 단어 인덱스: 이 컷이 시작하는 단어, stat_card 문구)
CUTS = [
    ("1a", "a person standing in front of a small neighborhood clinic holding a paper receipt and looking at a smartphone with a blank bright screen", 0, None,
     {"stat": "10월 7일부터", "subtitle": "네이버 지도·네이버페이·토스 앱 안에서"}),
    ("1b", "a paper receipt being drawn into a smartphone screen, a simple check mark glowing on the phone", 0, 8,
     {"stat": "실손 청구 끝까지", "subtitle": "금융위 9월 30일 발표"}),
    ("2a", "a paper receipt travelling a long winding path across a bridge from a smartphone to a distant building with many windows", 1, None,
     {"stat": "지금: 앱 → 실손24 사이트", "subtitle": "한 단계를 더 건너가야 했어요"}),
    ("2b", "a short straight path leading directly from a smartphone to an insurance office building, four empty form fields filling in on their own", 1, 8,
     {"stat": "10월 7일: 앱 안에서 바로", "subtitle": "마이데이터 동의 시 병원·진료일·보험사·계좌번호 입력 생략"}),
    ("3a", "a street of small clinics and pharmacies where only about half of the buildings are lit and connected by glowing lines", 2, None,
     {"stat": "47.7%", "subtitle": "연계 5만340곳 · 9월 28일 기준"}),
    ("3b", "a single clinic and a smartphone joined by a thin connecting line, with an empty speech bubble between them", 2, 13,
     {"stat": "아직 절반이 안 돼요", "subtitle": "실손24 홈페이지 참여병원·약국에서 확인"}),
]


def pb(style):
    return yaml.safe_load((ROOT / f"styles/{style}.yaml").read_text())


def prompt(style, subject):
    p = pb(style)
    ag = p.get("asset_generation", {})
    prefix = " ".join(str(ag.get("image_prompt_prefix", "")).split())
    anchors = " ".join(ag.get("consistency_anchors", []))
    neg = ag.get("image_negative_prompt", "")
    return (f"A vertical 9:16 still frame. {prefix} SUBJECT: {subject}. "
            f"CONSISTENCY: {anchors}. AVOID: {neg}. {PROHIB}")


def dirs(style):
    d = PROJ / style
    for sub in ("assets/images", "assets/audio", "artifacts", "renders"):
        (d / sub).mkdir(parents=True, exist_ok=True)
    return d


def stage_assets(style):
    d = dirs(style)
    imagen = GoogleImagen()
    for name, subject, *_ in CUTS:
        img = d / f"assets/images/{name}.png"
        if img.exists():
            continue
        r = imagen.execute({"prompt": prompt(style, subject), "aspect_ratio": "9:16",
                            "model": "gemini-3.1-flash-image", "output_path": str(img)})
        assert r.success, f"{style} {name}: {r.error}"
        print(f"img {style}/{name} ok", flush=True)
    aud = d / "assets/audio/narration_3.mp3"
    if not aud.exists():
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(SRC / "audio/narration.mp3"), "-t", f"{END:.3f}",
                        "-af", f"afade=t=out:st={END - 0.4:.3f}:d=0.4", str(aud)], check=True)


def stage_props(style):
    d = dirs(style)
    cuts = []
    for j, (name, _s, sc, wk, ov) in enumerate(CUTS):
        t0 = TIM[sc]["start"] + (TIM[sc]["words"][wk]["start"] - 0.1 if wk is not None else 0.0)
        if j == 0:
            t0 = 0.0
        nxt = CUTS[j + 1] if j + 1 < len(CUTS) else None
        if nxt:
            t1 = TIM[nxt[2]]["start"] + (TIM[nxt[2]]["words"][nxt[3]]["start"] - 0.1 if nxt[3] is not None else 0.0)
        else:
            t1 = END
        img = str(d / f"assets/images/{name}.png")
        cut = dict(id=f"cut-{name}", in_seconds=round(t0, 2), out_seconds=round(t1, 2), source=img,
                   animation="ken-burns" if j % 2 == 0 else "zoom-in",
                   type="stat_card", backgroundImage=img, backgroundOverlay=0.55, **ov)
        cuts.append(cut)
    props = dict(version="1.0", render_runtime="remotion", renderer_family="explainer-data-vertical",
                 playbook=style, cuts=cuts, captions=[],
                 audio=dict(narration=dict(src=str(d / "assets/audio/narration_3.mp3"), volume=1.0)))
    (d / "artifacts/edit_decisions.json").write_text(json.dumps(props, ensure_ascii=False, indent=1))
    print(f"props {style}: {len(cuts)} cuts, {END:.1f}s", flush=True)


def stage_render(style):
    d = dirs(style)
    props = json.loads((d / "artifacts/edit_decisions.json").read_text())
    r = VideoCompose().execute({"operation": "remotion_render", "edit_decisions": props, "playbook": style,
                                "output_path": str(d / "renders/final.mp4")})
    assert r.success, f"render {style}: {r.error}"
    print("render ok:", d / "renders/final.mp4", flush=True)


if __name__ == "__main__":
    stage = sys.argv[1] if len(sys.argv) > 1 else "all"
    styles = sys.argv[2:] or STYLES
    for st in styles:
        if stage in ("assets", "all"):
            stage_assets(st)
        if stage in ("props", "all"):
            stage_props(st)
        if stage in ("render", "all"):
            stage_render(st)
