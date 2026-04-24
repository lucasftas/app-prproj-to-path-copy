"""Testa o parse de .prproj e a extracao de ActualMediaFilePath."""

from __future__ import annotations

from pathlib import Path

import pytest

from src.prproj_reader import (
    PrprojReadError,
    extract_media_paths,
    list_media_paths,
    read_prproj_xml,
)


def test_read_prproj_xml_decodes_utf8(sample_prproj: Path) -> None:
    xml = read_prproj_xml(sample_prproj)
    # Acentos pt-BR devem vir intactos
    assert "2ª Edição" in xml
    assert "Edições" in xml
    assert "Narração" in xml


def test_read_prproj_xml_raises_if_not_gzip(tmp_path: Path) -> None:
    bad = tmp_path / "nao_gzip.prproj"
    bad.write_text("isso nao e gzip", encoding="utf-8")
    with pytest.raises(PrprojReadError):
        read_prproj_xml(bad)


def test_read_prproj_xml_raises_if_file_missing(tmp_path: Path) -> None:
    with pytest.raises(PrprojReadError):
        read_prproj_xml(tmp_path / "inexistente.prproj")


def test_extract_media_paths_deduplicates_and_sorts(sample_prproj: Path) -> None:
    xml = read_prproj_xml(sample_prproj)
    paths = extract_media_paths(xml)
    # SAMPLE_XML tem 5 MediaSource mas narracao.wav duplicado — resultado deve ter 4 unicos
    assert len(paths) == 4
    # Deve estar ordenado
    assert paths == sorted(paths)
    # Acentos preservados
    assert any("2ª Edição" in p for p in paths)
    assert any("Narração" in p for p in paths)


def test_list_media_paths_atalho(sample_prproj: Path) -> None:
    paths = list_media_paths(sample_prproj)
    assert len(paths) == 4
