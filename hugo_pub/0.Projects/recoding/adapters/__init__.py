"""ASR 어댑터 팩토리 — 엔진 교체 지점(유일한 플랫폼 분기 지점)"""
from __future__ import annotations

import sys

from .base import ASRAdapter, ASRError, Segment, Transcript

ENGINES = ("apple", "whispercpp")


def make_adapter(cfg) -> ASRAdapter:
    engine = str(cfg.get("asr", "engine", "apple")).strip().lower()

    if engine == "apple":
        if sys.platform != "darwin":
            raise ASRError(
                f"engine='apple' 은 macOS 전용입니다 (현재 {sys.platform}). "
                f"config.toml 의 asr.engine 을 'whispercpp' 로 바꾸세요."
            )
        from .asr_apple import AppleSpeechAdapter

        return AppleSpeechAdapter(cfg)

    if engine == "whispercpp":
        from .asr_whispercpp import WhisperCppAdapter

        return WhisperCppAdapter(cfg)

    raise ASRError(f"알 수 없는 asr.engine={engine!r} (가능: {', '.join(ENGINES)})")


__all__ = ["ASRAdapter", "ASRError", "Segment", "Transcript", "make_adapter", "ENGINES"]
