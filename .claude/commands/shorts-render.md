---
description: 렌더 → 합성 → 최종 검수 (업로드 전 단계)
argument-hint: <slug>
---
> **autoShorts 모듈 전용.** 아래의 모든 명령(`npm run`·`npx hyperframes`·`node -e`)과 경로(`episodes/…`·`templates/…`·`scripts/…`·`assets/…`·`CLAUDE.md`)는 `autoShorts/` 기준이다 — 셸은 `cd autoShorts &&` 로 실행하고, 파일은 `autoShorts/` 접두로 읽는다. 상위 규칙: `docs/PRODUCTION.md`.

`$ARGUMENTS` 에피소드를 최종 영상으로 만든다.

1. 환경 확인: `npx hyperframes doctor` (Chrome·FFmpeg 필수 항목), `assets/sfx/*.wav` 없으면 `npm run sfx`.
2. `npm run make -- $ARGUMENTS` (이미 음성이 있으면 캐시 사용 — 크레딧 추가 소모 없음)
3. verify 결과의 ✗ 항목은 원인을 찾아 고친 뒤 해당 단계부터 재실행.
4. `episodes/$ARGUMENTS/renders/check/contact-sheet.jpg` 와 개별 프레임을 직접 열어 확인:
   첫 프레임에 훅 텍스트가 보이는지, 텍스트 잘림·안전영역 침범, 자막과 화면 내용 일치, 마지막 프레임 CTA.
5. 음성-화면 싱크는 `npm run preview -- $ARGUMENTS` 로 사용자에게 확인 요청(끝나면 `--stop`).
6. 업로드 문구 미리보기: `npm run upload -- $ARGUMENTS` (dry-run). 실제 업로드(`--yes`)는 사용자가 요청할 때만.
