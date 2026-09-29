#!/usr/bin/env python3
"""OpenMontage GoogleImagen 브리지 — gen-bg.js 가 stdin 으로 작업 목록(JSON)을 넘긴다.

입력: [{"prompt": "...", "out": "/abs/path.png"}, ...]
출력: 한 줄에 하나씩 "@@RESULT {json}" (성공/실패). 그 외 줄은 라이브러리 로그라 무시해도 된다.
OpenMontage 위치는 OPENMONTAGE_DIR(기본: 저장소 옆 ../OpenMontage).
"""
import json, os, sys
from pathlib import Path

OM = Path(os.environ.get("OPENMONTAGE_DIR", Path(__file__).resolve().parents[3] / "OpenMontage"))
sys.path.insert(0, str(OM))
from lib.env_loader import load_env  # noqa: E402
load_env(OM)
from tools.graphics.google_imagen import GoogleImagen  # noqa: E402

MODEL = os.environ.get("BG_IMAGE_MODEL", "gemini-3.1-flash-image")
jobs = json.load(sys.stdin)
imagen = GoogleImagen()
for j in jobs:
    Path(j["out"]).parent.mkdir(parents=True, exist_ok=True)
    r = imagen.execute({"prompt": j["prompt"], "aspect_ratio": "9:16", "model": MODEL, "output_path": j["out"]})
    print("@@RESULT " + json.dumps({"out": j["out"], "ok": bool(r.success), "error": r.error, "model": MODEL},
                                   ensure_ascii=False), flush=True)
