"""GUI Tkinter do app-prproj-to-path-copy.

Fluxo:
  1. Na 1a execucao, pede caminho base (pasta destino fixa)
  2. Usuario seleciona um .prproj
  3. App parseia, classifica, checa existencia
  4. Mostra resumo (CLIP/Proxy, existentes, ausentes, tamanho)
  5. Botoes: [Executar agora] (dispara PS) ou [So gerar script]
"""

from __future__ import annotations

import os
import subprocess
import sys
import tkinter as tk
from pathlib import Path, PureWindowsPath
from tkinter import filedialog, messagebox, ttk

from . import config
from .classifier import MediaItem, classify
from .paths import human_size, safe_name, timestamp_suffix
from .prproj_reader import PrprojReadError, list_media_paths
from .script_generator import build_ps1_script, write_audit_txt, write_ps1


# ------------------------------------------------------------------------------
# Logica de processamento
# ------------------------------------------------------------------------------


def process_prproj(prproj_path: Path, caminho_base: Path) -> dict:
    """Processa um .prproj e prepara a subpasta destino + script + auditoria.

    Retorna dict com chaves:
      - subdir: Path da subpasta criada
      - ps1_path: Path do script gerado
      - audit_path: Path do lista-midias.txt
      - items: list[MediaItem]
      - prproj_name: nome do .prproj (sem extensao)
      - stats: dict com contagens e tamanho
    """
    media_paths = list_media_paths(prproj_path)

    items: list[MediaItem] = []
    for mp in media_paths:
        p = Path(mp)
        try:
            exists = p.is_file()
            size = p.stat().st_size if exists else 0
        except OSError:
            exists = False
            size = 0
        items.append(classify(mp, exists, size))

    prproj_name = prproj_path.stem
    subdir_name = f"{safe_name(prproj_name)}_{timestamp_suffix()}"
    subdir = caminho_base / subdir_name
    dest_clip = subdir / "CLIP"
    dest_proxy = subdir / "Proxy"
    dest_clip.mkdir(parents=True, exist_ok=True)
    dest_proxy.mkdir(parents=True, exist_ok=True)

    ps1_content = build_ps1_script(items, dest_clip, dest_proxy, prproj_name)
    ps1_path = write_ps1(ps1_content, subdir / "copiar.ps1")
    audit_path = write_audit_txt(items, subdir / "lista-midias.txt", prproj_name)

    clips = [i for i in items if i.kind == "clip"]
    proxies = [i for i in items if i.kind == "proxy"]
    existing = [i for i in items if i.exists]
    total_bytes = sum(i.size_bytes for i in existing)

    return {
        "subdir": subdir,
        "ps1_path": ps1_path,
        "audit_path": audit_path,
        "items": items,
        "prproj_name": prproj_name,
        "stats": {
            "total": len(items),
            "clip_count": len(clips),
            "proxy_count": len(proxies),
            "existing_count": len(existing),
            "missing_count": len(items) - len(existing),
            "existing_bytes": total_bytes,
        },
    }


def run_ps1_external(ps1_path: Path) -> None:
    """Dispara o .ps1 numa janela PowerShell nova (com -ExecutionPolicy Bypass)."""
    cmd = [
        "powershell.exe",
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        str(ps1_path),
    ]
    # CREATE_NEW_CONSOLE = 0x00000010 — abre janela visivel separada
    creationflags = 0x00000010 if sys.platform == "win32" else 0
    subprocess.Popen(cmd, creationflags=creationflags)


def open_in_explorer(path: Path) -> None:
    """Abre um path no Windows Explorer."""
    if sys.platform == "win32":
        os.startfile(str(path))  # noqa: S606
    else:
        subprocess.Popen(["xdg-open", str(path)])


# ------------------------------------------------------------------------------
# GUI
# ------------------------------------------------------------------------------


ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"
ICON_PATH = ASSETS_DIR / "icon.ico"


class App(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("prproj → path copy")
        self.geometry("720x520")
        self.minsize(640, 480)

        if ICON_PATH.is_file():
            try:
                self.iconbitmap(default=str(ICON_PATH))
            except tk.TclError:
                pass  # ambiente sem suporte a iconbitmap — ignora

        self._caminho_base: Path | None = None
        self._prproj_path: Path | None = None
        self._last_result: dict | None = None

        self._build_ui()
        self._refresh_caminho_base(initial=True)

    # ---------- UI construction ----------

    def _build_ui(self) -> None:
        pad = {"padx": 12, "pady": 8}

        header = ttk.Frame(self)
        header.pack(fill="x", **pad)
        ttk.Label(
            header,
            text="Consolidador de midias do Premiere (.prproj → CLIP/Proxy)",
            font=("Segoe UI", 12, "bold"),
        ).pack(anchor="w")
        ttk.Label(
            header,
            text="Gera subpasta unica + script PowerShell que usa a API nativa de copia do Windows.",
            foreground="#555",
        ).pack(anchor="w")

        # Caminho base
        base_frame = ttk.LabelFrame(self, text="Caminho base (destino fixo)")
        base_frame.pack(fill="x", **pad)
        self.var_caminho_base = tk.StringVar(value="(nao configurado)")
        ttk.Label(base_frame, textvariable=self.var_caminho_base, foreground="#0066cc").pack(
            side="left", padx=8, pady=6, fill="x", expand=True
        )
        ttk.Button(base_frame, text="Alterar...", command=self._pick_caminho_base).pack(
            side="right", padx=8, pady=6
        )

        # .prproj picker
        prproj_frame = ttk.LabelFrame(self, text="Arquivo .prproj")
        prproj_frame.pack(fill="x", **pad)
        self.var_prproj = tk.StringVar(value="(nenhum selecionado)")
        ttk.Label(prproj_frame, textvariable=self.var_prproj, foreground="#0066cc").pack(
            side="left", padx=8, pady=6, fill="x", expand=True
        )
        ttk.Button(prproj_frame, text="Selecionar...", command=self._pick_prproj).pack(
            side="right", padx=8, pady=6
        )

        # Action
        action_frame = ttk.Frame(self)
        action_frame.pack(fill="x", **pad)
        self.btn_process = ttk.Button(
            action_frame, text="Processar .prproj", command=self._on_process, state="disabled"
        )
        self.btn_process.pack(side="left")

        # Output / resumo
        output_frame = ttk.LabelFrame(self, text="Resumo")
        output_frame.pack(fill="both", expand=True, **pad)
        self.txt_output = tk.Text(
            output_frame, height=12, wrap="word", font=("Consolas", 10)
        )
        self.txt_output.pack(fill="both", expand=True, padx=6, pady=6)
        self.txt_output.config(state="disabled")

        # Footer: botoes pos-processamento (inicialmente escondidos)
        self.footer = ttk.Frame(self)
        self.footer.pack(fill="x", **pad)
        self.btn_execute = ttk.Button(
            self.footer, text="Executar agora", command=self._on_execute, state="disabled"
        )
        self.btn_execute.pack(side="left")
        self.btn_open_folder = ttk.Button(
            self.footer,
            text="Abrir pasta no Explorer",
            command=self._on_open_folder,
            state="disabled",
        )
        self.btn_open_folder.pack(side="left", padx=8)
        self.btn_open_script = ttk.Button(
            self.footer,
            text="Abrir script (sem executar)",
            command=self._on_open_script,
            state="disabled",
        )
        self.btn_open_script.pack(side="left")

    # ---------- Caminho base ----------

    def _refresh_caminho_base(self, initial: bool = False) -> None:
        """Le o caminho base do config. Se nao existir, abre dialog na 1a execucao."""
        cb = config.get_caminho_base()
        if cb and Path(cb).is_dir():
            self._caminho_base = Path(cb)
            self.var_caminho_base.set(str(self._caminho_base))
            return

        if initial:
            messagebox.showinfo(
                "Configuracao inicial",
                "Escolha a pasta base onde os projetos consolidados serao salvos.\n"
                "Essa escolha fica salva — voce pode alterar depois.",
            )
        self._pick_caminho_base()

    def _pick_caminho_base(self) -> None:
        initial = str(self._caminho_base) if self._caminho_base else os.path.expanduser("~")
        chosen = filedialog.askdirectory(
            title="Escolha a pasta base (destino fixo)",
            initialdir=initial,
            mustexist=True,
        )
        if not chosen:
            return
        self._caminho_base = Path(chosen)
        config.set_caminho_base(chosen)
        self.var_caminho_base.set(chosen)
        self._update_process_button_state()

    # ---------- .prproj ----------

    def _pick_prproj(self) -> None:
        initial = (
            str(self._prproj_path.parent) if self._prproj_path else os.path.expanduser("~")
        )
        chosen = filedialog.askopenfilename(
            title="Selecione um arquivo .prproj",
            initialdir=initial,
            filetypes=[("Adobe Premiere Project", "*.prproj"), ("Todos os arquivos", "*.*")],
        )
        if not chosen:
            return
        self._prproj_path = Path(chosen)
        self.var_prproj.set(chosen)
        self._update_process_button_state()

    def _update_process_button_state(self) -> None:
        ready = bool(self._caminho_base and self._prproj_path)
        self.btn_process.config(state="normal" if ready else "disabled")

    # ---------- Processamento ----------

    def _on_process(self) -> None:
        assert self._prproj_path and self._caminho_base
        self._write_output(f"Processando {self._prproj_path.name}...\n")
        self.update_idletasks()

        try:
            result = process_prproj(self._prproj_path, self._caminho_base)
        except PrprojReadError as exc:
            messagebox.showerror("Erro ao ler .prproj", str(exc))
            self._write_output(f"\nERRO: {exc}\n")
            return
        except Exception as exc:  # noqa: BLE001 — reportar qualquer falha pro usuario
            messagebox.showerror("Erro inesperado", f"{type(exc).__name__}: {exc}")
            self._write_output(f"\nERRO: {type(exc).__name__}: {exc}\n")
            return

        self._last_result = result
        self._show_summary(result)
        self.btn_execute.config(state="normal")
        self.btn_open_folder.config(state="normal")
        self.btn_open_script.config(state="normal")

    def _show_summary(self, result: dict) -> None:
        s = result["stats"]
        subdir: Path = result["subdir"]
        items: list[MediaItem] = result["items"]

        missing_items = [i for i in items if not i.exists]

        lines = [
            f"Projeto:   {result['prproj_name']}",
            f"Destino:   {subdir}",
            "",
            f"Total de midias encontradas: {s['total']}",
            f"  • CLIP  (alta):  {s['clip_count']}",
            f"  • Proxy:         {s['proxy_count']}",
            "",
            f"Existentes:  {s['existing_count']}  ({human_size(s['existing_bytes'])})",
            f"Ausentes:    {s['missing_count']}",
            "",
            f"Script gerado:   {result['ps1_path'].name}",
            f"Lista auditoria: {result['audit_path'].name}",
        ]

        if missing_items:
            lines.append("")
            lines.append(f"[{len(missing_items)} arquivo(s) ausente(s) — serao pulados]")
            for i in missing_items[:10]:
                lines.append(f"   AUSENTE: {PureWindowsPath(i.path).name}")
            if len(missing_items) > 10:
                lines.append(f"   ... e mais {len(missing_items) - 10}")

        lines.append("")
        lines.append("Pronto. Clique em 'Executar agora' pra copiar, ou so gerar.")
        self._write_output("\n".join(lines))

    def _on_execute(self) -> None:
        if not self._last_result:
            return
        ps1_path: Path = self._last_result["ps1_path"]
        try:
            run_ps1_external(ps1_path)
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("Erro ao executar", f"{type(exc).__name__}: {exc}")
            return

        # Feedback inline, sem bloquear a GUI — libera pra processar outro .prproj em paralelo
        self._append_output(
            "\n\n>>> Disparado. A janela nativa de copia do Windows vai aparecer.\n"
            ">>> Pode fechar o PowerShell, pode fechar este app — a copia continua\n"
            ">>> no Explorer ate terminar. Selecione outro .prproj pra rodar em paralelo."
        )
        # Reset parcial: mantem resumo, mas desabilita o botao executar
        # (pra evitar duplo-clique disparando o mesmo script duas vezes)
        self.btn_execute.config(state="disabled")

    def _on_open_folder(self) -> None:
        if not self._last_result:
            return
        open_in_explorer(self._last_result["subdir"])

    def _on_open_script(self) -> None:
        if not self._last_result:
            return
        open_in_explorer(self._last_result["ps1_path"])

    # ---------- Helpers ----------

    def _write_output(self, text: str) -> None:
        self.txt_output.config(state="normal")
        self.txt_output.delete("1.0", "end")
        self.txt_output.insert("1.0", text)
        self.txt_output.config(state="disabled")

    def _append_output(self, text: str) -> None:
        self.txt_output.config(state="normal")
        self.txt_output.insert("end", text)
        self.txt_output.see("end")
        self.txt_output.config(state="disabled")


def main() -> int:
    # Garante stdout/stderr UTF-8 no Windows
    if sys.platform == "win32":
        try:
            sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
            sys.stderr.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
        except Exception:  # noqa: BLE001 — best-effort
            pass
    app = App()
    app.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
