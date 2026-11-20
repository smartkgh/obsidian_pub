"""ASR 어댑터 공통 인터페이스 — 엔진 교체 경계"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path


class ASRError(RuntimeError):
    """전사 엔진 호출 실패"""


@dataclass
class Segment:
    start: float
    end: float
    text: str


@dataclass
class Transcript:
    segments: list[Segment] = field(default_factory=list)
    engine: str = "unknown"
    lang: str = "ko"
    duration: float = 0.0

    @property
    def text(self) -> str:
        return "\n".join(s.text for s in self.segments).strip()

    @property
    def char_count(self) -> int:
        return sum(len(s.text) for s in self.segments)


class ASRAdapter(ABC):
    """전사 엔진 어댑터.

    새 엔진을 붙일 때는 이 클래스를 상속해 transcribe() 만 구현하고
    adapters/__init__.py 의 make_adapter() 에 등록한다.
    """

    name: str = "base"
    needs_wav: bool = False   # True 면 파이프라인이 16kHz mono wav 로 변환해 넘긴다

    @abstractmethod
    def transcribe(self, audio: Path) -> Transcript:
        ...

    def describe(self) -> str:
        return f"{type(self).__name__}(name={self.name}, needs_wav={self.needs_wav})"
