"""설정 로딩 — config.toml + .env (의존성 없음)"""
from __future__ import annotations

import os
import tomllib
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CONFIG = ROOT / "config.toml"


def load_env_file(path: Path) -> int:
    """KEY=VALUE 형식 .env 로드. 이미 설정된 환경변수는 덮어쓰지 않는다."""
    if not path.exists():
        return 0
    count = 0
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export "):]
        if "=" not in line:
            continue
        key, val = line.split("=", 1)
        key = key.strip()
        val = val.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = val
            count += 1
    return count


class Config:
    """config.toml 래퍼. 섹션 이름은 점 표기('asr.apple')로 하위 접근."""

    def __init__(self, data: dict, root: Path = ROOT):
        self.data = data
        self.root = Path(root)

    @classmethod
    def load(cls, path: str | Path | None = None) -> "Config":
        p = Path(path) if path else DEFAULT_CONFIG
        p = Path(os.path.expanduser(str(p)))
        if not p.exists():
            raise FileNotFoundError(f"config not found: {p}")
        with p.open("rb") as f:
            data = tomllib.load(f)
        cfg = cls(data, p.resolve().parent)
        env_file = cfg.get("keyword", "env_file")
        if env_file:
            load_env_file(cfg.resolve(env_file))
        return cfg

    # --- 조회 -------------------------------------------------------------
    def sec(self, name: str) -> dict:
        node: Any = self.data
        for part in name.split("."):
            if not isinstance(node, dict) or part not in node:
                return {}
            node = node[part]
        return node if isinstance(node, dict) else {}

    def get(self, section: str, key: str, default: Any = None) -> Any:
        return self.sec(section).get(key, default)

    # --- 경로 -------------------------------------------------------------
    def resolve(self, value: Any) -> Path:
        p = Path(os.path.expanduser(str(value)))
        return p if p.is_absolute() else (self.root / p)

    def path(self, section: str, key: str, default: Any = None) -> Path:
        value = self.get(section, key, default)
        if value is None:
            raise KeyError(f"config [{section}].{key} 가 없습니다")
        return self.resolve(value)

    def command(self, section: str, key: str, default: Any = None) -> str:
        """경로가 섞여 있으면 절대경로로, 아니면 PATH 조회용 이름 그대로."""
        value = self.get(section, key, default)
        if value is None:
            raise KeyError(f"config [{section}].{key} 가 없습니다")
        text = os.path.expanduser(str(value))
        if "/" in text or os.sep in text:
            return str(self.resolve(text))
        return text
