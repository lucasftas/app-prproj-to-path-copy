"""Fixtures compartilhadas entre testes."""

from __future__ import annotations

import gzip
from pathlib import Path

import pytest

# XML sintetico com acentos pt-BR e UNC pra cobrir os casos criticos do app:
# - Classificacao CLIP vs Proxy (nome com _Proxy + pasta Proxies/)
# - Acentos preservados em paths (2ª, ção, etc)
# - Deduplicacao (mesmo path aparece 2x)
SAMPLE_XML = """<?xml version="1.0" encoding="UTF-8"?>
<Project>
  <ProjectItems>
    <MediaSource>
      <ActualMediaFilePath>\\\\servidor\\midias\\PROJETO 2ª Edição\\Aulas\\clip-0001.MP4</ActualMediaFilePath>
    </MediaSource>
    <MediaSource>
      <ActualMediaFilePath>\\\\servidor\\midias\\PROJETO 2ª Edição\\Aulas\\Proxies\\clip-0001_Proxy.MP4</ActualMediaFilePath>
    </MediaSource>
    <MediaSource>
      <ActualMediaFilePath>D:\\Editor\\Edições\\Audio\\Narração\\narracao.wav</ActualMediaFilePath>
    </MediaSource>
    <MediaSource>
      <ActualMediaFilePath>D:\\Editor\\Edições\\Audio\\Narração\\narracao.wav</ActualMediaFilePath>
    </MediaSource>
    <MediaSource>
      <ActualMediaFilePath>C:\\midia\\qualquer_proxy.mov</ActualMediaFilePath>
    </MediaSource>
  </ProjectItems>
</Project>
"""


@pytest.fixture
def sample_prproj(tmp_path: Path) -> Path:
    """Cria um .prproj sintetico (gzip + XML UTF-8) em tmp_path."""
    target = tmp_path / "sample.prproj"
    with gzip.open(target, "wb") as f:
        f.write(SAMPLE_XML.encode("utf-8"))
    return target
