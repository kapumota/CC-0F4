#!/usr/bin/env python3
"""Limpieza segura de caches generadas por Python y Jupyter en CC-0F4.

Por defecto solo muestra candidatos. --apply los elimina. No borra datos,
resultados de experimentos, notebooks, modelos, entornos virtuales ni .build.
Puede ejecutarse desde Git Bash o desde el terminal del contenedor Docker.
"""
from __future__ import annotations

import argparse
import os
import shutil
from pathlib import Path

CACHE_DIRS = frozenset({
    "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache",
    ".hypothesis", ".pytype",
})
PRUNE_DIRS = frozenset({
    ".git", ".ccf04", ".venv", "venv", "env", "ENV", ".conda",
    "node_modules", ".build", "build", "dist", "data", "datos",
    "datos_reales", "datasets", "resultados", "outputs", "models",
    "modelos", "checkpoints", "weights", "pesos", ".cache",
})
JUPYTER_DIRS = frozenset({".ipynb_checkpoints"})
CACHE_EXTENSIONS = (".pyc", ".pyo")
MAX_PREVIEW = 25


def find_candidates(root: Path, include_jupyter: bool = False) -> tuple[list[Path], list[Path]]:
    """Solo recoge archivos / directorios de cache reales, nunca symlinks."""
    dirs_to_remove: list[Path] = []
    files_to_remove: list[Path] = []
    for current, dirs, files in os.walk(root, topdown=True, followlinks=False):
        current_path = Path(current)
        kept = []
        for name in dirs:
            candidate = current_path / name
            if candidate.is_symlink():
                continue
            if name in CACHE_DIRS or (include_jupyter and name in JUPYTER_DIRS):
                dirs_to_remove.append(candidate)
            elif name not in PRUNE_DIRS and name not in JUPYTER_DIRS:
                kept.append(name)
        dirs[:] = kept
        for name in files:
            candidate = current_path / name
            if name.endswith(CACHE_EXTENSIONS) and not candidate.is_symlink():
                files_to_remove.append(candidate)
    return sorted(dirs_to_remove), sorted(files_to_remove)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true",
                        help="Eliminar caches detectadas. Sin esta opción solo informa.")
    parser.add_argument("--include-jupyter", action="store_true",
                        help="También eliminar .ipynb_checkpoints (solo con Jupyter cerrado).")
    parser.add_argument("--repo", type=Path,
                        default=Path(__file__).resolve().parent.parent,
                        help="Raíz del repositorio (opcional).")
    args = parser.parse_args()
    root = args.repo.resolve()
    if not (root / "Makefile").is_file() or not (root / "Semana9").is_dir():
        parser.error("--repo debe apuntar a la raíz de CC-0F4 (Makefile y Semana9)")
    if root.is_symlink():
        parser.error("No se aceptan raíces simbólicas")
    dirs, files = find_candidates(root, include_jupyter=args.include_jupyter)
    print("Repositorio:", root)
    print("Directorios de caché:", len(dirs), "| archivos .pyc/.pyo:", len(files))
    for path in (dirs + files)[:MAX_PREVIEW]:
        print("  ", path.relative_to(root))
    remaining = len(dirs) + len(files) - MAX_PREVIEW
    if remaining > 0:
        print(f"  ... y {remaining} elementos adicionales")
    if not args.apply:
        print("VISTA PREVIA: nada eliminado. Para limpiar agrega --apply.")
        return
    # Revalidación básica antes de borrar. No eliminar objetivos externos.
    for path in files:
        if path.is_symlink() or not path.is_file() or not path.resolve().is_relative_to(root):
            continue
        path.unlink()
    for path in dirs:
        if path.is_symlink() or not path.is_dir() or not path.resolve().is_relative_to(root):
            continue
        shutil.rmtree(path)
    print("LIMPIEZA TERMINADA. Se conservaron datos, resultados, notebooks y entornos.")


if __name__ == "__main__":
    main()
