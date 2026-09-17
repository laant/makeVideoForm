# PRODUCTION — 프로젝트 마스터 문서

> **모든 영상 제작은 이 문서에서 시작한다.** 모듈(flow-pipeline / OpenMontage / talkcraft)은
> 이 문서의 상위주제·연출 템플릿·공통 규칙을 따르는 실행 계층이다.
> 새 프로젝트를 시작할 때: ① 여기서 주제·포맷 확인 → ② 대본 작성(확인 게이트) → ③ 프롬프트 작성(확인 게이트) → ④ 모듈로 내려가 생산.

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
| `talkcraft/` | Remotion 코드 모션그래픽 | 계측선·동기화 100% 결정론 | 엔진 `talkcraft/video-talkcraft/` + 프로젝트 `talkcraft/<이름>/` (demo·gcans·guri·family, ⚠️ 비상업 라이선스 — 실험 전용) |
| `autoShorts/` | HTML/GSAP 템플릿 씬(HyperFrames 렌더) + FFmpeg 합성 | 씬 템플릿 5종·음성 타임스탬프 싱크·자동 검수·인스타 카드뉴스·YT/IG 업로드 | `autoShorts/CLAUDE.md` + 루트 `/shorts-*` 커맨드 (Apache-2.0, 상업 사용 가능) |

- 같은 대본을 여러 모듈로 병렬 제작해 비교하는 것이 기본 실험 방식 (G-Cans 03/04/05가 선례).
- 공용 자원: 폰트 `flow-pipeline/fonts/Pretendard-*.ttf`, PIL venv `OpenMontage/.venv`, TTS(Gemini Aoede = 한국어 네이티브 검증).

## 6. 산출물 위치

**완성본 모음(정본)**: `output/<프로젝트>/<모듈명>_final_send.mp4` — 모듈 깊숙한 원본들을 한곳에 모은 배포·검토용 디렉토리.
새 완성본이 생기면 `scripts/collect_outputs.py`의 MAPPING에 한 줄 추가 후 실행 (idempotent — 소스가 더 새것일 때만 갱신, 30MB 초과 원본은 자동 압축).

**업로드 준비물 — 완성본과 항상 함께 만든다(요청 없어도 자동)**:
- 영상별 썸네일 2장: `<파일명>_thumb1.jpg`(훅 장면) · `<파일명>_thumb2.jpg`(결정 장면). 모듈마다 화면이 달라 영상별.
- 프로젝트별 제목·설명 1파일: `titles.txt` — 숫자 포함형 5 · 질문형 5 · 감정 자극형 5 = 15개(제목 ≤60자, 설명 ≤3000자) + ★바이럴 1순위와 이유·차점. 주제가 같으므로 모듈과 무관하게 프로젝트당 하나.
- **배포(모든 모듈판 공통)**: `cd autoShorts && npm run publish -- <프로젝트> --module <모듈>` — `output/`의 완성본 + titles.txt ★제목 + thumb1로 YouTube Shorts·Instagram Reels 업로드. 기본 dry-run, 실제 업로드 `--yes`는 사용자 요청 시에만. 옵션: `--title N` · `--thumb 2|none` · `--only youtube|instagram` · `--at "YYYY-MM-DD HH:mm"`(YouTube 예약 공개) · `--again`. 기록은 `output/<프로젝트>/publish-log.json`(플랫폼당 1회 — 모듈판 중복 게시 방지). 대상 채널은 `autoShorts/.env` `YT_CHANNEL_HANDLE`(@knowledge-f-financial)과 토큰 채널이 일치해야 진행. OAuth 앱이 '테스트' 상태라 **토큰 7일 만료 → 주 1회 `npm run yt:auth`**(브랜드 채널 선택).
- 인스타 카드뉴스(autoShorts판이 있을 때): `output/<프로젝트>/cards/NN.png` — `npm run cards -- <slug>` 후 `collect_outputs.py`의 CARDS에 한 줄 추가·실행.

모듈 내 원본 위치:
- Flow판: `flow-pipeline/projects/<NN-이름>/out/final.mp4`
- OpenMontage판: `OpenMontage/projects/<이름>/renders/final.mp4`
- talkcraft판: `talkcraft/<이름>/remotion/out/final.mp4`
- autoShorts판: `autoShorts/episodes/<slug>/final.mp4`
- 삭제된 MPT의 과거 완주분: `_archive-mpt/`
