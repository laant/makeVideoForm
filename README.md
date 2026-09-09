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
│   └── demo·gcans·guri·family/  # 프로젝트들 (demo가 node_modules 원본 보유)
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

기본 실험 방식: **같은 대본을 여러 모듈로 병렬 제작해 비교** (오디오는 Gemini Aoede를 공유).

## 프로젝트 이력

| # | 프로젝트 | 축 | 모듈 | 완성본 |
|---|---|---|---|---|
| 01 | 숨은 보험금 10조 | 머니 정보 | flow·openmontage·talkcraft(+구 MPT) | `output/01-hidden-insurance/` |
| 02 | 800만원 시골집 리모델링 | 건축(트랜스포메이션) | flow | `output/02-country-house-reno/` |
| 03 | 도쿄 지하의 신전 G-Cans | 건축쇼츠 | flow·openmontage·talkcraft·mpt | `output/03-tokyo-gcans/` |
| 04 | 구리시 태극기 | 건축쇼츠(페이퍼 콜라주) | flow·openmontage·talkcraft | `output/04-guri-flags/` |
| 05 | 연안이씨 가족 그림책 | 개인(가로 16:9) | flow·openmontage·talkcraft | `output/05-yeonan-family/` |
| 06 | AI 사고력 1편 — 챗GPT가 헛소리하는 이유 | 실무 인사이트(3부작 1/3, 찰흙 3D) | flow·openmontage·talkcraft | `output/06-ai-thinking-ep1/` |

## 환경 메모

- API 키: ElevenLabs → `flow-pipeline/.env` · Google(GOOGLE_API_KEY, 결제 연결) → `OpenMontage/.env`
  (쉘의 GEMINI_API_KEY는 무효한 옛 키 — unset 후 .env 사용)
- Flow 웹: flow.google.com (Google 계정 lee.junghoon@gmail.com, 브라우저 자동화는 Aside MCP 경유)
- 공용 자원: 폰트 `flow-pipeline/fonts/`, PIL venv `OpenMontage/.venv`, TTS는 Gemini Aoede(한국어 네이티브)
- 새 완성본이 나오면: `scripts/collect_outputs.py`의 MAPPING에 한 줄 추가 → 실행 (마무리 절차)
