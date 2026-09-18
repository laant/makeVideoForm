---
description: 씬 HTML/GSAP 생성·커스텀 (나레이션 타임스탬프 동기화)
argument-hint: <slug> [sNN ...]
---
> **autoShorts 모듈 전용.** 아래의 모든 명령(`npm run`·`npx hyperframes`·`node -e`)과 경로(`episodes/…`·`templates/…`·`scripts/…`·`assets/…`·`CLAUDE.md`)는 `autoShorts/` 기준이다 — 셸은 `cd autoShorts &&` 로 실행하고, 파일은 `autoShorts/` 접두로 읽는다. 상위 규칙: `docs/PRODUCTION.md`.

인자: $ARGUMENTS (slug, 선택적으로 커스텀할 씬 id)

1. `npm run scenes -- <slug>` 로 템플릿 기반 씬을 생성한다.
2. 각 씬을 점검한다: onScreen 데이터가 나레이션과 맞는지, `…At: "word:…"` 키워드가 실제 timing.words 에 있는지.
   입력/비교/결과 씬이 모두 같은 레이아웃으로 반복되면 템플릿·배치를 바꿔 변화를 준다.
3. 템플릿으로 표현이 안 되는 씬(인자로 지정된 씬 포함)만 `episodes/<slug>/scenes/sNN.html` 을 직접 수정한다:
   - 첫 주석을 `autoshorts:custom` 으로 변경
   - 요소 등장은 `S.words` 의 실제 타임스탬프에 맞춰 stagger (`H.at("word:…")`)
   - 자막·효과음 타이밍은 나레이션과 겹치지 않게, 화면 텍스트는 안전영역 안에
   - `data-duration` 유지, 결정적 코드만, 에셋 경로는 에피소드 폴더 기준
   - 사용한 에셋을 **매니페스트 표**로 보고: `경로 | 종류(이미지·폰트·음원·로고) | 출처 | 라이선스·사용 근거`
     직접 만든 것·사용자 제공 자료는 그렇게 표시. 출처·라이선스가 불명확한 외부 에셋은 쓰지 말고 사용자에게 확인한다
4. 연출 옵션: 씬 전환 `transitionOut`(20종)·화면 효과 `effects`(19종)·효과음 `sfx`(17종) — `templates/scenes/README.md` 표에서
   영상 분위기에 맞는 것을 골라 episode.json 에 적는다(효과는 합성 단계 FFmpeg 적용이라 preview 에는 안 보임).
5. `npx hyperframes lint episodes/<slug>` 와 `npm run render -- <slug> --only sNN --draft` 로 확인하고,
   `ffmpeg -ss <초> -i renders/sNN.mp4 -frames:v 1 /tmp/…png` 로 핵심 순간 프레임을 뽑아 직접 확인한다.
