#!/usr/bin/env python3
"""구리시 태극기 (페이퍼 콜라주) — OpenMontage 프로덕션 드라이버.

사용: .venv/bin/python projects/guri-flags-paper/produce.py [assets|props|render|all]
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

OPEN = ("A vertical 9:16 still frame, handcrafted paper collage diorama in a pop-up "
        "book style, every element cut from textured cardstock with visible paper "
        "grain and layered edges.")
WORLD = ("the same handcrafted paper diorama of a small Korean riverside city with a "
         "winding blue paper river, a gray paper highway, dense tiny cardstock "
         "buildings and a layered green paper mountain on one side, standing on a "
         "warm cream tabletop, seen from a low three-quarter angle")
STYLE = ("STYLE: charming miniature paper craft with real cut-paper detail, soft "
         "handmade edges with subtle paper fiber, matte cardstock surfaces, no "
         "plastic gloss, warm soft studio light with gentle contact shadows, no sun "
         "disc.")
COLOR = ("COLOR IS RICH AND CLEAN: warm cream tabletop, soft sky blue river, fresh "
         "green mountain, crisp white flags with deep taegeuk red and blue, fully "
         "saturated, no gray wash and no desaturated grading.")
PROHIB = ("No text, no letters, no numbers, no labels, no logos, no watermark, no "
          "lens flare, no film grain, no vignette, no close-up faces.")
RED_TAIL = ("They are the only glowing red in the frame and carry no numbers and no "
            "text.")


def red(desc: str) -> str:
    return (f"RED: one pure glowing red technical dimension annotation {desc}, "
            f"drafting style, thin extension lines with a straight dimension line "
            f"between them and a small sharp arrowhead at each end, glowing neon red "
            f"clearly brighter than the matte paper red of the flag. {RED_TAIL}")


def P(*parts: str) -> str:
    return " ".join(p for p in parts if p)


ACC = "#D6323C"  # 태극 홍색 계열 강조

SCENES = [
    dict(id="s1", narration="강변북로를 달리다 구리로 넘어가는 순간, 하늘을 덮는 거대한 태극기를 만납니다.",
         imgs=[("s1", P(OPEN, "SUBJECT: " + WORLD + ", a tiny cute paper car driving along the paper highway beside the river, the huge soft shadow of a giant flag sliding across the road and swallowing the little car.", STYLE, COLOR, PROHIB), "zoom-in")]),
    dict(id="s2", narration="한 번쯤 보셨죠? 대체 왜, 하필 여기에 있는 걸까요?",
         imgs=[("s2", P(OPEN, "SUBJECT: " + WORLD + ", the tiny paper car stopped on the highway, an enormous paper Korean flag towering over the whole diorama behind it, gently rippling like a page in the wind.", STYLE, COLOR, PROHIB), "ken-burns")]),
    dict(id="s3", narration="시작은 이천 년대 초. 국경일에도 태극기를 다는 집이, 점점 사라졌습니다.",
         imgs=[("s3a", P(OPEN, "SUBJECT: " + WORLD + ", a cluster of tiny paper apartment towers with rows of empty balconies, small red paper X stickers popped onto the empty flag holders like pop-up book tabs.", STYLE, COLOR, PROHIB), "ken-burns"),
               ("s3b", P(OPEN, "SUBJECT: a tight close-up inside " + WORLD + ", one empty paper balcony with a small red paper X sticker on its flag holder.", STYLE, COLOR, PROHIB), "zoom-in")]),
    dict(id="s4", narration="그래서 구리시는 발상을 뒤집습니다. 시민이 안 달면, 시가 삼백육십오 일 달자.",
         imgs=[("s4a", P(OPEN, "SUBJECT: " + WORLD + ", a riverside park corner unfolding like a pop-up book page, paper lawns and tiny paper trees folding upright, an empty round flagpole pedestal rising from the grass.", STYLE, COLOR, PROHIB), "ken-burns"),
               ("s4b", P(OPEN, "SUBJECT: a tight close-up inside " + WORLD + ", the empty round paper flagpole pedestal waiting in the fresh paper grass.", STYLE, COLOR, PROHIB), "zoom-in")]),
    dict(id="s5", narration="이천칠 년 완공된 한강시민공원에, 오십 미터 게양대를 꽂아버립니다.",
         imgs=[("s5a", P(OPEN, "SUBJECT: " + WORLD + ", a tall paper flagpole standing fully risen from the riverside park pedestal like a pop-up book spine, a crisp paper Korean flag unfurled at its top far above the rooftops.", STYLE, COLOR, red("measures the full height of the flagpole from the ground to the pole top"), PROHIB), "ken-burns"),
               ("s5b", P(OPEN, "SUBJECT: a tight close-up inside " + WORLD + ", the crisp paper Korean flag unfurled at the very top of the tall paper flagpole.", STYLE, COLOR, PROHIB), "zoom-in")],
         overlay=dict(type="stat_card", stat="50m", subtitle="한강시민공원 게양대 · 2007", accentColor=ACC, backgroundOverlay=0.5)),
    dict(id="s6", narration="그런데 멈추지 않았습니다. 고구려 유적이 잠든 아차산에도, 뜻을 담고 싶었죠.",
         imgs=[("s6a", P(OPEN, "SUBJECT: " + WORLD + ", the layered green paper mountain slid open like pop-up book pages revealing clean stacked cardboard cross-section layers inside, tiny paper fortress stones resting on its slope.", STYLE, COLOR, PROHIB), "ken-burns"),
               ("s6b", P(OPEN, "SUBJECT: a tight close-up inside " + WORLD + ", tiny paper fortress stones resting on the green paper mountain slope.", STYLE, COLOR, PROHIB), "zoom-in")]),
    dict(id="s7", narration="이천십삼 년 광복절. 아차산에 아파트 이십오 층 높이, 칠십오 미터 게양대를 하나 더 세웁니다.",
         imgs=[("s7a", P(OPEN, "SUBJECT: " + WORLD + ", an even taller paper flagpole standing on the green mountain slope, clearly taller than the riverside one, a giant crisp paper Korean flag unfurled at its top above the whole diorama.", STYLE, COLOR, red("measures the full height of the mountain flagpole from the slope to the pole top"), PROHIB), "ken-burns"),
               ("s7b", P(OPEN, "SUBJECT: a tight close-up inside " + WORLD + ", the giant paper Korean flag snapping open at the summit of the towering mountain flagpole.", STYLE, COLOR, PROHIB), "zoom-in")],
         overlay=dict(type="stat_card", stat="75m", subtitle="아차산 게양대 · 아파트 25층 높이 · 2013", accentColor=ACC, backgroundOverlay=0.5)),
    dict(id="s8", narration="여기 걸린 태극기는 가로 십팔, 세로 십이 미터. 배구 코트보다 큰 천이 하늘에 떠 있는 셈입니다.",
         imgs=[("s8a", P(OPEN, "SUBJECT: " + WORLD + ", the giant paper Korean flag spread out flat in the sky above the diorama, a small paper volleyball court card sliding underneath it for comparison, visibly smaller than the flag.", STYLE, COLOR, red("measures the width and the height of the flat flag along its two edges"), PROHIB), "ken-burns"),
               ("s8b", P(OPEN, "SUBJECT: a tight close-up inside " + WORLD + ", the overlapping edge where the flat giant flag clearly sticks out past the smaller paper volleyball court card.", STYLE, COLOR, PROHIB), "zoom-in")],
         overlay=dict(type="stat_card", stat="18×12m", subtitle="배구 코트보다 큰 태극기", accentColor=ACC, backgroundOverlay=0.5)),
    dict(id="s9", narration="그렇게 강변에 하나, 산 위에 하나. 두 깃발이 구리 하늘을 나눠 지킵니다.",
         imgs=[("s9a", P(OPEN, "SUBJECT: " + WORLD + ", both giant paper flagpoles standing together in one view, one by the river and one on the mountain, their two flags rippling in the same gentle wind above the tiny city.", STYLE, COLOR, PROHIB), "ken-burns"),
               ("s9b", P(OPEN, "SUBJECT: a tight close-up inside " + WORLD + ", the midpoint of the sky where the two giant paper flags share the frame, rippling in rhythm.", STYLE, COLOR, PROHIB), "zoom-in")]),
    dict(id="s10", narration="시는 아예 태극기의 도시를 선언했고, 이천십 년엔 대통령 표창까지 받았습니다.",
         imgs=[("s10a", P(OPEN, "SUBJECT: " + WORLD + ", a blank paper certificate scroll popped up over the city hall building like a pop-up book card, a round red paper seal pressed onto its corner.", STYLE, COLOR, PROHIB), "ken-burns"),
               ("s10b", P(OPEN, "SUBJECT: a tight close-up inside " + WORLD + ", the freshly stamped round red paper seal on the corner of the blank certificate scroll.", STYLE, COLOR, PROHIB), "zoom-in")],
         overlay=dict(type="stat_card", stat="2010", subtitle="국기 선양 대통령 표창", accentColor=ACC, backgroundOverlay=0.5)),
    dict(id="s11", narration="지금도 시내 곳곳 태극기 거리엔, 일 년 삼백육십오 일 깃발이 펄럭입니다.",
         imgs=[("s11", P(OPEN, "SUBJECT: " + WORLD + ", dozens of tiny paper Korean flags standing upright along the paper streets like a finished domino chain, rippling together in a gentle wave.", STYLE, COLOR, PROHIB), "ken-burns")]),
    dict(id="s12", narration="다음에 강변북로에서 이 깃발을 만나면, 아는 척할 차례입니다. 이런 도시 마케팅 — 멋지다일까요, 과하다일까요?",
         imgs=[("s12", P(OPEN, "SUBJECT: " + WORLD + ", the tiny cute paper car driving along the paper highway once more, passing under the giant flag shadow, framed to mirror the opening shot, warm light settling over the diorama.", STYLE, COLOR, PROHIB), "zoom-in")]),
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
