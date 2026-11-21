"""단일 실행 락 — launchd 트리거와 수동 실행이 겹쳐도 두 프로세스가 같은 파일을 처리하지 않게 한다.

POSIX: fcntl.flock(비블로킹) / Windows: msvcrt.locking(비블로킹). 둘 다 실패하면 "이미 실행 중"으로 본다.
"""
from __future__ import annotations

import os
import sys
from contextlib import contextmanager
from pathlib import Path

if sys.platform == "win32":                       # pragma: no cover - 플랫폼 분기
    import msvcrt
else:
    import fcntl


class LockBusy(RuntimeError):
    """다른 프로세스가 이미 실행 중"""


@contextmanager
def single_instance(path: Path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(str(path), os.O_CREAT | os.O_RDWR, 0o644)
    try:
        try:
            if sys.platform == "win32":           # pragma: no cover
                msvcrt.locking(fd, msvcrt.LK_NBLCK, 1)
            else:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as exc:
            raise LockBusy(f"다른 recoding 프로세스가 실행 중입니다 ({path})") from exc

        os.truncate(fd, 0)
        os.write(fd, f"{os.getpid()}\n".encode())
        try:
            yield
        finally:
            try:
                if sys.platform == "win32":       # pragma: no cover
                    os.lseek(fd, 0, os.SEEK_SET)
                    msvcrt.locking(fd, msvcrt.LK_UNLCK, 1)
                else:
                    fcntl.flock(fd, fcntl.LOCK_UN)
            except OSError:
                pass
    finally:
        os.close(fd)
