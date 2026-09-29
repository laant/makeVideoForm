# 씬 템플릿

`_base.html`(배경·진행바·자막·헬퍼) + 템플릿 조각(`<style>` + `<script>`) = `episodes/<slug>/scenes/sNN.html`.

모든 템플릿 공통 `onScreen` 옵션
- `highlight: ["단어"]` 자막에서 강조색
- `showCaptions: false` 자막 끄기
- `bgImage: "media/x.png"` 배경 그림(에피소드 `media/` 기준, 느린 줌 인 + 가독성 그라데이션), `bgDim: 0~1` 어둡기(기본 0.6). 카드뉴스에는 적용 안 됨
- `card: false` 카드뉴스(`npm run cards`)에서 제외, `cardNote: "…"` 카드에만 보충 문구 추가
  (카드 하단 공통 문구는 episode.json `cards.footer`)

시간 지정(`…At`, list `items[].at`, `sfx[].at`): 숫자(씬 기준 초) | `"start"` | `"end"` | `"word:키워드"`(나레이션에서 해당 단어가 시작되는 순간)

| template | 용도 | onScreen |
|---|---|---|
| `title` | 훅/표지 | `title`(줄바꿈 `\n`), `kicker?`, `subtitle?`, `subtitleAt?`, `emoji?` |
| `compare` | 비교 | `heading?`, `left:{label,items[]}`, `right:{label,items[]}`, `rightAt?`, `verdict?`, `verdictAt?` |
| `list` | 목록 | `heading`, `items: ["텍스트" \| {text, at}]` |
| `demo` | 입력→결과 시연 | `app?`, `heading?`, `input`, `inputAt?`, `output: "…" \| ["줄"]`, `outputAt?` |
| `cta` | 행동 유도 | `headline`, `action`, `actionAt?`, `handle?`, `emoji?` |

## 배경 이미지 생성 — `npm run bg` (2026-09-29)

씬에 `onScreen.bgPrompt`(**피사체 한 줄, 영어**)를 적고 `npm run bg -- <slug>` 를 돌리면
`media/bg-sNN.png` 를 만들고 `bgImage`·`bgDim` 까지 채운다. 스타일은 에피소드의 `bg.preset`.

```json
"bg": { "preset": "clay", "layout": "plate" },            // 에피소드
"onScreen": { "bgPrompt": "a single round coin standing on its edge on the floor" }   // 씬
```

| preset | 느낌 | 쓰임 | 확인 |
|---|---|---|---|
| `clay` (기본) | 찰흙 3D · 어두운 스튜디오 | 재테크 기본 | 09·11~14번 |
| `paper` | 페이퍼 콜라주 · 팝업북 | 따뜻한 이야기·생활 | 04번 |
| `blueprint` | 청사진 선도면 · 격자 | 테크 기본 | 견본 |
| `glass` | 반투명 유리 3D | 미래·AI·핀테크 | 견본 |
| `isometric` | 플랫 아이소메트릭 일러스트 | 재테크·테크 공용 — 앱·서비스 | 14번 비교판 |
| `engraving` | 신문 판화 · 스티플·해칭 | 재테크 — 제도·법·시황 | 14번 비교판 |
| `studio` | 키노트풍 제품 렌더 · 반사 바닥 | 테크 — 신제품 (가장 차분) | 14번 비교판 |
| `exploded` | 분해도 · 부품이 떠 있는 3D | 테크 — 구조·작동 원리 | 14번 비교판 |
| `riso` | 리소그래프 2도 인쇄 질감 | 가벼운 생활정보 (가장 거침) | 14번 비교판 |

같은 대본(14번)을 9종 중 6종으로 만든 비교 영상: `output/14-optimal-plan/_style-compare/compare_all6.mp4`
(clay·isometric·engraving·studio·exploded·riso 동기 재생). 변형 에피소드는 `episodes/optimal-plan-<preset>/`.
체감 차이 크기: engraving ≈ exploded > riso > isometric > studio ≈ clay.

- 프롬프트 = `style + SUBJECT + layout + accent + prohibit` (`templates/bg-presets.json`). 피사체 말고는 전부 고정이라 분위기가 통일된다
- **`bgPrompt` 에 재질(clay·paper·glass…)을 쓰지 않는다** — 재질은 프리셋이 정한다. 피사체에 재질을 쓰면 프리셋을 이긴다(glass 견본이 찰흙으로 나온 원인)
- 글자·숫자는 금지 블록으로 막혀 있다. 숫자·한글은 템플릿이 코드로 그린다
- 림라이트 색은 `theme.accent` 에서 자동(`bg.accent` 로 덮어쓰기). `layout`: `plate`(글 뒤 배경판, 기본) / `hero`(피사체 크게)
- 견본 비교: `npm run bg -- --preview all` → `.cache/bg-previews/`
- 유료라 `make` 에 넣지 않았다. 이미 있는 파일은 건너뛴다(`--force` 로 재생성, `--only sNN`, `--dry`)
- 사용 프롬프트는 `refs/bg_manifest.json` 에 남는다

## 모션 어휘 (talkcraft 이식, 2026-09-23)

talkcraft(Remotion, PolyForm Noncommercial)의 공통 카드 4종을 HyperFrames 로 이식한 것.
**원본 타임테이블·이징을 그대로 옮겼다** — talkcraft 의 `power2Out/power3Out/backOut` 은
GSAP 의 `power2.out/power3.out/back.out()` 과 정확히 같은 곡선이라 변환이 1:1이다.
이식 근거와 lint 결과는 `../../../talkcraft/README.md` 참조.

| template | 용도 | onScreen |
|---|---|---|
| `number-slab-pop` | 결론감 있는 숫자 한 방 | `value`, `unit?`, `caption?`, `at?` |
| `number-counter` | 숫자가 굴러 올라가 착지 | `target`, `decimals?`, `label?`, `unit?`, `suffix?`, `caption?`, `at?`, `countDur?`, `instant?` |
| `alt-block-lines` | 색블록이 글자를 쓸어내는 대구 | `title?`, `rows: [{text, at?, accent?}]` |
| `strike-and-replace` | "A가 아니라 B" 정정 | `prefix?`, `from`, `to`, `suffix?`, `strikeAt?`, `swapDelay?`, `keepStrike?`, `subline?`, `sublineDelay?` |

- `at` 류는 다른 템플릿과 같이 `"word:키워드"` 앵커를 받는다. talkcraft 는 이 값을 손으로 주입했지만
  여기서는 `H.at()` 이 나레이션 타임스탬프에서 바로 계산한다.
- `number-counter` 의 카운트는 1~1.5초가 원칙이다(원본 주석: 2초 넘으면 시청자가 이미 문장을 다 들었다).
- `strike-and-replace` 는 새 값이 옛 값과 **같은 자리**에 들어오므로 취소선이 옛 값과 함께 사라진다(원본 거동 그대로).
  이식 초기에 이걸 '버그'로 보고 취소선을 남기게 바꿨다가, 새 값 위에 선이 그어져 의미가 뒤집히는 것을 14번에서 확인하고 되돌렸다.
  `keepStrike: true` 는 옛 값·새 값을 겹치지 않게 배치할 때만 쓴다.

## 연출 라이브러리 (Shorts Factory 가이드 16 트랜지션 · 18 화면 효과 · 17 효과음)

모두 FFmpeg 로 합성 단계(`npm run assemble`)에서 적용 — 결정적(시드 고정). HyperFrames preview 에는 트랜지션·화면 효과가 보이지 않는다.
목록의 원본은 `scripts/lib/fx.js`(트랜지션·효과), `scripts/gen-sfx.js`(효과음).

### 트랜지션 — 씬의 `transitionOut` (길이 `episode.transitionSeconds`, 기본 0.3s)

| 이름 | 가이드 항목 | 용도 |
|---|---|---|
| `cut` | (추가) | 하드 컷 (겹침 없음) |
| `crossfade` | 크로스페이드 | 크로스페이드 — 기본 |
| `white-flash` | 화이트 플래시 | 화이트 플래시 — 강조·반전 |
| `black-flash` | (추가) | 블랙 페이드 — 챕터 전환 |
| `rgb-split` | 색 채널 분리 | 색 채널 분리 — 글리치·테크 느낌 |
| `iris` | 원형 아이리스 | 원형 아이리스 — 결과 공개 |
| `glitch` | 글리치 | 디지털 글리치 — 오류·반전 |
| `light-leak` | 라이트 릭 | 라이트 릭 — 감성·회상 |
| `cross-warp` | 크로스 왜곡 | 크로스 왜곡 |
| `morph` | 모핑 (근사) | 모핑(픽셀 디졸브 근사) |
| `whoosh-left` | 휙 팬 | 휙 팬 ← (whoosh 효과음과 함께) |
| `whoosh-right` | 휙 팬 | 휙 팬 → |
| `slide-up` | (추가) | 위로 밀기 — 목록·다음 항목 |
| `zoom` | 시네마틱 줌 | 시네마틱 줌 인 |
| `gravity-lens` | 그래비티 렌즈 | 그래비티 렌즈 — 핀치 |
| `ripple` | 물결 | 물결 — 부드러운 전환 |
| `vortex` | 소용돌이 | 소용돌이 |
| `heat` | 열 왜곡 | 열 왜곡 — 아지랑이 |
| `noise-warp` | 노이즈 공간 왜곡 | 노이즈 공간 왜곡 |
| `burn` | 번 | 번 — 타들어가는 전환 |

### 화면 효과 — 씬의 `effects: ["scanlines", "vignette"]` (씬 전체, 순서대로)

| 이름 | 용도 |
|---|---|
| `blur` | 블러 — 배경화·포커스 아웃 |
| `mosaic` | 모자이크 |
| `color-bleed` | 컬러 번짐 — 아날로그 |
| `tape-damage` | VHS 테이프 손상 |
| `film-dust` | 필름 먼지·그레인 |
| `film-damage` | 낡은 필름 — 회상 |
| `halftone` | 하프톤 망점 |
| `duotone` | 듀오톤 인쇄 (네이비→옐로) |
| `dither` | 디더링 (2x2 Bayer) |
| `light-flare` | 라이트 플레어 |
| `monochrome` | 흑백 |
| `scanlines` | 스캔라인 |
| `chromatic-aberration` | 색수차 |
| `crt` | CRT 곡면 모니터 |
| `digital-glitch` | 디지털 글리치 |
| `woodblock` | 목판화 근사 (윤곽+포스터화) |
| `cross-hatch` | 크로스 해칭 펜화 |
| `painterly` | 회화풍 근사 |
| `vignette` | 비네트 — 시선 집중 |

가이드의 **ASCII** 효과는 미지원(문자 렌더링 필요). woodblock·painterly·morph 는 근사 구현.

### 효과음 — 씬의 `sfx: [{ name, at, volume }]` (`assets/sfx/<name>.wav`, `npm run sfx` 로 생성·같은 이름 wav 로 교체 가능)

| 이름 | 소리 | 추천 타이밍 |
|---|---|---|
| `click` | 클릭 | 버튼·선택 |
| `key` | 키 한 번 | 한 글자 입력 |
| `typing` | 연속 타이핑 | 입력 장면 |
| `whoosh` | 짧은 휙 | 장면 전환·등장 |
| `whoosh-long` | 긴 휙 | 큰 전환·팬 |
| `impact` | 임팩트 | 숫자·결론 쾅 |
| `impact-deep` | 깊은 임팩트 | 훅·반전 |
| `tone` | 고음 톤 | 강조·주의 |
| `pop` | 팝 | 요소 등장 |
| `ping` | 핑 | 체크·포인트 |
| `notify` | 알림 | 알림·CTA |
| `chime` | 완료 차임 | 완료·결과 |
| `sparkle` | 반짝 | 좋은 결과·보상 |
| `error` | 에러 비프 | 실패·나쁜 쪽 |
| `glitch` | 글리치 1 | 오류·글리치 전환 |
| `glitch-2` | 글리치 2 (노이즈) | 잡음·끊김 |
| `glitch-3` | 글리치 3 (하강) | 다운·종료 |

새 템플릿 추가: 이 폴더에 `<name>.html` 을 만들고 `scripts/lib/episode.js` 의 `TEMPLATE_NAMES` 에 추가.
템플릿 스크립트에서 쓸 수 있는 것: `S`(씬 데이터: words, speechEnd, duration, renderDuration, onScreen), `H`(el/at/spread/type/captions), `tl`, `stage`.
