#!/usr/bin/env python3
"""연안 이씨 가족 역사 그림책 영상 (가로 16:9, 아이들용) — OpenMontage 드라이버.

사용: .venv/bin/python projects/yeonan-family/produce.py [assets|props|render|all]
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

OPEN = ("A horizontal 16:9 storybook illustration, warm watercolor and colored-pencil "
        "children's picture book style, soft paper texture, gentle rounded shapes.")
STYLE = ("STYLE: hand-painted watercolor washes with soft colored-pencil outlines, warm "
         "gentle lighting, kind friendly faces, simple readable composition, no "
         "photorealism, no harsh shadows.")
COLOR = ("COLOR IS WARM AND GENTLE: cream paper base, soft ochre and sage green, warm "
         "coral accents, deep indigo for night scenes, fully harmonious, no gray wash.")
PROHIB = ("No text, no letters, no numbers, no labels, no logos, no watermark, no "
          "frames, no borders, no gore, no graphic violence, no scary imagery.")
HORSE = "the same loyal chestnut horse with a flowing dark mane"


def P(*parts: str) -> str:
    return " ".join(parts)


SCENES = [
    dict(id="s1", narration="우리 가족 이야기, 들려줄게. 우리는 이십사 대째 이어져 온 연안 이씨야. 우리의 뿌리는 통례문부사공파, 이 이야기는 전라남도 해남으로 이어진단다.",
         imgs=[("s1", P(OPEN, "SUBJECT: an old genealogy book glowing softly as it opens like a magic book, golden light and tiny stars rising from its pages, a gentle map of southern Korea beneath with a warm glow on the Haenam coast.", STYLE, COLOR, PROHIB), "ken-burns")]),
    dict(id="s2", narration="아주 먼 옛날 삼국시대, 시조 이무 할아버지는 당나라 장군이셨어. 신라와 당나라 사이에 전쟁이 날 뻔했을 때, 지혜롭게 막아내셨다고 전해져.",
         imgs=[("s2", P(OPEN, "SUBJECT: a kind general in elegant Tang dynasty armor standing between two royal courts, gently bringing two kings' hands together in peace, banners softening in the wind.", STYLE, COLOR, PROHIB), "ken-burns")]),
    dict(id="s3", narration="김유신 장군이 고마워하며 높은 벼슬을 주려 했지만 사양하셨고, 대신 받은 땅 연안이 우리의 본관이 되었단다.",
         imgs=[("s3", P(OPEN, "SUBJECT: the same kind general politely bowing to decline a golden medal offered by a Silla general, while gesturing warmly toward a peaceful riverside land with fields and low hills.", STYLE, COLOR, PROHIB), "zoom-in")]),
    dict(id="s4", narration="조선시대 이후백 할아버지는, 명나라에 잘못 적힌 우리나라 기록을 바로잡으러 간 용감한 선비였어.",
         imgs=[("s4", P(OPEN, "SUBJECT: a dignified Joseon scholar in a scholar's robe and black hat standing tall in a grand Chinese palace hall, holding a brush and an open book with quiet confidence.", STYLE, COLOR, PROHIB), "ken-burns")]),
    dict(id="s5", narration="친척의 부탁도 옳지 않으면 지워버릴 만큼 맑았던 청백리. 넘침을 경계하라는 계일, 그게 우리 가문의 정신이야.",
         imgs=[("s5", P(OPEN, "SUBJECT: a celadon cup filled almost to the brim on a wooden desk, a scholar's hand gently steadying it, beside it another hand calmly brushing away a name strip from a list, soft morning light.", STYLE, COLOR, PROHIB), "zoom-in")]),
    dict(id="s6", narration="임진왜란 때 이선경 할아버지가 왜군에게 돌아가시자, 아들 이유길 할아버지는 이순신 장군 곁에서 명량해전의 큰 공을 세웠지.",
         imgs=[("s6", P(OPEN, "SUBJECT: Joseon panokseon warships with sturdy wooden decks sailing bravely through swirling currents between narrow cliffs at Myeongnyang strait, flags fluttering, a young officer standing resolute at the bow.", STYLE, COLOR, PROHIB), "ken-burns")]),
    dict(id="s7", narration="세월이 흘러 할아버지는 멀리 만주 땅에서 싸우다 쓰러지셨어. 마지막 순간, 피 묻은 옷자락에 소식을 적어 아끼던 말에게 맡기셨단다.",
         imgs=[("s7", P(OPEN, f"SUBJECT: a snowy Manchurian plain at dusk, a wounded warrior kneeling beside {HORSE}, gently tying a folded red-stained cloth to its bridle, both faces tender and brave.", STYLE, COLOR, PROHIB), "zoom-in")]),
    dict(id="s8", narration="말은 그 옷을 입에 문 채, 천 킬로미터를 사흘 만에 달려 고향 집에 소식을 전하고 숨을 거두었어. 이 충성스러운 말의 무덤이 지금도 파주에 있는 의마총이야.",
         imgs=[("s8a", P(OPEN, f"SUBJECT: {HORSE} galloping alone across mountains and rivers through day and night, a folded cloth held gently in its mouth, stars and sunrise passing overhead in one flowing scene.", STYLE, COLOR, PROHIB), "ken-burns"),
               ("s8b", P(OPEN, f"SUBJECT: {HORSE} arriving at a humble thatched-roof house gate at dawn, gently lying down on the ground as a family rushes out with warm lanterns, tender and peaceful farewell mood.", STYLE, COLOR, PROHIB), "zoom-in")]),
    dict(id="s9", narration="임진왜란이 끝나고 형제들은 해남으로 내려왔어. 동생 이복길 할아버지는 정묘호란 때 의병 수천 명을 모으셨고, 그렇게 우리 가족은 해남 삼산면에서 사백 년 넘게 살아온 거야.",
         imgs=[("s9", P(OPEN, "SUBJECT: a warm village settling scene in Haenam with thatched-roof houses under a broad mountain, a scholar greeting villagers as families plant trees and unpack, sunset glow.", STYLE, COLOR, PROHIB), "ken-burns")]),
    dict(id="s10", narration="일제강점기, 김구 선생님이 가장 존경했던 분이 우리 가문의 이동녕 할아버지야. 학교를 세워 독립군을 기르고, 대한민국 임시정부를 이끄셨지.",
         imgs=[("s10", P(OPEN, "SUBJECT: dignified elderly independence leaders in white and dark hanbok holding a Korean flag together in front of a modest shanghai-style building, hopeful faces, morning light.", STYLE, COLOR, PROHIB), "ken-burns")]),
    dict(id="s11", narration="불의를 참지 않는 용기와, 넘침을 경계하는 겸손. 그 멋진 조상님들의 피가 지금 너희에게 흐르고 있단다.",
         imgs=[("s11", P(OPEN, "SUBJECT: translucent gentle ancestors, a general, a scholar, an admiral's officer and an elder, standing warmly like guardians behind two smiling modern children, golden hour light.", STYLE, COLOR, PROHIB), "zoom-in")]),
    dict(id="s12", narration="이십사 대째 이어지는 이 이야기의 주인공은, 바로 너희들이야. 자랑스럽게, 씩씩하게 자라렴.",
         imgs=[("s12", P(OPEN, "SUBJECT: the glowing genealogy book slowly closing with sparkles, two happy children silhouettes running toward a bright horizon over Haenam fields.", STYLE, COLOR, PROHIB), "ken-burns")]),
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
                r = imagen.execute({"prompt": prompt, "aspect_ratio": "16:9",
                                    "model": "gemini-3.1-flash-image", "output_path": str(img)})
                assert r.success, f"IMG {name}: {r.error}"
                print(f"img  {name}  ok", flush=True)
    print("assets done", flush=True)


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
        for (name, _prompt, anim), a, b in spans:
            cuts.append(dict(id=f"cut-{name}", in_seconds=round(a, 2), out_seconds=round(b, 2),
                             source=str(IMG_DIR / f"{name}.png"), animation=anim))
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
                 renderer_family="explainer-data", playbook="flat-motion-graphics",
                 cuts=cuts, captions=captions,
                 audio=dict(narration=dict(src=str(full), volume=1.0)),
                 subtitles=dict(style="word-by-word", language="ko"))
    (ART_DIR / "edit_decisions.json").write_text(json.dumps(props, ensure_ascii=False, indent=1))
    print(f"edit_decisions — 총 {t:.1f}s, cuts {len(cuts)}", flush=True)


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
