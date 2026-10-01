# 식후 걷기 — Codex B안

사용자 승인된 대본과 프롬프트: refs/production-plan-approved.md.
생성 이미지 3장: media/. 내장 image_gen 실제 프롬프트: refs/imagegen-prompts.json.
전문 모션그래픽: 근육의 포도당 이용 원리, 연구 설계·누적 지표 비교.
연구 수치는 Reynolds et al. (2016) iAUC 기하평균비 0.88을 100 대 88로 표시.

Gemini Aoede 내레이션, HyperFrames 렌더, FFmpeg 합성, 자동 기술 검사.
재렌더: node scripts/render.js postmeal-walk → python3 episodes/postmeal-walk/scripts/normalize-walk.py → node scripts/assemble.js postmeal-walk → node scripts/verify.js postmeal-walk.
custom 씬을 기본 템플릿으로 덮어쓰지 마세요.
업로드는 실행하지 않았습니다.
