#!/usr/bin/env python3
"""AI 사고력 시리즈 3편 (코딩 학원) — OpenMontage 프로덕션 드라이버.

사용: .venv/bin/python projects/ai-thinking-ep3/produce.py [assets|props|render|all]
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
    dict(id='s1', narration='AI가 코드를 다 짜주는 시대, 코딩 학원부터 끊었다는 부모님들. 절반은 맞고, 절반은 위험한 선택입니다.',
         imgs=[
               ('s1', P(OPEN, 'SUBJECT: a thick clay slab splitting cleanly in half in midair, one half bathed in a soft warm glow, the other half laced with harsh red cracks, the only red in the frame.', PROHIB), 'ken-burns'),
         ]),
    dict(id='s2', narration='맞는 절반. 컴퓨터 언어를 달달 외우는 시대는 정말 끝났습니다. 문법 암기는 이제 AI가 더 잘합니다.',
         imgs=[
               ('s2', P(OPEN, 'SUBJECT: a thick heavy clay grammar book crumbling into fine dust particles that drift away in the studio air.', PROHIB), 'ken-burns'),
         ]),
    dict(id='s3', narration='위험한 절반. 코딩교육의 진짜 알맹이는, 애초에 언어가 아니었거든요.',
         imgs=[
               ('s3', P(OPEN, 'SUBJECT: a small luminous geometric core structure revealed hovering amid the settling dust, glowing softly warm.', PROHIB), 'zoom-in'),
         ]),
    dict(id='s4', narration='블록 조립을 떠올려 보세요. 설명서대로 따라 만들면 결과물은 화려해도, 머릿속에 남는 게 없습니다.',
         imgs=[
               ('s4a', P(OPEN, 'SUBJECT: an ornate finished castle built from plain clay building blocks standing on a table, a small clay child staring only at an instruction booklet with scribble diagram marks.', PROHIB), 'ken-burns'),
               ('s4b', P(OPEN, 'SUBJECT: a close view of the instruction booklet pages covered only with faint meaningless scribble diagrams.', PROHIB), 'zoom-in'),
         ]),
    dict(id='s5', narration='왜 이렇게 나눴고, 왜 이 순서고, 틀리면 어디부터 확인할지. 설명할 수 있어야 진짜 훈련입니다.',
         imgs=[
               ('s5a', P(OPEN, 'SUBJECT: the same block castle disassembled in midair, its pieces floating in tidy ordered layers like exploded assembly steps, one single block edged with a red glow.', PROHIB), 'ken-burns'),
               ('s5b', P(OPEN, 'SUBJECT: a close view of the red-edged clay block floating among the tidy ordered pieces, the only red in the frame.', PROHIB), 'zoom-in'),
         ]),
    dict(id='s6', narration='AI는 뭐든 딸깍 한 번에 만들어줍니다. 하지만 딸깍 앞엔 무엇을 만들지 정하는 사람이, 딸깍 뒤엔 결과를 의심하는 사람이 있어야 합니다.',
         imgs=[
               ('s6a', P(OPEN, 'SUBJECT: a large rounded clay button in the center, one clay figure standing before it gesturing at floating blueprint shapes, another clay figure behind it examining a result panel through a magnifying glass.', PROHIB), 'ken-burns'),
               ('s6b', P(OPEN, 'SUBJECT: a close view of the clay figure holding a magnifying glass over a glowing result panel marked only with faint scribble lines.', PROHIB), 'zoom-in'),
         ]),
    dict(id='s7', narration='그래서 필요한 건 언어 수업이 아니라, 문제를 쪼개고 예외를 찾고 결과를 검증하는 논리 훈련입니다.',
         imgs=[
               ('s7a', P(OPEN, 'SUBJECT: three small clay podiums in a row: a big block splitting into smaller pieces on the first, one odd irregular piece lifted out on the second, a round stamp pressing down on the third.', PROHIB), 'ken-burns'),
               ('s7b', P(OPEN, 'SUBJECT: a tidy assembled clay structure standing complete, pulsing with a soft warm glow.', PROHIB), 'zoom-in'),
         ]),
    dict(id='s8', narration='끊어야 할 건 코딩이 아니라 암기입니다. 우리 아이에게 남길 건 어느 쪽일까요 — 따라 만든 성, 아니면 생각하는 힘.',
         imgs=[
               ('s8', P(OPEN, 'SUBJECT: a split scene: the ornate block castle standing on one side, and on the other a small clay child holding up the small luminous core in both hands.', PROHIB), 'zoom-in'),
         ]),
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
