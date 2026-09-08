#!/usr/bin/env python3
"""04 도쿄 G-Cans 건축쇼츠 — OpenMontage 프로덕션 드라이버.

flow-pipeline 3호와 같은 대본을 정지이미지(Gemini)+Ken Burns(Remotion)로 재현.
사용: python3 projects/tokyo-gcans-archi/produce.py [assets|props|render|all]
"""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent  # OpenMontage/
PROJ = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from lib.env_loader import load_env  # noqa: E402

load_env(ROOT)

from tools.audio.google_tts import GoogleTTS  # noqa: E402
from tools.graphics.google_imagen import GoogleImagen  # noqa: E402
from tools.video.video_compose import VideoCompose  # noqa: E402

# ---------- verbatim 블록 (3호 템플릿과 토씨 동일) ----------
OPEN = ("A vertical 9:16 still frame, semi-stylized 3D architectural visualization "
        "render sitting halfway between clean low-poly and photoreal.")
STYLE = ("STYLE: simplified readable geometry with real modeled detail, smooth shading "
         "with no visible polygon edges, matte materials with brushed steel, no mirror "
         "gloss, soft studio daylight with mild ambient occlusion, no sun disc.")
C_INT = ("COLOR IS RICH AND CLEAN: pale warm concrete, deep teal water, thin cold white "
         "light shafts, fully saturated, no gray wash and no desaturated grading.")
C_DIO = ("COLOR IS RICH AND CLEAN: soft green and warm beige rooftops, deep glossy blue "
         "water, pale neutral gray ground, fully saturated, no gray wash and no "
         "desaturated grading.")
C_SEC = ("COLOR IS RICH AND CLEAN: warm earth-brown soil layers, soft green surface, "
         "deep glossy blue water, pale neutral gray ground, fully saturated, no gray "
         "wash and no desaturated grading.")
PROHIB = ("No text, no letters, no numbers, no labels, no logos, no watermark, no lens "
          "flare, no film grain, no vignette, no close-up faces.")
HALL = ("the same vast underground concrete hall with rows of colossal square concrete "
        "pillars rising from a shallow sheet of still dark water, seen from a low "
        "three-quarter angle")
CITY = ("the same miniature diorama model of a low bowl-shaped river basin city with a "
        "winding river and dense tiny buildings standing on a flat neutral pale gray "
        "studio ground with soft contact shadows, seen from a low three-quarter angle")
SEC = ("the same cutaway cross-section model of the ground sliced open beneath the "
       "miniature river basin city standing on a flat neutral pale gray studio ground "
       "with soft contact shadows, seen from a straight side angle")
RED_TAIL = ("They are the only saturated red in the frame and carry no numbers and no "
            "text.")


def red(desc: str) -> str:
    return (f"RED: one pure red technical dimension annotation {desc}, drafting style, "
            f"thin extension lines with a straight dimension line between them and a "
            f"small sharp arrowhead at each end, glowing. {RED_TAIL}")


def P(*parts: str) -> str:
    return " ".join(p for p in parts if p)


# ---------- 씬 정의 (나레이션 = 3호 확정 대본) ----------
# img: (파일명, 프롬프트, 애니메이션) / overlay: remotion 컷 타입 오버레이 (두 번째 이미지에)
SCENES = [
    dict(id="s1", narration="도쿄 지하 오십 미터엔, 거대한 신전이 숨어 있습니다.",
         imgs=[("s1", P(OPEN, "SUBJECT: " + HALL + ", thin cold shafts of light falling from small ceiling grates far above, faint mist drifting between the pillars, the far end dissolving into darkness, monumental scale like an ancient temple.", STYLE, C_INT, red("measures the full height of one pillar from the water surface to its top"), PROHIB), "zoom-in")]),
    dict(id="s2", narration="신을 모시는 곳이 아닙니다. 도시를 지키는 기계입니다.",
         imgs=[("s2", P(OPEN, "SUBJECT: " + HALL + ", low fog hugging the water surface, mirror-like reflections of the pillars stretching across the wet floor, heavy silence, the ceiling lost in shadow far above.", STYLE, C_INT, PROHIB), "ken-burns")]),
    dict(id="s3", narration="도쿄 옆 사이타마는 그릇처럼 낮아, 비만 오면 강물이 넘쳤습니다.",
         imgs=[("s3a", P(OPEN, "SUBJECT: " + CITY + ", deep glossy blue water swelling out of the winding river and creeping over the banks into the tiny streets, rooftops turning into small islands one by one under a soft rain, wide full view of the bowl.", STYLE, C_DIO, PROHIB), "ken-burns"),
               ("s3b", P(OPEN, "SUBJECT: a tight close-up inside " + CITY + ", one flooded street corner where deep glossy blue water laps at a tiny doorway between crowded miniature houses.", STYLE, C_DIO, PROHIB), "zoom-in")]),
    dict(id="s4", narration="강을 넓히고 싶어도, 사람이 빽빽해 땅이 없었습니다.",
         imgs=[("s4a", P(OPEN, "SUBJECT: " + CITY + ", the narrow river squeezed hard on both banks by tiny houses packed wall to wall, not one empty lot anywhere, tiny rooftops crowding right up to the water's edge along its whole length, low wide view along the river.", STYLE, C_DIO, PROHIB), "ken-burns"),
               ("s4b", P(OPEN, "SUBJECT: a tight close-up inside " + CITY + ", the tightest pinch point where two rows of tiny houses nearly touch across the narrow water.", STYLE, C_DIO, PROHIB), "zoom-in")]),
    dict(id="s5", narration="그래서 물길을, 땅속 오십 미터 아래로 내렸습니다.",
         imgs=[("s5a", P(OPEN, "SUBJECT: " + SEC + ", a vertical cylindrical shaft boring straight down from the surface through clean layered soil, one huge horizontal tunnel opening at the very bottom, the tiny city sitting untouched on the surface above.", STYLE, C_SEC, red("measures the vertical depth from the surface level down to the tunnel"), PROHIB), "ken-burns"),
               ("s5b", P(OPEN, "SUBJECT: a tight close-up inside " + SEC + ", the round tunnel mouth opening at the bottom of the vertical shaft, clean sliced soil layers around it.", STYLE, C_SEC, PROHIB), "zoom-in")],
         overlay=dict(type="stat_card", stat="지하 50m", subtitle="도시 아래로 내린 물길", accentColor="#FF3B30", backgroundOverlay=0.55)),
    dict(id="s6", narration="지름 십 미터 터널이 육 점 사 킬로미터. 넘친 강 다섯 개를 지하로 삼킵니다.",
         imgs=[("s6a", P(OPEN, "SUBJECT: " + SEC + ", five small winding rivers on the surface each spilling into its own vertical shaft, all five shafts dropping down and merging into one huge horizontal tunnel running the full width of the model far below.", STYLE, C_SEC, red("measures the full horizontal length of the great tunnel from end to end"), PROHIB), "ken-burns"),
               ("s6b", P(OPEN, "SUBJECT: a tight close-up inside " + SEC + ", the junction where the last vertical shaft meets the huge horizontal tunnel, threads of deep glossy blue water sliding down into it.", STYLE, C_SEC, PROHIB), "zoom-in")],
         overlay=dict(type="stat_card", stat="6.4km", subtitle="지름 10m 터널 · 강 5개를 삼킨다", accentColor="#FF3B30", backgroundOverlay=0.55)),
    dict(id="s7", narration="하지만 폭포처럼 떨어진 물은, 그대로 두면 시설을 부숴버립니다.",
         imgs=[("s7a", P(OPEN, "SUBJECT: " + SEC + ", a massive column of deep glossy blue water plunging down one vertical shaft like a waterfall and slamming into the floor at the bottom, a violent white splash bursting outward.", STYLE, C_SEC, PROHIB), "ken-burns"),
               ("s7b", P(OPEN, "SUBJECT: a tight close-up inside " + SEC + ", the churning impact point at the shaft floor, a violent white splash and a visible shockwave ring bursting outward from where the water column slams down.", STYLE, C_SEC, PROHIB), "zoom-in")]),
    dict(id="s8", narration="그래서 만든 게 이 신전입니다. 오백 톤 기둥 오십구 개가, 물의 기세를 죽입니다.",
         imgs=[("s8a", P(OPEN, "SUBJECT: " + HALL + ", a surge of deep teal water rushing in from one side, crashing against pillar after pillar, breaking into softer swells as it spreads between the rows.", STYLE, C_INT, PROHIB), "ken-burns"),
               ("s8b", P(OPEN, "SUBJECT: a tight close-up inside " + HALL + ", one colossal pillar with the last slow swirl of water calming around its base.", STYLE, C_INT, PROHIB), "zoom-in")],
         overlay=dict(type="stat_card", stat="기둥 59개", subtitle="하나에 500톤 · 물의 기세를 죽인다", accentColor="#FF3B30", backgroundOverlay=0.55)),
    dict(id="s9", narration="마지막은 비행기입니다. 보잉 칠삼칠 엔진급 터빈 네 대가, 매초 이백 톤을 강으로 밀어냅니다.",
         imgs=[("s9a", P(OPEN, "SUBJECT: a colossal underground pump hall in the same facility, four giant jet-engine-like turbine pumps standing in a row with massive steel intake ducts, water mist swirling off the housings, glints of light on curved metal.", STYLE, C_INT, PROHIB), "ken-burns"),
               ("s9b", P(OPEN, "SUBJECT: a tight close-up of one giant jet-engine-like turbine pump in the same facility, wide fan blades inside the huge circular steel intake.", STYLE, C_INT, red("measures the diameter of the circular turbine intake across its widest span"), PROHIB), "zoom-in")],
         overlay=dict(type="kpi_grid", title="배수 능력", chartData=[dict(label="터빈", value=4, suffix="대"), dict(label="매초", value=200, suffix="톤")], columns=2, backgroundOverlay=0.55)),
    dict(id="s10", narration="완공까지 십삼 년, 이 조 원. 침수 피해는 구십 퍼센트 넘게 줄었습니다.",
         imgs=[("s10a", P(OPEN, "SUBJECT: " + CITY + ", heavy rain falling over the whole basin yet every tiny street staying bright and dry, deep glossy blue water sliding off into small round shaft mouths beside the river and vanishing underground.", STYLE, C_DIO, PROHIB), "ken-burns"),
               ("s10b", P(OPEN, "SUBJECT: a tight close-up inside " + CITY + ", one small round shaft mouth beside the river swallowing the last swirl of deep glossy blue water while rain falls.", STYLE, C_DIO, PROHIB), "zoom-in")],
         overlay=dict(type="kpi_grid", title="13년 · 2조 원의 결과", chartData=[dict(label="공사 기간", value=13, suffix="년"), dict(label="침수 피해 감소", value=90, suffix="%")], columns=2, backgroundOverlay=0.55)),
    dict(id="s11", narration="그리고 맑은 날엔, 그저 축구장 밑 조용한 어둠일 뿐입니다.",
         imgs=[("s11", P(OPEN, "SUBJECT: a cutaway cross-section model of the same facility on a flat neutral pale gray studio ground with soft contact shadows, seen from a straight side angle, a sunny green soccer field with tiny goalposts on the thin surface layer, and directly beneath it the vast dark pillared hall sitting silent and empty in the earth, separated by a clean sliced band of soil.", STYLE, C_DIO, PROHIB), "ken-burns")]),
    dict(id="s12", narration="서울 지하에도 이런 신전, 필요할까요 아닐까요? 진짜 반전은 다음 영상에 있습니다.",
         imgs=[("s12", P(OPEN, "SUBJECT: " + HALL + ", perfectly still and empty again, thin cold shafts of light from the ceiling grates slowly dimming, the far rows of pillars sinking into deeper darkness, framed to mirror the opening shot.", STYLE, C_INT, PROHIB), "zoom-in")]),
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
            print(f"tts  {sc['id']}  ok")
        for name, prompt, _anim in sc["imgs"]:
            img = IMG_DIR / f"{name}.png"
            if not img.exists():
                r = imagen.execute({"prompt": prompt, "aspect_ratio": "9:16",
                                    "model": "gemini-3.1-flash-image", "output_path": str(img)})
                assert r.success, f"IMG {name}: {r.error}"
                print(f"img  {name}  ok")
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
    print("asset_manifest 저장")


def stage_props() -> None:
    # 나레이션 합본 + 씬 타임라인
    durs = {sc["id"]: dur(AUD_DIR / f"{sc['id']}.mp3") for sc in SCENES}
    concat_list = PROJ / ".narr_concat.txt"
    concat_list.write_text("".join(f"file '{AUD_DIR}/{sc['id']}.mp3'\n" for sc in SCENES))
    full = AUD_DIR / "narration_full.mp3"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0",
                    "-i", str(concat_list), "-c:a", "libmp3lame", "-q:a", "2", str(full)],
                   check=True)
    cuts, captions = [], []
    t = 0.0
    PAD = 0.0  # concat이라 갭 없음
    for sc in SCENES:
        d = durs[sc["id"]]
        imgs = sc["imgs"]
        # 이미지 2장이면 55/45 분할, 오버레이는 두 번째 이미지에
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
        # 워드 캡션: 글자수 비례 배분
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
        t += d + PAD
    props = dict(version="1.0", render_runtime="remotion",
                 renderer_family="explainer-data-vertical", playbook="flat-motion-graphics",
                 cuts=cuts, captions=captions,
                 audio=dict(narration=dict(src=str(full), volume=1.0)),
                 subtitles=dict(style="word-by-word", language="ko"))
    (ART_DIR / "edit_decisions.json").write_text(json.dumps(props, ensure_ascii=False, indent=1))
    print(f"edit_decisions 저장 — 총 {t:.1f}s, cuts {len(cuts)}, captions {len(captions)}")


def stage_render() -> None:
    props = json.loads((ART_DIR / "edit_decisions.json").read_text())
    vc = VideoCompose()
    r = vc.execute({"operation": "remotion_render", "edit_decisions": props,
                    "output_path": str(REN_DIR / "final.mp4")})
    assert r.success, f"render: {r.error}"
    print("render ok:", REN_DIR / "final.mp4")


if __name__ == "__main__":
    stage = sys.argv[1] if len(sys.argv) > 1 else "all"
    if stage in ("assets", "all"):
        stage_assets()
    if stage in ("props", "all"):
        stage_props()
    if stage in ("render", "all"):
        stage_render()
