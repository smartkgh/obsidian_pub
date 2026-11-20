"""macOS Apple SpeechTranscriber 어댑터 (Swift 헬퍼 subprocess)"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

from .base import ASRAdapter, ASRError, Segment, Transcript


class AppleSpeechAdapter(ASRAdapter):
    name = "apple-SpeechTranscriber"
    needs_wav = False        # AVAudioFile 이 m4a 를 직접 읽는다

    def __init__(self, cfg):
        self.helper = cfg.path("asr.apple", "helper")
        self.locale = cfg.get("asr", "locale", "ko-KR")
        self.timeout = float(cfg.get("asr", "timeout_seconds", 3600))
        if not self.helper.exists():
            raise ASRError(
                f"SpeechHelper 가 없습니다: {self.helper}\n"
                f"  → {self.helper.parent}/build.sh 를 먼저 실행하세요"
            )

    def transcribe(self, audio: Path) -> Transcript:
        cmd = [str(self.helper), str(audio), "--locale", self.locale]
        try:
            proc = subprocess.run(
                cmd, capture_output=True, text=True, timeout=self.timeout, check=False
            )
        except subprocess.TimeoutExpired as exc:
            raise ASRError(f"전사 타임아웃({self.timeout}s): {audio.name}") from exc

        stdout = (proc.stdout or "").strip()
        if proc.returncode != 0 or not stdout:
            err = (proc.stderr or "").strip().splitlines()
            raise ASRError(
                f"SpeechHelper 실패(rc={proc.returncode}): {err[-1] if err else 'no output'}"
            )

        # 마지막 비어있지 않은 줄이 JSON
        line = [x for x in stdout.splitlines() if x.strip().startswith("{")][-1]
        try:
            data = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ASRError(f"JSON 파싱 실패: {line[:200]}") from exc

        if "error" in data:
            raise ASRError(data["error"])

        segments = [
            Segment(start=float(s.get("start", 0.0)), end=float(s.get("end", 0.0)),
                    text=str(s.get("text", "")))
            for s in data.get("segments", [])
        ]
        return Transcript(
            segments=segments,
            engine=data.get("engine", self.name),
            lang=str(data.get("locale", self.locale)).split("-")[0],
            duration=float(data.get("duration", 0.0)),
        )

    def describe(self) -> str:
        return f"apple(locale={self.locale}, helper={self.helper.name})"
