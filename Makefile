# Makefile para mostrar ayuda, verificar la estructura base del repositorio y limpiar caches de Python/Jupyter.
.PHONY: help check clean

help:
    @echo "CC-0F4"
    @echo "  make check   Verifica archivos basicos del repositorio"
    @echo "  make clean   Elimina caches locales de Python y Jupyter"

check:
    @test -f README.md
    @test -f LICENSE
    @test -f .gitignore
    @echo "Estructura basica: OK"

clean:
    @find . -type d -name '__pycache__' -prune -exec rm -rf {} +
    @find . -type d -name '.ipynb_checkpoints' -prune -exec rm -rf {} +
    @find . -type d -name '.pytest_cache' -prune -exec rm -rf {} +
    @find . -type d -name '.ruff_cache' -prune -exec rm -rf {} +
