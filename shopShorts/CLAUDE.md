# shopShorts — 쇼핑 쇼츠 모듈 (모듈⑤)

상위 규칙은 `../docs/PRODUCTION.md`. 이 모듈은 **autoShorts 와 완전히 분리**되어 있다.
autoShorts 의 파일은 어떤 경우에도 수정하지 않는다 (패턴만 가져왔다).

## 타입

| 타입 | 입력 | 흐름 |
|---|---|---|
| **a** 제휴 리뷰형 | 상품 URL + 리워드 링크 | 훅 → 스펙 정리 → 장단점 → 결론 → 링크 |
| **b** 정보형 큐레이션 | 주제 | 훅 → N선 순차 → 비교 → 결론 |
| **c** 단일 상품 홍보 | 상품 URL + 리워드 링크 | 훅 → 핵심 기능 → 가격 → 링크 |

## 파이프라인

```
npm run new -- <slug> <a|b|c> "주제"   # 폴더 + source.json/episode.json 뼈대
  ↓ ① 상품 수집 (Claude 가 Aside 로 수행) → source.json
  ↓ ② 기획안 작성 → PLAN.md            # ★ 사용자 확인 게이트 1
  ↓ ③ 대본·씬 확정 → episode.json scenes
npm run clips -- <slug> --dry          # ④ 필요한 클립만 확인 (API 호출 없음, 무료)
npm run clips -- <slug>                # ⑤ Higgsfield i2v 생성 (유료)  ★ 확인 게이트 2
npm run make -- <slug>                 # tts → scenes → render → assemble → verify
npm run cards -- <slug>                # 인스타 카드뉴스 (선택)
```

**순서를 지킬 것 — 클립 생성은 대본 뒤다.** 어떤 컷이 필요한지 정해지기 전에 생성하면
쓰지 않을 클립에 돈을 쓰거나, 정작 필요한 컷이 없어 다시 돌리게 된다.
씬마다 어떤 이미지를 어떤 카메라 모션으로 움직일지는 대본이 결정한다.

## 상품 수집 — Aside 브라우저 자동화

쿠팡·네이버는 봇 차단이 강하므로 **단순 HTTP 페치를 쓰지 않는다.** 사용자의 로그인된 Chrome 을
Aside MCP 로 몰아서 실제 페이지를 연 뒤 읽는다 (flow-pipeline/RUNBOOK.md 와 같은 방식).

수집해서 `source.json` 에 기록할 것:
- `name` `brand` `url` — 상품 페이지 원본 URL 은 출처로 반드시 보존
- `price.current` / `price.original` / `price.note` — 쿠폰가·할인 조건을 note 에
- `rating.score` `rating.count`
- `specs[]` — 화면에 그대로 뜨는 label/value. 페이지에 없는 값은 만들지 않는다
- `pros[]` `cons[]` — 판매 페이지와 리뷰에서 근거가 있는 것만
- `reviewThemes[]` — 반복되는 구매자 언급의 **요약**. 리뷰 원문을 그대로 옮기지 않는다
- `images[]` — **공개 이미지 URL 그대로**. Higgsfield 는 공개 URL 만 받고 base64·업로드를 지원하지 않는다
  - `role`: `hero`(대표) `detail`(디테일) `scale`(크기감) `usage`(사용장면) `package`(패키지)
- `collectedAt` — 수집 날짜. 고지의 기준일로 그대로 쓰인다

**source.json 에 없는 수치는 대본에 쓰지 않는다.** 가격·스펙을 기억이나 추정으로 채우지 않는다.

## 프레이밍 — 실사용 주장 금지

실제로 써보지 않았으므로 **후기 어법을 쓰지 않는다.** `verify` 가 자동으로 잡는다.

- 금지: "써봤" "사용해봤" "직접 써" "제가 쓰는" "실제로 써" "착용해봤" "먹어봤" "테스트해봤"
- 대신: "정리했습니다" "스펙상" "판매 페이지 기준" "구매자 리뷰에서 자주 나오는 말은"

## 3층 구조 (`header` / 본문 / `disclosure`)

상단 고정 헤더는 **필수로 채운다.** 레퍼런스 상위권(161만·69만·70만)의 공통 포맷이고,
중간 유입 시청자에게 주제를 즉시 전달하는 장치다. 권위 배지(`badge`)는 전문가 화자가 없는
우리 채널이 쓸 수 있는 유일한 권위 장치이므로 **제도적 사실**로 채운다 (예: "식약처 기능성").
상세는 `templates/scenes/README.md`.

**길이: 화장품·생활용품 카테고리는 20~30초.** 상위권 실측이 15.2초·23.8초·35.7초·36.8초였다.
`docs/shorts-guidelines.md` 의 45초는 일반 정보성 기준이므로 이 모듈에서는 따르지 않는다.

## 고지 (`disclosure`) — 비우면 빌드가 막힌다

`build-scenes` 와 `verify` 양쪽에서 강제한다.

| 필드 | 필수 조건 |
|---|---|
| `affiliate` | 리워드 링크가 있으면 (a·c 는 항상) |
| `aiGenerated` | `bgVideo` 클립을 쓰면 |
| `source` | 항상 — "가격·스펙은 YYYY-MM-DD 기준" |

세 줄이 조합되어 **전 씬 하단에 상시 배너**로 찍힌다 (autoShorts 는 카드에만 찍혔다 — 여기가 다르다).
`links[]` 의 URL 은 `caption` 에도 들어가야 verify 를 통과한다.

## Higgsfield 클립 (`npm run clips`)

`scripts/lib/higgsfield.js` 에 실측 규격이 들어 있다. **OpenMontage 의 `higgsfield_video.py` 는 틀렸다**
(인증 헤더·엔드포인트·모델명·페이로드 전부). 그 툴을 쓰지 말고 이 라이브러리를 쓴다.

- 엔드포인트: `POST /v1/image2video` → `GET /v1/job-sets/{id}`, 헤더 `hf-api-key` + `hf-secret`
- 모델: `dop-lite` / `dop-turbo` / `dop-preview` — text-to-video 는 **존재하지 않는다**
- 기본값(`SAFE_DEFAULTS`): 약한 모션(strength 0.35) + `enhance_prompt: false`
  - 2026-09-21 실측: strength 1.0 + enhance_prompt 자동 적용 시 5초 클립 뒤 1/3에서 피사체가 다른 물건으로 변형됐다.
    **쇼핑은 상품이 바뀌면 못 쓴다.** strength 를 함부로 올리지 않는다.
- 생성 후 반드시 **마지막 프레임을 눈으로 확인**한다. 상품 형태·색·로고가 원본과 다르면 버린다.
- `media/clips.json` 에 jobSetId·seed·프롬프트가 남는다 (멱등 — 재실행해도 재생성하지 않는다)

## 확인 게이트

`../docs/PRODUCTION.md` 와 동일하게 **대본 → 사용자 확인**, **클립 → 사용자 확인** 후에 자동 진행한다.
`npm run clips` 는 유료이므로 `--dry` 로 대상 수를 먼저 보고한 뒤 실행한다.
