PYTHON ?= python3
PIP := $(PYTHON) -m pip

TORCH_VERSION ?= 2.11.0
TORCH_CPU_INDEX ?= https://download.pytorch.org/whl/cpu
TORCH_CUDA_INDEX ?= https://download.pytorch.org/whl/cu128

IMAGE ?= cc0f4:2026-2
WORKDIR ?= $(CURDIR)
BUILD_DIR ?= .build

WEEK ?= 1
WEEK_DIR := Semana$(WEEK)
CUADERNO := $(WEEK_DIR)/Cuaderno$(WEEK)-CC-0F4.ipynb
LABORATORIO := $(WEEK_DIR)/Laboratorio$(WEEK)-CC-0F4.ipynb

.PHONY: help setup install-cpu install-gpu install-course doctor \
	check check-root check-week validate-notebooks validate-week \
	execute-cuaderno docker-build docker-check-cpu docker-check-gpu \
	docker-run-cpu docker-run-gpu docker-test-cuaderno clean FORCE

help:
	@echo "CC-0F4 - entorno global del curso"
	@echo ""
	@echo "Instalacion:"
	@echo "  make setup                     Crea el unico entorno .ccf04"
	@echo "  make install-cpu               Instala PyTorch CPU + stack completo"
	@echo "  make install-gpu               Instala PyTorch CUDA 12.8 + stack completo"
	@echo "  make doctor                    Muestra versiones principales"
	@echo ""
	@echo "Validacion:"
	@echo "  make check                     Verifica todas las semanas existentes"
	@echo "  make check-week WEEK=2         Verifica una semana"
	@echo "  make check-semana2             Alias generico por patron"
	@echo "  make validate-notebooks        Valida todos los notebooks existentes"
	@echo ""
	@echo "Ejecucion:"
	@echo "  make execute-cuaderno WEEK=2   Ejecuta el cuaderno canonico de una semana"
	@echo "  make execute-cuaderno2         Alias generico por patron"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-build              Construye la imagen global"
	@echo "  make docker-check-cpu          Comprueba PyTorch en CPU"
	@echo "  make docker-check-gpu          Comprueba acceso a GPU NVIDIA"
	@echo "  make docker-run-cpu            Inicia JupyterLab en CPU"
	@echo "  make docker-run-gpu            Inicia JupyterLab con GPU NVIDIA"
	@echo "  make docker-test-cuaderno2     Ejecuta un cuaderno por patron"
	@echo ""
	@echo "  make clean                     Elimina caches y artefactos"

setup:
	$(PYTHON) -m venv .ccf04
	@echo "Activa el entorno:"
	@echo "  Linux/WSL: source .ccf04/bin/activate"
	@echo "  Windows PowerShell: .ccf04\\Scripts\\Activate.ps1"

# PyTorch se instala primero para evitar que dependencias de alto nivel
# seleccionen otra build de torch desde PyPI.
install-cpu:
	$(PIP) install --upgrade pip
	$(PIP) install torch==$(TORCH_VERSION) --index-url $(TORCH_CPU_INDEX)
	$(MAKE) install-course

install-gpu:
	$(PIP) install --upgrade pip
	$(PIP) install torch==$(TORCH_VERSION) --index-url $(TORCH_CUDA_INDEX)
	$(MAKE) install-course

install-course:
	$(PIP) install -r requirements.txt

doctor:
	$(PYTHON) -c "import sys; print('python=', sys.version.split()[0])"
	$(PYTHON) -c "import torch; print('torch=', torch.__version__); print('cuda_available=', torch.cuda.is_available()); print('device_count=', torch.cuda.device_count()); print('device=', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU')"
	$(PYTHON) -c "import transformers, numpy, pandas; print('transformers=', transformers.__version__); print('numpy=', numpy.__version__); print('pandas=', pandas.__version__)"

check-root:
	@test -f README.md
	@test -f LICENSE
	@test -f requirements.txt
	@test -f Makefile
	@test -f Dockerfile
	@test -f ENTORNO.md
	@echo "Raiz del curso: OK"

check: check-root
	@set -e; \
	found=0; \
	for dir in Semana[0-9]*; do \
		[ -d "$$dir" ] || continue; \
		found=1; \
		num=$${dir#Semana}; \
		$(MAKE) --no-print-directory check-week WEEK=$$num; \
	done; \
	if [ $$found -eq 0 ]; then \
		echo "No se encontraron carpetas SemanaN."; \
		exit 1; \
	fi
	@echo "Todas las semanas existentes: OK"

check-week:
	@test -d "$(WEEK_DIR)"
	@test -f "$(WEEK_DIR)/README.md"
	@test -f "$(CUADERNO)"
	@test -f "$(LABORATORIO)"
	@$(MAKE) --no-print-directory validate-week WEEK=$(WEEK)
	@echo "$(WEEK_DIR): estructura y notebooks OK"

validate-notebooks:
	$(PYTHON) -c "from pathlib import Path; import nbformat; ps=sorted(Path('.').glob('Semana[0-9]*/*.ipynb')); assert ps, 'No hay notebooks'; [nbformat.validate(nbformat.read(str(p), as_version=4)) for p in ps]; print(f'nbformat: {len(ps)} notebooks OK')"

validate-week:
	$(PYTHON) -c "from pathlib import Path; import nbformat; ps=sorted(Path('$(WEEK_DIR)').glob('*.ipynb')); assert ps, 'No hay notebooks en $(WEEK_DIR)'; [nbformat.validate(nbformat.read(str(p), as_version=4)) for p in ps]; print(f'$(WEEK_DIR): {len(ps)} notebooks nbformat OK')"

execute-cuaderno:
	@test -f "$(CUADERNO)"
	@mkdir -p $(BUILD_DIR)
	jupyter nbconvert \
		--to notebook \
		--execute "$(CUADERNO)" \
		--ExecutePreprocessor.timeout=180 \
		--output "$(CURDIR)/$(BUILD_DIR)/Cuaderno$(WEEK)-CC-0F4.executed.ipynb"
	@echo "Cuaderno ejecutado: $(BUILD_DIR)/Cuaderno$(WEEK)-CC-0F4.executed.ipynb"

# Reglas patron: no se agregan targets por semana.
check-semana%: FORCE
	@$(MAKE) --no-print-directory check-week WEEK=$*

execute-cuaderno%: FORCE
	@$(MAKE) --no-print-directory execute-cuaderno WEEK=$*

docker-test-cuaderno%: FORCE
	@$(MAKE) --no-print-directory docker-test-cuaderno WEEK=$*

docker-build:
	docker build --pull -t $(IMAGE) .

docker-check-cpu:
	docker run --rm $(IMAGE) \
		python -c "import torch; print('torch=', torch.__version__); print('cuda_available=', torch.cuda.is_available()); print('device=', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU')"

docker-check-gpu:
	docker run --rm --gpus all $(IMAGE) \
		python -c "import torch; assert torch.cuda.is_available(), 'CUDA no disponible dentro del contenedor'; print('torch=', torch.__version__); print('gpu=', torch.cuda.get_device_name(0)); print('device_count=', torch.cuda.device_count())"

docker-run-cpu:
	docker run --rm -it \
		--shm-size=2g \
		-p 8888:8888 \
		-v "$(WORKDIR):/workspace/CC-0F4" \
		$(IMAGE)

docker-run-gpu:
	docker run --rm -it \
		--gpus all \
		--shm-size=2g \
		-p 8888:8888 \
		-v "$(WORKDIR):/workspace/CC-0F4" \
		$(IMAGE)

docker-test-cuaderno:
	@test -f "$(CUADERNO)"
	@mkdir -p $(BUILD_DIR)
	docker run --rm \
		--shm-size=2g \
		-v "$(WORKDIR):/workspace/CC-0F4" \
		$(IMAGE) \
		jupyter nbconvert \
			--to notebook \
			--execute "/workspace/CC-0F4/$(CUADERNO)" \
			--ExecutePreprocessor.timeout=180 \
			--output "/workspace/CC-0F4/$(BUILD_DIR)/Cuaderno$(WEEK)-CC-0F4.docker.executed.ipynb"
	@echo "Cuaderno ejecutado en Docker: $(BUILD_DIR)/Cuaderno$(WEEK)-CC-0F4.docker.executed.ipynb"

clean:
	@find . -type d -name '__pycache__' -prune -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name '.ipynb_checkpoints' -prune -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name '.pytest_cache' -prune -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name '.ruff_cache' -prune -exec rm -rf {} + 2>/dev/null || true
	@rm -rf $(BUILD_DIR)

FORCE:
