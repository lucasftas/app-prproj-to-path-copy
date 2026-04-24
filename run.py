"""Entry point do app — usado pelo PyInstaller e como atalho de execucao.

Mantem `src/` como pacote (imports relativos entre modulos funcionam), e este
arquivo na raiz serve como ponto de entrada sem ambiguidade.

Uso:
    python run.py                                    # dev
    python -m PyInstaller ... run.py                 # empacotamento
"""

from __future__ import annotations

import sys

from src.app import main


if __name__ == "__main__":
    sys.exit(main())
