# 426 호흡법 — Codex 연출판

48.367초 · 1080×1920 · 30fps · 1451프레임.
Codex: 조사, 대본, 생성 이미지 3장, 화면·타이포그래피·호흡 원 연출.
autoShorts: Gemini Aoede TTS, HyperFrames 렌더, FFmpeg 합성, 기술 검수.

refs/production-plan-approved.md: 조사 출처와 승인된 기획.
refs/imagegen-prompts.json: 실제 이미지 생성 프롬프트.
refs/timing-manifest.json 및 frame-verification.json: 4·2·6초 타이밍 증거.
refs/verification.txt: 최종 기술 검수 결과.

호흡 안내는 20.966667초부터 32.966667초까지 정확히 360프레임입니다.
게시 및 예약 업로드는 실행하지 않았습니다.

재렌더 시 custom 씬을 덮어쓰지 마세요. autoShorts 폴더에서:
node scripts/render.js breathing-426
python3 episodes/breathing-426/scripts/normalize-breathing-frames.py
node scripts/assemble.js breathing-426
node scripts/verify.js breathing-426
