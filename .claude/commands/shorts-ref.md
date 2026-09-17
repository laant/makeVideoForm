---
description: 레퍼런스 쇼츠 구조 분석 → 내 주제에 적용안
argument-hint: <slug>
---
> **autoShorts 모듈 전용.** 아래의 모든 명령(`npm run`·`npx hyperframes`·`node -e`)과 경로(`episodes/…`·`templates/…`·`scripts/…`·`assets/…`·`CLAUDE.md`)는 `autoShorts/` 기준이다 — 셸은 `cd autoShorts &&` 로 실행하고, 파일은 `autoShorts/` 접두로 읽는다. 상위 규칙: `docs/PRODUCTION.md`.

`episodes/$ARGUMENTS/episode.json` 의 `reference`(transcript · sceneFlow · url · reaction)와 `brief`,
`refs/` 의 캡처 이미지(직접 열어서 본다, `brief.files` 의 note 참고)를 읽고 분석한다.

출력(사용자에게 표로 보여주고, 요약을 `episode.json.reference.notes` 에 저장):
1. **오프닝 문장**: 첫 1~2초에 무엇을 약속/자극하는가, 왜 스크롤을 멈추게 하는가
2. **전개 구조**: 구간별(초 단위) 역할 — 훅 / 문제 / 시연 / 반전 / 결과 / CTA
3. **말투·템포**: 문장 길이, 반말/존댓말, 초당 글자 수 추정, 화면 전환 빈도
4. **화면 문법**: 입력 화면·비교·리스트·결과 중 무엇을 어떤 순서로 보여주는가 (sceneFlow·캡처 근거)
5. **내 주제 적용안**: 같은 구조로 내 주제를 채운 씬 흐름 초안 (문장은 새로 작성, 복제 금지).
   `brief` 의 goal·hook·mustShow·avoid·draft 가 있으면 그것을 우선하고 레퍼런스 구조와 어긋나는 곳을 짚는다.
6. 위험 요소: 훅과 실제 내용이 어긋날 지점, 과장 표현

전사가 없으면 말투·템포는 추측하지 말고 "전사 없음"으로 표시한다. 캡처·장면 메모로 알 수 있는 화면 구조만 분석한다.
레퍼런스 자료가 아무것도 없으면 분석하지 않고 `/shorts-script` 로 넘어가라고 안내한다.
