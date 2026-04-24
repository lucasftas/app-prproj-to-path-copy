"""Testa a heuristica CLIP vs Proxy."""

from __future__ import annotations

import pytest

from src.classifier import classify, is_proxy_path


@pytest.mark.parametrize(
    "path,expected",
    [
        # Com _Proxy no nome
        (r"\\servidor\midias\clip-4446_Proxy.MP4", True),
        (r"C:\midia\arquivo_proxy.mov", True),
        (r"D:\foo\BAR_Proxy.MXF", True),
        # Em pasta Proxies/ ou Proxy/
        (r"\\servidor\midias\Aulas\Proxies\clip-0001.MP4", True),
        (r"D:\projeto\Proxy\clip.mov", True),
        # Nao e proxy
        (r"\\servidor\midias\clip-4446.MP4", False),
        (r"D:\Editor\Edições\Audio\Narração\narracao.wav", False),
        (r"C:\foo\bar\video.mp4", False),
        # Edge: "proxy" no meio do nome mas sem underscore nao conta como sufixo
        # (heuristica intencional — nome como "proxyserver.mp4" nao deveria ser proxy)
        # Mas se tem _proxy sim conta. Ver implementacao.
    ],
)
def test_is_proxy_path(path: str, expected: bool) -> None:
    assert is_proxy_path(path) is expected


def test_classify_preserves_fields() -> None:
    path = r"\\servidor\share\x_Proxy.MP4"
    item = classify(path, exists=True, size_bytes=1024)
    assert item.path == path
    assert item.kind == "proxy"
    assert item.is_proxy
    assert item.exists
    assert item.size_bytes == 1024


def test_classify_clip_when_missing() -> None:
    item = classify(r"D:\foo\video.mp4", exists=False, size_bytes=0)
    assert item.kind == "clip"
    assert not item.is_proxy
    assert not item.exists
