#!/usr/bin/env python3
"""AI 사고력 시리즈 1편 (회색 찰흙 3D) — OpenMontage 프로덕션 드라이버.

사용: .venv/bin/python projects/ai-thinking-ep1/produce.py [assets|props|render|all]
"""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
PROJ = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from lib.env_loader import load_env  # noqa: E402

load_env(ROOT)

from tools.audio.google_tts import GoogleTTS  # noqa: E402
from tools.graphics.google_imagen import GoogleImagen  # noqa: E402
from tools.video.video_compose import VideoCompose  # noqa: E402

OPEN = ("A vertical 9:16 still frame, minimalist monochrome gray 3D render, matte "
        "clay material, soft diffused studio lighting, gentle ambient occlusion, "
        "isometric camera, clean dark charcoal background with subtle vignette.")
PROHIB = ("No text, no letters, no numbers, no labels, no logos, no watermark, no "
          "lens flare, no film grain, no photorealism.")
SCRIB = ("marked only with faint meaningless ink scribbles and smudges, never any "
         "letters or characters")


def P(*parts: str) -> str:
    return " ".join(p for p in parts if p)


ACC = "#E5372F"

SCENES = [
    dict(id="s1", narration="AI 결과물이 매번 허접한 진짜 이유. 프롬프트 탓이 아닙니다.",
         imgs=[("s1a", P(OPEN, "SUBJECT: a large matte gray clay computer monitor showing a chat panel " + SCRIB + ", a dense scribble block freshly pasted in, tangled gray scribble ribbons spilling out of the screen onto the clay desk.", PROHIB), "ken-burns"),
               ("s1b", P(OPEN, "SUBJECT: the same matte gray clay computer monitor with a bold glowing red cross mark slammed onto the center of the screen, the only red in the frame.", PROHIB), "zoom-in")]),
    dict(id="s2", narration="가장 큰 실수는 이겁니다. 신발 신고, 버스 타고, 할인 확인하고, 문구점 들르고.",
         imgs=[("s2a", P(OPEN, "SUBJECT: an oversized matte gray clay shopping basket on a round pedestal, mismatched clay objects raining down into it — a sneaker, a small city bus, a blank price tag, a pencil, a curling receipt roll " + SCRIB + ".", PROHIB), "ken-burns"),
               ("s2b", P(OPEN, "SUBJECT: the oversized clay shopping basket overflowing, clay objects tumbling over the rim in a chaotic heap on the dark floor.", PROHIB), "zoom-in")]),
    dict(id="s3", narration="큰 흐름과 세부 행동을 한 줄에 섞는 것. AI는 여기서 길을 잃습니다.",
         imgs=[("s3a", P(OPEN, "SUBJECT: a small friendly matte gray clay robot standing among scattered clay objects, a single gray ribbon path winding from the robot and tangling into hopeless loops and knots around the objects.", PROHIB), "ken-burns"),
               ("s3b", P(OPEN, "SUBJECT: a close view of the small clay robot with its head tilted in a dizzy wobble, shoulders slumping, tangled gray ribbon loops filling the background.", PROHIB), "zoom-in")]),
    dict(id="s4", narration="잘 시키는 사람은 수준을 맞춥니다. 출발, 마트, 문구점, 귀가.",
         imgs=[("s4a", P(OPEN, "SUBJECT: four large rounded matte gray clay tiles floating in a clean horizontal row, each embossed with a simple pictogram only — an open door, a shopping cart, a pencil, a house — a soft warm glow pulsing around the row, icons only and absolutely no letters.", PROHIB), "ken-burns"),
               ("s4b", P(OPEN, "SUBJECT: a close view of two of the rounded clay tiles, their embossed pictograms crisp and simple, rim-lit by a soft warm glow.", PROHIB), "zoom-in")]),
    dict(id="s5", narration="같은 크기의 뼈대를 먼저 세우고, 세부 조건은 그 아래에 답니다.",
         imgs=[("s5a", P(OPEN, "SUBJECT: beneath the clean horizontal row of four rounded clay tiles, smaller blank clay tiles unfolding downward, connected by thin clay lines into a tidy mind-map tree, the structure glowing softly warm.", PROHIB), "ken-burns"),
               ("s5b", P(OPEN, "SUBJECT: a close view of one branch of the tidy clay mind-map tree, small blank tiles hanging from thin clay lines under their parent tile.", PROHIB), "zoom-in")]),
    dict(id="s6", narration="이게 코딩 교육이 원래 가르치려던 것입니다. 언어 암기가 아니라, 복잡한 문제를 쪼개고 순서를 설계하는 힘.",
         imgs=[("s6a", P(OPEN, "SUBJECT: the clay mind-map tiles morphing into stacked rectangular clay panels arranged like an editor window, each panel carrying only faint meaningless ink scribble lines at varying indents, never any letters or characters, any panel in the frame shows only abstract scribble marks.", PROHIB), "ken-burns"),
               ("s6b", P(OPEN, "SUBJECT: the rectangular clay panels snapped together into one neat structured column pulsing with a soft warm glow, " + SCRIB + ".", PROHIB), "zoom-in")]),
    dict(id="s7", narration="AI가 실행을 다 해주는 시대. '어떻게'는 대체돼도, '무엇을'의 뼈대를 세우는 사람은 대체되지 않습니다.",
         imgs=[("s7a", P(OPEN, "SUBJECT: a matte gray clay hand pressing a single large rounded button, streams of softly glowing particles cascading upward and assembling into orderly floating structures.", PROHIB), "ken-burns"),
               ("s7b", P(OPEN, "SUBJECT: a calm clay person standing in silhouette watching the glowing structures rise, a gentle warm rim light on their composed face.", PROHIB), "zoom-in")]),
    dict(id="s8", narration="그런데 뼈대를 잘 세우고도, 일 못한다는 소리를 듣는 사람들이 있습니다. 그 소름 돋는 공통점은 다음 편에서.",
         imgs=[("s8", P(OPEN, "SUBJECT: rows of identical matte gray clay office workers frozen at tiny clay desks in a dark hall, a single cold red-tinted spotlight on one worker in the center who is turning toward the camera, the only red in the frame.", PROHIB), "zoom-in")],
         overlay=dict(type="stat_card", stat="다음 편", subtitle="일 못하는 사람들의 공통점", accentColor=ACC, backgroundOverlay=0.5)),
]

IMG_DIR = PROJ / "assets" / "images"
AUD_DIR = PROJ / "assets" / "audio"
REN_DIR = PROJ / "renders"
ART_DIR = PROJ / "artifacts"
for d in (IMG_DIR, AUD_DIR, REN_DIR, ART_DIR):
    d.mkdir(parents=True, exist_ok=True)


def dur(p: Path) -> float:
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                          "-of", "csv=p=0", str(p)], capture_output=True, text=True, check=True)
    return float(out.stdout.strip())


def stage_assets() -> None:
    imagen, tts = GoogleImagen(), GoogleTTS()
    manifest = []
    for sc in SCENES:
        out = AUD_DIR / f"{sc['id']}.mp3"
        if not out.exists():
            r = tts.execute({"text": sc["narration"], "model": "gemini-3.1-flash-tts-preview",
                             "voice": "Aoede", "output_path": str(out)})
            assert r.success, f"TTS {sc['id']}: {r.error}"
            print(f"tts  {sc['id']}  ok", flush=True)
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
    for sc in SCENES:
        manifest.append(dict(id=f"nar-{sc['id']}", type="narration",
                             path=f"assets/audio/{sc['id']}.mp3", source_tool="google_tts",
                             scene_id=sc["id"], model="gemini-3.1-flash-tts-preview",
                             voice="Aoede", text=sc["narration"]))
    (ART_DIR / "asset_manifest.json").write_text(
        json.dumps({"version": "1.0", "assets": manifest}, ensure_ascii=False, indent=1))
    print("asset_manifest 저장", flush=True)


def stage_props() -> None:
    durs = {sc["id"]: dur(AUD_DIR / f"{sc['id']}.mp3") for sc in SCENES}
    concat_list = PROJ / ".narr_concat.txt"
    concat_list.write_text("".join(f"file '{AUD_DIR}/{sc['id']}.mp3'\n" for sc in SCENES))
    full = AUD_DIR / "narration_full.mp3"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0",
                    "-i", str(concat_list), "-c:a", "libmp3lame", "-q:a", "2", str(full)],
                   check=True)
    cuts, captions = [], []
    t = 0.0
    for sc in SCENES:
        d = durs[sc["id"]]
        imgs = sc["imgs"]
        spans = ([(imgs[0], t, t + d)] if len(imgs) == 1 else
                 [(imgs[0], t, t + d * 0.55), (imgs[1], t + d * 0.55, t + d)])
        for i, ((name, _prompt, anim), a, b) in enumerate(spans):
            cut = dict(id=f"cut-{name}", in_seconds=round(a, 2), out_seconds=round(b, 2),
                       source=str(IMG_DIR / f"{name}.png"), animation=anim)
            if "overlay" in sc and i == len(spans) - 1:
                ov = dict(sc["overlay"])
                ov["backgroundImage"] = str(IMG_DIR / f"{name}.png")
                cut.update(ov)
            cuts.append(cut)
        words = sc["narration"].split()
        weights = [len(w) + 1 for w in words]
        total = sum(weights)
        wt = t
        for w, wgt in zip(words, weights):
            wd = d * wgt / total
            captions.append(dict(word=w + " ", startMs=int(wt * 1000),
                                 endMs=int((wt + wd) * 1000),
                                 pageBreakAfter=w.endswith((".", "?", ","))))
            wt += wd
        t += d
    props = dict(version="1.0", render_runtime="remotion",
                 renderer_family="explainer-data-vertical", playbook="flat-motion-graphics",
                 cuts=cuts, captions=captions,
                 audio=dict(narration=dict(src=str(full), volume=1.0)),
                 subtitles=dict(style="word-by-word", language="ko"))
    (ART_DIR / "edit_decisions.json").write_text(json.dumps(props, ensure_ascii=False, indent=1))
    print(f"edit_decisions 저장 — 총 {t:.1f}s, cuts {len(cuts)}, captions {len(captions)}", flush=True)


def stage_render() -> None:
    props = json.loads((ART_DIR / "edit_decisions.json").read_text())
    vc = VideoCompose()
    r = vc.execute({"operation": "remotion_render", "edit_decisions": props,
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
