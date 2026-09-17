# autoShorts — Shorts Factory

> **myNextSeason 모듈④.** 상위 규칙은 [`../docs/PRODUCTION.md`](../docs/PRODUCTION.md). 설치는 루트 `bash scripts/bootstrap.sh`가 처리하며, 슬래시 커맨드 `/shorts-*`는 루트 `.claude/commands/`에 있어 myNextSeason 루트에서 `claude`를 실행해 씁니다.

하루 10분으로 세로형 쇼츠/릴스(9:16)를 만드는 자동화 파이프라인입니다.

```
레퍼런스 분석 → 대본 → ElevenLabs 음성 → HTML/GSAP 씬 → HyperFrames 렌더 → FFmpeg 합성·검수 → YouTube/Instagram 업로드
```

사람은 **레퍼런스 선택 · 대본 확정 · 최종 검수**만 하고, 나머지는 Claude Code와 Node 스크립트가 처리합니다.

## 특징

- **episode.json 하나로 관리** — 대본, 씬, 효과음, 캡션, 업로드 설정을 한 파일에 저장합니다.
- **음성 기준 싱크** — ElevenLabs가 돌려주는 글자별 타임스탬프로 자막과 화면 요소가 나오는 시점을 맞춥니다.
- **바뀐 문장만 음성 재생성** — 씬마다 해시로 캐시해서 크레딧을 아낍니다.
- **씬 템플릿 5종** — `title` · `compare` · `list` · `demo` · `cta`, 트랜지션 3종, 효과음 7종(FFmpeg로 직접 생성, 저작권 걱정 없음)
- **자동 검수** — 해상도·FPS·코덱·길이·검은 화면·무음 구간을 확인하고, 씬별 프레임을 한 장에 모은 이미지를 만듭니다.
- **업로드 안전장치** — 기본은 미리보기만 하고 `--yes`를 붙여야 실제로 올립니다. YouTube는 기본 비공개입니다.

## 요구 사항

- macOS (`--mock` 테스트 음성에 `say` 사용)
- Node.js 22 이상
- FFmpeg / ffprobe (`brew install ffmpeg`)
- Google Chrome (HyperFrames 렌더링)

## 설치

```bash
cd myNextSeason/autoShorts   # 저장소는 myNextSeason에 포함됨
npm install
npm run sfx                 # 효과음 생성 (이미 있으면 건너뜀)
npx hyperframes doctor      # FFmpeg·Chrome 확인 (whisper/Kokoro/Docker 는 선택 사항)
cp .env.example .env
```

설치가 끝나면 크레딧 없이 샘플로 전체 흐름을 확인할 수 있습니다.

```bash
npm run make -- sample --mock
open episodes/sample/final.mp4
```

## 설정 (.env)

| 항목 | 준비 방법 |
|---|---|
| `ELEVENLABS_API_KEY`, `ELEVENLABS_VOICE_ID` | ElevenLabs → Voices → Instant Voice Clone으로 1–2분짜리 깨끗한 녹음을 올린 뒤, 만들어진 목소리의 voice_id를 넣습니다. |
| `YT_CLIENT_ID`, `YT_CLIENT_SECRET` | Google Cloud에서 YouTube Data API v3를 켜고, OAuth 동의 화면(테스트 사용자에 본인 추가)과 OAuth 클라이언트(**데스크톱 앱**)를 만든 뒤 `npm run yt:auth`를 한 번 실행합니다. |
| `IG_USER_ID`, `IG_ACCESS_TOKEN` | Instagram 비즈니스/크리에이터 계정과 `instagram_content_publish` 권한이 있는 장기 토큰이 필요합니다. Instagram 로그인으로 받은 토큰이면 `IG_GRAPH_HOST=graph.instagram.com`으로 바꿉니다. |

## 사용법

myNextSeason 루트에서 `claude`를 실행하고 아래 순서로 진행합니다.

| 단계 | 명령 | 하는 일 |
|---|---|---|
| 0. 입력 | `npm run new -- <slug> "주제"` | 입력 페이지가 열림. 주제·타깃·CTA, 방향, 레퍼런스(전사·장면 메모·캡처), 대본 초안, 색·자료, 업로드 문구를 한 번에 입력 |
| 1. 킥오프 | `/shorts-new <slug>` | 입력 내용 확인, 비었거나 모호한 것만 질문 |
| 2. 레퍼런스 분석 | `/shorts-ref <slug>` | 전사·캡처로 구조를 분석해 내 주제에 적용 (레퍼런스가 없으면 건너뜀) |
| 3. 대본·씬 설계 | `/shorts-script <slug>` | 씬별 대본 표를 만들고 episode.json에 저장 (**여기서 대본 확정**) |
| 4. 음성 | `npm run tts -- <slug>` → `/shorts-voice-check <slug>` | 음성 생성 후 발음·속도·멈춤 검수 |
| 5. 씬 | `/shorts-scenes <slug> [sNN]` | 템플릿으로 씬 생성, 필요한 씬만 직접 연출 |
| 6. 완성 | `/shorts-render <slug>` | 렌더 → 합성 → 검수 → `final.mp4` |
| 7. 업로드 | `npm run upload -- <slug> --yes` | YouTube·Instagram 업로드 |

> 레퍼런스 링크만으로는 Claude가 영상 내용을 볼 수 없습니다. 입력 페이지에 자막·나레이션 전사를 붙여 넣거나 캡처를 끌어다 놓으세요.

### 스크립트

```bash
npm run new -- <slug> "주제"            # 에피소드 뼈대 생성 + 입력 페이지 [--no-intake]
npm run intake -- <slug>                  # 입력 페이지 다시 열기
npm run make -- <slug> [--mock] [--draft] [--force]
                                          # tts → scenes → render → assemble → verify
npm run tts -- <slug> [--mock|--force]    # 음성 + 타임스탬프 (바뀐 씬만 생성)
npm run scenes -- <slug> [--force]        # 씬 HTML 생성
npm run render -- <slug> [--only s02] [--draft]
npm run assemble -- <slug>                # 트랜지션 + 나레이션 + 효과음 합성
npm run verify -- <slug>                  # 기술 검수 + renders/check/contact-sheet.jpg
npm run cards -- <slug> [--only s02]      # 인스타 카드뉴스(1:1) → cards/01.png …
npm run preview -- <slug> [--stop]        # HyperFrames Studio 미리보기
npm run upload -- <slug> [--yes] [--only youtube|instagram] [--again]
npm run yt:auth                           # YouTube OAuth 최초 인증
npm run sfx [-- --force]                  # 효과음 재생성
```

## episode.json

```jsonc
{
  "slug": "chatgpt-meeting",
  "topic": "ChatGPT로 회의록 3초 만에 정리하기",
  "voice": { "voiceId": "", "speed": 1.05 },        // 비우면 .env 값 사용
  "theme": { "bg": "#0b0b0f", "accent": "#ffd84d" },
  "scenes": [
    {
      "id": "s01",
      "template": "title",
      "narration": "회의록 정리, 아직도 손으로 하세요?",
      "onScreen": { "kicker": "직장인 필수", "title": "회의록 정리\n3초 컷", "highlight": ["손으로"] },
      "sfx": [{ "name": "whoosh", "at": "start" }],
      "transitionOut": "white-flash"
    }
  ],
  "caption": "회의록 정리 3초 컷 📝",
  "hashtags": ["#ChatGPT", "#업무자동화"],
  "upload": { "title": "회의록 정리 3초 컷", "youtube": true, "instagram": true }
}
```

- `timing`은 `npm run tts`가 자동으로 채웁니다.
- 시간 지정(`at`, `…At`): 초 단위 숫자 | `"start"` | `"end"` | `"word:키워드"`(나레이션에서 그 단어가 시작되는 순간)
- 템플릿별 `onScreen` 필드는 [templates/scenes/README.md](templates/scenes/README.md)를 참고하세요.
- 전체 스키마: [scripts/lib/episode.js](scripts/lib/episode.js)

## 구조

```
autoShorts/
├─ CLAUDE.md                 # Claude Code 작업 규칙
├─ templates/scenes/         # _base.html + 씬 템플릿 5종
├─ assets/sfx/               # 효과음 (같은 이름의 wav로 교체 가능)
├─ scripts/
│  ├─ tts.js  build-scenes.js  render.js  assemble.js  verify.js  make.js
│  ├─ lib/                   # episode 스키마, 경로, 프로세스 헬퍼
│  └─ upload/                # youtube.js, instagram.js, index.js
└─ episodes/<slug>/
   ├─ episode.json           # 단일 소스
   ├─ refs/                  # 레퍼런스 캡처 + reference.md(입력 페이지가 생성)
   ├─ media/                 # 영상에 쓸 자료 (입력 페이지에서 업로드)
   ├─ scenes/                # 생성된 씬 HTML (git 포함)
   ├─ audio/  renders/  final.mp4   # 생성물 (git 제외)
```

## 씬 커스텀

템플릿으로 충분하면 `episode.json`만 고칩니다. 특별한 연출이 필요할 때는 `episodes/<slug>/scenes/sNN.html`을 직접 수정하고, 파일 안의 `autoshorts:generated` 주석을 `autoshorts:custom`으로 바꾸면 다시 생성할 때 덮어쓰지 않습니다. 이때 `data-duration`은 원래 값을 유지해야 싱크가 맞습니다.

## 대본 팁

- 한 씬에 한 문장(1.5~5초), 전체 20~45초 권장 (90초 초과 금지)
- 첫 2초 안에 훅을 넣고, 훅에서 약속한 결과를 영상 안에서 반드시 보여줍니다.
- 긴 텍스트는 화면으로, 나레이션은 핵심만
- 영문·숫자는 읽는 대로 적습니다 (예: "GPT" → "지피티")
- 레퍼런스는 구조와 템포만 빌리고 문장은 새로 씁니다.

## 참고

- 워크플로 원안: [every-ai Shorts Factory](https://every-ai-iota.vercel.app/shorts-factory)
- [HyperFrames](https://github.com/heygen-com/hyperframes) — `npx hyperframes docs <topic>`
- [ElevenLabs Text to Speech with timestamps](https://elevenlabs.io/docs/api-reference/text-to-speech/convert-with-timestamps)
