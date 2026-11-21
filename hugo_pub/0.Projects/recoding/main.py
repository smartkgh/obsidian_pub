#!/usr/bin/env python3
"""recoding — 음성 녹음 → Obsidian 노트 자동 전사 CLI

사용 예:
  python3 main.py doctor                # 환경 점검
  python3 main.py once                  # 안정화된 신규 파일 전부 처리
  python3 main.py once --limit 2        # 최대 2개만
  python3 main.py file "음성 001.m4a"    # 지정 파일 1개 즉시 처리
  python3 main.py watch                 # 상주 감시(폴링)
  python3 main.py list                  # 처리 이력
  python3 main.py bootstrap             # 현재 파일 전부 ignored (기존분 일괄 처리 방지)
  python3 main.py reset --all           # 이력 초기화(재처리 가능)
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MIN_PY = (3, 11)

VENV_PYTHONS = (ROOT / ".venv/bin/python3", ROOT / ".venv/Scripts/python.exe")


def _ensure_interpreter() -> None:
    """시스템 파이썬(3.9 등)으로 실행되면 프로젝트 venv 파이썬으로 자기 자신을 재실행한다."""
    if sys.version_info >= MIN_PY:
        return
    # 재실행 대상 = 원래 진입 스크립트(main.py / run_tests.py …)
    entry = Path(sys.argv[0]).resolve() if sys.argv and sys.argv[0] else ROOT / "main.py"
    if not entry.exists():
        entry = ROOT / "main.py"
    for candidate in VENV_PYTHONS:
        if candidate.exists():
            os.execv(str(candidate), [str(candidate), str(entry), *sys.argv[1:]])
    sys.exit(
        f"Python {MIN_PY[0]}.{MIN_PY[1]}+ 가 필요합니다 (현재 {sys.version.split()[0]}).\n"
        f"  가상환경 생성: ~/.pyenv/versions/3.12.3/bin/python3 -m venv {ROOT}/.venv"
    )


_ensure_interpreter()

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import argparse  # noqa: E402
import shutil  # noqa: E402
import subprocess  # noqa: E402
import time  # noqa: E402
import unicodedata  # noqa: E402

from core import render  # noqa: E402
from core.config import Config  # noqa: E402
from core.lock import LockBusy, single_instance  # noqa: E402
from core.log import setup  # noqa: E402
from core.pipeline import Pipeline, file_sha1  # noqa: E402

MUTATING_COMMANDS = {"once", "watch", "file", "bootstrap", "reset"}

PY_OK = sys.version_info >= MIN_PY


def nfc(text: str) -> str:
    return unicodedata.normalize("NFC", str(text))


# ---------------------------------------------------------------- doctor
def cmd_doctor(cfg: Config, log, args) -> int:
    ok = True
    print(f"python        : {sys.version.split()[0]} {'OK' if PY_OK else 'NG (3.11+ 필요)'}")
    ok &= PY_OK

    for section, key in (("audio", "ffmpeg"), ("audio", "ffprobe")):
        try:
            path = cfg.command(section, key)
            found = shutil.which(path) or Path(path).exists()
        except KeyError:
            found, path = False, "(미설정)"
        print(f"{key:<14}: {path} {'OK' if found else 'NG'}")
        ok &= bool(found)

    for label, section, key in (
        ("incoming", "paths", "incoming"),
        ("output", "paths", "output"),
        ("state", "paths", "state"),
    ):
        path = cfg.path(section, key)
        exists = path.exists()
        writable = exists and os.access(path, os.W_OK)
        print(f"{label:<14}: {path} {'OK' if writable else ('읽기전용' if exists else 'NG(없음)')}")
        ok &= writable

    try:
        pipe = Pipeline(cfg, log, dry_run=True)
        print(f"asr engine    : {pipe.adapter.describe()} OK")
        print(f"settle        : {pipe.settle}s / min_duration {pipe.min_duration}s")
    except Exception as exc:                     # noqa: BLE001
        print(f"asr engine    : NG — {exc}")
        return 1

    api_env = str(cfg.get("keyword", "api_key_env", "DEEPSEEK_API_KEY"))
    has_key = bool(os.environ.get(api_env))
    print(f"keyword LLM   : {cfg.get('keyword', 'provider')} / key {api_env} "
          f"{'설정됨' if has_key else '없음 → 휴리스틱 폴백'}")

    stats = pipe.ledger.stats()
    print("ledger        : " + (", ".join(f"{k}={v}" for k, v in sorted(stats.items())) or "비어있음"))
    return 0 if ok else 1


# ------------------------------------------------------------------ list
def cmd_list(cfg: Config, log, args) -> int:
    pipe = Pipeline(cfg, log, dry_run=True)
    rows = pipe.ledger.rows()[: args.limit]
    if not rows:
        print("이력 없음")
        return 0
    print(f"{'status':<12}{'dur':>7}  {'keyword':<16}{'file':<34}engine")
    print("-" * 96)
    for row in rows:
        dur = render.fmt_duration(row["duration"] or 0)
        print(f"{row['status']:<12}{dur:>7}  {nfc(row['keyword'] or '-')[:15]:<16}"
              f"{nfc(row['filename'])[:33]:<34}{row['engine'] or '-'}")
    print("-" * 96)
    print(" / ".join(f"{k}={v}" for k, v in sorted(pipe.ledger.stats().items())))
    return 0


# -------------------------------------------------------------- commands
def cmd_once(cfg: Config, log, args) -> int:
    pipe = Pipeline(cfg, log, dry_run=args.dry_run)
    results = pipe.run_once(limit=args.limit, include_failed=args.retry, wait_settle=True)
    if not results:
        print("처리 대상 없음 (신규 파일은 다음 주기에 처리됩니다)")
        return 0
    for res in results:
        if res.status == "done":
            print(f"✓ {nfc(res.filename)} → {res.out_path.name if res.out_path else '-'}"
                  f"  [{res.keyword}]")
        else:
            print(f"· {nfc(res.filename)} → {res.status} {res.error or ''}")
    return 0 if all(r.status in ("done", "skipped") for r in results) else 1


def cmd_file(cfg: Config, log, args) -> int:
    pipe = Pipeline(cfg, log, dry_run=args.dry_run)
    target = Path(os.path.expanduser(args.target))
    if not target.exists():
        for base in (pipe.incoming, pipe.done_dir, pipe.failed_dir):
            candidate = base / nfc(args.target)
            if candidate.exists():
                target = candidate
                break
    if not target.exists():
        # NFD 파일명 매칭 (macOS)
        import unicodedata as ud

        want = ud.normalize("NFD", args.target)
        for base in (pipe.incoming, pipe.done_dir, pipe.failed_dir):
            if not base.exists():
                continue
            for path in base.iterdir():
                if ud.normalize("NFD", path.name) == want:
                    target = path
                    break
            if target.exists():
                break
    if not target.exists():
        print(f"파일을 찾을 수 없습니다: {args.target}", file=sys.stderr)
        return 2

    res = pipe.process(target)
    if res.status == "done":
        print(f"✓ {nfc(res.filename)} → {res.out_path.name if res.out_path else '-'}")
        print(f"  키워드: {res.keyword} / 요약: {res.provider} / {res.duration:.1f}s / {res.elapsed_ms}ms")
        return 0
    print(f"✗ {nfc(res.filename)} → {res.status}: {res.error}", file=sys.stderr)
    return 1


def cmd_watch(cfg: Config, log, args) -> int:
    pipe = Pipeline(cfg, log, dry_run=args.dry_run)
    interval = int(cfg.get("watch", "interval_seconds", 30))
    print(f"감시 시작: {pipe.incoming} (폴링 {interval}s, Ctrl-C 종료)")
    try:
        while True:
            for res in pipe.run_once(limit=args.limit, include_failed=False):
                print(f"{res.status}: {nfc(res.filename)} {res.keyword or res.error or ''}")
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\n종료")
        return 0


def cmd_bootstrap(cfg: Config, log, args) -> int:
    pipe = Pipeline(cfg, log, dry_run=args.dry_run)
    count = pipe.bootstrap()
    print(f"ignored 로 등록: {count}개 (기존 파일은 자동 처리되지 않습니다)")
    return 0


def cmd_reset(cfg: Config, log, args) -> int:
    pipe = Pipeline(cfg, log, dry_run=True)
    if args.all:
        rows = pipe.ledger.rows()
        for row in rows:
            pipe.ledger.delete(row["sha1"])
        print(f"이력 삭제: {len(rows)}건")
        return 0
    if not args.target:
        print("--all 또는 파일명을 지정하세요", file=sys.stderr)
        return 2
    target = Path(os.path.expanduser(args.target))
    if not target.exists():
        for base in (pipe.incoming, pipe.done_dir, pipe.failed_dir):
            candidate = base / nfc(args.target)
            if candidate.exists():
                target = candidate
                break
    if not target.exists():
        print(f"파일 없음: {args.target}", file=sys.stderr)
        return 2
    pipe.ledger.delete(file_sha1(target))
    print(f"이력 삭제: {nfc(target.name)}")
    return 0


def cmd_helper(cfg: Config, log, args) -> int:
    """macOS SpeechHelper 직접 호출 (디버깅용)"""
    helper = cfg.path("asr.apple", "helper")
    cmd = [str(helper), *args.helper_args]
    return subprocess.call(cmd)


# ------------------------------------------------------------------ main
def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="recoding", description="음성 녹음 → Obsidian 자동 전사"
    )
    parser.add_argument("--config", help="config.toml 경로 (기본: 프로젝트 루트)")
    parser.add_argument("-v", "--verbose", action="store_true", help="DEBUG 로그")
    parser.add_argument("-n", "--dry-run", action="store_true", help="파일 쓰기·이동 없이 실행")

    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("doctor", help="환경 점검")
    sub.add_parser("bootstrap", help="현재 파일을 ignored 등록(기존분 보호)")

    p_once = sub.add_parser("once", help="신규 파일 처리 후 종료")
    p_once.add_argument("--limit", type=int, default=None, help="최대 처리 개수")
    p_once.add_argument("--retry", action="store_true", help="failed 상태도 재시도")

    p_file = sub.add_parser("file", help="지정 파일 1개 처리")
    p_file.add_argument("target", help="파일 경로 또는 수신 폴더 내 파일명")

    p_watch = sub.add_parser("watch", help="상주 감시(폴링)")
    p_watch.add_argument("--limit", type=int, default=None)

    p_list = sub.add_parser("list", help="처리 이력")
    p_list.add_argument("--limit", type=int, default=30)

    p_reset = sub.add_parser("reset", help="이력 삭제(재처리 허용)")
    p_reset.add_argument("target", nargs="?", help="파일명")
    p_reset.add_argument("--all", action="store_true", help="전체 이력 삭제")

    p_helper = sub.add_parser("helper", help="SpeechHelper 직접 호출(디버깅)")
    p_helper.add_argument("helper_args", nargs=argparse.REMAINDER)

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    cfg = Config.load(args.config)

    log_dir = cfg.path("paths", "state") / "logs"
    log = setup(log_dir, verbose=args.verbose)

    handlers = {
        "doctor": cmd_doctor,
        "list": cmd_list,
        "once": cmd_once,
        "file": cmd_file,
        "watch": cmd_watch,
        "bootstrap": cmd_bootstrap,
        "reset": cmd_reset,
        "helper": cmd_helper,
    }
    handler = handlers[args.command]
    if args.command not in MUTATING_COMMANDS:
        return handler(cfg, log, args)

    # launchd 트리거와 수동 실행이 겹쳐도 같은 파일을 두 번 처리하지 않도록 단일 실행 보장
    try:
        with single_instance(cfg.path("paths", "state") / "lock"):
            return handler(cfg, log, args)
    except LockBusy as exc:
        print(f"건너뜀: {exc}", file=sys.stderr)
        return 0


if __name__ == "__main__":
    sys.exit(main())
