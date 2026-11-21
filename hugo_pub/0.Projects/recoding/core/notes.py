"""Obsidian 노트 본문 유틸 — 섹션 추출"""
from __future__ import annotations

TRANSCRIPT_HEADING = "## 전사"


def section(text: str, heading: str) -> str:
    """`heading` 이후부터 다음 2단계 헤딩(`## `) 전까지의 본문. 없으면 빈 문자열."""
    if heading not in text:
        return ""
    rest = text.split(heading, 1)[1]
    cut = rest.find("\n## ")
    return (rest if cut < 0 else rest[:cut]).strip()


def transcript_section(text: str) -> str:
    """노트 md 에서 `## 전사` 섹션만 추출"""
    return section(text, TRANSCRIPT_HEADING)
