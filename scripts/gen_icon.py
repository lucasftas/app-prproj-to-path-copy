"""Gera assets/icon.ico a partir de um design programatico.

Design: tile laranja com degrade diagonal + letras "pp" brancas (de prproj)
sobre um icone de "cópia" (duas folhas sobrepostas).

Uso:
    python scripts/gen_icon.py

Requer Pillow (pip install Pillow). So precisa rodar quando quiser regenerar.
O .ico gerado entra em assets/icon.ico e deve ser commitado.
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT = REPO_ROOT / "assets" / "icon.ico"


def _make_base(size: int) -> Image.Image:
    """Cria a imagem base do icone em RGBA no tamanho dado."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Fundo: tile arredondado com degrade laranja (tema Premiere + Windows copy dialog)
    radius = max(6, size // 6)
    bg_from = (255, 140, 40)  # laranja claro
    bg_to = (220, 80, 15)  # laranja escuro

    # Desenha um quadrado arredondado por camadas pra simular gradiente diagonal
    for i in range(size):
        t = i / max(size - 1, 1)
        r = int(bg_from[0] * (1 - t) + bg_to[0] * t)
        g = int(bg_from[1] * (1 - t) + bg_to[1] * t)
        b = int(bg_from[2] * (1 - t) + bg_to[2] * t)
        draw.line([(0, i), (size, i)], fill=(r, g, b, 255))

    # Mascara arredondada
    mask = Image.new("L", (size, size), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.rounded_rectangle([0, 0, size - 1, size - 1], radius=radius, fill=255)

    bg = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    bg.paste(img, (0, 0), mask)

    # Overlay: duas "folhas" sobrepostas (simbolo de copia)
    overlay = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)

    # Dimensoes das folhas (fracoes do size)
    s_w = int(size * 0.48)
    s_h = int(size * 0.60)
    # Folha de tras (clara, com leve sombra)
    bx1 = int(size * 0.22)
    by1 = int(size * 0.14)
    od.rounded_rectangle(
        [bx1, by1, bx1 + s_w, by1 + s_h],
        radius=max(2, size // 20),
        fill=(255, 255, 255, 235),
        outline=(210, 90, 25, 255),
        width=max(1, size // 64),
    )
    # Linhas de "texto" na folha de tras
    for k in range(3):
        ly = by1 + int(s_h * (0.25 + 0.18 * k))
        od.line(
            [(bx1 + s_w * 0.12, ly), (bx1 + s_w * 0.78, ly)],
            fill=(220, 90, 25, 220),
            width=max(1, size // 64),
        )

    # Folha da frente (sobrepoe parcialmente, deslocada pra direita/baixo)
    fx1 = int(size * 0.36)
    fy1 = int(size * 0.28)
    od.rounded_rectangle(
        [fx1, fy1, fx1 + s_w, fy1 + s_h],
        radius=max(2, size // 20),
        fill=(255, 255, 255, 255),
        outline=(180, 60, 10, 255),
        width=max(1, size // 48),
    )
    # Linhas de "texto" na folha da frente
    for k in range(3):
        ly = fy1 + int(s_h * (0.25 + 0.18 * k))
        od.line(
            [(fx1 + s_w * 0.12, ly), (fx1 + s_w * 0.78, ly)],
            fill=(180, 60, 10, 240),
            width=max(1, size // 48),
        )

    out = Image.alpha_composite(bg, overlay)

    # Leve sombra interna pra dar profundidade
    if size >= 48:
        shadow = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        sd = ImageDraw.Draw(shadow)
        sd.rounded_rectangle(
            [0, 0, size - 1, size - 1],
            radius=radius,
            outline=(0, 0, 0, 90),
            width=1,
        )
        shadow = shadow.filter(ImageFilter.GaussianBlur(radius=1))
        out = Image.alpha_composite(out, shadow)

    return out


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    # Pillow cria o ICO a partir de uma imagem grande e faz downsample pros tamanhos listados.
    # Isso gera icones mais nitidos pra cada contexto do Windows.
    base = _make_base(256)
    sizes = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    base.save(OUT, format="ICO", sizes=sizes)
    print(f"Icone gerado: {OUT} ({OUT.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
