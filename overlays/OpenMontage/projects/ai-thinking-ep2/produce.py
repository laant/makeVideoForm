#!/usr/bin/env python3
"""AI 사고력 시리즈 2편 (숨은 목적) — OpenMontage 프로덕션 드라이버.

사용: .venv/bin/python projects/ai-thinking-ep2/produce.py [assets|props|render|all]
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


def P(*parts: str) -> str:
    return " ".join(p for p in parts if p)


ACC = "#E5372F"

SCENES = [
    dict(id='s1', narration='일 못한다는 소리를 듣는 사람들. 놀랍게도, 다들 성실합니다.',
         imgs=[
               ('s1a', P(OPEN, 'SUBJECT: rows of matte gray clay office workers typing diligently at tiny desks under soft even light, all leaning into their work.', PROHIB), 'ken-burns'),
               ('s1b', P(OPEN, 'SUBJECT: a close view of diligent clay hands stamping and stacking papers marked only with faint meaningless ink scribbles and smudges, never any letters or characters.', PROHIB), 'zoom-in'),
         ]),
    dict(id='s2', narration='큰 전시회 준비. 간판이 잘못되면 다시 만드는 데 오래 걸리니, 담당 피엠이 부탁합니다. 간판부터 확인해 주세요.',
         imgs=[
               ('s2a', P(OPEN, 'SUBJECT: a clay exhibition hall diorama with booths under construction, a blank signboard hanging above each booth, a clay project manager figure holding a clipboard with scribble marks.', PROHIB), 'ken-burns'),
               ('s2b', P(OPEN, 'SUBJECT: a close view of one large blank clay signboard being hoisted by tiny ropes above an unfinished booth.', PROHIB), 'zoom-in'),
         ]),
    dict(id='s3', narration='돌아온 대답. 어차피 나중에 다 점검할 거니까, 완성되면 한꺼번에 볼게요.',
         imgs=[
               ('s3', P(OPEN, 'SUBJECT: a clay quality-inspector figure standing with crossed arms beside a tall stack of checklist boards with scribble marks, unfinished booths lined up behind.', PROHIB), 'ken-burns'),
         ]),
    dict(id='s4', narration='언뜻 효율적이죠. 같은 부스를 두 번 안 다녀도 되니까. 하지만 이 대답은 목적을 놓쳤습니다.',
         imgs=[
               ('s4a', P(OPEN, 'SUBJECT: a single neat gray ribbon path looping once through all the clay booths in a perfect efficient route.', PROHIB), 'ken-burns'),
               ('s4b', P(OPEN, 'SUBJECT: the same exhibition diorama fallen into dimmer light, the neat ribbon path still in place but the hall feeling heavy and shadowed.', PROHIB), 'zoom-in'),
         ]),
    dict(id='s5', narration='간판을 먼저 보라는 건 걸음을 아끼려는 게 아니라, 다시 만들 시간을 벌려는 것. 나의 효율과 전체의 효율은 다릅니다.',
         imgs=[
               ('s5a', P(OPEN, 'SUBJECT: one signboard among the booths glowing with an ominous red tint while a clay desk calendar beside the hall sheds blank pages into the air.', PROHIB), 'ken-burns'),
               ('s5b', P(OPEN, 'SUBJECT: a close view of a cracked clay signboard edged with a harsh red glow, the only red in the frame.', PROHIB), 'zoom-in'),
         ]),
    dict(id='s6', narration='AI도 똑같습니다. 시킨 문장은 충실히 처리하지만, 말하지 않은 진짜 목적까지는 모릅니다.',
         imgs=[
               ('s6a', P(OPEN, 'SUBJECT: a friendly clay robot working diligently at a workbench while reading an instruction sheet with scribble marks, a completely empty round thought bubble floating above its head.', PROHIB), 'ken-burns'),
               ('s6b', P(OPEN, "SUBJECT: a close view of the empty round clay thought bubble, smooth and blank, floating above the robot's head.", PROHIB), 'zoom-in'),
         ]),
    dict(id='s7', narration="그래서 잘 시키는 사람은 '무엇을'만 말하지 않습니다. 왜 먼저인지, 무엇이 성공인지, 기준까지 함께 줍니다.",
         imgs=[
               ('s7a', P(OPEN, 'SUBJECT: an instruction sheet on a clay table with three rounded clay cards floating above it in a warm glow, each embossed with a simple pictogram only — a flag, a target, a check mark.', PROHIB), 'ken-burns'),
               ('s7b', P(OPEN, 'SUBJECT: a close view of the three warmly glowing rounded cards with their embossed flag, target and check mark pictograms.', PROHIB), 'zoom-in'),
         ]),
    dict(id='s8', narration='그런데 이 사고력을 가르친다는 코딩 학원. 계속 보내야 할지는, 다음 편에서 끝내드립니다.',
         imgs=[
               ('s8', P(OPEN, 'SUBJECT: a small clay child silhouette standing before a huge pile of plain building blocks in a dark room under a single soft spotlight.', PROHIB), 'zoom-in'),
         ],
         overlay={'type': 'stat_card', 'stat': '다음 편', 'subtitle': '코딩 학원, 끊어도 될까', 'accentColor': '#E5372F', 'backgroundOverlay': 0.5}),
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
