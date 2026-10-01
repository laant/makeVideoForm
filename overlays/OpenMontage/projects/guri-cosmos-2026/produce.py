#!/usr/bin/env python3
"""2026 구리 코스모스 축제 — OpenMontage 프로덕션 드라이버 (21번).

autoShorts 판(`autoShorts/episodes/guri-cosmos-2026/`)과 같은 대본·같은 나레이션(음성 파일·단어 시각 재사용).
이미지는 페이퍼 콜라주 디오라마(04번 guri-flags-paper 계열 문법)로 새로 생성, stat_card 로 사실 카드.
사용: .venv/bin/python projects/guri-cosmos-2026/produce.py [assets|props|render|all]
"""
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
PROJ = Path(__file__).resolve().parent
EP = ROOT.parent / "autoShorts/episodes/guri-cosmos-2026"
sys.path.insert(0, str(ROOT))

from lib.env_loader import load_env  # noqa: E402

load_env(ROOT)

from tools.graphics.google_imagen import GoogleImagen  # noqa: E402
from tools.video.video_compose import VideoCompose  # noqa: E402

OPEN = ("A vertical 9:16 still frame, handcrafted paper collage diorama in a pop-up book style, "
        "every element cut from textured cardstock with visible paper grain and layered edges.")
WORLD = ("the same handcrafted paper diorama of a wide riverside park in autumn: a soft blue paper river, "
         "a long field of paper cosmos flowers in pink, magenta and white on thin green stems, "
         "a low paper city skyline and a layered paper mountain far behind, on a warm cream tabletop, "
         "seen from a low three-quarter angle")
STYLE = ("STYLE: charming miniature paper craft with real cut-paper detail, soft handmade edges with subtle "
         "paper fiber, matte cardstock, warm soft light with gentle contact shadows, no sun disc.")
COLOR = ("COLOR: rich clean pinks and magentas of cosmos petals, fresh green stems, soft sky blue river, "
         "warm cream, fully saturated, no gray wash.")
PROHIB = "No text, no letters, no numbers, no labels, no logos, no watermark, no lens flare, no close-up faces."


def P(*parts: str) -> str:
    return " ".join(p for p in parts if p)


PINK = "#E85C8F"
SCENES = [
    dict(id="s01", imgs=[
        ("s1a", P(OPEN, "SUBJECT: " + WORLD + ", the cosmos field stretching wide across the whole frame.", STYLE, COLOR, PROHIB), "zoom-in")],
        overlay={"type": "stat_card", "stat": "축구장 11개 꽃밭", "subtitle": "딱 사흘만 · 꽃단지 79,620㎡",
                 "accentColor": PINK, "backgroundOverlay": 0.35}),
    dict(id="s02", imgs=[
        ("s2a", P(OPEN, "SUBJECT: " + WORLD + ", a small blank paper calendar card standing upright among the cosmos near the river bank.", STYLE, COLOR, PROHIB), "ken-burns")],
        overlay={"type": "stat_card", "stat": "10.9 금 ~ 10.11 일", "subtitle": "구리한강시민공원 · 꽃멍하러 구리로 ON",
                 "accentColor": PINK, "backgroundOverlay": 0.35}),
    dict(id="s03", imgs=[
        ("s3a", P(OPEN, "SUBJECT: " + WORLD + ", the cosmos field visibly spreading far beyond a small low paper fence that marks a smaller old patch.", STYLE, COLOR, PROHIB), "zoom-out")],
        overlay={"type": "stat_card", "stat": "+11,940㎡", "subtitle": "작년보다 넓어진 꽃단지 · 총 79,620㎡",
                 "accentColor": PINK, "backgroundOverlay": 0.4}),
    dict(id="s04", imgs=[
        ("s4a", P(OPEN, "SUBJECT: " + WORLD + ", at night, a small glowing paper outdoor stage beside the cosmos field with tiny paper lanterns.", STYLE, "COLOR: deep navy night paper sky, warm stage glow, pink cosmos catching the light.", PROHIB), "ken-burns"),
        ("s4b", P(OPEN, "SUBJECT: " + WORLD + ", at night, small cut-paper fireworks bursting in the navy paper sky above the cosmos field and the river.", STYLE, "COLOR: deep navy night paper sky, gold and pink paper fireworks.", PROHIB), "zoom-in")],
        overlay={"type": "stat_card", "stat": "매일 밤 7시 무대", "subtitle": "토 양파·김다현 외 · 일 홍이삭·박혜신 외 + 불꽃쇼",
                 "accentColor": PINK, "backgroundOverlay": 0.4}),
    dict(id="s05", imgs=[
        ("s5a", P(OPEN, "SUBJECT: " + WORLD + ", in warm afternoon light, a small paper outdoor stage with a single standing paper microphone in front of the cosmos.", STYLE, COLOR, PROHIB), "zoom-in")],
        overlay={"type": "stat_card", "stat": "전국 코스모스 가요제", "subtitle": "10월 10일(토) 오후 4시 · 메인무대",
                 "accentColor": PINK, "backgroundOverlay": 0.4}),
    dict(id="s06", imgs=[
        ("s6a", P(OPEN, "SUBJECT: " + WORLD + ", a small cute paper village bus driving along a paper road toward the cosmos field.", STYLE, COLOR, PROHIB), "ken-burns"),
        ("s6b", P(OPEN, "SUBJECT: " + WORLD + ", a tiny paper shuttle tram with open cars rolling along a path through the cosmos field.", STYLE, COLOR, PROHIB), "zoom-in")],
        overlay={"type": "stat_card", "stat": "대중교통으로", "subtitle": "8호선 장자호수공원역 → 마을버스 · 공원 안 무료 셔틀",
                 "accentColor": PINK, "backgroundOverlay": 0.4}),
    dict(id="s07", imgs=[
        ("s7a", P(OPEN, "SUBJECT: " + WORLD + ", at golden hour, a winding paper path through the cosmos field leading toward the river.", STYLE, "COLOR: warm golden-hour light on pink cosmos, soft peach sky.", PROHIB), "zoom-out")],
        overlay={"type": "stat_card", "stat": "꽃멍하러 구리로 ON", "subtitle": "10.9 ~ 10.11 · 구리한강시민공원에 방문해 보세요",
                 "accentColor": PINK, "backgroundOverlay": 0.35}),
]

IMG_DIR = PROJ / "assets" / "images"
AUD_DIR = PROJ / "assets" / "audio"
REN_DIR = PROJ / "renders"
ART_DIR = PROJ / "artifacts"
for d in (IMG_DIR, AUD_DIR, REN_DIR, ART_DIR):
    d.mkdir(parents=True, exist_ok=True)

EPJ = json.loads((EP / "episode.json").read_text())
TIM = {s["id"]: s["timing"] for s in EPJ["scenes"]}


def stage_assets() -> None:
    imagen = GoogleImagen()
    manifest = []
    for sc in SCENES:
        for name, prompt, _anim in sc["imgs"]:
            img = IMG_DIR / f"{name}.png"
            if not img.exists():
                r = imagen.execute({"prompt": prompt, "aspect_ratio": "9:16",
                                    "model": "gemini-3.1-flash-image", "output_path": str(img)})
                assert r.success, f"IMG {name}: {r.error}"
                print(f"img  {name}  ok", flush=True)
            manifest.append(dict(id=f"img-{name}", type="image", path=f"assets/images/{name}.png",
                                 source_tool="google_imagen", scene_id=sc["id"],
                                 model="gemini-3.1-flash-image", prompt=prompt))
    shutil.copy(EP / "audio/narration.mp3", AUD_DIR / "narration_full.mp3")  # autoShorts 판 나레이션 그대로
    manifest.append(dict(id="nar-full", type="narration", path="assets/audio/narration_full.mp3",
                         source_tool="autoShorts tts (Gemini Aoede)", text=" ".join(s["narration"] for s in EPJ["scenes"])))
    (ART_DIR / "asset_manifest.json").write_text(
        json.dumps({"version": "1.0", "assets": manifest}, ensure_ascii=False, indent=1))
    print("asset_manifest 저장", flush=True)


def stage_props() -> None:
    cuts, captions = [], []
    for sc in SCENES:
        tm = TIM[sc["id"]]
        t, d = tm["start"], tm["duration"]
        imgs = sc["imgs"]
        spans = ([(imgs[0], t, t + d)] if len(imgs) == 1 else
                 [(imgs[0], t, t + d * 0.5), (imgs[1], t + d * 0.5, t + d)])
        for i, ((name, _p, anim), a, b) in enumerate(spans):
            cut = dict(id=f"cut-{name}", in_seconds=round(a, 2), out_seconds=round(b, 2),
                       source=str(IMG_DIR / f"{name}.png"), animation=anim)
            if i == len(spans) - 1:
                ov = dict(sc["overlay"])
                ov["backgroundImage"] = str(IMG_DIR / f"{name}.png")
                cut.update(ov)
            cuts.append(cut)
        for w in tm["words"]:  # autoShorts 단어 시각 그대로
            captions.append(dict(word=w["text"] + " ", startMs=int((t + w["start"]) * 1000),
                                 endMs=int((t + w["end"]) * 1000), pageBreakAfter=w["text"].endswith((".", "?", ","))))
    total = TIM[SCENES[-1]["id"]]["start"] + TIM[SCENES[-1]["id"]]["duration"]
    props = dict(version="1.0", render_runtime="remotion",
                 renderer_family="explainer-data-vertical", playbook="flat-motion-graphics",
                 cuts=cuts, captions=captions,
                 audio=dict(narration=dict(src=str(AUD_DIR / "narration_full.mp3"), volume=1.0)),
                 subtitles=dict(style="word-by-word", language="ko"))
    (ART_DIR / "edit_decisions.json").write_text(json.dumps(props, ensure_ascii=False, indent=1))
    print(f"edit_decisions 저장 — 총 {total:.1f}s, cuts {len(cuts)}, captions {len(captions)}", flush=True)


def stage_render() -> None:
    props = json.loads((ART_DIR / "edit_decisions.json").read_text())
    r = VideoCompose().execute({"operation": "remotion_render", "edit_decisions": props,
                                "output_path": str(REN_DIR / "final.mp4")})
    assert r.success, f"render: {r.error}"
    print("render ok:", REN_DIR / "final.mp4", flush=True)


if __name__ == "__main__":
    stage = sys.argv[1] if len(sys.argv) > 1 else "all"
    if stage in ("assets", "all"):
        stage_assets()
    if stage in ("props", "all"):
        stage_props()
    if stage in ("render", "all"):
        stage_render()
