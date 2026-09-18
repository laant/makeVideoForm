# autoShorts — Shorts Factory

레퍼런스 분석 → 대본 → ElevenLabs 음성 → HTML/GSAP 씬 → HyperFrames 렌더 → FFmpeg 합성 → 업로드.
사람은 **레퍼런스 선택 · 대본 확정 · 최종 검수**만 한다. 나머지는 Claude Code + 스크립트.

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
npm run scenes -- <slug> [--force]
npm run render -- <slug> [--only s02] [--draft]
npm run assemble -- <slug>
npm run verify -- <slug>               # 결과: renders/check/contact-sheet.jpg
npm run cards -- <slug> [--only s02]   # 인스타 카드뉴스 1080x1080 → cards/01.png… (자막 없음, 음성 없어도 가능)
npm run preview -- <slug> [--stop]     # HyperFrames Studio (씬 + 나레이션 합본)
npm run upload -- <slug>               # dry-run. 실제 업로드는 --yes (사용자 확인 후에만)
npm run publish -- <프로젝트> --module <모듈> [--title N] [--thumb 1|2|none] [--only youtube|instagram] [--at "YYYY-MM-DD HH:mm"] [--yes] [--again]
                                       # myNextSeason output/ 완성본(모든 모듈판) 배포 — 제목·설명은 titles.txt(★ 기본)
                                       # YouTube 기본 = 업로드 +10분 예약 공개 (YT_SCHEDULE_DELAY_MIN), --privacy 지정 시 예약 없음
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
- HyperFrames 규칙: `Date.now()`/`Math.random()`/네트워크 금지, 타임라인은 `{ paused: true }` 로 `window.__timelines[id]` 등록,
  에셋 경로는 에피소드 폴더 기준(`vendor/…`, `audio/…`, `../` 금지). 문서: `npx hyperframes docs <topic>`.

## 안전
- 업로드는 사용자가 명시적으로 요청했을 때만 `--yes`. YouTube 기본 `private`.
- `upload`·`publish` 는 업로드 전 점검(`scripts/lib/precheck.js`)이 ✗ 면 멈춘다. `--skip-precheck` 는 사용자가 원할 때만.
- 결과 보고는 **실행·확인한 것** / **사람이 확인할 것** 을 나눠 쓴다.
- `.env`, `.secrets/` 내용은 출력하지 않는다.
