# SETUP — 새 머신 복원 가이드 (전 모듈)

이 저장소는 "영상을 다시 만들 수 있는 모든 것"(문서·대본·프롬프트·드라이버·패치)을 담는다.
미디어 산출물(clips/renders/output)·API 키·node_modules·.venv는 담지 않으며, 아래 절차로 복원한다.

## 빠른 복원 (권장)

```bash
git clone --recurse-submodules <저장소URL> myNextSeason
cd myNextSeason
bash scripts/bootstrap.sh        # 아래 2~4단계를 자동 실행
# 이후 .env 두 개에 키만 입력하면 끝 (5단계)
```

이미 클론했는데 서브모듈이 비어 있다면: `git submodule update --init`

---

## 수동 복원 (bootstrap이 하는 일 + 모듈별 상세)

### 1. 서브모듈 (업스트림 클론 2종)

| 경로 | 원본 | 비고 |
|---|---|---|
| `OpenMontage/` | github.com/calesthio/OpenMontage | 커밋 고정. 우리 수정은 패치·오버레이로 별도 관리 |
| `talkcraft/video-talkcraft/` | github.com/Vincentwei1021/video-talkcraft | 커밋 고정. 한국어 정렬 패치 별도 |

```bash
git submodule update --init
```

### 2. 패치 적용 (업스트림 파일 수정분)

```bash
git -C OpenMontage apply ../patches/openmontage.diff
#  └ Gemini 네이티브 TTS 경로(google_tts.py) · ExplainerVertical 컴포지션 등록(Root.tsx)
#    · remotion_render 라우팅(video_compose.py) · edit_decisions 스키마 확장
git -C talkcraft/video-talkcraft apply ../../patches/video-talkcraft.diff
#  └ timestamps_cpu.py 한국어 정렬(--language ko, 한글 CJK 앵커) · make_timing.py 보정
```

### 3. 오버레이 복사 (서브모듈 내부의 자작 파일 — 내부 gitignore 때문에 부모가 보관)

```bash
cp -R overlays/OpenMontage/ OpenMontage/
#  └ MYNEXTSEASON.md + projects/*/produce.py (프로젝트 드라이버 3종)
```

### 4. 의존성 재설치

```bash
# OpenMontage 파이썬 venv (PIL 포함 — flow-pipeline 자막 렌더도 이 venv를 씀)
python3 -m venv OpenMontage/.venv
OpenMontage/.venv/bin/pip install -r OpenMontage/requirements.txt

# Remotion 의존성 (talkcraft — demo가 원본, 나머지는 심링크로 공유)
(cd talkcraft/demo/remotion && npm install)
#  gcans/guri/family의 node_modules는 ../../demo/remotion/node_modules 심링크 —
#  끊겨 있으면: ln -s ../../demo/remotion/node_modules talkcraft/<이름>/remotion/node_modules

# Remotion 의존성 (OpenMontage 렌더러)
(cd OpenMontage/remotion-composer && npm install)
```

전제 도구: `python3`(3.10+), `node`+`npm`, `ffmpeg`/`ffprobe`(brew), `ditto`(macOS 기본).

### 5. API 키 (.env — git 제외, 직접 작성)

```bash
echo 'ELEVENLABS_API_KEY=<키>' > flow-pipeline/.env      # Sarah 등 ElevenLabs 더빙용
echo 'GOOGLE_API_KEY=<키>'     > OpenMontage/.env        # Gemini 이미지·TTS (결제 연결 필요)
```

⚠️ 쉘 환경변수 GEMINI_API_KEY가 있으면 unset (무효한 옛 키가 끼어드는 사고 방지).

### 6. 브라우저 자동화 (flow-pipeline 전용, 머신별 1회)

- Aside 앱 설치·로그인 → `claude mcp add aside -- ~/.local/bin/aside mcp` (프로젝트 스코프)
- Aside 브라우저에서 flow.google.com에 Google 계정 로그인 (Flow 크레딧 있는 계정)
- 상세 절차: `flow-pipeline/RUNBOOK.md`

---

## 모듈별 동작 확인

| 모듈 | 스모크 테스트 |
|---|---|
| flow-pipeline | `cd flow-pipeline && FLOW_PROJECT=<프로젝트> python3 scripts/assemble.py` (클립·오디오 있는 프로젝트에서) |
| OpenMontage | `cd OpenMontage && .venv/bin/python projects/yeonan-family/produce.py assets` (키 필요) |
| talkcraft | `cd talkcraft/family/remotion && npx remotion compositions src/entry.ts` |
| 수집기 | `python3 scripts/collect_outputs.py` (소스 없으면 skip으로 표시됨 — 정상) |

## 유지보수 규칙 (서브모듈을 고칠 때 — 안 지키면 새 머신에서 유실됨)

서브모듈(OpenMontage·video-talkcraft) 내부는 부모 저장소에 커밋되지 않는다. 그래서:

1. **업스트림 파일을 수정하면** → 패치를 다시 뜬다
   ```bash
   git -C OpenMontage diff > patches/openmontage.diff
   git -C talkcraft/video-talkcraft diff -- scripts/ > patches/video-talkcraft.diff
   ```
   (video-talkcraft는 package-lock.json 변경을 제외하기 위해 `-- scripts/`로 한정)
2. **서브모듈 안에 새 파일을 만들면** (예: `OpenMontage/projects/<새프로젝트>/produce.py`) → `overlays/`에 같은 경로로 복사한다
   ```bash
   cp OpenMontage/projects/<이름>/produce.py overlays/OpenMontage/projects/<이름>/
   ```
3. 이후 부모 저장소에서 `git add patches overlays` → 커밋.

Claude로 작업할 때는 Claude가 이 절차를 자동으로 챙긴다.

## 복원되지 않는 것 (의도적)

- **미디어 산출물**: `output/`(완성본), `*/clips|renders|assets|out/`(중간물) — 필요하면 이전 머신에서 `output/`만 복사. 없어도 프롬프트·대본으로 재생산 가능
- `_archive-mpt/` — 삭제된 MPT 모듈의 과거 완주분 (보관용)
- Flow 웹 프로젝트 — Google 계정에 남아 있으므로 로그인하면 그대로 접근 가능 (URL은 각 `queue.json`에 기록됨)
