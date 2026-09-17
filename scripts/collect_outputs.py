#!/usr/bin/env python3
"""완성본 수집기 — 각 모듈 깊숙이 생기는 final을 최상위 output/으로 모은다.

구조: output/<프로젝트>/<모듈명>_final_send.mp4
- 소스에 final_send.mp4(압축본)가 있으면 그대로 복사, 없으면 final*.mp4를 crf26으로 압축.
- 소스가 더 새것일 때만 갱신 (idempotent).
- 새 프로젝트/모듈이 생기면 아래 MAPPING에 한 줄 추가.
- autoShorts 인스타 카드뉴스(cards/NN.png)는 CARDS에 한 줄 추가 → output/<프로젝트>/cards/ 로 동기화.

사용: python3 scripts/collect_outputs.py
"""
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent  # myNextSeason/
OUT = ROOT / "output"

# (프로젝트, 모듈) → 소스 후보 목록 (앞선 것 우선; final_send 우선 배치)
MAPPING: dict[tuple[str, str], list[str]] = {
    ("01-hidden-insurance", "flow"): [
        "flow-pipeline/projects/01-hidden-insurance/out/final_send.mp4",
        "flow-pipeline/projects/01-hidden-insurance/out/final.mp4"],
    ("01-hidden-insurance", "openmontage"): [
        "OpenMontage/projects/hidden-insurance-money/renders/final_v3.mp4"],
    ("01-hidden-insurance", "talkcraft"): [
        "talkcraft/demo/remotion/out/delivery.mp4"],
    ("02-country-house-reno", "flow"): [
        "flow-pipeline/projects/02-country-house-reno/out/final_send.mp4",
        "flow-pipeline/projects/02-country-house-reno/out/final.mp4"],
    ("03-tokyo-gcans", "flow"): [
        "flow-pipeline/projects/03-tokyo-gcans/out/final_send.mp4",
        "flow-pipeline/projects/03-tokyo-gcans/out/final.mp4"],
    ("03-tokyo-gcans", "openmontage"): [
        "OpenMontage/projects/tokyo-gcans-archi/renders/final_send.mp4",
        "OpenMontage/projects/tokyo-gcans-archi/renders/final.mp4"],
    ("03-tokyo-gcans", "talkcraft"): [
        "talkcraft/gcans/remotion/out/final_send.mp4",
        "talkcraft/gcans/remotion/out/final.mp4"],
    ("03-tokyo-gcans", "mpt"): [
        "_archive-mpt/e79a0500-final.mp4"],  # MPT 모듈 삭제됨 — 아카이브 참조
    ("06-ai-thinking-ep1", "flow"): [
        "flow-pipeline/projects/06-ai-thinking-ep1/out/final.mp4"],
    ("06-ai-thinking-ep1", "openmontage"): [
        "OpenMontage/projects/ai-thinking-ep1/renders/final.mp4"],
    ("06-ai-thinking-ep1", "talkcraft"): [
        "talkcraft/thinking/remotion/out/final.mp4"],
    ("09-youth-savings-2nd", "openmontage"): [
        "OpenMontage/projects/youth-savings-2nd/renders/final.mp4"],
    ("09-youth-savings-2nd", "talkcraft"): [
        "talkcraft/savings/remotion/out/final.mp4"],
    ("09-youth-savings-2nd", "autoshorts"): [
        "autoShorts/episodes/youth-savings-2nd/final.mp4"],
    ("09-youth-savings-2nd", "flow"): [
        "flow-pipeline/projects/09-youth-savings-2nd/out/final.mp4"],
    ("07-ai-thinking-ep2", "openmontage"): [
        "OpenMontage/projects/ai-thinking-ep2/renders/final.mp4"],
    ("08-ai-thinking-ep3", "openmontage"): [
        "OpenMontage/projects/ai-thinking-ep3/renders/final.mp4"],
    ("05-yeonan-family", "openmontage"): [
        "OpenMontage/projects/yeonan-family/renders/final_send.mp4",
        "OpenMontage/projects/yeonan-family/renders/final.mp4"],
    ("05-yeonan-family", "flow"): [
        "flow-pipeline/projects/05-yeonan-family/out/final_send.mp4",
        "flow-pipeline/projects/05-yeonan-family/out/final.mp4"],
    ("05-yeonan-family", "talkcraft"): [
        "talkcraft/family/remotion/out/final_send.mp4",
        "talkcraft/family/remotion/out/final.mp4"],
    ("04-guri-flags", "flow"): [
        "flow-pipeline/projects/04-guri-flags/out/final_send.mp4",
        "flow-pipeline/projects/04-guri-flags/out/final.mp4"],
    ("04-guri-flags", "openmontage"): [
        "OpenMontage/projects/guri-flags-paper/renders/final_send.mp4",
        "OpenMontage/projects/guri-flags-paper/renders/final.mp4"],
    ("04-guri-flags", "talkcraft"): [
        "talkcraft/guri/remotion/out/final_send.mp4",
        "talkcraft/guri/remotion/out/final.mp4"],
}

# 프로젝트 → autoShorts 카드뉴스 폴더 (npm run cards 결과, PNG만 복사 · src/ HTML 제외)
CARDS: dict[str, str] = {
    "09-youth-savings-2nd": "autoShorts/episodes/youth-savings-2nd/cards",
}


def collect_cards() -> None:
    for project, rel in CARDS.items():
        src_dir = ROOT / rel
        pngs = sorted(src_dir.glob("[0-9][0-9].png")) if src_dir.is_dir() else []
        if not pngs:
            print(f"skip  {project}/cards — 소스 없음")
            continue
        dest_dir = OUT / project / "cards"
        dest_dir.mkdir(parents=True, exist_ok=True)
        copied = 0
        for src in pngs:
            dest = dest_dir / src.name
            if not dest.exists() or dest.stat().st_mtime < src.stat().st_mtime:
                shutil.copy2(src, dest)
                copied += 1
        # 카드 수가 줄었으면 남은 옛 번호 제거 (cards.js와 같은 동작)
        names = {s.name for s in pngs}
        removed = [d for d in dest_dir.glob("[0-9][0-9].png") if d.name not in names]
        for d in removed:
            d.unlink()
        state = f"copy {copied}장" if copied or removed else "최신 상태"
        if removed:
            state += f", 삭제 {len(removed)}장"
        print(f"cards {project} — {len(pngs)}장 ({state})")


def main() -> None:
    for (project, module), candidates in MAPPING.items():
        src = next((ROOT / c for c in candidates if (ROOT / c).exists()), None)
        if src is None:
            print(f"skip  {project}/{module} — 소스 없음")
            continue
        dest_dir = OUT / project
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest = dest_dir / f"{module}_final_send.mp4"
        if dest.exists() and dest.stat().st_mtime >= src.stat().st_mtime:
            print(f"ok    {project}/{module} — 최신 상태")
            continue
        if src.name.endswith("_send.mp4") or src.stat().st_size <= 30 * 1024 * 1024:
            shutil.copy2(src, dest)
            print(f"copy  {project}/{module} ← {src.relative_to(ROOT)}")
        else:
            subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(src),
                            "-c:v", "libx264", "-crf", "26", "-c:a", "aac", "-b:a", "128k",
                            str(dest)], check=True)
            print(f"press {project}/{module} ← {src.relative_to(ROOT)} (압축)")
    collect_cards()


if __name__ == "__main__":
    main()
