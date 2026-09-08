#!/usr/bin/env python3
"""~/Downloads에 떨어진 Flow 다운로드를 <프로젝트>/clips/cutNN.mp4로 수거.

사용: FLOW_PROJECT=<프로젝트명> python3 scripts/collect.py [--dry-run]
      (또는 cd projects/<이름> 후 실행 — projlib.find_project 규칙)

매핑 근거 (우선순위):
1. <프로젝트>/download_log.json — 러너가 다운로드 직후 기록한 {"cutNN": "<파일명>"} 매핑
2. 파일명이 이미 cutNN_타임스탬프.mp4 형태인 경우 (같은 컷 여러 개면 최신본 채택)

동작:
- 기존 clips/cutNN.mp4가 있으면 clips/_old/로 백업 후 교체
- queue.json의 해당 컷 status를 downloaded로 갱신
- 처리한 download_log.json 항목은 제거 (재실행 안전)
"""
import json
import re
import shutil
import sys
from pathlib import Path

from projlib import find_project

DOWNLOADS = Path.home() / "Downloads"
PROJ = find_project()
CLIPS = PROJ / "clips"
OLD = CLIPS / "_old"
QUEUE = PROJ / "queue.json"
DLLOG = PROJ / "download_log.json"

CUT_PAT = re.compile(r"^(cut\d{2})_(\d{12,})\.mp4$")


def place(cut: str, src: Path, dry: bool, queue: dict) -> None:
    dest = CLIPS / f"{cut}.mp4"
    print(f"{cut}: {src.name} -> {dest.relative_to(PROJ)}")
    if dry:
        return
    if dest.exists():
        OLD.mkdir(exist_ok=True)
        shutil.move(dest, OLD / f"{cut}.mp4")
        print(f"  (기존본 -> clips/_old/{cut}.mp4)")
    shutil.move(src, dest)
    for item in queue["cuts"]:
        if item["cut"] == cut:
            item["status"] = "downloaded"


def main(dry: bool) -> None:
    queue = json.loads(QUEUE.read_text())
    CLIPS.mkdir(exist_ok=True)
    moved = False

    # 1) download_log.json 매핑
    if DLLOG.exists():
        log = json.loads(DLLOG.read_text())
        remaining = {}
        for cut, fname in log.items():
            src = DOWNLOADS / fname
            if src.exists():
                place(cut, src, dry, queue)
                moved = True
            else:
                print(f"{cut}: {fname} 이(가) ~/Downloads에 없음 — 로그 유지")
                remaining[cut] = fname
        if not dry:
            DLLOG.write_text(json.dumps(remaining, ensure_ascii=False, indent=2))

    # 2) cutNN_* 패턴 파일
    by_cut: dict[str, list[Path]] = {}
    for f in DOWNLOADS.glob("cut*_*.mp4"):
        m = CUT_PAT.match(f.name)
        if m:
            by_cut.setdefault(m.group(1), []).append(f)
    for cut, files in sorted(by_cut.items()):
        files.sort(key=lambda p: p.name)
        place(cut, files[-1], dry, queue)
        moved = True
        if not dry:
            for f in files[:-1]:
                f.unlink()

    if not moved:
        print("수거할 파일 없음")
        return
    if not dry:
        QUEUE.write_text(json.dumps(queue, ensure_ascii=False, indent=2))
        print("queue.json 갱신 완료")


if __name__ == "__main__":
    main("--dry-run" in sys.argv)
