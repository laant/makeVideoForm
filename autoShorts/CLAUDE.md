# autoShorts — Shorts Factory

레퍼런스 분석 → 대본 → ElevenLabs 음성 → HTML/GSAP 씬 → HyperFrames 렌더 → FFmpeg 합성 → 업로드.
사람은 **레퍼런스 선택 · 대본 확정 · 최종 검수**만 한다. 나머지는 Claude Code + 스크립트.

## Codex 제작 기본값 (2026-09-29)

사용자가 선택한 기준은 `episodes/optimal-plan-codex-director/` B안이다. Codex가 대본 기반 이미지 생성과 HTML/CSS/GSAP 장면 연출을 함께 담당하고, 이 모듈은 기존 TTS·렌더·합성·검수를 처리한다. 이미지에는 Codex 내장 이미지 생성기를 우선 사용하며, 아래 `npm run bg` 기본 규칙은 이 사용자 선호보다 우선하지 않는다. 색상·그림체는 주제에 맞춰 설계한다. 상세는 `../docs/PRODUCTION.md`의 '기본 제작 방식 — Codex B안'을 따른다. 실제 게시에는 별도의 사용자 업로드 요청이 필요하다.

## 단일 소스
- `episodes/<slug>/episode.json` 이 대본·씬·효과음·캡션·업로드 설정의 유일한 원본이다. 대화에만 남기지 말고 반드시 여기에 쓴다.
- 스키마: `scripts/lib/episode.js` (zod). 템플릿별 `onScreen` 필드: `templates/scenes/README.md`.
- `timing` 은 `npm run tts` 가 채운다. 손으로 쓰지 않는다.
- 사람이 미리 적은 제작 의도는 `brief`·`reference` 에 있다. 질문하기 전에 먼저 읽고, 채워진 것은 다시 묻지 않는다.

## 명령
```bash
npm run new -- <slug> "주제"          # 에피소드 뼈대 + 입력 페이지(제작 의도를 한 번에 입력)
npm run intake -- <slug>               # 입력 페이지 다시 열기 (episode.json brief/reference, refs/, media/)
npm run make -- <slug> [--mock]        # tts → scenes → render → assemble → verify
npm run tts -- <slug> [--mock|--force] # 바뀐 씬만 ElevenLabs 호출 (해시 캐시)
npm run bg -- <slug> [--dry|--force|--only s02]   # 배경 이미지 생성 (씬 onScreen.bgPrompt + bg.preset, 유료)
npm run bg -- --preview all             # 스타일 프리셋 견본
npm run scenes -- <slug> [--force]
npm run render -- <slug> [--only s02] [--draft]
npm run assemble -- <slug>
npm run verify -- <slug>               # 결과: renders/check/contact-sheet.jpg
npm run cards -- <slug> [--only s02]   # 인스타 카드뉴스 1080x1080 → cards/01.png… (자막 없음, 음성 없어도 가능)
npm run preview -- <slug> [--stop]     # HyperFrames Studio (씬 + 나레이션 합본)
npm run upload -- <slug>               # dry-run. 실제 업로드는 --yes (사용자 확인 후에만)
npm run yt:auth -- --channel finance|tech    # 채널별 토큰 → .secrets/youtube-token.<키>.json (7일 만료 시 해당 채널만)
npm run publish -- <프로젝트> --module <모듈> [--channel finance|tech] [--title N] [--thumb 1|2|none] [--only youtube|instagram] [--at "YYYY-MM-DD HH:mm"] [--yes] [--again]
                                       # myNextSeason output/ 완성본(모든 모듈판) 배포 — 제목·설명은 titles.txt(★ 기본)
                                       # YouTube 기본 = 업로드 +10분 예약 공개 (YT_SCHEDULE_DELAY_MIN), --privacy 지정 시 예약 없음
npm run clip -- <프로젝트> --module <모듈> [--log --url <주소>]  # 네이버 클립 준비(Aside 세션 폴더 복사·300자 설명)·기록 — 폼은 Aside 로 (../docs/naver-clip.md)
```
`--mock` 은 macOS `say` 로 음성을 대신해 크레딧 없이 파이프라인을 점검한다.

## 워크플로 (슬래시 커맨드)
0. `npm run new` 입력 페이지 → 1. `/shorts-new` 킥오프(입력 확인, 빈 곳만 질문) → 2. `/shorts-ref` 레퍼런스 분석 → 3. `/shorts-script` 대본·씬 설계
4. `npm run tts` → `/shorts-voice-check` → 5. `/shorts-scenes` (필요한 씬만 커스텀) → 6. `/shorts-render`

## 대본 규칙
- 레퍼런스의 **구조**(훅 → 전개 → 페이오프 → CTA, 문장 길이, 템포)를 빌리고 문장은 베끼지 않는다.
- 나레이션은 핵심만, 긴 텍스트는 화면(onScreen)으로. 한 씬 = 한 문장(1.5~5초).
- 모든 나레이션 문장에 대해 화면에서 **무엇을 입력/무엇을 하고/무엇이 보이는지**가 정해져 있어야 한다.
- 첫 씬 첫 2초 안에 훅, 훅에서 약속한 것을 영상 안에서 반드시 보여준다(훅-페이오프 정합성).
- **지어내기 금지**: 레퍼런스·brief·제공 자료에 없는 성과·수치·개인 경험·후기를 만들지 않는다. 출처 없는 숫자는 확정 전에 사용자에게 확인.
- 링크·설명란·고정 댓글을 안내하면 `caption` 에 실제 URL 을 넣는다.
- 총 길이 20~45초 권장, 90초 초과 금지. 숫자·영문 약어는 발음대로 풀어 쓴다(예: "GPT" → "지피티").

## 씬 규칙
- 1080×1920, 안전영역: 상단 260px·하단 560px 은 텍스트 금지(플랫폼 UI). 자막은 base 가 처리.
- 템플릿으로 충분하면 episode.json 만 수정한다. 특수 연출이 필요할 때만 `scenes/sNN.html` 을 직접 수정하고
  첫 주석을 `autoshorts:generated …` → `autoshorts:custom` 으로 바꿔 재생성에서 보호한다.
- custom 씬도 `data-duration` 은 `timing.duration`(+ 트랜지션 꼬리) 와 같아야 한다. `npm run render` 가 경고한다.
- 연출 라이브러리: `transitionOut`(20종) · `effects`(화면 효과 19종) · `sfx`(17종) — 표는 `templates/scenes/README.md`, 정의는 `scripts/lib/fx.js`·`scripts/gen-sfx.js`.
  트랜지션·화면 효과는 합성 단계(FFmpeg)에서 적용되어 preview 에는 보이지 않는다.
- 외부 이미지·폰트·음원은 출처·라이선스를 확인하고 에셋 매니페스트로 보고한다.
- 배경 그림은 `npm run bg` 로 만든다(기본 '그림판'). 씬마다 `onScreen.bgPrompt` 에 **재질 없는 피사체 한 줄**만 쓰고,
  스타일은 에피소드 `bg.preset` — 9종(clay·paper·blueprint·glass·isometric·engraving·studio·exploded·riso), 쓰임은 `templates/scenes/README.md`. 스크래치 스크립트로 따로 만들지 않는다.
- HyperFrames 규칙: `Date.now()`/`Math.random()`/네트워크 금지, 타임라인은 `{ paused: true }` 로 `window.__timelines[id]` 등록,
  에셋 경로는 에피소드 폴더 기준(`vendor/…`, `audio/…`, `../` 금지). 문서: `npx hyperframes docs <topic>`.

## 안전
- 업로드는 사용자가 명시적으로 요청했을 때만 `--yes`. YouTube 기본 `private`.
- YouTube 채널은 셋이다 — `finance`(@knowledge-f-financial, 재테크·생활정보, 기본) / `tech`(@upup__tech, 테크 상식) /
  `personal`(사용자 계정 기본 채널 — 그 외 영상: 건축쇼츠·개인 프로젝트 등). **업로드 전 어느 채널인지 정하고 `--channel` 을 명시한다.**
  `.env` `YT_CHANNEL_<키>`(@핸들 또는 UC… ID), 토큰은 채널별 파일. 인증 때 다른 채널을 고르면 저장하지 않고, 업로드 때 토큰 채널이 다르면 멈춘다.
  새 채널 키는 `npm run yt:auth -- --channel <새키>` 한 번이면 고른 채널이 `.env` 에 자동 등록된다(이미 다른 키로 등록된 채널은 거부).
- `upload`·`publish` 는 업로드 전 점검(`scripts/lib/precheck.js`)이 ✗ 면 멈춘다. `--skip-precheck` 는 사용자가 원할 때만.
- 결과 보고는 **실행·확인한 것** / **사람이 확인할 것** 을 나눠 쓴다.
- `.env`, `.secrets/` 내용은 출력하지 않는다.


## 2026-10-02 사용자 음성 교정 — 이전 선희 설정보다 우선
- 사용자는 S12 쇼츠의 Microsoft Edge 선희 음성을 거부하고 “음성은 원래 autoshorts에 있는 방식으로해줘 … 다음에도 아예넣지말자”라고 요청했다. 이후 해당 제작 흐름에서 Edge TTS/선희를 사용하지 않는다. 모든 내레이션 제거 요청은 아니다.
- 기존 요금제 기준작 `optimal-plan-codex-director`의 실제 음성 설정을 따른다: `provider=gemini`, `modelId=gemini-3.1-flash-tts-preview`, `voiceId=Aoede`, `prompt=""`. `scripts/tts.js`의 Gemini 생성·Whisper 단어 정렬을 사용하며 다른 음성으로 임의 대체하지 않는다.
- 음성 교체 시 실제 새 타이밍으로 자막·장면·효과음을 재조정하고 원본 영상·음성을 보존한다. 공급자 오류/권한 거절/추가 결제·구독·새 자격증명이 필요하면 해당 단계만 중단하고 알린다.

- 같은 날 추가 피드백: 음성대본도 딱딱하다고 거부했다. 기존 요금제 B안의 짧은 구어체·상황 중심·기대→조건→확인 행동 흐름을 따른다. 사양 수치의 연속 낭독은 줄이고 상세 수치는 화면에 배치한다.
