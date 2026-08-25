PYTHON ?= python3
PIP := $(PYTHON) -m pip

TORCH_VERSION ?= 2.11.0
TORCH_CPU_INDEX ?= https://download.pytorch.org/whl/cpu
TORCH_CUDA_INDEX ?= https://download.pytorch.org/whl/cu128

IMAGE ?= cc0f4:2026-2
WORKDIR ?= $(CURDIR)
BUILD_DIR ?= .build

CUADERNO1 := Semana1/Cuaderno1-CC-0F4.ipynb
LAB1 := Semana1/Laboratorio1-CC-0F4.ipynb
LECTURA1 := Semana1/Lectura1-CC-0F4.md
LECTURA2 := Semana1/Lectura2-CC-0F4.md
README1 := Semana1/README.md
ENTORNO := ENTORNO.md

.PHONY: help setup install-base install-cpu install-gpu doctor \
	check check-files check-semana1 validate-notebooks execute-cuaderno1 \
	docker-build docker-check-cpu docker-check-gpu \
	docker-run-cpu docker-run-gpu docker-test-cuaderno1-cpu clean

help:
	@echo "CC-0F4 - entorno reproducible"
	@echo ""
	@echo "Entorno local:"
	@echo "  make setup                    Crea .ccf04"
	@echo "  make install-cpu              Instala dependencias + PyTorch CPU"
	@echo "  make install-gpu              Instala dependencias + PyTorch CUDA 12.8"
	@echo "  make doctor                   Muestra versiones y dispositivo disponible"
	@echo ""
	@echo "Validacion:"
	@echo "  make check                    Ejecuta verificaciones de Semana 1"
	@echo "  make check-files              Verifica archivos requeridos"
	@echo "  make validate-notebooks       Valida estructura de notebooks"
	@echo "  make execute-cuaderno1        Ejecuta Cuaderno1 de inicio a fin"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-build             Construye la imagen"
	@echo "  make docker-check-cpu         Comprueba PyTorch sin GPU expuesta"
	@echo "  make docker-check-gpu         Comprueba acceso a GPU NVIDIA"
	@echo "  make docker-run-cpu           Inicia JupyterLab en CPU"
	@echo "  make docker-run-gpu           Inicia JupyterLab con GPU NVIDIA"
	@echo "  make docker-test-cuaderno1-cpu Ejecuta Cuaderno1 dentro del contenedor"
	@echo ""
	@echo "  make clean                    Elimina caches y artefactos"

setup:
	$(PYTHON) -m venv .ccf04
	@echo "Activa el entorno:"
	@echo "  Linux/WSL: source .ccf04/bin/activate"
	@echo "  Windows PowerShell: .ccf04\\Scripts\\Activate.ps1"

install-base:
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

install-cpu: install-base
	$(PIP) install torch==$(TORCH_VERSION) --index-url $(TORCH_CPU_INDEX)

install-gpu: install-base
	$(PIP) install torch==$(TORCH_VERSION) --index-url $(TORCH_CUDA_INDEX)

doctor:
	$(PYTHON) -c "import sys; print('python=', sys.version.split()[0])"
	$(PYTHON) -c "import torch; print('torch=', torch.__version__); print('cuda_available=', torch.cuda.is_available()); print('device_count=', torch.cuda.device_count()); print('device=', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU')"

check: check-semana1

check-semana1: check-files validate-notebooks
	@echo "Semana 1: estructura y notebooks OK"

check-files:
	@test -f README.md
	@test -f LICENSE
	@test -f requirements.txt
	@test -f Makefile
	@test -f Dockerfile
	@test -f $(ENTORNO)
	@test -f $(README1)
	@test -f $(CUADERNO1)
	@test -f $(LAB1)
	@test -f $(LECTURA1)
	@test -f $(LECTURA2)
	@echo "Archivos requeridos: OK"

validate-notebooks:
	$(PYTHON) -c "import json; [json.load(open(p, encoding='utf-8')) for p in ['$(CUADERNO1)','$(LAB1)']]; print('Notebook JSON: OK')"
	$(PYTHON) -c "import nbformat; [nbformat.validate(nbformat.read(p, as_version=4)) for p in ['$(CUADERNO1)','$(LAB1)']]; print('nbformat: OK')"

execute-cuaderno1:
	@mkdir -p $(BUILD_DIR)
	jupyter nbconvert \
		--to notebook \
		--execute $(CUADERNO1) \
		--ExecutePreprocessor.timeout=180 \
		--output "$(CURDIR)/$(BUILD_DIR)/Cuaderno1-CC-0F4.executed.ipynb"
	@echo "Cuaderno1 ejecutado: $(BUILD_DIR)/Cuaderno1-CC-0F4.executed.ipynb"

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

docker-test-cuaderno1-cpu:
	@mkdir -p $(BUILD_DIR)
	docker run --rm \
		--shm-size=2g \
		-v "$(WORKDIR):/workspace/CC-0F4" \
		$(IMAGE) \
		jupyter nbconvert \
			--to notebook \
			--execute /workspace/CC-0F4/$(CUADERNO1) \
			--ExecutePreprocessor.timeout=180 \
			--output /workspace/CC-0F4/$(BUILD_DIR)/Cuaderno1-CC-0F4.docker.executed.ipynb
	@echo "Cuaderno1 ejecutado dentro de Docker: $(BUILD_DIR)/Cuaderno1-CC-0F4.docker.executed.ipynb"

clean:
	@find . -type d -name '__pycache__' -prune -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name '.ipynb_checkpoints' -prune -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name '.pytest_cache' -prune -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name '.ruff_cache' -prune -exec rm -rf {} + 2>/dev/null || true
	@rm -rf $(BUILD_DIR)
