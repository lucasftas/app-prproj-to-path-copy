# Implementations

Historico de implementacoes. Versoes mais recentes no topo.

## v0.1.0 — 2026-04-24

**MVP funcional — GUI + geracao de script robocopy.**

Implementacoes:
- `src/app.py` — GUI Tkinter (janela unica, fluxo: selecionar `.prproj` → resumo → gerar/executar)
- `src/prproj_reader.py` — descomprime gzip, extrai `<ActualMediaFilePath>` via regex, deduplica
- `src/classifier.py` — heuristica CLIP vs Proxy (nome com `_Proxy` ou em pasta `Proxies/`)
- `src/config.py` — persistencia do caminho base em `%APPDATA%\app-prproj-to-path-copy\config.json`
- `src/script_generator.py` — gera `copiar.ps1` com BOM (UTF-8-SIG) e CRLF + `lista-midias.txt`
- `src/paths.py` — helper `long_path()` e utilidades de filesystem
- `tests/test_prproj_reader.py` — teste basico com fixture minificado

Decisoes tecnicas-chave:
- Python + Tkinter stdlib (zero deps de runtime)
- **Shell.Application.CopyHere** como engine de copia (janela nativa laranja do Windows, copia roda no Explorer = matar o PS/app nao para a copia, multiplas em paralelo)
- Script `.ps1` com UTF-8 BOM + CRLF pra PS 5.1 aceitar acentos
- Subpasta unica por import: `<nome-prproj>_<YYYYMMDD-HHMMSS>/` pra nunca colidir
- Nao aborta em arquivos ausentes, so loga
- Icone gerado programaticamente via Pillow (scripts/gen_icon.py) — 7 tamanhos (16-256px)
- App GUI non-blocking apos dispararar exec (permite processar outros .prproj em paralelo)
- Pipeline de build: PyInstaller onedir + Inno Setup 6 (scripts/build_release.ps1)
- Instalador Windows de 8.9 MB (bundle interno 24 MB) disponivel na release v0.1.0
