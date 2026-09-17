---
description: 생성된 나레이션 음성 검수 (발음·문장 정렬·구간 타임마커)
argument-hint: <slug>
---
> **autoShorts 모듈 전용.** 아래의 모든 명령(`npm run`·`npx hyperframes`·`node -e`)과 경로(`episodes/…`·`templates/…`·`scripts/…`·`assets/…`·`CLAUDE.md`)는 `autoShorts/` 기준이다 — 셸은 `cd autoShorts &&` 로 실행하고, 파일은 `autoShorts/` 접두로 읽는다. 상위 규칙: `docs/PRODUCTION.md`.

`episodes/$ARGUMENTS` 의 음성을 검수한다. 추측이 아니라 실제 파일/타임스탬프 기준으로 판단한다.

1. episode.json 의 각 씬 `timing.words` 와 `narration` 을 비교해 표로 출력:
   `씬 | 시작~끝(전체 기준) | 발화 길이 | 초당 음절 | 이상 징후`
2. 이상 징후 기준:
   - words 를 이어붙인 텍스트가 narration 과 다름 (누락·반복·숫자/영문 오독 가능성)
   - 초당 음절 > 8 (너무 빠름) 또는 < 4 (늘어짐)
   - 단어 간 공백 > 0.6s (어색한 멈춤)
   - 씬 발화 길이 < 1.2s (화면 연출이 안 보일 만큼 짧음)
3. 전체 길이 `ffprobe episodes/$ARGUMENTS/audio/narration.mp3` 확인.
4. 발음 문제 의심 구간은 사용자가 직접 들어볼 수 있게 `afplay` 명령과 해당 씬 파일(`audio/sNN.mp3`)을 안내한다.
5. 수정안: narration 표기 변경(발음대로 쓰기, 쉼표 추가), voice 설정(speed/stability) 조정 제안.
   수정 시 해당 씬만 재생성되므로 `npm run tts -- $ARGUMENTS` 재실행을 안내한다.
