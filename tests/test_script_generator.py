"""Testa a geracao do .ps1 (UTF-8 BOM, CRLF, escape, conteudo)."""

from __future__ import annotations

from pathlib import Path

from src.classifier import MediaItem
from src.script_generator import _ps_escape, build_ps1_script, write_audit_txt, write_ps1


def test_ps_escape_quotes_and_dollar() -> None:
    # Aspa dupla dentro de path vira `"
    assert _ps_escape('hello "world"') == 'hello `"world`"'
    # $ escapado
    assert _ps_escape("valor $x") == "valor `$x"
    # Backtick duplicado
    assert _ps_escape("a`b") == "a``b"


def test_write_ps1_has_utf8_bom_and_crlf(tmp_path: Path) -> None:
    items = [
        MediaItem(
            path=r"\\servidor\midias\2ª Edição\arquivo.mp4",
            kind="clip",
            exists=True,
            size_bytes=1000,
        ),
    ]
    content = build_ps1_script(items, tmp_path / "CLIP", tmp_path / "Proxy", "TEST")
    out = write_ps1(content, tmp_path / "copiar.ps1")

    raw = out.read_bytes()
    # BOM UTF-8
    assert raw[:3] == b"\xef\xbb\xbf"
    # Tem CRLF em algum lugar (line ending Windows)
    assert b"\r\n" in raw
    # Acentos preservados (apos BOM, o arquivo deve ter os bytes UTF-8 de "2ª Edição")
    assert "2ª Edição".encode("utf-8") in raw


def test_build_ps1_classifies_clip_vs_proxy(tmp_path: Path) -> None:
    items = [
        MediaItem(path=r"D:\a\video.mp4", kind="clip", exists=True, size_bytes=100),
        MediaItem(path=r"D:\a\video_Proxy.mp4", kind="proxy", exists=True, size_bytes=50),
        MediaItem(path=r"D:\b\missing.mov", kind="clip", exists=False, size_bytes=0),
    ]
    content = build_ps1_script(items, tmp_path / "CLIP", tmp_path / "Proxy", "TEST")

    # Usa Shell.Application.CopyHere (nao robocopy)
    assert "New-Object -ComObject Shell.Application" in content
    assert "$nsClip  = $shell.Namespace($destClip)" in content
    assert "$nsProxy = $shell.Namespace($destProxy)" in content

    # Item CLIP existente copia pro $nsClip
    assert "$nsClip.CopyHere($item, $flags)" in content
    # Item Proxy existente copia pro $nsProxy
    assert "$nsProxy.CopyHere($item, $flags)" in content

    # Flag 0x10 = FOF_NOCONFIRMATION (preserva janela de progresso)
    assert "$flags = 0x10" in content

    # Nome de cada arquivo aparece
    assert "video.mp4" in content
    assert "video_Proxy.mp4" in content

    # Ausente deve virar log amarelo, nao CopyHere
    assert "AUSENTE" in content
    assert "missing.mov" in content

    # Cabecalho de encoding presente
    assert "chcp 65001" in content


def test_build_ps1_does_not_reference_robocopy(tmp_path: Path) -> None:
    """Regressao: script nao deve mais usar robocopy (migrado pra Shell API)."""
    items = [MediaItem(path=r"D:\a\v.mp4", kind="clip", exists=True, size_bytes=10)]
    content = build_ps1_script(items, tmp_path / "CLIP", tmp_path / "Proxy", "TEST")
    assert "robocopy" not in content.lower()


def test_audit_txt_has_counts_and_paths(tmp_path: Path) -> None:
    items = [
        MediaItem(path=r"D:\a\video.mp4", kind="clip", exists=True, size_bytes=1024),
        MediaItem(path=r"D:\a\missing.mov", kind="clip", exists=False, size_bytes=0),
    ]
    out = write_audit_txt(items, tmp_path / "lista.txt", "MEU PROJETO")
    text = out.read_text(encoding="utf-8")
    assert "MEU PROJETO" in text
    assert "Total de midias: 2" in text
    assert "video.mp4" in text
    assert "missing.mov" in text
