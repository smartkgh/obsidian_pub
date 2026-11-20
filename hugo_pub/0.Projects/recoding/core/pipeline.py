"""파이프라인 오케스트레이션: 감지 → 안정화 → 중복 → 전사 → 정리 → 키워드 → 저장 → 아카이브"""
from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import time
import unicodedata
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from adapters import ASRError, Segment, make_adapter

from . import keyword, render, spacing
from .ledger import Ledger

AUDIO_EXT = {".m4a", ".mp3", ".wav", ".caf", ".aac", ".flac", ".ogg", ".m4b", ".mp4", ".amr"}
ACTIVE_STATUSES = ("new", "pending", "transcribing")


class CorruptFileError(RuntimeError):
    """디코딩 불가 / 손상 파일"""


def nfc(text: str) -> str:
    return unicodedata.normalize("NFC", str(text))


def file_sha1(path: Path, chunk_size: int = 1 << 20) -> str:
    digest = hashlib.sha1()
    with open(path, "rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


@dataclass
class Result:
    status: str
    sha1: str
    filename: str
    keyword: str | None = None
    out_path: Path | None = None
    duration: float = 0.0
    elapsed_ms: int = 0
    provider: str | None = None
    error: str | None = None
    segments: list[Segment] = field(default_factory=list, repr=False)


def clean_segments(segments: list[Segment]) -> list[Segment]:
    """빈 세그먼트·연속 중복·무음 환각 제거"""
    cleaned: list[Segment] = []
    prev = None
    for seg in segments:
        text = " ".join(str(seg.text).split())
        if not text or text == prev:
            continue
        cleaned.append(Segment(start=seg.start, end=seg.end, text=text))
        prev = text
    if len(cleaned) > 1:
        cleaned = [s for s in cleaned if not keyword.is_hallucination(s.text)]
    return cleaned


class Pipeline:
    def __init__(self, cfg, log, dry_run: bool = False):
        self.cfg = cfg
        self.log = log
        self.dry_run = dry_run

        self.incoming = cfg.path("paths", "incoming")
        self.outdir = cfg.path("paths", "output")
        self.statedir = cfg.path("paths", "state")
        self.tmpdir = self.statedir / "tmp"
        self.done_dir = cfg.path("archive", "done_dir", str(self.incoming / "_done"))
        self.failed_dir = cfg.path("archive", "failed_dir", str(self.incoming / "_failed"))

        for directory in (self.incoming, self.outdir, self.statedir, self.tmpdir,
                          self.done_dir, self.failed_dir):
            directory.mkdir(parents=True, exist_ok=True)

        self.ledger = Ledger(self.statedir / "ledger.sqlite")
        self.adapter = make_adapter(cfg)

        self.min_duration = float(cfg.get("asr", "min_duration", 3.0))
        self.settle = float(cfg.get("asr", "settle_seconds", 10))
        self.move_originals = bool(cfg.get("archive", "move_originals", True))
        self.ffmpeg = cfg.command("audio", "ffmpeg", "ffmpeg")
        self.ffprobe = cfg.command("audio", "ffprobe", "ffprobe")
        self.last_new_count = 0

    # ------------------------------------------------------------------ 감지
    def iter_audio(self, directory: Path | None = None):
        directory = directory or self.incoming
        if not directory.exists():
            return
        for path in sorted(directory.iterdir(), key=lambda p: p.stat().st_mtime):
            if not path.is_file():
                continue
            name = path.name
            if name.startswith("."):           # .stfolder, .syncthing.*.tmp, .DS_Store
                continue
            if path.suffix.lower() not in AUDIO_EXT:
                continue
            yield path

    def scan(self, include_failed: bool = False) -> list[tuple[Path, str, dict]]:
        """안정화(size+mtime 2회 동일) 통과한 파일만 반환"""
        ready: list[tuple[Path, str, dict]] = []
        now = time.time()
        self.last_new_count = 0

        for path in self.iter_audio():
            try:
                stat = path.stat()
                sha1 = file_sha1(path)
            except (FileNotFoundError, PermissionError):
                # Syncthing 재동기화·백신 잠금 등으로 사라지거나 읽을 수 없으면 다음 주기로
                self.log.debug("스캔 중 사라짐/잠김: %s", path.name)
                continue
            row = self.ledger.get(sha1)

            if row is None:
                self.ledger.insert_seen(sha1, nfc(path.name), stat.st_size, stat.st_mtime)
                self.last_new_count += 1
                self.log.info("신규 감지: %s (안정화 후 처리)", nfc(path.name))
                continue

            status = row["status"]
            if status == "done":
                if self.move_originals and not self.dry_run:
                    self._archive(path)
                    self.log.info("이미 처리된 파일 → _done/ 이동: %s", nfc(path.name))
                continue
            if status == "skipped" and not include_failed:
                if self.move_originals and not self.dry_run:
                    self._archive(path)
                continue
            if status in ("ignored",):
                continue
            if status == "failed":
                if not include_failed:
                    continue
                self.ledger.set_status(sha1, "pending", error=None)
                row = self.ledger.get(sha1) or row
                status = "pending"
            if status not in ACTIVE_STATUSES:
                continue

            changed = (
                row["seen_size"] != stat.st_size
                or abs((row["seen_mtime"] or 0) - stat.st_mtime) > 1e-6
            )
            if changed:
                self.ledger.update(sha1, seen_size=stat.st_size,
                                   seen_mtime=stat.st_mtime, seen_at=now)
                continue
            if now - float(row["seen_at"] or 0) < self.settle:
                continue

            ready.append((path, sha1, dict(row)))

        return ready

    # -------------------------------------------------------------- 전처리
    def probe_duration(self, path: Path) -> float:
        cmd = [self.ffprobe, "-v", "error", "-show_entries", "format=duration",
               "-of", "csv=p=0", str(path)]
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        except (subprocess.TimeoutExpired, OSError) as exc:
            raise CorruptFileError(f"ffprobe 실행 실패: {exc}") from exc
        out = (proc.stdout or "").strip()
        if proc.returncode != 0 or not out:
            raise CorruptFileError(f"ffprobe 실패: {(proc.stderr or '').strip()[:200]}")
        try:
            return float(out.splitlines()[0])
        except ValueError as exc:
            raise CorruptFileError(f"duration 파싱 실패: {out!r}") from exc

    def to_wav(self, path: Path) -> Path:
        wav = self.tmpdir / (file_sha1(path)[:16] + ".wav")
        cmd = [self.ffmpeg, "-nostdin", "-y", "-i", str(path),
               "-ac", "1", "-ar", "16000", "-c:a", "pcm_s16le", str(wav)]
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)
        if proc.returncode != 0 or not wav.exists():
            raise ASRError(f"ffmpeg 변환 실패: {(proc.stderr or '').strip().splitlines()[-1:]}"
                           ) from None
        return wav

    # ---------------------------------------------------------------- 처리
    def process(self, path: Path, sha1: str | None = None) -> Result:
        started = time.time()
        path = Path(path)
        name = nfc(path.name)
        sha1 = sha1 or file_sha1(path)

        row = self.ledger.get(sha1)
        if row is None:
            stat = path.stat()
            self.ledger.insert_seen(sha1, name, stat.st_size, stat.st_mtime, status="pending")

        self.log.info("처리 시작: %s", name)
        self.ledger.set_status(sha1, "transcribing", filename=name, error=None)

        tmp_files: list[Path] = []
        try:
            duration = self.probe_duration(path)
            self.ledger.update(sha1, duration=duration)

            if duration < self.min_duration:
                self.log.info("skip(짧음): %s %.1fs < %.1fs", name, duration, self.min_duration)
                self.ledger.set_status(sha1, "skipped", error=f"too short {duration:.1f}s")
                if self.move_originals and not self.dry_run:
                    self._archive(path)
                return Result("skipped", sha1, name, duration=duration)

            audio = path
            if self.adapter.needs_wav:
                audio = self.to_wav(path)
                tmp_files.append(audio)

            transcript = self.adapter.transcribe(audio)
            segments = clean_segments(transcript.segments)
            if not segments:
                raise ASRError("전사 결과가 비어 있음 (무음 또는 인식 실패)")

            text = "\n".join(seg.text for seg in segments)
            kw, summary, provider = keyword.generate(text, self.cfg, self.log)

            body_text = "\n\n".join(render.paragraphs(segments))
            body_text = spacing.fix_spacing(body_text, self.cfg, self.log)

            recorded = datetime.fromtimestamp(path.stat().st_mtime).astimezone()
            now = datetime.now().astimezone()
            body = render.render_note(
                keyword=kw,
                summary=summary,
                source_name=name,
                recorded=recorded,
                duration=duration or transcript.duration,
                transcribed=now,
                engine=transcript.engine,
                lang=transcript.lang,
                segments=segments,
                include_timestamps=bool(self.cfg.get("output", "include_timestamps", True)),
                include_summary=bool(self.cfg.get("output", "include_summary", True)),
                transcript_body=body_text,
            )

            stem = self.output_stem(kw, recorded)
            out_path = render.unique_path(self.outdir, stem)

            if self.dry_run:
                self.log.info("[dry-run] %s → %s.md (%d자)", name, out_path.stem, len(text))
            else:
                self.outdir.mkdir(parents=True, exist_ok=True)
                out_path.write_text(body, encoding="utf-8")
                if bool(self.cfg.get("output", "raw_json", True)):
                    self._save_raw(out_path, transcript, segments, kw, summary, name)
                if self.move_originals:
                    self._archive(path)

            elapsed = int((time.time() - started) * 1000)
            if self.dry_run:
                # dry-run 은 이력을 'done' 으로 확정하지 않는다(다음 실행에서 다시 대상이 되도록)
                self.ledger.set_status(sha1, "pending", error="dry-run")
            else:
                self.ledger.set_status(
                    sha1, "done", engine=transcript.engine, keyword=kw, summary=summary,
                    out_path=str(out_path), elapsed_ms=elapsed, error=None,
                )
            self.log.info("완료: %s → %s.md (키워드 %s, %s, %.1fs, %dms)",
                          name, out_path.stem, kw, provider, duration, elapsed)
            return Result("done", sha1, name, kw, out_path, duration, elapsed,
                          provider=provider, segments=segments)

        except Exception as exc:                       # noqa: BLE001 — 어떤 실패든 기록
            elapsed = int((time.time() - started) * 1000)
            self.ledger.set_status(sha1, "failed", error=str(exc)[:500], elapsed_ms=elapsed)
            self.log.error("실패: %s — %s", name, exc)
            if isinstance(exc, CorruptFileError) and not self.dry_run:
                try:
                    self._move(path, self.failed_dir)
                    self.log.info("손상 파일 → _failed/: %s", name)
                except OSError:
                    pass
            return Result("failed", sha1, name, error=str(exc), elapsed_ms=elapsed)

        finally:
            for tmp in tmp_files:
                try:
                    tmp.unlink(missing_ok=True)
                except OSError:
                    pass

    # ---------------------------------------------------------------- 출력
    def output_stem(self, kw: str, recorded: datetime) -> str:
        template = str(self.cfg.get("output", "filename", "{keyword}"))
        raw = template.format(
            keyword=kw,
            date=recorded.strftime("%Y-%m-%d"),
            time=recorded.strftime("%H%M"),
        )
        max_chars = int(self.cfg.get("output", "max_keyword_chars", 40))
        return render.safe_filename(raw, max_chars + 12)

    def _save_raw(self, out_path: Path, transcript, segments, kw, summary, source_name) -> None:
        raw_dir = self.outdir / "_raw"
        raw_dir.mkdir(parents=True, exist_ok=True)
        payload = {
            "keyword": kw,
            "summary": summary,
            "source": source_name,
            "engine": transcript.engine,
            "lang": transcript.lang,
            "duration": transcript.duration,
            "segments": [
                {"start": round(s.start, 3), "end": round(s.end, 3), "text": s.text}
                for s in segments
            ],
        }
        (raw_dir / f"{out_path.stem}.json").write_text(
            json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    # ------------------------------------------------------------ 아카이브
    def _move(self, src: Path, dest_dir: Path) -> Path:
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest = dest_dir / src.name
        index = 2
        while dest.exists():
            dest = dest_dir / f"{src.stem}-{index}{src.suffix}"
            index += 1
        shutil.move(str(src), str(dest))
        return dest

    def _archive(self, path: Path) -> Path | None:
        if path.parent == self.done_dir:        # 이미 아카이브 안에 있으면 그대로
            return path
        try:
            return self._move(path, self.done_dir)
        except (OSError, FileNotFoundError) as exc:
            self.log.warning("아카이브 실패(무시): %s — %s", path.name, exc)
            return None

    # ---------------------------------------------------------------- 실행
    def run_once(self, limit: int | None = None, include_failed: bool = False,
                 wait_settle: bool = False) -> list[Result]:
        ready = self.scan(include_failed=include_failed)

        # 방금 등록된(new/pending) 파일이 있으면 같은 실행 안에서 안정화 대기 후 재확인한다.
        # → launchd WatchPaths 가 한 번만 트리거해도 10초 뒤 바로 처리된다.
        if not ready and wait_settle and self.last_new_count > 0:
            self.log.info("안정화 대기 %ds 후 재확인", int(self.settle))
            time.sleep(self.settle + 1)
            ready = self.scan(include_failed=include_failed)

        if limit:
            ready = ready[:limit]
        if not ready:
            self.log.debug("처리할 파일 없음")
            return []
        return [self.process(path, sha1) for path, sha1, _row in ready]

    def bootstrap(self) -> int:
        """현재 폴더에 있는 파일을 'ignored'로 등록 — 기존 파일 일괄 처리 방지"""
        count = 0
        for path in self.iter_audio():
            stat = path.stat()
            sha1 = file_sha1(path)
            row = self.ledger.get(sha1)
            if row is None:
                self.ledger.insert_seen(sha1, nfc(path.name), stat.st_size,
                                        stat.st_mtime, status="ignored")
                count += 1
                self.log.info("ignored 등록: %s", nfc(path.name))
            elif row["status"] in ACTIVE_STATUSES:
                self.ledger.set_status(sha1, "ignored")
                count += 1
                self.log.info("ignored 전환: %s", nfc(path.name))
        return count
