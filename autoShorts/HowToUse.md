# autoShorts 사용법

> **myNextSeason 모듈④.** 상위 규칙은 [`../docs/PRODUCTION.md`](../docs/PRODUCTION.md). 설치는 루트 `bash scripts/bootstrap.sh`가 처리하며, 슬래시 커맨드 `/shorts-*`는 루트 `.claude/commands/`에 있어 myNextSeason 루트에서 `claude`를 실행해 씁니다.

## 1. 처음 한 번만: 설정

`autoShorts` 폴더에서 `.env` 파일을 만든 뒤 아래 값을 채웁니다.

```bash
cp .env.example .env
```

| 항목 | 해야 할 일 |
|---|---|
| **ElevenLabs** (필수) | 1분 정도의 깨끗한 녹음으로 Voices → Instant Voice Clone을 만듭니다. 그다음 `ELEVENLABS_API_KEY`와 `ELEVENLABS_VOICE_ID`를 넣습니다. |
| **YouTube** (업로드할 때) | Google Cloud에서 YouTube Data API v3를 켜고 OAuth 클라이언트("데스크톱 앱")를 만듭니다. `YT_CLIENT_ID`와 `YT_CLIENT_SECRET`을 넣고 `npm run yt:auth`를 한 번 실행합니다. |
| **Instagram** (업로드할 때) | 비즈니스 또는 크리에이터 계정이 필요합니다. `IG_USER_ID`와 `IG_ACCESS_TOKEN`을 넣습니다. |

키를 넣은 뒤 샘플을 진짜 목소리로 만들어 확인해 보세요.

```bash
npm run make -- sample --force
```

## 2. 매일 쓰는 흐름 (10분 정도)

myNextSeason 루트에서 `claude`를 실행한 뒤 아래 순서로 진행합니다.

### ① 입력 페이지에 한 번에 적기 (직접)

```bash
npm run new -- chatgpt-meeting "ChatGPT로 회의록 정리하기"
```

브라우저에 입력 페이지가 열립니다. 필수는 **주제·타깃 시청자·CTA** 뿐이고, 나머지는 아는 만큼만 채우면 됩니다. 입력은 자동 저장됩니다.

| 칸 | 적는 것 |
|---|---|
| 방향 | 핵심 메시지, 훅 아이디어, 말투(예시 문장), 목표 길이, 꼭 보여줄 것 / 피할 것 |
| 레퍼런스 | 따라 하고 싶은 영상의 URL, 자막·나레이션 전사, 초 단위 장면 메모, 캡처(끌어다 놓기·⌘V) |
| 대본 초안 | 정해 둔 대사가 있으면 한 줄에 한 씬씩 `나레이션 \| 화면` |
| 화면 | 색 테마, 연출 요청, 영상에 넣을 캡처·로고 |
| 업로드 | 제목, 캡션, 해시태그 (비우면 Claude가 채움) |

> 링크만으로는 Claude가 영상 내용을 볼 수 없습니다. 전사를 붙여 넣거나 캡처를 올려 주세요. 레퍼런스 없이 내 대본 초안만으로 진행해도 됩니다.

다 적었으면 **입력 완료**를 누릅니다. 나중에 고치려면 `npm run intake -- chatgpt-meeting`.

### ② 시작

```
/shorts-new chatgpt-meeting
```

Claude가 입력 내용을 확인하고, 비었거나 모호한 것만 한 번에 묻습니다.

### ③ 레퍼런스 분석 → 대본 작성

```
/shorts-ref chatgpt-meeting
/shorts-script chatgpt-meeting
```

Claude가 씬별 대본 표를 보여줍니다. 여기서 문장을 고쳐 달라고 하면 됩니다. **이 대본을 확정하는 게 사람이 하는 핵심 작업**입니다.

### ④ 음성 생성 → 검수

```
npm run tts -- chatgpt-meeting
/shorts-voice-check chatgpt-meeting
```

발음이 이상하거나 너무 빠른 구간을 짚어 줍니다. 문장을 고치면 그 씬만 다시 생성되어 크레딧이 절약됩니다.

### ⑤ 영상 만들기 → 확인

```
/shorts-render chatgpt-meeting
```

- 렌더링, 합성, 기술 검수까지 한 번에 진행됩니다.
- 결과 영상은 `episodes/chatgpt-meeting/final.mp4`에 생깁니다.
- `open episodes/chatgpt-meeting/final.mp4`로 직접 보고 확인합니다.

### ⑥ 업로드

```bash
npm run upload -- chatgpt-meeting          # 무엇이 올라갈지 미리보기만
npm run upload -- chatgpt-meeting --yes    # 실제 업로드
```

Claude에게 "업로드해줘"라고 해도 됩니다. YouTube는 기본이 비공개로 올라갑니다.

## 3. 수정하고 싶을 때

| 상황 | 방법 |
|---|---|
| 문구, 화면 텍스트, 효과음 | Claude에게 "s03 비교 항목 바꿔줘"처럼 말하면 `episode.json`을 고칩니다. 그다음 `npm run make -- <slug>`를 실행하면 바뀐 부분만 다시 만듭니다. |
| 템플릿으로 안 되는 특별한 연출 | `/shorts-scenes <slug> s02`를 쓰면 Claude가 그 씬의 HTML을 직접 고칩니다. 고친 씬은 다시 생성할 때 덮어쓰지 않습니다. |
| 크레딧 없이 테스트 | 명령 끝에 `--mock`을 붙이면 macOS 음성을 씁니다. |
| 인스타 카드뉴스도 필요할 때 | `npm run cards -- <slug>`로 씬마다 1080×1080 이미지를 `cards/01.png…`에 만듭니다. 자막 없이 모든 요소가 나온 상태이고, 하단 문구는 `cards.footer`, 카드에만 넣을 설명은 씬의 `onScreen.cardNote`에 적습니다. |

## 4. 팁

- 한 씬에 한 문장(1.5~5초), 전체는 20~45초가 적당합니다.
- 영문이나 숫자는 읽는 대로 적어야 발음이 정확합니다 (예: "GPT" → "지피티").
- 사용할 수 있는 화면 템플릿은 [templates/scenes/README.md](templates/scenes/README.md)에 정리돼 있습니다.

## 5. 다른 컴퓨터에서 받을 때

```bash
cd myNextSeason/autoShorts   # 저장소는 myNextSeason에 포함됨
npm install
cp .env.example .env   # 키 다시 입력
```

생성된 음성과 영상은 저장소에 올라가지 않으므로 `npm run make -- <slug>`로 다시 만들어야 합니다. 이때 음성은 ElevenLabs 크레딧을 다시 씁니다.
