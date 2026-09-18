---
description: 대본 + 씬 설계 → episode.json scenes 작성
argument-hint: <slug>
---
> **autoShorts 모듈 전용.** 아래의 모든 명령(`npm run`·`npx hyperframes`·`node -e`)과 경로(`episodes/…`·`templates/…`·`scripts/…`·`assets/…`·`CLAUDE.md`)는 `autoShorts/` 기준이다 — 셸은 `cd autoShorts &&` 로 실행하고, 파일은 `autoShorts/` 접두로 읽는다. 상위 규칙: `docs/PRODUCTION.md`.

`episodes/$ARGUMENTS/episode.json` 의 `brief`·`reference.notes`·topic/audience/tone/cta 를 바탕으로 대본과 씬을 설계한다.
CLAUDE.md 의 "대본 규칙"과 `templates/scenes/README.md` 를 먼저 읽는다.

입력 반영:
- `brief.draft` 가 있으면 그것이 출발점이다. 한 줄 = 한 씬(`나레이션 | 화면`). 규칙(씬 길이·발음 표기·훅-페이오프)에
  어긋나는 곳만 고치고, 고친 이유를 표에 표시한다. 사용자의 문장을 임의로 갈아엎지 않는다.
- `brief.goal`(핵심 메시지)·`hook`·`mustShow` 는 반드시 대본/화면에 들어가고, `avoid` 는 쓰지 않는다.
- 총 길이는 `brief.lengthSec` 목표(±5초). `brief.visual` 은 템플릿·트랜지션·효과음 선택에 반영.
- `media/` 자료(`brief.files` use=asset, note 참고)는 어느 씬에 쓸지 정한다. 템플릿으로 못 넣는 자료는
  해당 씬을 `/shorts-scenes` 커스텀 대상으로 표시한다.

작성 기준:
- **지어내기 금지**: 소스(레퍼런스·brief·media·사용자 제공 자료)에 없는 성과·수치·개인 경험·후기를 만들지 않는다.
  숫자·날짜·조건은 표에 출처 열을 달고, 출처가 없으면 확정 전에 사용자에게 확인한다.
- 링크·설명란·고정 댓글을 안내하는 문장을 쓰면 `caption`에 실제 URL 을 함께 넣는다 (업로드 전 점검이 막는다).
- 레퍼런스의 말투·템포를 따르되 문장은 새로 쓴다.
- 나레이션 문장마다 표로 정리: `씬 | 나레이션 | 화면에서 입력하는 것 | 화면 동작 | 보이는 결과 | 템플릿 | 효과음`
- 긴 텍스트(프롬프트 원문, 목록 상세)는 onScreen 으로 보내고 나레이션은 핵심만.
- 훅(첫 씬)에서 약속한 결과가 어느 씬에서 보이는지 명시해 훅-페이오프를 검증한다.
- 씬 수와 예상 총 길이(한국어 약 6~7음절/초)를 제시한다.
- 발음 주의: 영문·숫자는 읽는 대로 한글로(예: "3초" OK, "GPT-5" → "지피티 파이브").

표를 보여준 뒤 episode.json 의 `scenes` 를 채우고, `caption`·`hashtags`·`upload.title` 은 **비어 있을 때만** 채운다
(사람이 입력 페이지에서 쓴 문구는 유지). 저장 후
`node -e "import('./scripts/lib/episode.js').then(m=>m.loadEpisode('$ARGUMENTS'))"` 로 스키마 검증한다.
사용자 확정 후 `npm run tts -- $ARGUMENTS` 를 제안한다(크레딧 소모 — 확인 없이 실행하지 않음. 테스트는 `--mock`).
