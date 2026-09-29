#!/usr/bin/env python3
"""가변 조리개 (테크) — OpenMontage 프로덕션 드라이버.

13번 프로젝트의 autoShorts 판(`autoShorts/episodes/aperture-explained/`)과 같은 대본으로
만드는 OpenMontage 병렬판. 같은 대본을 여러 모듈로 제작해 비교하는 것이 이 저장소의 기본 실험 방식.

사용: .venv/bin/python projects/aperture-explained/produce.py [assets|props|render|all]
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

OPEN = ("A vertical 9:16 still frame, minimalist monochrome charcoal-gray 3D render, matte "
        "clay material, soft diffused studio lighting, gentle ambient occlusion, "
        "clean near-black background with subtle vignette.")
ACC = ("LIGHT: one faint cool blue rim light touches a single edge of the subject. "
       "No other colour anywhere in the frame.")
PROHIB = ("No text, no letters, no numbers, no labels, no logos, no brand marks, no watermark, "
          "no lens flare, no film grain, no photorealism, no people, no faces.")


def P(*parts: str) -> str:
    return " ".join(p for p in parts if p)


BLUE = "#7CC4FF"

SCENES = [
    dict(id="s1", narration="삼성이 버린 기술을, 애플이 팔 년 뒤에 넣었습니다.",
         imgs=[
             ("s1a", P(OPEN, "SUBJECT: a matte gray clay camera lens barrel lying on its side on a dark "
                             "floor, plain and unmarked, a second identical barrel standing upright behind it.",
                       ACC, PROHIB), "ken-burns"),
             ("s1b", P(OPEN, "SUBJECT: a tight close view of the standing clay lens barrel's front rim.",
                       ACC, PROHIB), "zoom-in"),
         ]),

    dict(id="s2", narration="조리개는 빛이 들어오는 구멍입니다. 가변 조리개는 그 크기를 바꿉니다.",
         imgs=[
             ("s2a", P(OPEN, "SUBJECT: a thick matte gray clay plate standing upright with a single round "
                             "hole through its centre, a soft shaft of light passing through the hole onto "
                             "the dark floor behind.", ACC, PROHIB), "ken-burns"),
             ("s2b", P(OPEN, "SUBJECT: two matte gray clay plates side by side, each with a round hole "
                             "through the centre, the left hole clearly wide and the right hole clearly "
                             "narrow.", ACC, PROHIB), "zoom-in"),
         ],
         overlay={"type": "stat_card", "stat": "빛이 들어오는 구멍",
                  "subtitle": "가변 조리개는 이 크기를 바꾼다",
                  "accentColor": BLUE, "backgroundOverlay": 0.5}),

    dict(id="s3", narration="크게 열면 빛이 많이 들어오고 배경이 흐려집니다. 조이면 앞뒤가 선명해지는 대신 빛이 줍니다.",
         imgs=[
             ("s3a", P(OPEN, "SUBJECT: a wide clay ring opening with a broad beam of light pouring through "
                             "it, and behind the beam a row of three clay spheres where only the nearest "
                             "one is crisp and the far two dissolve into soft blur.", ACC, PROHIB), "ken-burns"),
             ("s3b", P(OPEN, "SUBJECT: a narrow clay ring opening with a thin beam of light, and behind it "
                             "the same row of three clay spheres now all equally crisp and sharp.",
                       ACC, PROHIB), "zoom-in"),
         ],
         overlay={"type": "stat_card", "stat": "둘 다 가질 수는 없다",
                  "subtitle": "열면 빛↑ 배경 흐림 · 조이면 선명↑ 빛↓",
                  "accentColor": BLUE, "backgroundOverlay": 0.5}),

    dict(id="s4", narration="삼성은 이천십팔 년에 넣었다가 이천이십 년에 뺐습니다. 센서가 커지면서 넣을 자리가 없었고, 어두운 곳은 소프트웨어가 대신했습니다.",
         imgs=[
             ("s4a", P(OPEN, "SUBJECT: a matte gray clay lens barrel that is clearly far too large for the "
                             "small square clay tray it is set into, its body overflowing the tray edges.",
                       ACC, PROHIB), "ken-burns"),
             ("s4b", P(OPEN, "SUBJECT: a close view of a small clay gear and a thin clay blade lying "
                             "discarded on the dark floor beside the crowded tray.", ACC, PROHIB), "zoom-in"),
         ],
         overlay={"type": "stat_card", "stat": "2018 → 2020",
                  "subtitle": "갤럭시 S9 도입 · 갤럭시 S20 폐지",
                  "accentColor": BLUE, "backgroundOverlay": 0.5}),

    dict(id="s5", narration="그런데 센서가 더 커지자, 가까운 음식이나 여러 줄 단체 사진에서 뒤가 날아갔습니다. 흐리게는 만들어도, 흐린 걸 선명하게 되돌리진 못합니다.",
         imgs=[
             ("s5a", P(OPEN, "SUBJECT: five matte gray clay figures standing in two staggered rows on a "
                             "dark floor, only the front row crisply defined while the back row melts into "
                             "heavy soft blur.", ACC, PROHIB), "ken-burns"),
             ("s5b", P(OPEN, "SUBJECT: a close view of one blurred clay figure in the back row, its edges "
                             "smeared and unrecoverable.", ACC, PROHIB), "zoom-in"),
         ],
         overlay={"type": "stat_card", "stat": "되돌릴 수 없다",
                  "subtitle": "흐리게는 만들어도, 흐린 건 선명해지지 않는다",
                  "accentColor": BLUE, "backgroundOverlay": 0.5}),

    dict(id="s6", narration="그래서 물리 조리개가 돌아왔습니다. 아이폰 십팔 프로는 네 단계입니다. 자세한 건 아래 설명란을 참고하세요.",
         imgs=[
             ("s6a", P(OPEN, "SUBJECT: six thin overlapping clay blades arranged in a circle on a dark "
                             "floor, forming a clean hexagonal iris opening at the centre.", ACC, PROHIB), "ken-burns"),
             ("s6b", P(OPEN, "SUBJECT: a tight close view of the hexagonal clay iris opening, the blades "
                             "drawn almost shut leaving only a small gap.", ACC, PROHIB), "zoom-in"),
         ],
         overlay={"type": "stat_card", "stat": "f/1.48 ~ f/4.0",
                  "subtitle": "네 단계 · 블레이드 6장 (Apple 공식 사양)",
                  "accentColor": BLUE, "backgroundOverlay": 0.5}),
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
