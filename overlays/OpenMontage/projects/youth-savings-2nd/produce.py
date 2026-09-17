#!/usr/bin/env python3
"""2026 청년미래적금 2차 (회색 찰흙 3D · 머니정보) — OpenMontage 프로덕션 드라이버.

사용: .venv/bin/python projects/youth-savings-2nd/produce.py [assets|props|render|all]
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
    dict(id='s1', narration='연 십구 점 사 퍼센트 효과. 백삼십팔만 명이 몰렸던 그 적금, 십월 칠일 다시 열립니다.',
         imgs=[
               ('s1a', P(OPEN, 'SUBJECT: a pair of giant matte gray clay bank doors swung open with warm golden light pouring out, a dense crowd of tiny clay figures streaming toward the entrance.', PROHIB), 'ken-burns'),
               ('s1b', P(OPEN, 'SUBJECT: a close view of the glowing bank doorway with tiny clay figures passing through the warm light.', PROHIB), 'zoom-in'),
         ], overlay={'type': 'stat_card', 'stat': '19.4%', 'subtitle': '연 최고 효과 · 10월 7일 2차 오픈', 'accentColor': '#C98A1A', 'backgroundOverlay': 0.5}),
    dict(id='s2', narration='만 열아홉부터 서른넷, 총급여 칠천오백만 원 이하, 가구 중위소득 이백 퍼센트 이하. 군 복무는 최대 육 년 빼줍니다.',
         imgs=[
               ('s2a', P(OPEN, 'SUBJECT: a long matte gray clay ruler with plain tick marks on the floor, a small clay figure standing on one tick and a small clay soldier figure pushing a round marker backward along the ruler.', PROHIB), 'ken-burns'),
               ('s2b', P(OPEN, 'SUBJECT: a close view of the round clay marker settled on the ruler tick with a soft warm glow.', PROHIB), 'zoom-in'),
         ], overlay={'type': 'stat_card', 'stat': '만 19~34세', 'subtitle': '총급여 7,500만↓ · 중위소득 200%↓ · 복무 최대 6년 차감', 'accentColor': '#C98A1A', 'backgroundOverlay': 0.5}),
    dict(id='s3', narration='월 오십만 원, 삼 년이면 원금 천팔백. 정부가 일반형 백팔만 원, 우대형 이백십육만 원을 얹어줍니다. 이자는 비과세.',
         imgs=[
               ('s3a', P(OPEN, 'SUBJECT: a tall column of matte gray clay coins on a round pedestal, a large clay hand placing an extra bundle of coins on top that glows softly warm.', PROHIB), 'ken-burns'),
               ('s3b', P(OPEN, 'SUBJECT: a round clay stamp bouncing off the coin column, repelled, the column untouched.', PROHIB), 'zoom-in'),
         ], overlay={'type': 'stat_card', 'stat': '+216만 원', 'subtitle': '우대형 기여금 (월 50만 × 3년) · 일반형 108만 · 이자 비과세', 'accentColor': '#C98A1A', 'backgroundOverlay': 0.5}),
    dict(id='s4', narration='중소기업 재직자나 신규 취업자면 우대형. 기여금이 두 배니까 해당되면 무조건 우대형입니다.',
         imgs=[
               ('s4a', P(OPEN, 'SUBJECT: two matte gray clay coin stacks side by side on a pedestal, the right stack exactly twice the height of the left and wrapped in a soft warm glow.', PROHIB), 'ken-burns'),
               ('s4b', P(OPEN, 'SUBJECT: a close view of the taller warmly glowing coin stack.', PROHIB), 'zoom-in'),
         ], overlay={'type': 'stat_card', 'stat': '12%', 'subtitle': '우대형 기여금 (일반형 6%)', 'accentColor': '#C98A1A', 'backgroundOverlay': 0.5}),
    dict(id='s5', narration='칠일은 출생연도 홀수, 팔일은 짝수, 십이일부터는 누구나. 십육일이 마지막입니다.',
         imgs=[
               ('s5a', P(OPEN, 'SUBJECT: three blank rounded matte gray clay calendar tiles standing in a row, tiny clay figures in two lines walking toward the first two tiles.', PROHIB), 'ken-burns'),
               ('s5b', P(OPEN, 'SUBJECT: a close view of the third blank calendar tile with its edge lit by a harsh red glow, the only red in the frame.', PROHIB), 'zoom-in'),
         ], overlay={'type': 'stat_card', 'stat': '10.7 ~ 10.16', 'subtitle': '7일 홀수 · 8일 짝수 · 12일~ 누구나', 'accentColor': '#E5372F', 'backgroundOverlay': 0.5}),
    dict(id='s6', narration='청년도약계좌가 있어도 갈아탈 수 있습니다. 순서가 생명. 새 계좌를 먼저 만들고, 그다음 특별중도해지.',
         imgs=[
               ('s6a', P(OPEN, 'SUBJECT: two blank matte gray clay passbooks on two platforms joined by a small clay bridge, a clay figure crossing toward the new passbook which glows softly warm.', PROHIB), 'ken-burns'),
               ('s6b', P(OPEN, 'SUBJECT: a close view of the old clay passbook sliding down into a slot while a faint red cross mark hovers over the reverse path, the only red in the frame.', PROHIB), 'zoom-in'),
         ], overlay={'type': 'stat_card', 'stat': '① 개설 → ② 해지', 'subtitle': '청년도약계좌 특별중도해지 (혜택 유지)', 'accentColor': '#C98A1A', 'backgroundOverlay': 0.5}),
    dict(id='s7', narration='내년엔 우대형이 최대 이십오 퍼센트까지 오를 수 있는데, 지금 가입해도 소급됩니다. 기다리면 손해입니다.',
         imgs=[
               ('s7a', P(OPEN, 'SUBJECT: a matte gray clay coin stack with a clay arrow rising from its top stretching high, beside it a large clay clock with hands turned backward, a soft warm glow over the stack.', PROHIB), 'ken-burns'),
               ('s7b', P(OPEN, 'SUBJECT: a close view of the clay arrow tip glowing warm high above the coin stack.', PROHIB), 'zoom-in'),
         ], overlay={'type': 'stat_card', 'stat': '최대 25%', 'subtitle': '내년 예산안 통과 시 소급 상향', 'accentColor': '#C98A1A', 'backgroundOverlay': 0.5}),
    dict(id='s8', narration='십일월 중순 심사 결과가 오면 계좌 개설. 은행 앱 알림 켜 두고, 당신은 홀수생인지 짝수생인지 댓글로.',
         imgs=[
               ('s8', P(OPEN, 'SUBJECT: a matte gray clay smartphone standing upright with a rounded bell shape glowing softly warm on its screen, a clay finger tapping it, two blank rounded clay cards hovering on the left and right.', PROHIB), 'zoom-in'),
         ], overlay={'type': 'stat_card', 'stat': '1397', 'subtitle': '서민금융진흥원 · 11월 16~27일 계좌 개설', 'accentColor': '#C98A1A', 'backgroundOverlay': 0.5}),
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
