"""Helpers de filesystem: long paths, timestamps e sanitizacao de nomes."""

from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path


def timestamp_suffix() -> str:
    """Retorna sufixo timestamp no formato YYYYMMDD-HHMMSS pra subpastas unicas."""
    return datetime.now().strftime("%Y%m%d-%H%M%S")


_INVALID_WIN_CHARS = re.compile(r'[<>:"/\\|?*\x00-\x1f]')


def safe_name(name: str, max_len: int = 120) -> str:
    """Sanitiza um nome pra uso como pasta/arquivo no Windows.

    Remove caracteres invalidos mas preserva acentos pt-BR. Trunca se muito longo.
    """
    cleaned = _INVALID_WIN_CHARS.sub("_", name).strip(" .")
    if not cleaned:
        cleaned = "sem_nome"
    if len(cleaned) > max_len:
        cleaned = cleaned[:max_len].rstrip(" .")
    return cleaned


def long_path(path: str | Path) -> str:
    """Converte um path pra formato long-path do Windows (\\\\?\\ prefix).

    Para UNC (`\\\\servidor\\share\\...`) usa `\\\\?\\UNC\\servidor\\share\\...`.
    Para paths locais (`C:\\...`) usa `\\\\?\\C:\\...`.
    Paths relativos sao resolvidos antes.
    """
    p = str(Path(path).resolve())
    if p.startswith("\\\\?\\"):
        return p
    if p.startswith("\\\\"):
        return "\\\\?\\UNC\\" + p[2:]
    return "\\\\?\\" + p


def human_size(num_bytes: int) -> str:
    """Formata tamanho em bytes como string legivel (KB, MB, GB, TB)."""
    n: float = float(num_bytes)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if abs(n) < 1024.0:
            return f"{n:.2f} {unit}"
        n /= 1024.0
    return f"{n:.2f} PB"
