# 씬 템플릿

`_base.html`(배경·진행바·자막·헬퍼) + 템플릿 조각(`<style>` + `<script>`) = `episodes/<slug>/scenes/sNN.html`.

모든 템플릿 공통 `onScreen` 옵션
- `highlight: ["단어"]` 자막에서 강조색
- `showCaptions: false` 자막 끄기
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

트랜지션(`transitionOut`): `crossfade` | `white-flash` | `zoom` | `cut` — FFmpeg xfade 로 합성 단계에서 적용.
효과음(`sfx[].name`): `click` `typing` `whoosh` `pop` `chime` `notify` `error` — `assets/sfx/*.wav` (교체 가능).
권장 타이밍: 입력=click/typing, 등장=pop, 장면전환=whoosh, 완료=chime, 알림=notify, 실패/비교의 나쁜 쪽=error.

새 템플릿 추가: 이 폴더에 `<name>.html` 을 만들고 `scripts/lib/episode.js` 의 `TEMPLATE_NAMES` 에 추가.
템플릿 스크립트에서 쓸 수 있는 것: `S`(씬 데이터: words, speechEnd, duration, renderDuration, onScreen), `H`(el/at/spread/type/captions), `tl`, `stage`.
