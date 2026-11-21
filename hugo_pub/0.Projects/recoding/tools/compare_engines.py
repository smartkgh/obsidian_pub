#!/usr/bin/env python3
"""두 엔진 전사 비교 — apple(SpeechTranscriber) vs whispercpp

이미 처리된 노트(result/*.md)의 전사문과, 같은 원본을 whisper-cli 로 다시 전사한 결과를
나란히 비교한다. 원본·노트·ledger 는 읽기만 하고 수정하지 않는다.

사용:
  python3 tools/compare_engines.py                     # 기본 3개
  python3 tools/compare_engines.py "음성 002.m4a" …    # 지정 파일
  결과물: /tmp/engin-compare/{이름}.{apple,whisper}.txt + 요약 표(stdout)
"""
from __future__ import annotations

import difflib
import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from core import render  # noqa: E402
from core.config import Config  # noqa: E402
from core.log import setup  # noqa: E402
from core.notes import transcript_section  # noqa: E402
from core.pipeline import Pipeline, file_sha1  # noqa: E402

OUT = Path("/tmp/engin-compare")
DEFAULT = ["음성 002.m4a", "음성 007.m4a", "음성 003.m4a", "음성 261117_180209.m4a"]


def whisper_config(base: Config) -> Config:
    data = {k: (dict(v) if isinstance(v, dict) else v) for k, v in base.data.items()}
    data["asr"]["engine"] = "whispercpp"
    return Config(data, base.root)


def norm(text: str) -> str:
    return re.sub(r"\s+", "", text)


def find_source(pipe: Pipeline, name: str) -> Path:
    for base in (pipe.incoming, pipe.done_dir, pipe.failed_dir):
        candidate = base / name
        if candidate.exists():
            return candidate
    raise SystemExit(f"원본을 찾을 수 없습니다: {name}")


def main(argv: list[str]) -> int:
    base = Config.load(ROOT / "config.toml")
    log = setup(base.path("paths", "state") / "logs")
    apple_pipe = Pipeline(base, log, dry_run=True)
    whisper_pipe = Pipeline(whisper_config(base), log, dry_run=True)
    targets = argv[1:] or DEFAULT
    OUT.mkdir(parents=True, exist_ok=True)

    rows = []
    for name in targets:
        src = find_source(apple_pipe, name)
        sha1 = file_sha1(src)
        row = apple_pipe.ledger.get(sha1)
        if row is None or not row["out_path"]:
            print(f"건너뜀(노트 없음): {name}")
            continue
        note = Path(row["out_path"])
        apple_text = transcript_section(note.read_text(encoding="utf-8"))
        duration = row["duration"] or 0.0

        # whisper 재전사
        started = time.time()
        wav = whisper_pipe.to_wav(src)
        try:
            tr = whisper_pipe.adapter.transcribe(wav)
        finally:
            wav.unlink(missing_ok=True)
        elapsed = time.time() - started
        whisper_text = tr.text

        stem = note.stem
        (OUT / f"{stem}.apple.txt").write_text(apple_text, encoding="utf-8")
        (OUT / f"{stem}.whisper.txt").write_text(whisper_text, encoding="utf-8")

        sim = difflib.SequenceMatcher(None, norm(apple_text), norm(whisper_text)).ratio()
        rows.append({
            "name": name, "stem": stem, "duration": duration,
            "apple_chars": len(norm(apple_text)), "whisper_chars": len(norm(whisper_text)),
            "apple_ms": row["elapsed_ms"] or 0, "whisper_s": elapsed,
            "apple_seg": apple_text.count("\n\n") + 1, "whisper_seg": len(tr.segments),
            "ratio": sim,
        })
        print(f"✓ {stem}: {render.fmt_duration(duration)} · "
              f"apple {len(norm(apple_text)):,}자 / whisper {len(norm(whisper_text)):,}자 · "
              f"유사도 {sim:.0%} · whisper {elapsed:.1f}s")

    print("\n| 파일 | 길이 | Apple(자/ms) | whisper(자/초) | 유사도 |")
    print("|---|---|---|---|---|")
    for r in rows:
        print(f"| {r['stem']} | {render.fmt_duration(r['duration'])} | "
              f"{r['apple_chars']:,} / {r['apple_ms']:,} | "
              f"{r['whisper_chars']:,} / {r['whisper_s']:.1f}s | {r['ratio']:.0%} |")
    print(f"\n전사문 저장: {OUT}/")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
