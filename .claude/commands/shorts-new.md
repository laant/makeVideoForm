---
description: 새 쇼츠 에피소드 킥오프 (입력 페이지 내용 확인 → 빈 곳만 질문 → 전체 워크플로 시작)
argument-hint: <slug> [주제]
---
> **autoShorts 모듈 전용.** 아래의 모든 명령(`npm run`·`npx hyperframes`·`node -e`)과 경로(`episodes/…`·`templates/…`·`scripts/…`·`assets/…`·`CLAUDE.md`)는 `autoShorts/` 기준이다 — 셸은 `cd autoShorts &&` 로 실행하고, 파일은 `autoShorts/` 접두로 읽는다. 상위 규칙: `docs/PRODUCTION.md`.

새 쇼츠 에피소드를 시작한다. 인자: $ARGUMENTS

1. `episodes/<slug>/episode.json` 이 없으면 `npm run new -- <slug> "<주제>"` 를 **백그라운드로** 실행한다.
   입력 페이지가 브라우저에 열리니 사용자에게 채우고 "입력 완료"를 누르라고 안내하고 기다린다.
   (완료 버튼을 누르면 프로세스가 종료되어 알림이 온다.)
2. episode.json 을 읽는다. 사람이 미리 적은 입력은 여기 있다:
   - `topic` `audience` `tone` `cta`
   - `brief`: goal(핵심 메시지) · hook · lengthSec · mustShow · avoid · draft(대본 초안: 한 줄 = `나레이션 | 화면`) · visual(연출 요청) · files
   - `reference`: url · reaction · transcript · sceneFlow, 캡처는 `refs/`
   - 영상에 쓸 자료는 `media/` (`brief.files[].note` 에 메모)
   - `theme`, `caption` `hashtags` `upload`
3. **이미 채워진 항목은 다시 묻지 않는다.** 대본을 쓰는 데 정말 필요한데 비어 있거나 모호한 것만 한 번에 묻는다.
   필수(topic/audience/cta)가 비었거나, 입력끼리 충돌하거나(예: 훅과 핵심 메시지가 다른 얘기), 주제 특화 정보
   (시연할 실제 프롬프트·앱 화면 등)가 없어 지어내야 하는 경우. 물을 게 없으면 묻지 않는다.
   답은 episode.json 해당 필드에 기록한다. 긴 수정이 필요하면 `npm run intake -- <slug>` 를 안내해도 된다.
4. 입력 요약(3~5줄)을 보여주고 다음 단계로 바로 진행한다:
   - 레퍼런스(전사·장면 메모·캡처 중 하나라도)가 있으면 `/shorts-ref <slug>`
   - 없으면 레퍼런스 분석은 건너뛰고 `/shorts-script <slug>`
