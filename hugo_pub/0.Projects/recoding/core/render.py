"""Obsidian 노트 렌더링 · 파일명 규칙"""
from __future__ import annotations

import re
import unicodedata
from datetime import datetime
from pathlib import Path

from adapters.base import Segment

FORBIDDEN = set('/\\:*?"<>|')
BAD_TAG = re.compile(r"[\s#\[\]{},]+")


def nfc(text: str) -> str:
    return unicodedata.normalize("NFC", str(text))


def safe_filename(text: str, max_chars: int = 40) -> str:
    """파일명으로 쓸 수 있는 형태로 정리 (NFC · 금지문자 제거 · 길이 제한)"""
    name = nfc(text).strip()
    name = "".join("_" if ch in FORBIDDEN else ch for ch in name)
    name = re.sub(r"\s+", " ", name).strip(" ._")
    if len(name) > max_chars:
        name = name[:max_chars].rstrip(" ._")
    return name or "녹음"


def safe_tag(text: str) -> str:
    tag = BAD_TAG.sub("_", nfc(text).strip())
    return tag.strip("_") or "recoding"


def unique_path(directory: Path, stem: str, suffix: str = ".md") -> Path:
    """중복 시 -2, -3 …"""
    candidate = directory / f"{stem}{suffix}"
    index = 2
    while candidate.exists():
        candidate = directory / f"{stem}-{index}{suffix}"
        index += 1
    return candidate


def fmt_duration(seconds: float) -> str:
    total = int(round(seconds or 0))
    h, rem = divmod(total, 3600)
    m, s = divmod(rem, 60)
    return f"{h:02d}:{m:02d}:{s:02d}"


def fmt_ts(seconds: float) -> str:
    total = int(seconds or 0)
    h, rem = divmod(total, 3600)
    m, s = divmod(rem, 60)
    return f"{h:d}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"


def yaml_str(value: str) -> str:
    text = nfc(str(value)).replace('"', '\\"')
    return f'"{text}"'


def paragraphs(segments: list[Segment], gap: float = 3.0, max_chars: int = 500) -> list[str]:
    """시간 간격/길이 기준으로 문단 묶음"""
    out: list[str] = []
    buf = ""
    prev_end = None
    for seg in segments:
        text = seg.text.strip()
        if not text:
            continue
        if buf and prev_end is not None and seg.start - prev_end >= gap:
            out.append(buf.strip())
            buf = ""
        if buf and not buf.endswith((" ", "\n")):
            buf += " "
        buf += text
        prev_end = seg.end
        if len(buf) >= max_chars:
            out.append(buf.strip())
            buf = ""
            prev_end = None
    if buf.strip():
        out.append(buf.strip())
    return out


def render_note(
    *,
    keyword: str,
    summary: str,
    source_name: str,
    recorded: datetime,
    duration: float,
    transcribed: datetime,
    engine: str,
    lang: str,
    segments: list[Segment],
    include_timestamps: bool,
    include_summary: bool,
    transcript_body: str | None = None,
) -> str:
    title = nfc(keyword)
    lines: list[str] = ["---"]
    lines.append(f"title: {yaml_str(title)}")
    lines.append(f"source: {yaml_str(source_name)}")
    lines.append(f"recorded: {recorded.isoformat(timespec='seconds')}")
    lines.append(f"duration: {fmt_duration(duration)}")
    lines.append(f"transcribed: {transcribed.isoformat(timespec='seconds')}")
    lines.append(f"engine: {yaml_str(engine)}")
    lines.append(f"lang: {lang}")
    lines.append("tags:")
    lines.append("  - recoding")
    lines.append(f"  - {safe_tag(keyword)}")
    lines.append("---")
    lines.append("")
    lines.append(f"# {title}")
    lines.append("")

    if include_summary and summary:
        lines.append("> [!quote] 핵심 한 줄")
        lines.append(f"> {nfc(summary).strip()}")
        lines.append("")

    lines.append("## 전사")
    lines.append("")
    if transcript_body:
        for para in transcript_body.strip().split("\n\n"):
            para = para.strip()
            if para:
                lines.append(para)
                lines.append("")
    else:
        for para in paragraphs(segments):
            lines.append(para)
            lines.append("")

    if include_timestamps and len(segments) > 1:
        lines.append("## 구간")
        lines.append("")
        for seg in segments:
            text = nfc(seg.text).strip()
            if text:
                lines.append(f"- {fmt_ts(seg.start)} {text}")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"
