"""Config persistente em %APPDATA%\\app-prproj-to-path-copy\\config.json."""

from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any

APP_NAME = "app-prproj-to-path-copy"
CONFIG_FILENAME = "config.json"


def _config_dir() -> Path:
    """Retorna o diretorio de config no APPDATA do usuario (cria se nao existir)."""
    appdata = os.environ.get("APPDATA")
    if appdata:
        base = Path(appdata)
    else:
        # Fallback defensivo pra nao-Windows ou env sem APPDATA
        base = Path.home() / ".config"
    cfg_dir = base / APP_NAME
    cfg_dir.mkdir(parents=True, exist_ok=True)
    return cfg_dir


def config_path() -> Path:
    """Path absoluto do arquivo de config."""
    return _config_dir() / CONFIG_FILENAME


def load() -> dict[str, Any]:
    """Le o config do disco. Retorna {} se nao existe ou esta corrompido."""
    p = config_path()
    if not p.is_file():
        return {}
    try:
        with open(p, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except (json.JSONDecodeError, OSError):
        return {}


def save(data: dict[str, Any]) -> None:
    """Grava o config no disco com encoding UTF-8 e acentos preservados."""
    data = {**data, "ultima_abertura": datetime.now().isoformat(timespec="seconds")}
    p = config_path()
    with open(p, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_caminho_base() -> str | None:
    """Retorna o caminho base configurado ou None se nao setado."""
    return load().get("caminho_base")


def set_caminho_base(path: str) -> None:
    """Define e persiste o caminho base."""
    cfg = load()
    cfg["caminho_base"] = path
    save(cfg)
