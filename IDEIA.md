# app-prproj-to-path-copy

**Status:** 🧠 Brain dump v2 — visão GUI alinhada em 2026-04-24

Este arquivo é um **brief detalhado** capturando a ideia e as descobertas técnicas. Serve como input para a implementação do MVP.

**Histórico:**
- 2026-04-23: protótipos em PowerShell funcionais (versão CLI, validada em 2 projetos reais com ~60 mídias cada)
- 2026-04-24: escopo mudou de **CLI flatten** para **GUI com caminho base fixo + subpastas CLIP/Proxy + script robocopy gerado**
- 2026-04-24 (pm): 2ª revisão → trocado **robocopy** por **`Shell.Application.CopyHere`** (API nativa do Windows Explorer). Motivo: a janela nativa de cópia do Windows é familiar ao usuário, e a cópia roda no processo do Explorer — matar o PowerShell/app NÃO para a cópia, múltiplas cópias em paralelo funcionam naturalmente (aproveita NVMe rápido). Também adicionado ícone em `assets/icon.ico`.

---

## 🎯 Proposta (v2 — visão atual)

Ferramenta **desktop com GUI** que lê um arquivo de projeto do **Adobe Premiere Pro** (`.prproj`), extrai a lista de **todas as mídias vinculadas** (vídeo, áudio, imagens), e:

1. **Classifica** cada mídia em **CLIP (alta)** ou **Proxy** (heurística: nome contém `_Proxy`)
2. **Cria uma subpasta única** dentro de um caminho base fixo (configurado uma vez), com estrutura `<nome-prproj>_<timestamp>/CLIP/` + `<nome-prproj>_<timestamp>/Proxy/`
3. **Gera um script `.ps1`** (UTF-8 BOM) que usa `Shell.Application.CopyHere` (API nativa do Windows) — a mesma janela de cópia que o Explorer mostra, com barra de progresso laranja, velocidade e ETA
4. **Pergunta ao usuário** antes de executar (com resumo: N originais, M proxies, X GB estimado, Y ausentes)
5. Se aprovado: **abre o script** numa janela PowerShell nova com `-ExecutionPolicy Bypass`, usuário vê progresso do robocopy

Em linguagem simples: **"abro o app, jogo o .prproj, confirmo, e o Windows copia tudo organizado em CLIP/Proxy na minha pasta fixa"**.

---

## 🧨 Problema que resolve

Em fluxos de edição de vídeo com múltiplos editores/máquinas, os projetos Premiere frequentemente têm mídias espalhadas em:
- Servidores de rede (paths UNC tipo `\\servidor\share\...`)
- HDs externos (letras variáveis `A:`, `E:`)
- Máquinas de terceiros/colegas
- Drives locais

Quando é preciso:
- **Consolidar** mídias pra backup/arquivamento
- **Migrar** projeto pra outra máquina
- **Enviar** as brutas pra um editor freelancer
- **Recriar** proxies/versões offline

...o Premiere tem o "Project Manager", mas ele é lento, trava em UNC longo e não aceita bem mídias offline. Esta ferramenta resolve com um **app simples + script PS gerado** — funciona mesmo com mídias offline (só loga como AUSENTE e segue).

---

## 👤 Usuário-alvo

Editores e produtores de conteúdo em vídeo que precisam consolidar mídias de projetos Premiere frequentemente. Usuário técnico o bastante pra rodar Python/PowerShell, mas prefere GUI pra tarefas rotineiras de consolidação.

---

## 🔁 Fluxo principal (MVP v0.1.0)

1. Usuário abre o app (duplo-clique no executável ou `python src/app.py`)
2. **Primeira execução:** app pede pra escolher o **caminho base** (pasta onde todos os projetos consolidados vão morar). Salva em `%APPDATA%\app-prproj-to-path-copy\config.json`.
3. Usuário **arrasta o `.prproj`** pra janela ou clica "Selecionar arquivo..."
4. App processa:
   - Descomprime `.prproj` (gzip + XML UTF-8)
   - Extrai todos os `<ActualMediaFilePath>` do XML
   - Remove duplicatas
   - Classifica cada path: contém `_Proxy.` ou está em pasta `Proxies\` → **Proxy**, caso contrário → **CLIP**
   - Verifica existência de cada arquivo (log AUSENTE pros offline)
5. App **mostra resumo** na GUI:
   ```
   Projeto: PROJETO EXEMPLO.prproj
   Destino: D:\Consolidado\PROJETO EXEMPLO_20260424-1530\
   
   CLIP (alta):    47 arquivos, 234 GB — 35 existentes, 12 ausentes
   Proxy:          47 arquivos,  12 GB — 44 existentes,  3 ausentes
   
   [Só gerar script]   [Executar agora]
   ```
6. App **gera o script** `copiar.ps1` (UTF-8 BOM) na subpasta destino, com comandos robocopy um-por-arquivo
7. Se "Executar agora": dispara `powershell -ExecutionPolicy Bypass -File "<subpasta>\copiar.ps1"` numa janela nova — usuário acompanha o progresso do robocopy

### Evolução futura (fora do MVP v0.1.0)
- Drag-and-drop nativo (requer `tkinterdnd2`)
- Flag `--relink` que reescreve o `.prproj` com os paths novos
- Flag `--dry-run` pra só listar sem copiar
- Suporte a `.aep` (After Effects), `.drp` (DaVinci), `.fcpxml` (Final Cut)
- Progress bar integrada na GUI (em vez de abrir terminal externo)
- Verificação de integridade (size + hash opcional)
- Modo "move" em vez de copy
- Empacotar como `.exe` via PyInstaller (single-file, sem Python instalado)
- Histórico de projetos consolidados (lista recente na GUI)

---

## 🔌 Inputs e Outputs

### Input
- **1 arquivo `.prproj`** (UNC, local, com acentos, com paths longos — tudo suportado)

### Output
- **Subpasta única** dentro do caminho base: `<nome-prproj>_<YYYYMMDD-HHMMSS>/`
- Dentro dela:
  - `CLIP/` → mídias em alta
  - `Proxy/` → mídias proxy
  - `copiar.ps1` → script gerado (UTF-8 BOM) com comandos robocopy
  - `lista-midias.txt` → auditoria com todos os paths encontrados, classificação e status (OK/AUSENTE)

### Config persistente
- `%APPDATA%\app-prproj-to-path-copy\config.json`:
  ```json
  {
    "caminho_base": "D:\\Consolidado",
    "ultima_abertura": "2026-04-24T15:30:00"
  }
  ```

---

## ⚙️ Stack e arquitetura

**Stack:** **Python 3.12+** + **Tkinter** (stdlib, zero deps de runtime)

**Por que Tkinter:**
- Stdlib pura — zero instalação extra
- Simples de empacotar com PyInstaller depois
- Interface enxuta combina com o escopo do app (1 input, 1 botão, 1 resumo)
- Python geralmente já está instalado em máquinas de edição (muitos fluxos usam)

**Por que Python e não PowerShell puro:**
- Script `.ps1` foi o protótipo (funcionou), mas tem armadilhas crônicas:
  1. Execution policy bloqueia execução por default
  2. PS 5.1 lê `.ps1` sem BOM como ANSI → corrompe acentos
  3. CMD.EXE não suporta UNC como CWD (quebra `.bat` wrapper)
- Python resolve: UTF-8 nativo, sem execution policy, UNC OK como CWD
- O `.ps1` gerado pelo Python já nasce com BOM correto

**Por que robocopy (e não `shutil.copy2` puro em Python):**
- Robocopy é nativo do Windows e **mostra progresso bonito** no terminal (%, velocidade, ETA)
- Lida nativamente com paths longos (>260 chars)
- Lida nativamente com UNC
- Retry automático em falhas transientes de rede
- Usuário pode cancelar com Ctrl+C e retomar depois rodando o mesmo script
- O app fica responsável só de **gerar** o script — o robocopy faz o trabalho pesado

### Arquitetura do MVP

```
app-prproj-to-path-copy/
├── src/
│   ├── __init__.py
│   ├── app.py                  # Tkinter GUI — entrypoint
│   ├── prproj_reader.py        # descomprime + extrai <ActualMediaFilePath>
│   ├── classifier.py           # CLIP vs Proxy (heurística por nome/pasta)
│   ├── script_generator.py     # gera copiar.ps1 UTF-8 BOM
│   ├── config.py               # persist caminho base em %APPDATA%
│   └── paths.py                # helpers: long_path(), safe_dirname()
├── tests/
│   ├── test_prproj_reader.py
│   ├── test_classifier.py
│   └── fixtures/
│       └── sample.prproj       # fixture pequeno gerado/minificado
├── requirements.txt            # vazio (runtime) + pytest (dev)
├── pyproject.toml              # metadata + entry_point
├── .gitignore
├── README.md
├── CLAUDE.md                   # regras do projeto pro Claude Code
├── CHANGELOG.md
├── IMPLEMENTATIONS.md
├── OPERATIONS.md
└── IDEIA.md                    # este arquivo (brain dump)
```

---

## 🧪 Descobertas técnicas (da sessão de prototipagem)

### 1. `.prproj` é gzip + XML UTF-8
```python
import gzip
with gzip.open(prproj_path, 'rb') as f:
    xml_bytes = f.read()
xml_str = xml_bytes.decode('utf-8')
```

### 2. Paths das mídias estão em `<ActualMediaFilePath>`
```python
import re
paths = re.findall(r'<ActualMediaFilePath>([^<]+)</ActualMediaFilePath>', xml_str)
paths = sorted(set(paths))  # deduplica
```

### 3. Classificação CLIP vs Proxy (heurística)
Baseado nos `.prproj` reais testados:
- Proxies têm sufixo `_Proxy` no nome do arquivo (ex: `FFB-4446_Proxy.MP4`)
- Às vezes estão em subpasta `Proxies/` na hierarquia original
- Originais não têm esse sufixo (ex: `FFB-4446.MP4`)

```python
def is_proxy(path: str) -> bool:
    name = Path(path).name.lower()
    parent = Path(path).parent.name.lower()
    return '_proxy' in name or parent == 'proxies'
```

### 4. Caminhos pt-BR
Exemplos típicos de paths problemáticos:
- `\\servidor\midias\PROJETO 2ª Edição\Aulas\...`
- `D:\Editor\Edições\Audio\Narração\...`

Python 3 com `open(encoding='utf-8')` resolve. **Nunca deixar encoding implícito** no Windows.

### 5. Caminhos longos (>260 chars)
Python 3.6+ no Windows 10 1607+ com `LongPathsEnabled=1` lida bem. Defensivo: helper `long_path()` que injeta `\\?\` ou `\\?\UNC\`.

### 6. Mídias frequentemente offline
Em projetos testados, ~80% das mídias estavam offline (drives externos não montados, máquinas de rede desligadas). **App DEVE funcionar com ausentes** — só loga e segue.

### 7. Robocopy por arquivo individual
Robocopy copia **diretórios**, não arquivos. Pra copiar um arquivo único:
```powershell
robocopy "<dir_origem>" "<dir_destino>" "<nome_arquivo>" /R:2 /W:5 /NP
```
Flags:
- `/R:2` = 2 retries em falhas (default é 1 milhão, catastrófico)
- `/W:5` = 5 segundos entre retries
- `/NP` = no progress % (poui output; cada arquivo tem tamanho + velocidade mesmo assim)

### 8. Script `.ps1` gerado — UTF-8 BOM obrigatório
```python
# Python escreve com BOM usando 'utf-8-sig'
with open(script_path, 'w', encoding='utf-8-sig', newline='\r\n') as f:
    f.write(ps_script_content)
```
`newline='\r\n'` porque PowerShell no Windows espera CRLF.

---

## 🔥 Problemas de encoding pt-BR — LIÇÕES APRENDIDAS

A sessão de prototipagem em PowerShell (2026-04-23) quebrou **4 vezes seguidas** por corrupção de acentos. Documentando aqui pra a versão Python **NASCER já resolvendo**.

### Problema 1: `.ps1` sem BOM → PS 5.1 lê como ANSI
**Sintoma:** strings hardcoded com `Edição`, `Gravações` viraram `EdiÃ§Ã£o`, `GravaÃ§Ãµes`.
**Causa:** PowerShell 5.1 lê `.ps1` sem BOM como CP1252.
**Fix no Python:** escrever `.ps1` com `encoding='utf-8-sig'` (adiciona BOM automaticamente).

### Problema 2: `.bat` wrapper quebra em UNC
**Sintoma:** CMD.EXE não suporta UNC como CWD.
**Fix:** nunca usar `.bat`. Sempre `.ps1` direto com `-ExecutionPolicy Bypass`.

### Problema 3: ExecutionPolicy bloqueia `.ps1`
**Fix:** invocar com `powershell -ExecutionPolicy Bypass -File "<script>"`.

### Problema 4: Copy-paste de paths com acento corrompe no terminal
**Fix no Python:** `sys.stdout.reconfigure(encoding='utf-8')` no início do `app.py`.

### Checklist defensivo

- [ ] Toda `open()` tem `encoding='utf-8'` (leitura) ou `encoding='utf-8-sig'` (escrita do `.ps1`)
- [ ] `json.dump()` usa `ensure_ascii=False`
- [ ] `subprocess.run()` usa `text=True, encoding='utf-8'`
- [ ] Testes com paths com acentos (`\\servidor\...2ª Edição\...`)
- [ ] Caminhos >260 chars testados
- [ ] UNC como input e como CWD
- [ ] `.ps1` gerado testado lendo no PS 5.1 (abrir e verificar bytes BOM `EF BB BF`)

---

## 📦 Escopo do MVP (v0.1.0)

### Incluído
- [x] GUI Tkinter (janela simples, 1 input de arquivo, botões)
- [x] Persistência do caminho base em `%APPDATA%`
- [x] Parse `.prproj` (gzip + XML)
- [x] Extrair `<ActualMediaFilePath>` únicos
- [x] Classificar CLIP vs Proxy (heurística)
- [x] Criar subpasta única `<nome>_<timestamp>/CLIP/` + `Proxy/`
- [x] Gerar `copiar.ps1` UTF-8 BOM com robocopy por arquivo
- [x] Gerar `lista-midias.txt` de auditoria
- [x] Mostrar resumo na GUI antes de executar
- [x] Botão "Executar agora" → dispara PowerShell externo
- [x] Suporte a acentos pt-BR
- [x] Suporte a caminhos longos (>260)
- [x] Suporte a UNC
- [x] Tratar arquivos ausentes sem abortar

### Fora de escopo (v0.1.0)
- Drag-and-drop (usar file picker padrão; DnD em v0.2.0)
- Progress bar integrada na GUI (só terminal externo do robocopy)
- Flag `--relink`
- Suporte a `.aep`, `.drp`, `.fcpxml`
- Empacotar como `.exe` standalone (roda como `python src/app.py`)
- Histórico de projetos consolidados

---

## 🔗 Referências

### Protótipos já validados
Dois scripts PowerShell anteriores (versão CLI, ~60 mídias cada) rodaram com sucesso em projetos reais antes do port pra Python + GUI.

### Docs
- Formato `.prproj`: gzip + XML com `<Project>` → `<ProjectItems>` → `<MediaSource>` → `<ActualMediaFilePath>`
- Python gzip: https://docs.python.org/3/library/gzip.html
- Robocopy flags: https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/robocopy
- Windows long paths: https://learn.microsoft.com/en-us/windows/win32/fileio/maximum-file-path-limitation

### Regras globais aplicáveis (`~/.claude/CLAUDE.md`)
- Encoding pt-BR + caminhos longos Windows
- Padrão para novos repositórios privados
- Gatilho "bora" e "filé"
