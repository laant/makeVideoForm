# myNextSeason

얼굴·카메라 없이 AI 파이프라인으로 영상(유튜브 쇼츠 + 개인 프로젝트)을 기획·제작·수집하는 작업장.
2026-09-01 시작.

> **모든 제작의 시작점: [`docs/PRODUCTION.md`](docs/PRODUCTION.md)** · **새 머신 복원: [`docs/SETUP.md`](docs/SETUP.md)** (`bash scripts/bootstrap.sh`) — 상위주제, 대본 규칙, 연출 프롬프트 템플릿,
> 확인 게이트(대본 확인 → 프롬프트 확인 → 자동 생산), 모듈 역할이 정의된 마스터 문서.

## 디렉토리 구조

```
myNextSeason/
├── docs/                    # ★ 상위 계층 (여기서 시작)
│   ├── PRODUCTION.md        #   마스터 문서
│   ├── shorts-guidelines.md #   대본 작성·검수 룰 (훅·리텐션·CTA·자막)
│   ├── templates/           #   연출 프롬프트 템플릿 (건축쇼츠 아키비즈 등)
│   └── topics/              #   주제 백로그 (건축쇼츠 후보 리스트)
│
├── flow-pipeline/           # 모듈① Google Flow(Veo) 생성 영상
│   ├── RUNBOOK.md           #   Aside 브라우저 자동화 절차 (제출·다운로드·수거)
│   ├── scripts/             #   dub(TTS)·collect(다운로드 수거)·assemble(자막·조립)
│   ├── fonts/               #   Pretendard (자막·슬랩 렌더용)
│   └── projects/<NN-이름>/  #   프로젝트별 프롬프트·클립·오디오·완성본
│
├── OpenMontage/             # 모듈② Gemini 이미지 + Ken Burns + 데이터 오버레이
│   ├── MYNEXTSEASON.md      #   이 프로젝트와의 연결 문서
│   └── projects/<이름>/     #   produce.py (assets→props→render 3단계 드라이버)
│
├── talkcraft/               # 모듈③ Remotion 코드 모션그래픽 (⚠️ 비상업 라이선스 — 실험 전용)
│   ├── README.md            #   구조·새 프로젝트 복제법
│   ├── video-talkcraft/     #   엔진·스킬 원본 (업스트림)
│   └── projects/            #   영상 프로젝트 demo·gcans·guri·family·savings·thinking (demo가 node_modules 원본 보유)
│
├── experiments/             # 모듈⑥ opus 코드 렌더(PIL 종이공작·ink-theater) — MOTION-RULES
│   ├── paperkit.py · audiokit.py  #   공용 도구 (종이 질감·라벨·BGM 합성)
│   ├── ink-character-kit/   #   ink-theater 캐릭터 제작 규격·템플릿
│   └── projects/<이름>/     #   영상 프로젝트 (script·tts·render·treatment, .venv 는 opus-paper-04 공유)
│
├── autoShorts/              # 모듈④ HTML/GSAP 템플릿 씬 → HyperFrames 렌더 → FFmpeg (+YT/IG 업로드)
│   ├── CLAUDE.md            #   작업 규칙 (슬래시 커맨드 /shorts-* 는 루트 .claude/commands/)
│   └── episodes/<slug>/     #   episode.json 단일 소스 · scenes · final.mp4
│
├── shopShorts/              # 모듈⑤ 쇼핑 쇼츠 — 상품 페이지 수집 → Higgsfield i2v 클립 → 오버레이
│   ├── CLAUDE.md            #   작업 규칙 (a 제휴리뷰 / b 큐레이션 / c 단일홍보, 고지 강제)
│   └── episodes/<slug>/     #   source.json(상품 원천) + episode.json + media/ 클립
│
├── patches/                 # 업스트림(OpenMontage·video-talkcraft) 수정분 diff
├── overlays/                # 서브모듈 내부 자작 파일 보관 (bootstrap이 복사)
├── output/                  # ★ 완성본 정본 — <프로젝트>/<모듈명>_final_send.mp4 (git 제외)
├── scripts/collect_outputs.py  # 완성본 수집기 (MAPPING에 추가 후 실행, idempotent)
└── _archive-mpt/            # 삭제된 MoneyPrinterTurbo 모듈의 과거 완주분 보관
```

## 모듈 한 줄 요약

| 모듈 | 문법 | 강점 | 비용 |
|---|---|---|---|
| flow-pipeline | Veo 생성 영상 (Aside 브라우저 자동화) | 진짜 카메라 무빙·물/천 시뮬 | Flow 크레딧 (~10/컷, 구독 포함) |
| OpenMontage | 3D/일러스트 스틸 + 모션 + stat_card | 무결 원샷·계측선 정확·숫자 오버레이 | ~$0.04/이미지 |
| talkcraft | 코드로 그리는 모션그래픽 | 계측선·동기화·태극기 등 100% 결정론 | $0 (로컬 렌더) |
| autoShorts | HTML/GSAP 템플릿 씬 (HyperFrames) | 템플릿 5종·음성 싱크·자동 검수·업로드까지 | TTS만 (Gemini/ElevenLabs) |
| shopShorts | 상품 이미지 → Higgsfield i2v + 텍스트 오버레이 | 상품 페이지 수집·고지 자동 강제·리워드 링크 검증 | i2v 클립당 (Higgsfield 크레딧) |

기본 실험 방식: **같은 대본을 여러 모듈로 병렬 제작해 비교** (오디오는 Gemini Aoede를 공유).

## 프로젝트 이력

| # | 프로젝트 | 축 | 모듈 | 완성본 |
|---|---|---|---|---|
| 01 | 숨은 보험금 10조 | 머니 정보 | flow·openmontage·talkcraft(+구 MPT) | `output/01-hidden-insurance/` |
| 02 | 800만원 시골집 리모델링 | 건축(트랜스포메이션) | flow | `output/02-country-house-reno/` |
| 03 | 도쿄 지하의 신전 G-Cans | 건축쇼츠 | flow·openmontage·talkcraft·mpt | `output/03-tokyo-gcans/` |
| 04 | 구리시 태극기 | 건축쇼츠(페이퍼 콜라주) | flow·openmontage·talkcraft·autoshorts(45초 2종) | `output/04-guri-flags/` |
| 05 | 연안이씨 가족 그림책 | 개인(가로 16:9) | flow·openmontage·talkcraft | `output/05-yeonan-family/` |
| 06 | AI 사고력 1편 — 챗GPT가 헛소리하는 이유 | 실무 인사이트(3부작 1/3, 찰흙 3D) | flow·openmontage·talkcraft | `output/06-ai-thinking-ep1/` |
| 07 | AI 사고력 2편 — 일 못하는 사람들의 공통점 | 실무 인사이트(3부작 2/3) | openmontage | `output/07-ai-thinking-ep2/` |
| 08 | AI 사고력 3편 — 그 자동화 강의, 결제 전에 | 교육 인사이트(3부작 3/3, 개정판) | openmontage | `output/08-ai-thinking-ep3/` |
| 09 | 청년미래적금 2차 신청 총정리 | 머니 정보(시의성, 찰흙 3D) | openmontage·talkcraft·autoshorts·flow(크레딧 대기) | `output/09-youth-savings-2nd/` |
| 10 | 미라클뮤즈 아하바하메디크림 | **쇼핑 쇼츠(a 제휴 리뷰, 28초)** | shopshorts | `output/10-miraclemuse-ahabha/` |
| 11 | '5% 올랐다'만 보면 안 되는 이유 | 머니 정보(코인 시황 읽는 법, 차트 custom 씬) | autoshorts | `output/11-bitcoin-check/` |
| 12 | 삼성이 버린 기술, 애플이 8년 뒤에 | **테크**(가변 조리개, 조리개 SVG custom 씬) | autoshorts | `output/12-aperture-return/` — ⚠️ 테크 채널 신설 예정, 업로드 보류 |
| 13 | 조리개가 뭔지부터, 왜 돌아왔는지까지 | 테크(12번 + 원글 제작자판 조합) | autoshorts(49초)·openmontage(52초) | `output/13-aperture-explained/` — 테크 채널용 |
| 14 | 통신사 최적요금제 안내, 바로 바꾸면 손해일 수도 | 머니 정보(10/1 시행 시의성) | autoshorts | `output/14-optimal-plan/` |
| 15 | 426 호흡법, 12초 동안 같이 해보세요 | 생활 건강 · 근거와 주의사항 포함 | autoshorts · Codex 연출 (48.4초) | `output/15-breathing-426/` |
| 16 | '무향' 핸드크림이면 정말 향료가 없을까? | 쇼핑(쇼핑커넥트) · AAD·표시규정 보강 | opus-paper(코드 종이공작 · 가을 질감, 49.7초) | `output/16-autumn-handcream/` — 재테크 채널 · 네이버 클립 업로드 |
| 17 | 가방에 넣을 핸드크림, 무향으로 찾고 있나요? | 쇼핑(쇼핑커넥트 · 동구밭 단일 상품) | gemini-opus(Gemini 16:9 제품영상 → 9:16 재구성 · 새 나레이션·자막·합성 BGM · 실측 평점 카드, 24.3초) | `output/17-donggubat-handcream/` — 네이버 클립 전용(YouTube 쇼츠 설명 링크 클릭 불가) |
| 18 | 바람막이면 비도 막아줄까? | 쇼핑(쇼핑커넥트 · 데카트론 런 100) · 기상청 체감온도 | opus-paper(코드 종이공작 · 쌀쌀한 색감, 48.1초) | `output/18-autumn-windbreaker/` — 재테크 채널 · 네이버 클립 |
| 19 | 스마트태그3, 아이폰에서도 될까? | 테크 · 삼성 발표 각주 기준 | autoshorts(청사진)·opus-paper(네이비 방안지) — 같은 나레이션 | `output/19-smarttag3-ios/` — opus판만 테크 채널 · 네이버 클립 |
| 27 | 실손보험 청구, 이제 네이버·토스에서 끝날까? | 재테크 · 금융위 9/30 보도자료·실손24 이용안내 원문 대조 | opus-paper(MOTION-RULES 첫 적용 · 영수증 모티프 · 자막 없음 · 박자·모션 블러 4장, 66.6초) | `output/27-silson24-platform/` — 재테크 채널 · 네이버 클립 |
| 26 | 2026년 9월 미국 고용보고서 | 재테크 · BLS 9월분(10/2 발표) 원문 대조 | narration(사용자 모션그래픽 + Gemini Aoede 나레이션, 장면 길이 맞춤 41.7초) | `output/26-2026-09-us-jobs-motion-v2/` — 재테크 채널 · 네이버 클립 |
| 25 | 가디건 하나로 가을 준비 | 쇼핑(쇼핑커넥트 · 스파오 라운드넥 카디건) · 공식 상품정보 | edit(사용자 편집본 · 공식 상품 사진 + AI 착장 연출, 자막+합성 배경음, 44초) | `output/25-SPAO_44s_edit_project/` — 재테크 채널 · 네이버 클립 |
| 22 | 갤럭시 버즈 온, 지하철보다 산책에 맞을까? | 테크 · 삼성 뉴스룸 공식 자료 | opus-paper(네이비 방안지 · 착용 사진 Gemini 종이공작 변환) | `output/22-galaxy-buds-on/` — 테크 채널 · 네이버 클립 |
| 23 | 작은 글씨, 카메라로 보여주고 물어볼 수 있을까? | 테크 · Google 블로그(제미나이 라이브 가이드 비전) | opus-paper · redesign(사용자 리디자인판, 편집 파일 `guided-vision_editable/`) | `output/23-guided-vision/` — redesign판 테크 채널 · 네이버 클립 |
| 24 | 오늘 밤 9시 반 미국 고용보고서, 체크 4가지 | 재테크 · BLS 발표문(8월분) 기준 | opus-paper(크림 장부지 · 블로그 이미지 3장) | `output/24-us-jobs-report/` — 재테크 채널만(클립 업로드 실패, 발표 시각 지나 생략) |
| 21 | 축구장 11개 크기 코스모스 꽃밭, 딱 사흘만 | 지역 축제(2026 구리 코스모스 축제) · 공식 사이트 기준 | opus-paper · openmontage · autoshorts(paper) · autoshorts-om(조합) — 같은 나레이션 | `output/21-guri-cosmos/` — opus판 personal·클립 공개, 조합판 10/6 18:00 예약 |

| 20 | 식후 걷기와 혈당 | 생활 건강 · 연구 및 원리 설명 | autoshorts · Codex B안 | `output/20-postmeal-walk/` |

## 환경 메모

- API 키: ElevenLabs → `flow-pipeline/.env` · Google(GOOGLE_API_KEY, 결제 연결) → `OpenMontage/.env` · autoShorts(Gemini TTS·ElevenLabs·YT/IG) → `autoShorts/.env` · shopShorts(Higgsfield·Gemini TTS) → `shopShorts/.env`
  (쉘의 GEMINI_API_KEY는 무효한 옛 키 — unset 후 .env 사용)
- Flow 웹: flow.google.com (Google 계정 lee.junghoon@gmail.com, 브라우저 자동화는 Aside MCP 경유)
- 공용 자원: 폰트 `flow-pipeline/fonts/`, PIL venv `OpenMontage/.venv`, TTS는 Gemini Aoede(한국어 네이티브)
- 새 완성본이 나오면: `scripts/collect_outputs.py`의 MAPPING에 한 줄 추가 → 실행 (마무리 절차). autoShorts 카드뉴스는 CARDS에 추가 → `output/<프로젝트>/cards/`
