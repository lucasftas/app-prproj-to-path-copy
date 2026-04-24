# app-prproj-to-path-copy — Regras do Projeto

## Visao geral

App desktop Python + Tkinter que extrai midias vinculadas de um `.prproj` do Premiere e gera um script `robocopy` pra consolidar tudo numa pasta fixa, separado em `CLIP/` e `Proxy/`.

**Stack:**
- Python 3.12+ (stdlib pura no runtime — zero deps)
- Tkinter (GUI)
- Robocopy (engine de copia — nativo do Windows)
- PowerShell 5.1+ (executa o script gerado)

**Plataforma:** Windows 10/11 (uso exclusivo — depende de `%APPDATA%`, robocopy, PS)

---

## Regras invioláveis

### 1. Encoding UTF-8 explicito em TODA operacao de I/O

Windows default e cp1252. **Sempre** passar encoding:

```python
# Leitura de arquivo texto
with open(path, 'r', encoding='utf-8') as f: ...

# Escrita de .ps1 (precisa BOM pro PS 5.1 ler acentos)
with open(ps1_path, 'w', encoding='utf-8-sig', newline='\r\n') as f: ...

# JSON
json.dump(data, f, ensure_ascii=False, indent=2)

# subprocess
subprocess.run(..., text=True, encoding='utf-8')
```

### 2. `.ps1` gerado SEMPRE com UTF-8 BOM + CRLF

Nao negociavel. PowerShell 5.1 (padrao Win11) le `.ps1` sem BOM como CP1252 e corrompe acentos. Validacao: primeiros 3 bytes do arquivo devem ser `EF BB BF`.

### 3. Nunca usar `.bat` wrapper

`.bat` quebra em UNC como CWD. Sempre `.ps1` direto com `-ExecutionPolicy Bypass`.

### 4. Tratar arquivos ausentes sem abortar

Midias offline sao comuns (47/57 no primeiro `.prproj` testado). App NUNCA deve crashar por isso — so logar AUSENTE e seguir.

### 5. Nao renomear o `.code-workspace` nem a pasta raiz

Renomear derruba a sessao do Claude Code (a extensao perde a referencia ao path).

---

## Convencoes de codigo

- **Type hints** em todas as funcoes publicas (`def foo(x: str) -> Path:`)
- **Docstrings** curtas nas funcoes publicas (1 linha so se o nome ja diz tudo; 2-3 linhas se tem regra de negocio)
- **Nomes em portugues** so em strings de UI e logs visiveis pro usuario. Codigo (variaveis, funcoes, classes): ingles.
- **Imports ordenados**: stdlib → third-party → local
- **`pathlib.Path`** em vez de `os.path` sempre que possivel

---

## Padrao de commits

Portugues + prefixo convencional + co-author Claude:

```
feat: adiciona classificador CLIP vs Proxy

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
```

Prefixos: `feat:`, `fix:`, `refactor:`, `docs:`, `test:`, `chore:`.

---

## Como rodar

```powershell
cd D:\GitHub\app-prproj-to-path-copy
python -m src.app
```

Pra desenvolvimento (instala como pacote editavel):
```powershell
pip install -e .
prproj-copy
```

Testes:
```powershell
pip install pytest
pytest
```

---

## Estrutura

```
src/
├── app.py                 # Tkinter GUI — entrypoint (main)
├── prproj_reader.py       # gzip + XML → lista de ActualMediaFilePath
├── classifier.py          # CLIP vs Proxy (heuristica por nome/pasta)
├── config.py              # persistencia em %APPDATA%\app-prproj-to-path-copy\
├── script_generator.py    # gera copiar.ps1 + lista-midias.txt
└── paths.py               # helpers: long_path(), timestamp_suffix()

tests/
├── test_prproj_reader.py
├── test_classifier.py
└── fixtures/
    └── sample.prproj      # fixture minificado pra testes

docs/
├── IDEIA.md               # brain dump detalhado
├── README.md              # onboarding
├── CHANGELOG.md
├── IMPLEMENTATIONS.md
└── OPERATIONS.md
```

---

## Gatilho "filé"

Ver `~/.claude/CLAUDE.md` (regras globais). Resumo: commit + push + release + update de docs.

## Gatilho "bora"

Este projeto **ja passou** pela fase `bora` (IDEIA.md ja detalhado, estrutura criada). Nao executar `bora` novamente aqui.

---

## Referencias externas

- Shell.Application (COM) — Namespace, ParseName, CopyHere:
  https://learn.microsoft.com/en-us/windows/win32/shell/shelldispatch
- Robocopy docs (caso mudemos a engine no futuro):
  https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/robocopy
- Formato `.prproj` (gzip + XML com `<ActualMediaFilePath>`) — comunidade Adobe
