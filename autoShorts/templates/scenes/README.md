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
