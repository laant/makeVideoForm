"""프로젝트 디렉토리 해석 공용 모듈.

flow-pipeline은 projects/<이름>/ 단위로 여러 영상 프로젝트를 관리한다.
스크립트들이 대상 프로젝트를 찾는 규칙 (우선순위):
  1. 환경변수 FLOW_PROJECT (projects/ 하위 이름 또는 절대/상대 경로)
  2. 현재 작업 디렉토리에 cuts.json이 있으면 그곳 (cd projects/xxx 후 실행하는 경우)
  3. projects/ 안에 프로젝트가 딱 하나면 그것
그 외에는 후보 목록을 보여주고 종료.
"""
import os
import pathlib
import sys

PIPELINE_ROOT = pathlib.Path(__file__).resolve().parent.parent
PROJECTS = PIPELINE_ROOT / "projects"


def find_project() -> pathlib.Path:
    env = os.environ.get("FLOW_PROJECT")
    if env:
        p = pathlib.Path(env)
        if not p.is_dir():
            p = PROJECTS / env
        if not p.is_dir():
            sys.exit(f"FLOW_PROJECT={env} 에 해당하는 디렉토리가 없습니다")
        return p.resolve()

    cwd = pathlib.Path.cwd()
    if (cwd / "cuts.json").exists() or (cwd / "queue.json").exists():
        return cwd

    candidates = sorted(d for d in PROJECTS.iterdir() if d.is_dir()) if PROJECTS.is_dir() else []
    if len(candidates) == 1:
        return candidates[0]

    names = "\n".join(f"  - {d.name}" for d in candidates) or "  (없음)"
    sys.exit(
        "대상 프로젝트를 지정하세요. 방법:\n"
        f"  FLOW_PROJECT=<이름> python3 scripts/<script>.py ...\n"
        f"  또는 cd projects/<이름> 후 실행\n프로젝트 목록:\n{names}"
    )
