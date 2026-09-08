# Flow 웹 자동화 런북 (Aside 브라우저 경유)

> **상위 문서: [`../docs/PRODUCTION.md`](../docs/PRODUCTION.md)** — 상위주제·연출 프롬프트 템플릿·확인 게이트는 마스터 문서를 따른다.
> 이 런북은 Flow 모듈의 "실행 방법"만 다룬다. 대본·프롬프트가 확정된 뒤에 여기로 내려온다.

> 검증일: 2026-09-02. Chrome 확장 대신 **mcp__aside__repl**(Playwright)로 Google Flow를 구동한다.
> Claude가 이 문서대로 repl을 실행하는 방식 — 쉘 단독 실행 불가(aside는 MCP 전용).

## 디렉토리 구조 (프로젝트별 분리)

```
flow-pipeline/
  .env                  # ElevenLabs 키 (공용)
  RUNBOOK.md            # 이 문서 (공용)
  scripts/              # 공용 스크립트 — FLOW_PROJECT env 또는 cwd로 대상 프로젝트 결정
    projlib.py          #   프로젝트 해석 규칙 (env → cwd → 유일 프로젝트)
    dub.py              #   cuts.json → audio/cutNN.mp3 (ElevenLabs)
    collect.py          #   ~/Downloads → clips/cutNN.mp4 (download_log.json 매핑)
    assemble.py         #   clips+audio+자막 → out/final.mp4
  projects/
    01-hidden-insurance/   # 1호: 숨은 보험금 10조 (cut01 v2까지 진행됨)
      prompts.md           #   Flow(Veo) 컷별 프롬프트 원문
      cuts.json            #   컷 정의 (나레이션 포함) — dub/assemble 입력
      queue.json           #   자동화 큐: 컷별 프롬프트+상태(pending/failed/downloaded) + project_url
      download_log.json    #   컷↔다운로드 파일명 매핑 (러너가 기록, collect가 소비)
      audio/ clips/ subs/ out/
```

**새 프로젝트 시작**: `projects/NN-<이름>/` 생성 → `prompts.md`·`cuts.json` 작성 → queue.json은 prompts.md에서 생성(아래 스니펫) → Flow 웹에서 "새 프로젝트" 만들고 그 URL을 queue.json의 `project_url`에 기록.

> ⚠️ **확인 게이트 (2026-09-03 사용자 지시)**: ①대본 ②컷별 프롬프트는 각각 **사용자 확인을 받은 뒤** 다음 단계로 진행. 생성 이후(다운로드~조립)만 자동. 그림체: 설명컷은 회색 찰흙 3D(1호 `3d` 접미사 verbatim), 실사컷은 2호 방식. 상세는 메모리 `shorts-approval-workflow` 및 `../docs/PRODUCTION.md` 참고.

```bash
# prompts.md → queue.json 생성 (01-hidden-insurance에서 쓴 파서)
cd projects/<이름> && python3 - <<'EOF'
import re, json
md = open('prompts.md').read()
cuts = [{"cut": f"cut{int(m[0]):02d}", "style": m[1].strip(), "target_sec": int(m[2]),
         "narration": m[3].strip(), "prompt": m[4].strip(), "status": "pending",
         "flow_media_name": None}
        for m in re.findall(r'## 컷 (\d+) — (.+?) · 목표 (\d+)초\n나레이션: (.+?)\n```\n(.+?)\n```', md, re.S)]
json.dump({"project_url": "<Flow 프로젝트 URL 기입>", "model": "Omni 1.1 Flash", "aspect": "9:16",
           "outputs_per_prompt": 1, "credits_per_video_estimate": 10, "cuts": cuts},
          open('queue.json','w'), ensure_ascii=False, indent=2)
print(len(cuts), 'cuts')
EOF
```

## 전제 (전부 검증됨)

- Google 계정: **lee.junghoon@gmail.com** (PRO, Flow 크레딧 2026-09-02 기준 ~690) — jlee@anyeats.co.kr 아님.
- 대상 Flow 프로젝트: 해당 프로젝트 `queue.json`의 `project_url`.
- 에이전트 설정(프로젝트 화면 우측 채팅 → tune 아이콘): 동영상 **9:16 / x1 / Omni 1.1 Flash**, 생성 전 확인 "**안 함**" — 저장돼 있음. 바뀌었으면 복구할 것.
- 비용: Flash 6초 1개당 크레딧 ~10.
- 다운로드는 **~/Downloads/<미디어이름>_<타임스탬프>.mp4** 로 떨어짐 (repl의 saveAs는 세션 디렉토리 밖 금지라 못 씀).
- ⚠️ 01-hidden-insurance의 Flow 웹 기존 미디어 이름(cutNN)은 **신뢰 금지** — 9/1 사고로 뒤바뀌어 있음 (예: "cut13" 이름의 미디어가 실제로는 컷02 내용). 매핑 근거는 항상 **상세 화면 우측의 생성 프롬프트 텍스트**.

## 컷 1개 처리 절차 (queue.json의 pending 항목마다 반복) — 2026-09-02 cut01로 E2E 검증 완료

1. **탭 확보**: `listBrowserTabs()`로 Flow 프로젝트 탭 찾기 → `attachBrowserTab(id)`. 없으면 `openTab(project_url)`.
2. **프롬프트 제출**: 하단 중앙 플로팅 입력바("무엇을 만들고 싶으신가요?", "에이전트" 칩 옆). DOM textarea는 별개 요소라 fill이 안 먹힘 — **좌표 클릭 + insertText**가 검증된 방법:
   ```js
   await flowPage.mouse.click(700, 799);          // 입력바 클릭 (1440x900 뷰포트 기준)
   await flowPage.keyboard.insertText(item.prompt);
   await flowPage.mouse.click(995, 843);           // 보내기(→) 버튼
   ```
   ⚠️ 우측 패널(에이전트 설정 등)이 열려 있으면 입력바가 가려짐 — 먼저 close/Escape.
3. **생성 대기**: 입력바가 "생각 중..."으로 바뀜 → 그리드 좌상단에 새 카드가 진행률 %와 함께 등장. `body.innerText()`에서 `\d+%` 가 사라질 때까지 15~20초 간격 폴링 (Flash 6초 기준 실측 ~60초). 채팅에 "실패"가 뜨면 → 프롬프트 정책 이슈. queue에 `status: "failed"` 기록하고 다음 컷 진행.
4. **열기·검증**: 그리드 좌상단 새 카드 클릭(`mouse.click(320, 210)`) → 상세 화면 우측 프롬프트 앞 60자가 queue의 prompt와 일치하는지 확인. 에이전트가 자동으로 영문 제목을 붙임(예: "Bank vault interior with banknotes").
   - ⚠️ **제목 개명은 불가**: 제목 input은 fill/type이 되지만 Enter/blur 시 서버 커밋 없이 원복됨. 시도하지 말 것.
5. **다운로드 + 로그 기록**:
   ```js
   const dlp = flowPage.waitForEvent('download', { timeout: 30000 });
   await flowPage.locator('button:has-text("download")').first().click();
   const dl = await dlp;
   console.log(dl.suggestedFilename()); // <에이전트제목>_YYYYMMDDHHmm.mp4 → ~/Downloads에 저장됨
   ```
   받은 파일명을 해당 프로젝트의 `download_log.json`에 `{"cutNN": "<파일명>"}`으로 즉시 기록(Bash/Write). **이 로그가 컷 매핑의 근거** — 컷 하나 처리할 때마다 바로 기록해야 뒤바뀜이 원천 차단됨.
6. **돌아가기**: "완료" 버튼 → 그리드로 복귀 → 다음 컷 반복.
7. 전체(또는 중간) 종료 후 **수거**: `FLOW_PROJECT=<이름> python3 scripts/collect.py` → download_log.json 매핑대로 ~/Downloads → clips/cutNN.mp4 이동(기존본은 clips/_old/ 백업), queue.json status 갱신, 처리된 로그 항목 제거.
8. 이후 기존 파이프라인: `FLOW_PROJECT=<이름> python3 scripts/dub.py <voice_id>` → `FLOW_PROJECT=<이름> python3 scripts/assemble.py`. (생성물은 10초로 나옴 — 목표 길이 트림은 assemble 단계 담당)

## 운영 메모

- 크레딧 확인: 우상단 PRO 아바타 버튼 클릭 → "NNN Google Flow 크레딧". 배치 시작 전 잔량 ≥ 컷수×10 확인.
- 클릭 셀렉터: 머티리얼 아이콘 텍스트가 접근성 이름에 포함됨 → `button:has-text("download")`, `button:has-text("tune")`, `button:has-text("arrow_forward")` 패턴이 잘 먹힘. `getByRole`은 한글 이름에서 종종 실패.
- repl 변수는 호출 간 유지되지만 **같은 이름 재선언 금지** — 변수명에 접미사 붙여가며 사용.
- 일괄 다운로드 대안: 프로젝트 화면 우상단 more_vert 메뉴 → "프로젝트 다운로드" (전체 zip. 단, 파일명 매핑은 별도 확인 필요 — 미검증).
- 모델 교체: tune 설정에서 동영상 모델 드롭다운 (기본 Omni 1.1 Flash. 고품질 필요 시 상위 모델 선택, 크레딧 소모 큼).
