PYTHON ?= python3
PIP := $(PYTHON) -m pip

TORCH_VERSION ?= 2.11.0
TORCH_CPU_INDEX ?= https://download.pytorch.org/whl/cpu
TORCH_CUDA_INDEX ?= https://download.pytorch.org/whl/cu128

IMAGE ?= cc0f4:semana1
WORKDIR ?= $(CURDIR)
BUILD_DIR ?= .build

CUADERNO1 := Semana1/Cuaderno1-CC-0F4.ipynb
LAB1 := Semana1/Laboratorio1-CC-0F4.ipynb

.PHONY: help setup install-base install-cpu install-gpu \
	check check-semana1 fix-semana1 validate-notebooks execute-cuaderno1 \
	docker-build docker-run-cpu docker-run-gpu docker-check clean

help:
	@echo "CC-0F4"
	@echo ""
	@echo "Entorno local:"
	@echo "  make setup             Crea .venv"
	@echo "  make install-cpu       Instala dependencias + PyTorch CPU"
	@echo "  make install-gpu       Instala dependencias + PyTorch CUDA 12.8"
	@echo ""
	@echo "Calidad:"
	@echo "  make check             Verifica estructura general y Semana 1"
	@echo "  make check-semana1     Audita nombres, estilo y contrato"
	@echo "  make fix-semana1       Aplica reemplazos editoriales seguros y audita"
	@echo "  make validate-notebooks Valida JSON/nbformat"
	@echo "  make execute-cuaderno1 Ejecuta el cuaderno canónico completo"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-build      Construye imagen reproducible"
	@echo "  make docker-run-cpu    JupyterLab sin exponer GPU"
	@echo "  make docker-run-gpu    JupyterLab con --gpus all"
	@echo "  make docker-check      Verifica torch y disponibilidad CUDA"
	@echo ""
	@echo "  make clean             Elimina caches y artefactos locales"

setup:
	$(PYTHON) -m venv .venv
	@echo "Activa el entorno antes de instalar:"
	@echo "  Linux/macOS: source .venv/bin/activate"
	@echo "  Windows PowerShell: .venv\\Scripts\\Activate.ps1"

install-base:
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

install-cpu: install-base
	$(PIP) install torch==$(TORCH_VERSION) --index-url $(TORCH_CPU_INDEX)

install-gpu: install-base
	$(PIP) install torch==$(TORCH_VERSION) --index-url $(TORCH_CUDA_INDEX)

check: check-semana1 validate-notebooks

check-semana1:
	$(PYTHON) scripts/audit_semana1.py

fix-semana1:
	$(PYTHON) scripts/audit_semana1.py --fix
	$(PYTHON) scripts/audit_semana1.py

validate-notebooks:
	$(PYTHON) -c "import json; [json.load(open(p, encoding='utf-8')) for p in ['$(CUADERNO1)','$(LAB1)']]; print('Notebook JSON: OK')"
	$(PYTHON) -c "import nbformat; [nbformat.validate(nbformat.read(p, as_version=4)) for p in ['$(CUADERNO1)','$(LAB1)']]; print('nbformat: OK')"

execute-cuaderno1:
	mkdir -p $(BUILD_DIR)
	jupyter nbconvert \
		--to notebook \
		--execute $(CUADERNO1) \
		--ExecutePreprocessor.timeout=180 \
		--output "$(CURDIR)/$(BUILD_DIR)/Cuaderno1-CC-0F4.executed.ipynb"

docker-build:
	docker build -t $(IMAGE) .

docker-run-cpu:
	docker run --rm -it \
		-p 8888:8888 \
		-v "$(WORKDIR):/workspace/CC-0F4" \
		$(IMAGE)

docker-run-gpu:
	docker run --rm -it \
		--gpus all \
		-p 8888:8888 \
		-v "$(WORKDIR):/workspace/CC-0F4" \
		$(IMAGE)

docker-check:
	docker run --rm $(IMAGE) \
		python -c "import torch; print('torch=', torch.__version__); print('cuda_available=', torch.cuda.is_available()); print('device_count=', torch.cuda.device_count())"

clean:
	@find . -type d -name '__pycache__' -prune -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name '.ipynb_checkpoints' -prune -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name '.pytest_cache' -prune -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name '.ruff_cache' -prune -exec rm -rf {} + 2>/dev/null || true
	@rm -rf $(BUILD_DIR)
