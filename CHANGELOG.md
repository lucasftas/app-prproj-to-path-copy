# Changelog

Formato baseado em [Keep a Changelog](https://keepachangelog.com/).
Versoes mais recentes no topo.

## [0.1.0] — 2026-04-24

Primeira versao publica — MVP funcional com janela nativa de copia do Windows.

### Added
- Estrutura inicial do projeto Python (src/, tests/, docs)
- GUI Tkinter com selecao de `.prproj` e configuracao persistente do caminho base
- Parse de `.prproj` (gzip + XML) e extracao de `<ActualMediaFilePath>`
- Classificador CLIP vs Proxy (heuristica por nome/pasta)
- Gerador de script `.ps1` UTF-8 BOM usando `Shell.Application.CopyHere` (janela nativa de copia do Windows)
- Icone do app em `assets/icon.ico` (script `scripts/gen_icon.py` via Pillow)
- Auditoria via `lista-midias.txt` por projeto consolidado
- Resumo na GUI com contagem de existentes/ausentes e tamanho estimado
- Execucao non-blocking: copia roda no Explorer, permite multiplas execucoes em paralelo
- License MIT + README open-source com badges, quickstart, roadmap
- **Instalador Windows** (`prproj-to-path-copy-0.1.0-setup.exe`, 8.9 MB) gerado via PyInstaller + Inno Setup 6
- Script de build automatizado em `scripts/build_release.ps1` (PyInstaller onedir -> Inno Setup)
- Suporte ao modo empacotado no `src/app.py` (usa `sys._MEIPASS` pra localizar assets)
