"""Classifica midias em CLIP (alta) vs Proxy baseado em heuristica de nome/pasta."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import PureWindowsPath


@dataclass(frozen=True)
class MediaItem:
    """Representa uma midia classificada.

    Attrs:
        path: caminho original como veio do .prproj.
        kind: 'proxy' ou 'clip'.
        exists: True se o arquivo existe no filesystem.
        size_bytes: tamanho em bytes (0 se nao existe).
    """

    path: str
    kind: str  # 'proxy' | 'clip'
    exists: bool
    size_bytes: int

    @property
    def is_proxy(self) -> bool:
        return self.kind == "proxy"


def is_proxy_path(path: str) -> bool:
    """Heuristica: true se o path parece ser uma midia Proxy.

    Regras (qualquer uma bate):
    - Nome do arquivo contem `_proxy` (case-insensitive) — ex: `FFB-4446_Proxy.MP4`
    - Algum dos diretorios ancestrais se chama `Proxies` ou `Proxy` (case-insensitive)
    """
    p = PureWindowsPath(path)
    name_lower = p.name.lower()
    if "_proxy" in name_lower:
        return True
    for part in p.parts:
        if part.lower() in ("proxies", "proxy"):
            return True
    return False


def classify(path: str, exists: bool, size_bytes: int) -> MediaItem:
    """Classifica um path em CLIP vs Proxy e retorna um MediaItem."""
    kind = "proxy" if is_proxy_path(path) else "clip"
    return MediaItem(path=path, kind=kind, exists=exists, size_bytes=size_bytes)
