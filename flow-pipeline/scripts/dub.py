#!/usr/bin/env python3
"""ElevenLabs 컷별 더빙 생성.

사용: FLOW_PROJECT=<프로젝트명> python3 scripts/dub.py [voice_id]
  - <프로젝트>/cuts.json 의 narration 을 컷별로 TTS → <프로젝트>/audio/cut01.mp3 ...
  - voice_id 생략 시 한국어 프리메이드 보이스 목록을 조회해 보여주고 종료
  - 프로젝트 지정 규칙은 projlib.find_project 참고 (cd projects/<이름> 후 실행도 가능)
"""
import json, os, sys, pathlib, urllib.request

from projlib import find_project

API = "https://api.elevenlabs.io/v1"
KEY = os.environ.get("ELEVENLABS_API_KEY")
if not KEY:  # 환경변수 없으면 프로젝트 루트 .env 에서 읽는다
    env = pathlib.Path(__file__).parent.parent / ".env"
    if env.exists():
        for line in env.read_text().splitlines():
            if line.startswith("ELEVENLABS_API_KEY=") and "여기에" not in line:
                KEY = line.split("=", 1)[1].strip().strip('"')
if not KEY:
    sys.exit("flow-pipeline/.env 파일의 ELEVENLABS_API_KEY= 뒤에 키를 붙여넣으세요")

def req(path, data=None, headers=None):
    h = {"xi-api-key": KEY, "Content-Type": "application/json"}
    if headers: h.update(headers)
    r = urllib.request.Request(API + path, headers=h,
                               data=json.dumps(data).encode() if data else None)
    return urllib.request.urlopen(r)

if len(sys.argv) < 2:
    voices = json.load(req("/voices"))["voices"]
    print("voice_id 를 지정하세요. 사용 가능한 보이스:")
    for v in voices:
        print(f"  {v['voice_id']}  {v['name']}  {v.get('labels', {})}")
    sys.exit(0)

voice = sys.argv[1]
root = find_project()
cuts = json.load(open(root / "cuts.json"))["cuts"]
(root / "audio").mkdir(exist_ok=True)

for c in cuts:
    out = root / "audio" / f"cut{c['id']:02d}.mp3"
    if out.exists():
        print(f"skip {out.name}")
        continue
    body = {
        "text": c["narration"],
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.75, "speed": 1.0},
    }
    resp = req(f"/text-to-speech/{voice}", body)
    out.write_bytes(resp.read())
    print(f"ok   {out.name}  ({len(c['narration'])}자)")
print("done")
