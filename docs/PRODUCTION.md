# PRODUCTION — 프로젝트 마스터 문서

> **모든 영상 제작은 이 문서에서 시작한다.** 모듈(flow-pipeline / OpenMontage / talkcraft)은
> 이 문서의 상위주제·연출 템플릿·공통 규칙을 따르는 실행 계층이다.
> 새 프로젝트를 시작할 때: ① 여기서 주제·포맷 확인 → ② 대본 작성(확인 게이트) → ③ 프롬프트 작성(확인 게이트) → ④ 모듈로 내려가 생산.

## 기본 제작 방식 — Codex B안 (2026-09-29 사용자 선택)

사용자는 14번 `optimal-plan-codex-director` B안을 선호하며, 앞으로 Codex에 영상 제작을 맡기면 이 방식을 기본으로 진행하도록 요청했다.

- Codex가 대본 의미에 맞춰 이미지 콘셉트·프롬프트·장면 구성·타이포그래피·동작을 함께 설계한다. 고정 그림체나 B안의 녹색 팔레트를 모든 주제에 복제하라는 의미는 아니다.
- 이미지 제작은 Codex 내장 이미지 생성기를 기본으로 사용한다. 기존 Google 이미지 생성 스크립트/프리셋은 사용자가 지정할 때 선택한다. Flow 생성 영상은 별도 경로다.
- autoShorts의 HTML/CSS/GSAP 커스텀 씬을 작성하고, 단어별 타임스탬프에 맞춰 핵심 정보와 강조를 연출한다. 템플릿은 적합할 때 활용하되 배경 교체만으로 끝내지 않는다.
- 기존 TTS·타이밍·효과음·HyperFrames 렌더·FFmpeg 합성·자동 검수를 활용한다. 장면별 이미지를 직접 확인하고 구도·가독성·싱크 문제를 고친 뒤 납품한다.
- 기존 대본과 음성이 승인되어 있으면 재활용한다. 원본은 보존하고, 이미지·최종 생성 프롬프트·커스텀 씬·완성 영상·검수 결과를 프로젝트에 저장한다.
- 이 선호는 제작 방식에 관한 지시이며 상시 업로드 권한을 뜻하지 않는다. 실제 업로드/예약 게시는 사용자의 해당 요청에 따라 기존 채널 인증과 게시 이력 확인 절차로 진행한다.

## 1. 상위주제 (채널 축)

| 축 | 컨셉 | 상태 |
|---|---|---|
| A. 생활 머니 정보 | "모르면 손해 보는 돈" — 환급금·지원금·절약·세금. RPM 높음 + 검색 수요 | 1호 "숨은 보험금 10조" 완주 (4모듈 실증) |
| B. 건축쇼츠 | 반전·문제-해결 서사가 있는 건축물/인프라. 3D 인포그래픽 문법 | **현재 주력 실험.** 3~5호 "도쿄 G-Cans" 3모듈 비교 완료 |

- B축 요청 프로토콜: 사용자가 "서사 있는 건축물 후보 제시해줘" → 후보 제안(`topics/archi-candidates.md`) → 선택 → 레퍼런스 구조 대본.
- 후보 선정 기준: 대중적 인지도 + 의외의 사실(상식 파괴 훅) + 문제→해결→새 문제 핑퐁 + 단면도/미니어처로 그려질 내부 구조.

## 2. 대본 규칙 (공통)

상세: [shorts-guidelines.md](shorts-guidelines.md) (질문형 훅 금지·자막 20자·미완결 엔딩·양자택일 CTA·루프 구조·15초 궁금증·30초 반전)

건축쇼츠 추가 3요소 (레퍼런스: 한강 수중보 570만뷰 분석):
1. **상식 파괴 훅** — 당연한 상식을 재정의하는 단정문으로 시작
2. **문제→해결→새 문제→해결 핑퐁** — 해결이 다음 문제를 낳는 전개
3. **구체적 숫자** — 수치·연도를 곳곳에 배치, 발화 시점에 화면 표기 (검증 필수: 대본 확정 전 웹 팩트체크)

TTS·표기 공통 규칙: 숫자는 한글 표기("오십 미터"), AI 생성 화면 안에 텍스트·숫자 금지(한글 깨짐 — 수치는 렌더러 오버레이가 담당).

## 3. 연출 프롬프트 (템플릿)

| 템플릿 | 용도 | 파일 |
|---|---|---|
| **건축쇼츠 아키비즈** (주력) | semi-stylized 3D 렌더 + 빨간 계측선 + 카메라 비트 규칙 | [templates/archi-shorts-prompt-template.md](templates/archi-shorts-prompt-template.md) |
| 기본형 (2호 방식) | 실사풍 컷별 프롬프트 + 그림체 문장 verbatim 반복 | 2호 `flow-pipeline/projects/02-country-house-reno/prompts.md` 참조 |
| 회색 찰흙 3D (설명컷) | 모노크롬 클레이 설명 컷 | 1호 `flow-pipeline/projects/01-hidden-insurance/cuts.json`의 `3d` 접미사 |

건축쇼츠 템플릿 핵심 규칙 (상세는 템플릿 문서):
- 구조·어휘·길이를 템플릿과 동일하게, 내용만 대본에 맞춤
- 카메라: 8초 비트 2개까지 — 사건 중 횡이동만, 끝나면 급속 푸시인 클로즈업. 설명 구간(시작·끝 제외)은 멀티샷(3샷 하드컷)
- **계측선(빨강)은 대본에 명확한 수치가 있는 컷에만.** 보조선 고정/이동 매번 명시. 빨간 소품 컷엔 계측선 금지
- 납품 형식: 한국어 설명 + 영문 코드블록 + 설정 표 + 글자수 + 충돌 위험도
- 일관성: 그림체 문장·장소 고정 문장은 전 컷 토씨 불변

## 4. 확인 게이트 (필수 프로세스)

1. **대본** (컷별 나레이션·구성 + 숫자 검증) → **사용자 확인**
2. **컷별 프롬프트** (템플릿 적용) → **사용자 확인**
3. 생성→다운로드→더빙→조립 → 자동 진행

수정 사항은 메모리 `shorts-approval-workflow` 학습 로그에 축적. 몇 회 무수정 후 게이트 제거 제안 가능.

## 5. 모듈 역할 (실행 계층)

| 모듈 | 문법 | 강점 | 진입점 |
|---|---|---|---|
| `flow-pipeline/` | Veo 생성형 영상 (Aside 자동화) | 진짜 카메라 무빙·물 시뮬 | `flow-pipeline/RUNBOOK.md` |
| `OpenMontage/` | Gemini 3D 스틸 + Ken Burns + 데이터 오버레이 | 무결 원샷·계측선 정확·stat_card | `OpenMontage/projects/tokyo-gcans-archi/produce.py` 패턴 |
| `talkcraft/` | Remotion 코드 모션그래픽 | **동결 (2026-09-23)** — PolyForm Noncommercial 이라 수익화용 불가. 공통 카드 4종은 autoShorts 로 이식 완료. 과거 프로젝트 재렌더용으로만 보존 | `talkcraft/README.md` |
| `autoShorts/` | HTML/GSAP 템플릿 씬(HyperFrames 렌더) + FFmpeg 합성 | 씬 템플릿 5종·연출 라이브러리(트랜지션 20·화면 효과 19·효과음 17)·음성 타임스탬프 싱크·자동 검수(머리·꼬리 잘림·자리표시자)·업로드 전 점검(링크·URL)·인스타 카드뉴스·YT/IG 업로드 | `autoShorts/CLAUDE.md` + 루트 `/shorts-*` 커맨드 (Apache-2.0, 상업 사용 가능) |
| `shopShorts/` | 상품 이미지 → Higgsfield image-to-video 클립 + 텍스트 오버레이 | 상품 페이지 수집(Aside)·고지 자동 강제(빠지면 빌드 중단)·실사용 주장 차단·리워드 링크 검증 | `shopShorts/CLAUDE.md` (a 제휴리뷰 / b 큐레이션 / c 단일홍보) |

- 같은 대본을 여러 모듈로 병렬 제작해 비교하는 것이 기본 실험 방식 (G-Cans 03/04/05가 선례).
- **autoShorts는 기본으로 '그림판'** (2026-09-18 사용자 지시): OpenMontage판이 함께 제작되면 그 이미지를 `onScreen.bgImage`로 깔고, 태극기처럼 AI가 틀리는 대상은 코드(`H.taegukgi()` 등)로 그린다. 글자 카드판은 사용자가 따로 요청할 때만. 그림이 필요 없는 경우는 사용자가 별도로 말한다.
- **렌더 런타임은 HyperFrames(Apache-2.0)로 통일한다.** autoShorts·shopShorts 는 전면, OpenMontage 는
  `render_runtime = "hyperframes"` 로 선택 가능(Phase 1). 단어 단위 자막 번인·아바타 립싱크는
  아직 Remotion 전용이므로 그때만 예외 — `OpenMontage/skills/core/hyperframes.md` 의 결정 매트릭스를 따른다.
- 공용 자원: 폰트 `flow-pipeline/fonts/Pretendard-*.ttf`, PIL venv `OpenMontage/.venv`, TTS(Gemini Aoede = 한국어 네이티브 검증).

## 6. 산출물 위치

**완성본 모음(정본)**: `output/<프로젝트>/<모듈명>_final_send.mp4` — 모듈 깊숙한 원본들을 한곳에 모은 배포·검토용 디렉토리.
새 완성본이 생기면 `scripts/collect_outputs.py`의 MAPPING에 한 줄 추가 후 실행 (idempotent — 소스가 더 새것일 때만 갱신, 30MB 초과 원본은 자동 압축).

**업로드 준비물 — 완성본과 항상 함께 만든다(요청 없어도 자동)**:
- 영상별 썸네일 2장: `<파일명>_thumb1.jpg`(훅 장면) · `<파일명>_thumb2.jpg`(결정 장면). 모듈마다 화면이 달라 영상별.
- 프로젝트별 제목·설명 1파일: `titles.txt` — 숫자 포함형 5 · 질문형 5 · 감정 자극형 5 = 15개(제목 ≤60자, 설명 ≤3000자) + ★바이럴 1순위와 이유·차점. 주제가 같으므로 모듈과 무관하게 프로젝트당 하나.
- **배포(모든 모듈판 공통)**: `cd autoShorts && npm run publish -- <프로젝트> --module <모듈>` — `output/`의 완성본 + titles.txt ★제목 + thumb1로 YouTube Shorts·Instagram Reels 업로드. 기본 dry-run, 실제 업로드 `--yes`는 사용자 요청 시에만. 옵션: `--title N` · `--thumb 2|none` · `--only youtube|instagram` · **YouTube는 기본으로 업로드 시점 +10분 예약 공개**(`.env` `YT_SCHEDULE_DELAY_MIN`) · `--at "YYYY-MM-DD HH:mm"`(예약 시각 지정) · `--privacy private|unlisted|public`(예약 없이 즉시) · `--again`. 기록은 `output/<프로젝트>/publish-log.json`(플랫폼당 1회 — 모듈판 중복 게시 방지). **채널은 `--channel finance|tech|personal`** — finance=@knowledge-f-financial(재테크·생활정보, 기본) · tech=@upup__tech(테크 상식) · personal=사용자 계정 기본 채널(그 외 — 건축쇼츠·개인 등). 토큰은 채널별 파일(`autoShorts/.secrets/youtube-token.<키>.json`)이라 서로 덮어쓰지 않고, 토큰 채널이 `YT_CHANNEL_<키>`와 다르면 멈춘다. OAuth 앱이 '테스트' 상태라 **토큰 7일 만료 → `npm run yt:auth -- --channel <키>`**(만료된 채널만).
- **네이버 클립**(@some____uuuu): 공개 API 없음 → `npm run clip -- <프로젝트> --module <모듈>`로 준비 후 Claude 가 Aside 브라우저로 clipcreators 폼 입력. 제목 칸 없이 설명 300자 · 쇼핑커넥트 태그 1개 · 내 블로그 글 링크 · 등록=즉시 공개(요청 시만). 절차 `docs/naver-clip.md`.
- 인스타 카드뉴스(autoShorts판이 있을 때): `output/<프로젝트>/cards/NN.png` — `npm run cards -- <slug>` 후 `collect_outputs.py`의 CARDS에 한 줄 추가·실행.

모듈 내 원본 위치:
- Flow판: `flow-pipeline/projects/<NN-이름>/out/final.mp4`
- OpenMontage판: `OpenMontage/projects/<이름>/renders/final.mp4`
- talkcraft판: `talkcraft/<이름>/remotion/out/final.mp4`
- autoShorts판: `autoShorts/episodes/<slug>/final.mp4`
- 삭제된 MPT의 과거 완주분: `_archive-mpt/`


## 2026-10-02 사용자 음성 교정 — 이전 선희 설정보다 우선
- 사용자는 S12 쇼츠의 Microsoft Edge 선희 음성을 거부하고 “음성은 원래 autoshorts에 있는 방식으로해줘 … 다음에도 아예넣지말자”라고 요청했다. 이후 해당 제작 흐름에서 Edge TTS/선희를 사용하지 않는다. 모든 내레이션 제거 요청은 아니다.
- 기존 요금제 기준작 `optimal-plan-codex-director`의 실제 음성 설정을 따른다: `provider=gemini`, `modelId=gemini-3.1-flash-tts-preview`, `voiceId=Aoede`, `prompt=""`. `scripts/tts.js`의 Gemini 생성·Whisper 단어 정렬을 사용하며 다른 음성으로 임의 대체하지 않는다.
- 음성 교체 시 실제 새 타이밍으로 자막·장면·효과음을 재조정하고 원본 영상·음성을 보존한다. 공급자 오류/권한 거절/추가 결제·구독·새 자격증명이 필요하면 해당 단계만 중단하고 알린다.
