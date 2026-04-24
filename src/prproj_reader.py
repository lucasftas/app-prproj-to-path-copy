"""Le um .prproj (gzip + XML) e extrai todos os <ActualMediaFilePath>."""

from __future__ import annotations

import gzip
import re
from pathlib import Path

_MEDIA_PATH_RE = re.compile(r"<ActualMediaFilePath>([^<]+)</ActualMediaFilePath>")


class PrprojReadError(Exception):
    """Erro ao ler/descomprimir um .prproj."""


def read_prproj_xml(prproj_path: str | Path) -> str:
    """Descomprime o .prproj e retorna o XML como string UTF-8.

    Levanta PrprojReadError se o arquivo nao for um gzip valido ou se o
    conteudo nao puder ser decodificado como UTF-8.
    """
    path = Path(prproj_path)
    if not path.is_file():
        raise PrprojReadError(f"Arquivo nao encontrado: {path}")
    try:
        with gzip.open(path, "rb") as f:
            xml_bytes = f.read()
    except OSError as exc:
        raise PrprojReadError(
            f".prproj nao parece ser gzip valido ({path}): {exc}"
        ) from exc
    try:
        return xml_bytes.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise PrprojReadError(
            f"XML do .prproj nao esta em UTF-8 ({path}): {exc}"
        ) from exc


def extract_media_paths(xml_str: str) -> list[str]:
    """Extrai todos os <ActualMediaFilePath> unicos, em ordem alfabetica."""
    paths = _MEDIA_PATH_RE.findall(xml_str)
    return sorted(set(p.strip() for p in paths if p.strip()))


def list_media_paths(prproj_path: str | Path) -> list[str]:
    """Atalho: le o .prproj e retorna os ActualMediaFilePath unicos ordenados."""
    xml_str = read_prproj_xml(prproj_path)
    return extract_media_paths(xml_str)
