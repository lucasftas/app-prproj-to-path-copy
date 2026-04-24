<div align="center">

# 🎬 prproj-to-path-copy

**Consolide todas as mídias de um projeto do Adobe Premiere em uma pasta só — com a janela de cópia nativa do Windows.**

![Platform](https://img.shields.io/badge/platform-Windows%2010%2F11-0078D4?logo=windows&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.12%2B-3776AB?logo=python&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-green)
![Stdlib](https://img.shields.io/badge/dependencies-stdlib%20only-brightgreen)
![Status](https://img.shields.io/badge/status-v0.1.0%20MVP-blue)

Abre o app → joga o `.prproj` → confirma → Windows copia tudo organizado em `CLIP/` e `Proxy/`.

</div>

---

## ⚡ Demo

```
┌──────────────────────────────────────────────────────────────────┐
│  prproj → path copy                                       [─][□][✕]│
├──────────────────────────────────────────────────────────────────┤
│  Consolidador de mídias do Premiere (.prproj → CLIP/Proxy)       │
│                                                                  │
│  ┌─ Caminho base (destino fixo) ──────────────────────────────┐ │
│  │  D:\Consolidado                               [ Alterar… ] │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ┌─ Arquivo .prproj ──────────────────────────────────────────┐ │
│  │  D:\Projetos\PROJETO DEMO.prproj             [ Selecionar… ]│ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  [ Processar .prproj ]                                           │
│                                                                  │
│  ┌─ Resumo ───────────────────────────────────────────────────┐ │
│  │  Projeto:   PROJETO DEMO                                    │ │
│  │  Destino:   D:\Consolidado\PROJETO DEMO_20260424-1530\      │ │
│  │                                                            │ │
│  │  Total de mídias encontradas: 114                          │ │
│  │    • CLIP (alta):  57                                      │ │
│  │    • Proxy:        57                                      │ │
│  │                                                            │ │
│  │  Existentes:  110  (234.56 GB)                             │ │
│  │  Ausentes:     4                                           │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  [ Executar agora ]  [ Abrir pasta ]  [ Abrir script ]           │
└──────────────────────────────────────────────────────────────────┘
```

Depois de clicar **Executar agora**, a janela de cópia nativa do Windows aparece (a mesma do Explorer — laranja, com progresso, velocidade e ETA). A cópia roda dentro do próprio Explorer, então você pode **fechar o app e o terminal — as cópias continuam**.

---

## 🧨 O problema

Tem um `.prproj` e precisa mandar só as mídias vinculadas pra outra máquina, editor freelancer, ou backup consolidado?

O **Project Manager** do Premiere é lento, trava em paths UNC longos, fica zuado com mídias offline, e se recusa a continuar quando falta um arquivo. Na prática, muita gente acaba copiando arquivo por arquivo na mão.

**Este app resolve assim:**
- Lê o `.prproj` (que é só gzip + XML por dentro)
- Extrai todas as mídias vinculadas
- Classifica em **CLIP** (originais em alta) vs **Proxy** automaticamente
- Gera uma pasta nova por projeto (nunca colide com outros)
- Dispara a API de cópia nativa do Windows
- Continua mesmo com mídias offline (só loga como ausente e segue)

---

## ✨ Features

- 🪟 **Janela de cópia nativa do Windows** — mesma do Explorer, com barra de progresso, velocidade e ETA
- 🧠 **Roda no Explorer, não no app** — fecha o terminal, fecha o app, reinicia a máquina: a cópia tá enfileirada no Windows e continua
- 🚀 **Paralelismo natural** — abre 5 projetos simultâneos sem bloquear (aproveita NVMe a 7000MB/s)
- 📁 **CLIP vs Proxy automático** — heurística simples: arquivo com `_Proxy` no nome ou em pasta `Proxies/` vai pra `Proxy/`; resto vai pra `CLIP/`
- 🇧🇷 **Acentos pt-BR preservados** — `Edição`, `Narração`, `2ª Edição` funcionam em paths, nomes de projeto e nomes de arquivo (UTF-8 BOM no script gerado)
- 🌐 **UNC e paths longos** — suporta `\\servidor\share\...` e paths > 260 chars nativamente
- 🚫 **Não trava em mídias offline** — arquivos ausentes viram log, não crash
- 📝 **Script `.ps1` auditável** — você pode abrir, revisar, editar, rodar de novo depois
- 🗂️ **Zero dependências de runtime** — Python 3.12 stdlib pura (Tkinter, gzip, xml, pathlib)
- 💾 **Configuração persistente** — escolheu o destino uma vez, salvou em `%APPDATA%` pra sempre

---

## 🚀 Quickstart

```powershell
git clone https://github.com/lucasftas/app-prproj-to-path-copy.git
cd app-prproj-to-path-copy
python -m src.app
```

Pronto. Na primeira execução, o app pede a pasta destino (salva em `%APPDATA%\app-prproj-to-path-copy\config.json`). Depois é só arrastar/selecionar um `.prproj`.

### Opcional — instalar como comando global

```powershell
pip install -e .
prproj-copy
```

---

## 📂 O que o app gera

Para cada `.prproj` processado:

```
<caminho-base>/
└── NOME_DO_PROJETO_20260424-1530/
    ├── CLIP/             # originais em alta
    │   ├── FFB-0001.MP4
    │   ├── FFB-0002.MP4
    │   └── ...
    ├── Proxy/            # proxies
    │   ├── FFB-0001_Proxy.MP4
    │   └── ...
    ├── copiar.ps1        # script PowerShell (UTF-8 BOM) que dispara as cópias
    └── lista-midias.txt  # auditoria: todo path, classificação e status (OK/AUSENTE)
```

---

## 🛠️ Como funciona por dentro

1. **`.prproj` é gzip + XML.** O app descomprime com `gzip` da stdlib e lê o XML como UTF-8.
2. **Extrai todo elemento `<ActualMediaFilePath>`** (regex simples, dedup, sort).
3. **Classifica cada path** em CLIP vs Proxy (heurística por nome/pasta).
4. **Confere existência** de cada mídia no filesystem (mídias offline viram AUSENTE).
5. **Gera um `.ps1` com UTF-8 BOM e CRLF** que usa `Shell.Application.CopyHere` — a mesma API COM que o Windows Explorer usa quando você copia arquivos na GUI.
6. **Dispara o script** em PowerShell externo com `-ExecutionPolicy Bypass`. O PS chama a API, o Explorer assume a cópia, e aí podemos fechar tudo — o Explorer continua sozinho.

**Por que `Shell.Application.CopyHere` e não `robocopy`/`Copy-Item`/`shutil`:**
- Mostra a janela de progresso nativa do Windows (o que o usuário já reconhece)
- A cópia roda no processo do Explorer, não no script — processo independente
- Consolidação automática de múltiplas operações no mesmo destino
- Lida com UNC, permissões, retry de rede do jeito que o Windows já sabe

---

## ⚙️ Stack

- **Linguagem:** Python 3.12+ (stdlib pura no runtime — zero deps)
- **GUI:** Tkinter
- **Engine de cópia:** `Shell.Application` (COM) via PowerShell
- **Plataforma:** Windows 10/11 (usa `%APPDATA%`, `Shell.Application`, PowerShell)

Dependências **opcionais**:
- `pytest` — testes (`pip install pytest && pytest`)
- `Pillow` — só pra regenerar o ícone (`python scripts/gen_icon.py`)

---

## 🗺️ Roadmap

v0.1.0 (atual) — MVP funcional:
- [x] GUI Tkinter
- [x] Parse `.prproj` + classificação CLIP/Proxy
- [x] Script `.ps1` UTF-8 BOM com `Shell.Application.CopyHere`
- [x] Configuração persistente em `%APPDATA%`
- [x] Auditoria em `lista-midias.txt`

v0.2.0 (planejado):
- [ ] Drag-and-drop nativo (via `tkinterdnd2`)
- [ ] Histórico dos últimos projetos consolidados
- [ ] Flag `--dry-run` pra listar sem copiar
- [ ] Empacotamento como `.exe` standalone (PyInstaller)
- [ ] Progress bar integrada na GUI (além do terminal)

v0.3.0+ (ideias):
- [ ] Suporte a `.aep` (After Effects), `.drp` (DaVinci Resolve), `.fcpxml` (Final Cut)
- [ ] Modo `--relink` que reescreve o `.prproj` com os novos paths
- [ ] Verificação de integridade (tamanho + hash opcional)
- [ ] Interface web local (servir via Flask/FastAPI pra rede)

---

## 🧪 Testes

```powershell
pip install pytest
pytest
```

20 testes cobrindo: parse do `.prproj`, extração de mídias, classificação CLIP/Proxy, geração do script com BOM UTF-8 + CRLF, escape de caracteres especiais do PowerShell.

---

## 🤝 Contribuindo

Issues e PRs bem-vindos! Esse app nasceu pra resolver um fluxo específico de edição de vídeo, mas a lógica é geral o bastante pra crescer. Algumas direções que eu adoraria ver:

- Port pra macOS (a Shell API é só Windows — no macOS pode usar `Finder` via AppleScript)
- Suporte a outros formatos de projeto (AE, DaVinci, FCP)
- Drag-and-drop com preview das mídias
- Modo CLI puro pra uso em scripts de automação

Antes de mandar PR grande, abre uma issue pra discutir. Pra mudanças pequenas (bug fix, doc typo), manda direto.

---

## 📝 Licença

[MIT](LICENSE). Use, copie, modifique, redistribua — só mantenha o aviso de copyright.

---

<div align="center">

**Feito com ☕ pra resolver um problema real de edição de vídeo.**

Se salvou seu dia, [⭐ deixe uma estrela](https://github.com/lucasftas/app-prproj-to-path-copy) — me ajuda a priorizar o próximo feature.

</div>
