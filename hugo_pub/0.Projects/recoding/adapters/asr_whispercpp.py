"""whisper.cpp (whisper-cli) 어댑터 — 윈도우/리눅스 공용 경로

macOS 에서도 동작하므로, 1차 개발 단계에서 "윈도우 이식 리허설" 용으로 쓴다.
설치: brew install whisper-cpp   (Windows: 미리 빌드된 whisper-cli.exe + ggml 모델)
"""
from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
from pathlib import Path

from .base import ASRAdapter, ASRError, Segment, Transcript


class WhisperCppAdapter(ASRAdapter):
    name = "whisper.cpp"
    needs_wav = True

    def __init__(self, cfg):
        self.binary = cfg.command("asr.whispercpp", "binary", "whisper-cli")
        self.model = cfg.path("asr.whispercpp", "model")
        self.lang = str(cfg.get("asr", "locale", "ko-KR")).split("-")[0]
        self.extra_args = list(cfg.get("asr.whispercpp", "extra_args", []) or [])
        self.timeout = float(cfg.get("asr", "timeout_seconds", 3600))

        resolved = shutil.which(self.binary)
        if resolved is None and not Path(self.binary).exists():
            raise ASRError(
                f"whisper-cli 를 찾을 수 없습니다: {self.binary}\n"
                f"  macOS: brew install whisper-cpp / Windows: whisper-cli.exe 경로를 config 에 지정"
            )
        self.binary = resolved or self.binary

        if not self.model.exists():
            raise ASRError(
                f"모델 파일이 없습니다: {self.model}\n"
                f"  예: curl -L -o {self.model} "
                f"https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-large-v3-turbo.bin"
            )

    def transcribe(self, audio: Path) -> Transcript:
        with tempfile.TemporaryDirectory(prefix="whisper-") as tmp:
            prefix = Path(tmp) / "out"
            cmd = [
                self.binary, "-m", str(self.model), "-f", str(audio),
                "-l", self.lang, "-oj", "-of", str(prefix), *self.extra_args,
            ]
            try:
                proc = subprocess.run(
                    cmd, capture_output=True, text=True, timeout=self.timeout, check=False
                )
            except subprocess.TimeoutExpired as exc:
                raise ASRError(f"whisper-cli 타임아웃({self.timeout}s): {audio.name}") from exc

            json_path = prefix.with_suffix(".json")
            if proc.returncode != 0 or not json_path.exists():
                tail = (proc.stderr or "").strip().splitlines()
                raise ASRError(
                    f"whisper-cli 실패(rc={proc.returncode}): {tail[-1] if tail else 'no output'}"
                )
            data = json.loads(json_path.read_text(encoding="utf-8"))

        segments: list[Segment] = []
        for item in data.get("transcription", []):
            offsets = item.get("offsets") or {}
            start = float(offsets.get("from", 0)) / 1000.0
            end = float(offsets.get("to", 0)) / 1000.0
            text = str(item.get("text", "")).strip()
            if text:
                segments.append(Segment(start=start, end=end, text=text))

        last_end = segments[-1].end if segments else 0.0
        return Transcript(
            segments=segments, engine="whisper.cpp", lang=self.lang, duration=last_end
        )

    def describe(self) -> str:
        return f"whispercpp(bin={self.binary}, model={self.model.name})"
