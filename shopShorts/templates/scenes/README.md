# 씬 템플릿 (쇼핑 쇼츠)

`_base.html`(헤더·배경·진행바·자막·고지배너·헬퍼) + 템플릿 조각(`<style>`+`<script>`) = `episodes/<slug>/scenes/sNN.html`

## 3층 구조

화장품·생활용품 쇼츠 상위권의 공통 포맷 (2026-09-22 레퍼런스 분석: 161만·69만·70만 조회 영상).

| 층 | 영역 | 내용 | 소스 |
|---|---|---|---|
| 1층 | 상단 340px | **고정 헤더** — kicker · 굵은 제목 · 권위 배지 | `episode.header` |
| 2층 | 중앙 | 배경 클립/이미지 + 템플릿 콘텐츠 + 자막 | `scenes[].onScreen` |
| 3층 | 하단 | 고지 배너 (제휴·AI생성·기준일) | `episode.disclosure` |

헤더는 **전 씬에 동일하게** 박힌다. 스크롤하다 중간에 들어온 시청자도 주제를 즉시 알게 하는 장치다.
`header.title` 을 비우면 헤더를 렌더하지 않고 `.stage` 가 원래 위치(top 260px)로 올라간다.

```json
"header": { "kicker": "성분 확인법", "title": "이중기능성이라고\n다 같은 거 아닙니다", "badge": "식약처\n기능성" }
```

## 자막

레퍼런스가 한 번에 2~5글자로 끊으므로 `maxChars` 기본값은 **8**이다(autoShorts 는 14).
단, **숫자를 한글로 읽는 낱말이 이어지는 동안에는 14까지 허용**한다 —
"별점은 사점" / "육입니다" 처럼 수치가 두 줄로 쪼개지는 것을 막기 위해서다.

## 공통 `onScreen` 옵션

- `bgVideo: "media/p01-hero.mp4"` — **Higgsfield 클립 배경** (`npm run clips` 산출물). 최우선
- `bgVideoStart: 0` — 클립에서 쓸 시작 지점(초)
- `bgImage: "media/x.png"` — 정지 이미지 배경 (클립이 없을 때. 느린 줌 인이 걸린다)
- `bgDim: 0~1` — 배경 어둡기 (기본 0.6)
- `highlight: ["단어"]` — 자막에서 강조색
- `showCaptions: false` — 자막 끄기
- `card: false` / `cardNote: "…"` — 카드뉴스 제외 / 카드 전용 문구

`bgVideo` 와 `bgImage` 를 함께 주면 `bgVideo` 가 이긴다.
클립은 이미 카메라 무빙이 있으므로 Ken Burns 를 추가로 걸지 않는다.

시간 지정(`…At`, `rows[].at`): 숫자(씬 기준 초) | `"start"` | `"end"` | `"word:키워드"`(나레이션에서 그 단어가 시작되는 순간)

## 템플릿

| template | 용도 | onScreen |
|---|---|---|
| `hook` | 훅/표지 | `title`(줄바꿈 `\n`), `kicker?`, `badge?`, `badgeAt?`, `subtitle?`, `subtitleAt?` |
| `product` | 상품 한 개 소개 | `name`, `brand?`, `price?`, `priceAt?`, `was?`, `priceNote?`, `rating?`, `ratingCount?`, `ratingAt?`, `tag?`, `tagAt?` |
| `spec` | 스펙 표 | `heading?`, `rows: [{label, value, at?}]` |
| `compare` | 2개 비교 | `heading?`, `left:{label,items[]}`, `right:{label,items[]}`, `rightAt?`, `verdict?`, `verdictAt?` |
| `verdict` | 결론 | `call`, `reason?`, `reasonAt?`, `forWho?`, `notFor?` |
| `cta-link` | 링크 유도 | `headline`, `action`, `actionAt?`, `where?`, `handle?` |

씬에 `productId: "p01"` 을 달면 어느 상품 이야기인지 기록된다 (source.json 의 products[].id).

## 고지 배너

전 씬 하단에 `episode.disclosure` 가 상시 렌더된다 — 템플릿이 끄거나 가릴 수 없다.
`.stage` 는 하단 560px 를 비우고, 자막은 bottom 440px 이라 배너와 겹치지 않는다.
