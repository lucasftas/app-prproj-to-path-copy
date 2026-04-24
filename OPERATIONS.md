# Operations Log

Registro de operacoes e solicitacoes da sessao, agrupadas por data. Versoes mais recentes no topo.

## 2026-04-24

- [x] Revisao do IDEIA.md (escopo confirmado: GUI com caminho base fixo + subpastas CLIP/Proxy + script PowerShell gerado)
- [x] IDEIA.md reescrito com a visao v2
- [x] Estrutura base do projeto criada (pyproject.toml, requirements.txt, .gitignore, docs)
- [x] Modulos src/ implementados (app, prproj_reader, classifier, config, script_generator, paths)
- [x] Testes em tests/ (reader, classifier, script_generator)
- [x] Teste de layout da GUI aprovado
- [x] Trocado robocopy por Shell.Application.CopyHere (janela nativa de copia do Windows)
- [x] Icone gerado (assets/icon.ico) via scripts/gen_icon.py com Pillow
- [x] App non-blocking apos disparar execucao (permite paralelismo)
- [x] Release publica v0.1.0 — git init, LICENSE MIT, README reescrito pra open-source, pyproject.toml com URLs do repo, gh repo create --public, topics setados, release v0.1.0 criada
- [x] Auditoria de privacidade: removidas todas as referencias a nomes internos (servidores, projetos, marca) dos arquivos versionados
