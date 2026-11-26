"""처리 이력 ledger (SQLite, WAL) — 중복 방지 + 상태 복구"""
from __future__ import annotations

import sqlite3
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable

SCHEMA = """
CREATE TABLE IF NOT EXISTS files (
    sha1        TEXT PRIMARY KEY,
    filename    TEXT NOT NULL,
    size        INTEGER NOT NULL,
    mtime       REAL NOT NULL,
    duration    REAL,
    status      TEXT NOT NULL,          -- new|pending|transcribing|done|failed|skipped|ignored
    engine      TEXT,
    keyword     TEXT,
    summary     TEXT,
    out_path    TEXT,
    elapsed_ms  INTEGER,
    error       TEXT,
    seen_size   INTEGER,
    seen_mtime  REAL,
    seen_at     REAL,
    created_at  TEXT NOT NULL,
    updated_at  TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_files_status ON files(status);
"""

STATUSES = ("new", "pending", "transcribing", "done", "failed", "skipped", "ignored")


def now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


class Ledger:
    def __init__(self, path: Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(self.path), timeout=30)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.execute("PRAGMA synchronous=NORMAL")
        self.conn.executescript(SCHEMA)
        self.conn.commit()

    # --- 읽기 -------------------------------------------------------------
    def get(self, sha1: str) -> sqlite3.Row | None:
        cur = self.conn.execute("SELECT * FROM files WHERE sha1 = ?", (sha1,))
        return cur.fetchone()

    def rows(self, status: str | Iterable[str] | None = None) -> list[sqlite3.Row]:
        if status is None:
            cur = self.conn.execute("SELECT * FROM files ORDER BY created_at DESC")
        elif isinstance(status, str):
            cur = self.conn.execute(
                "SELECT * FROM files WHERE status = ? ORDER BY created_at DESC", (status,)
            )
        else:
            marks = ",".join("?" * len(list(status)))
            cur = self.conn.execute(
                f"SELECT * FROM files WHERE status IN ({marks}) ORDER BY created_at DESC",
                tuple(status),
            )
        return cur.fetchall()

    def stats(self) -> dict[str, int]:
        cur = self.conn.execute("SELECT status, COUNT(*) FROM files GROUP BY status")
        return {row[0]: row[1] for row in cur.fetchall()}

    def count(self, statuses: Iterable[str]) -> int:
        statuses = list(statuses)
        if not statuses:
            return 0
        marks = ",".join("?" * len(statuses))
        cur = self.conn.execute(
            f"SELECT COUNT(*) FROM files WHERE status IN ({marks})", tuple(statuses)
        )
        return int(cur.fetchone()[0])

    def keywords(self, limit: int = 200) -> list[str]:
        cur = self.conn.execute(
            "SELECT keyword FROM files WHERE keyword IS NOT NULL ORDER BY updated_at DESC LIMIT ?",
            (limit,),
        )
        return [r[0] for r in cur.fetchall() if r[0]]

    # --- 쓰기 -------------------------------------------------------------
    def insert_seen(self, sha1: str, filename: str, size: int, mtime: float,
                    status: str = "new") -> None:
        ts = now_iso()
        self.conn.execute(
            """INSERT INTO files (sha1, filename, size, mtime, status,
                                  seen_size, seen_mtime, seen_at, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
               ON CONFLICT(sha1) DO NOTHING""",
            (sha1, filename, size, mtime, status, size, mtime, time.time(), ts, ts),
        )
        self.conn.commit()

    def update(self, sha1: str, **fields: Any) -> None:
        if not fields:
            return
        fields["updated_at"] = now_iso()
        keys = ", ".join(f"{k} = ?" for k in fields) 
        self.conn.execute(f"UPDATE files SET {keys} WHERE sha1 = ?", (*fields.values(), sha1))
        self.conn.commit()

    def set_status(self, sha1: str, status: str, **fields: Any) -> None:
        assert status in STATUSES, status
        self.update(sha1, status=status, **fields)

    def delete(self, sha1: str) -> None:
        self.conn.execute("DELETE FROM files WHERE sha1 = ?", (sha1,))
        self.conn.commit()

    def close(self) -> None:
        self.conn.close()
