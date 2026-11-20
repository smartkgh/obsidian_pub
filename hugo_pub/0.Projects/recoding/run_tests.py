#!/usr/bin/env python3
"""테스트 실행기 — `python3 run_tests.py` (구버전 파이썬이면 main.py 가드가 .venv 로 재실행)

  python3 run_tests.py            # 요약
  python3 run_tests.py -v         # 테스트별 출력
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

import main  # noqa: E402,F401  ← 인터프리터 가드(.venv 재실행) 트리거


def main_entry() -> int:
    suite = unittest.defaultTestLoader.discover(str(ROOT / "tests"), top_level_dir=str(ROOT))
    verbosity = 2 if "-v" in sys.argv[1:] else 1
    result = unittest.TextTestRunner(verbosity=verbosity).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(main_entry())
