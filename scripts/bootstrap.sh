#!/usr/bin/env bash
# 새 머신 복원 부트스트랩 — docs/SETUP.md 2~4단계 자동화.
# 사용: bash scripts/bootstrap.sh   (저장소 루트 어디서 실행해도 됨)
set -euo pipefail
cd "$(dirname "$0")/.."

echo "== 1/5 서브모듈 =="
git submodule update --init

echo "== 2/5 업스트림 패치 =="
if git -C OpenMontage apply --check ../patches/openmontage.diff 2>/dev/null; then
  git -C OpenMontage apply ../patches/openmontage.diff && echo "  OpenMontage 패치 적용"
else
  echo "  OpenMontage 패치 스킵 (이미 적용됐거나 충돌 — git -C OpenMontage status로 확인)"
fi
if git -C talkcraft/video-talkcraft apply --check ../../patches/video-talkcraft.diff 2>/dev/null; then
  git -C talkcraft/video-talkcraft apply ../../patches/video-talkcraft.diff && echo "  video-talkcraft 패치 적용"
else
  echo "  video-talkcraft 패치 스킵 (이미 적용됐거나 충돌)"
fi

echo "== 3/5 오버레이 (서브모듈 내부 자작 파일) =="
cp -R overlays/OpenMontage/ OpenMontage/
echo "  MYNEXTSEASON.md + projects/*/produce.py 복사"

echo "== 4/5 파이썬 venv =="
if [ ! -x OpenMontage/.venv/bin/python ]; then
  python3 -m venv OpenMontage/.venv
  OpenMontage/.venv/bin/pip install -q -r OpenMontage/requirements.txt
  echo "  OpenMontage/.venv 생성·설치 완료"
else
  echo "  OpenMontage/.venv 이미 존재 — 스킵"
fi

echo "== 5/5 node_modules =="
[ -d talkcraft/demo/remotion/node_modules ] || (cd talkcraft/demo/remotion && npm install)
for p in gcans guri family; do
  link="talkcraft/$p/remotion/node_modules"
  [ -e "$link" ] || ln -s ../../demo/remotion/node_modules "$link"
done
[ -d OpenMontage/remotion-composer/node_modules ] || (cd OpenMontage/remotion-composer && npm install)
[ -d autoShorts/node_modules ] || (cd autoShorts && npm install)
(cd autoShorts && npm run sfx)
echo "  talkcraft(demo 공유 심링크)·remotion-composer·autoShorts 준비 완료"

echo ""
echo "✅ bootstrap 완료. 남은 수동 단계 (docs/SETUP.md 5~6):"
echo "   1) flow-pipeline/.env  → ELEVENLABS_API_KEY=..."
echo "   2) OpenMontage/.env    → GOOGLE_API_KEY=..."
echo "   3) autoShorts/.env     → cp autoShorts/.env.example autoShorts/.env 후 GEMINI_API_KEY 등 (whisper 모델은 첫 tts 때 자동 다운로드)"
echo "   4) (flow 사용 시) Aside 설치·MCP 등록·flow.google.com 로그인 — flow-pipeline/RUNBOOK.md"
