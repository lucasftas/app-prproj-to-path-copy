r"""Gera o copiar.ps1 e o lista-midias.txt.

O script usa a API nativa do Windows (Shell.Application.CopyHere) —
a mesma que o Explorer usa quando voce copia arquivos pelo Windows.
Beneficios vs robocopy:
  - Mostra a janela de progresso nativa (laranja, com velocidade/ETA)
  - Copia roda no processo do Explorer — matar o PowerShell NAO para a copia
  - Multiplas operacoes com mesmo destino sao consolidadas em uma unica janela
  - Funciona em paralelo com outras execucoes do app (NVMe 7000MB/s)

Flags do CopyHere usadas:
  0x10 = FOF_NOCONFIRMATION (responder "Yes to All" automaticamente, substitui arquivos)

Limitacoes conhecidas:
  - CopyHere pode falhar silenciosamente em paths > 260 chars sem o prefixo \\?\.
    Na pratica, a maioria dos .prproj testados funciona. Casos extremos seriam
    tratados em v0.2.0 com fallback pra robocopy.
"""

from __future__ import annotations

from collections.abc import Iterable
from datetime import datetime
from pathlib import Path, PureWindowsPath

from .classifier import MediaItem
from .paths import human_size


def _ps_escape(s: str) -> str:
    """Escapa uma string pra uso dentro de aspas duplas no PowerShell.

    Dentro de `"..."`, `"`, `$` e backtick precisam ser escapados com backtick.
    """
    return s.replace("`", "``").replace('"', '`"').replace("$", "`$")


def build_ps1_script(
    items: Iterable[MediaItem],
    dest_clip: Path,
    dest_proxy: Path,
    prproj_name: str,
) -> str:
    """Monta o conteudo do copiar.ps1 usando Shell.Application.CopyHere."""
    items = list(items)
    clip_items = [i for i in items if i.kind == "clip"]
    proxy_items = [i for i in items if i.kind == "proxy"]

    total = len(items)
    existing = sum(1 for i in items if i.exists)
    missing = total - existing

    lines: list[str] = []
    lines.append("# Script gerado por app-prproj-to-path-copy")
    lines.append(f"# Projeto: {prproj_name}")
    lines.append(f"# Gerado em: {datetime.now().isoformat(timespec='seconds')}")
    lines.append(
        f"# Total: {total} midias ({len(clip_items)} CLIP + {len(proxy_items)} Proxy) "
        f"| Existentes: {existing} | Ausentes: {missing}"
    )
    lines.append("#")
    lines.append("# Usa Shell.Application.CopyHere — a API nativa do Windows Explorer.")
    lines.append("# A copia e feita pelo Explorer; matar este terminal NAO para a copia.")
    lines.append("")
    lines.append("$ErrorActionPreference = 'Continue'")
    lines.append("chcp 65001 > $null")
    lines.append("[Console]::OutputEncoding = [System.Text.Encoding]::UTF8")
    lines.append("")
    lines.append(f'$destClip  = "{_ps_escape(str(dest_clip))}"')
    lines.append(f'$destProxy = "{_ps_escape(str(dest_proxy))}"')
    lines.append("")
    lines.append("New-Item -ItemType Directory -Force -Path $destClip  | Out-Null")
    lines.append("New-Item -ItemType Directory -Force -Path $destProxy | Out-Null")
    lines.append("")
    lines.append("$shell = New-Object -ComObject Shell.Application")
    lines.append("$nsClip  = $shell.Namespace($destClip)")
    lines.append("$nsProxy = $shell.Namespace($destProxy)")
    lines.append("")
    lines.append("# 0x10 = FOF_NOCONFIRMATION (substituir sem perguntar, mantem a janela de progresso)")
    lines.append("$flags = 0x10")
    lines.append("")
    lines.append('Write-Host ""')
    lines.append(
        f'Write-Host "=== Consolidando {total} midias '
        f'({len(clip_items)} CLIP + {len(proxy_items)} Proxy) ===" -ForegroundColor Cyan'
    )
    lines.append(
        'Write-Host "Enfileirando na janela nativa de copia do Windows..." '
        "-ForegroundColor Cyan"
    )
    lines.append('Write-Host ""')
    lines.append("")
    lines.append("$okCount = 0")
    lines.append("$missCount = 0")
    lines.append("")

    for idx, item in enumerate(items, start=1):
        dest_ns_var = "$nsClip" if item.kind == "clip" else "$nsProxy"
        p = PureWindowsPath(item.path)
        src_dir = str(p.parent)
        filename = p.name
        label_prefix = f"[{idx}/{total}] {item.kind.upper()}"

        if not item.exists:
            lines.append(
                f'Write-Host "{_ps_escape(label_prefix)} AUSENTE: '
                f'{_ps_escape(item.path)}" -ForegroundColor Yellow'
            )
            lines.append("$missCount++")
            lines.append("")
            continue

        lines.append(f'$src = "{_ps_escape(item.path)}"')
        lines.append(f'$srcDir = "{_ps_escape(src_dir)}"')
        lines.append(f'$fileName = "{_ps_escape(filename)}"')
        lines.append("$srcNs = $shell.Namespace($srcDir)")
        lines.append("if ($srcNs) {")
        lines.append("    $item = $srcNs.ParseName($fileName)")
        lines.append("    if ($item) {")
        lines.append(f"        {dest_ns_var}.CopyHere($item, $flags)")
        lines.append(
            f'        Write-Host "{_ps_escape(label_prefix)} '
            f'enfileirado: {_ps_escape(filename)}" -ForegroundColor Green'
        )
        lines.append("        $okCount++")
        lines.append("    } else {")
        lines.append(
            f'        Write-Host "{_ps_escape(label_prefix)} '
            f'ERRO (ParseName falhou): {_ps_escape(item.path)}" -ForegroundColor Red'
        )
        lines.append("        $missCount++")
        lines.append("    }")
        lines.append("} else {")
        lines.append(
            f'    Write-Host "{_ps_escape(label_prefix)} '
            f'ERRO (Namespace inacessivel): {_ps_escape(src_dir)}" -ForegroundColor Red'
        )
        lines.append("    $missCount++")
        lines.append("}")
        lines.append("")

    lines.append('Write-Host ""')
    lines.append(
        'Write-Host "=== Enfileirado: $okCount copias | $missCount ausentes/erros ===" '
        "-ForegroundColor Cyan"
    )
    lines.append(
        'Write-Host "A copia continua na janela nativa do Windows." '
        "-ForegroundColor Cyan"
    )
    lines.append(
        'Write-Host "Voce pode fechar esta janela sem afetar a copia." '
        "-ForegroundColor DarkCyan"
    )
    lines.append('Write-Host ""')
    lines.append('Write-Host "Pressione ENTER para fechar este terminal..."')
    lines.append("Read-Host | Out-Null")

    return "\n".join(lines)


def write_ps1(script_content: str, dest_path: Path) -> Path:
    """Escreve o .ps1 com UTF-8 BOM + CRLF.

    Usa 'utf-8-sig' pra PS 5.1 ler acentos corretamente. CRLF via newline='\\r\\n'.
    """
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    with open(dest_path, "w", encoding="utf-8-sig", newline="\r\n") as f:
        f.write(script_content)
    return dest_path


def write_audit_txt(items: Iterable[MediaItem], dest_path: Path, prproj_name: str) -> Path:
    """Escreve o lista-midias.txt com classificacao e status por midia."""
    items = list(items)
    clip_items = [i for i in items if i.kind == "clip"]
    proxy_items = [i for i in items if i.kind == "proxy"]
    existing = [i for i in items if i.exists]
    missing = [i for i in items if not i.exists]
    total_bytes = sum(i.size_bytes for i in existing)

    lines: list[str] = []
    lines.append(f"Lista de midias do projeto: {prproj_name}")
    lines.append(f"Gerado em: {datetime.now().isoformat(timespec='seconds')}")
    lines.append("")
    lines.append(f"Total de midias: {len(items)}")
    lines.append(f"  - CLIP:  {len(clip_items)}")
    lines.append(f"  - Proxy: {len(proxy_items)}")
    lines.append(f"Existentes: {len(existing)} ({human_size(total_bytes)})")
    lines.append(f"Ausentes:   {len(missing)}")
    lines.append("")
    lines.append("=" * 80)
    lines.append("EXISTENTES")
    lines.append("=" * 80)
    for i in existing:
        lines.append(f"[{i.kind.upper():5}] {human_size(i.size_bytes):>10}  {i.path}")
    lines.append("")
    lines.append("=" * 80)
    lines.append("AUSENTES")
    lines.append("=" * 80)
    for i in missing:
        lines.append(f"[{i.kind.upper():5}]             {i.path}")

    dest_path.parent.mkdir(parents=True, exist_ok=True)
    with open(dest_path, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines))
    return dest_path
