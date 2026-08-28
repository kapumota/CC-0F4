# Makefile 
PYTHON ?= python
PIP := $(PYTHON) -m pip

TORCH_VERSION ?= 2.11.0
TORCHVISION_VERSION ?= 0.26.0
TORCHAUDIO_VERSION ?= 2.11.0

TORCH_CPU_INDEX ?= https://download.pytorch.org/whl/cpu
TORCH_CUDA_INDEX ?= https://download.pytorch.org/whl/cu128

IMAGE ?= cc0f4:2026-2
WORKDIR ?= $(CURDIR)
BUILD_DIR ?= .build
NOTEBOOK_TIMEOUT ?= 600

# Si se define, check valida solo estas semanas.
# Ejemplo:
# make CHECK_WEEKS="1 2 3 4" check
CHECK_WEEKS ?=

WEEK ?= 1
WEEK_DIR := Semana$(WEEK)
CUADERNO := $(WEEK_DIR)/Cuaderno$(WEEK)-CC-0F4.ipynb
LABORATORIO := $(WEEK_DIR)/Laboratorio$(WEEK)-CC-0F4.ipynb

# Semanas que deliberadamente no tienen laboratorio canónico.
# Semana 3 usa el jueves completo para la evaluación oral E1.
NO_LAB_WEEKS ?= 3

.PHONY: help setup \
	install-cpu install-gpu install-course verify-torch-stack doctor \
	check check-root check-week validate-notebooks validate-week \
	execute-cuaderno \
	docker-build docker-check-cpu docker-check-gpu \
	docker-run-cpu docker-run-gpu docker-test-cuaderno \
	clean FORCE


help:
	@echo "CC-0F4 - entorno global del curso"
	@echo ""
	@echo "Instalacion:"
	@echo "  make setup"
	@echo "      Crea el unico entorno .ccf04"
	@echo ""
	@echo "  make install-cpu"
	@echo "      Instala PyTorch CPU + stack completo"
	@echo ""
	@echo "  make install-gpu"
	@echo "      Instala PyTorch CUDA 12.8 + stack completo"
	@echo ""
	@echo "  make verify-torch-stack"
	@echo "      Verifica versiones del stack PyTorch"
	@echo ""
	@echo "  make doctor"
	@echo "      Muestra versiones principales"
	@echo ""
	@echo "Validacion:"
	@echo "  make check"
	@echo "      Verifica todas las semanas existentes"
	@echo ""
	@echo "  make CHECK_WEEKS=\"1 2 3 4\" check"
	@echo "      Verifica solo las semanas indicadas"
	@echo ""
	@echo "  make check-week WEEK=2"
	@echo "  make check-semana2"
	@echo "  make validate-notebooks"
	@echo ""
	@echo "Ejecucion:"
	@echo "  make execute-cuaderno WEEK=2"
	@echo "  make execute-cuaderno2"
	@echo ""
	@echo "  CC0F4_RUN_REAL_LLM=0 make execute-cuaderno3"
	@echo "  CC0F4_RUN_REAL_RETRIEVAL=0 make execute-cuaderno4"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-build"
	@echo "  make docker-check-cpu"
	@echo "  make docker-check-gpu"
	@echo "  make docker-run-cpu"
	@echo "  make docker-run-gpu"
	@echo "  make docker-test-cuaderno2"
	@echo ""
	@echo "Limpieza:"
	@echo "  make clean"


setup:
	@test ! -d .ccf04 || { \
		echo "ERROR: .ccf04 ya existe"; \
		echo "Activa el entorno existente en lugar de recrearlo."; \
		exit 1; \
	}
	$(PYTHON) -m venv .ccf04
	@echo ""
	@echo "Activa el entorno:"
	@echo "  Linux/WSL:"
	@echo "    source .ccf04/bin/activate"
	@echo ""
	@echo "  Windows Git Bash:"
	@echo "    source .ccf04/Scripts/activate"
	@echo ""
	@echo "  Windows PowerShell:"
	@echo "    .ccf04\\Scripts\\Activate.ps1"


# PyTorch, torchvision y torchaudio se fijan conjuntamente.
# Esto evita que una dependencia como open-clip-torch instale una
# torchvision más reciente que termine actualizando torch.
install-cpu:
	$(PIP) install --upgrade pip
	$(PIP) install \
		torch==$(TORCH_VERSION) \
		torchvision==$(TORCHVISION_VERSION) \
		torchaudio==$(TORCHAUDIO_VERSION) \
		--index-url $(TORCH_CPU_INDEX)
	$(MAKE) --no-print-directory install-course
	$(MAKE) --no-print-directory verify-torch-stack
	$(PIP) check


install-gpu:
	$(PIP) install --upgrade pip
	$(PIP) install \
		torch==$(TORCH_VERSION) \
		torchvision==$(TORCHVISION_VERSION) \
		torchaudio==$(TORCHAUDIO_VERSION) \
		--index-url $(TORCH_CUDA_INDEX)
	$(MAKE) --no-print-directory install-course
	$(MAKE) --no-print-directory verify-torch-stack
	$(PIP) check


# only-if-needed es también la estrategia normal de pip, pero se declara
# explícitamente porque el stack PyTorch ya fue seleccionado arriba.
install-course:
	$(PIP) install \
		--upgrade-strategy only-if-needed \
		-r requirements.txt


verify-torch-stack:
	$(PYTHON) -c "import torch, torchvision, torchaudio; \
	actual=(torch.__version__.split('+')[0], torchvision.__version__.split('+')[0], torchaudio.__version__.split('+')[0]); \
	expected=('$(TORCH_VERSION)', '$(TORCHVISION_VERSION)', '$(TORCHAUDIO_VERSION)'); \
	assert actual == expected, f'Stack PyTorch incorrecto: actual={actual}, esperado={expected}'; \
	print('Stack PyTorch: OK', actual)"


doctor:
	$(PYTHON) -c "import sys; print('python=', sys.version.split()[0]); print('executable=', sys.executable); print('prefix=', sys.prefix)"
	$(PYTHON) -c "import torch; print('torch=', torch.__version__); print('cuda_available=', torch.cuda.is_available()); print('device_count=', torch.cuda.device_count()); print('device=', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU')"
	$(PYTHON) -c "import torchvision, torchaudio; print('torchvision=', torchvision.__version__); print('torchaudio=', torchaudio.__version__)"
	$(PYTHON) -c "import transformers, numpy, pandas; print('transformers=', transformers.__version__); print('numpy=', numpy.__version__); print('pandas=', pandas.__version__)"
	$(PYTHON) -c "import nbformat, nbconvert; print('nbformat=', nbformat.__version__); print('nbconvert=', nbconvert.__version__)"


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
	if [ -n "$(strip $(CHECK_WEEKS))" ]; then \
		for num in $(CHECK_WEEKS); do \
			case "$$num" in \
				''|*[!0-9]*) \
					echo "Semana invalida en CHECK_WEEKS: $$num"; \
					exit 1 ;; \
			esac; \
			$(MAKE) --no-print-directory check-week WEEK="$$num"; \
		done; \
		echo "Semanas solicitadas: OK"; \
	else \
		found=0; \
		for dir in Semana[0-9]*; do \
			[ -d "$$dir" ] || continue; \
			num=$${dir#Semana}; \
			case "$$num" in \
				''|*[!0-9]*) continue ;; \
			esac; \
			found=1; \
			$(MAKE) --no-print-directory check-week WEEK="$$num"; \
		done; \
		if [ $$found -eq 0 ]; then \
			echo "No se encontraron carpetas SemanaN."; \
			exit 1; \
		fi; \
		echo "Todas las semanas existentes: OK"; \
	fi


check-week:
	@test -d "$(WEEK_DIR)"
	@test -f "$(WEEK_DIR)/README.md"
	@test -f "$(CUADERNO)"
	@case " $(NO_LAB_WEEKS) " in \
		*" $(WEEK) "*) \
			echo "$(WEEK_DIR): sin laboratorio canonico" ;; \
		*) \
			test -f "$(LABORATORIO)" ;; \
	esac
	@$(MAKE) --no-print-directory validate-week WEEK=$(WEEK)
	@echo "$(WEEK_DIR): estructura y notebooks OK"


validate-notebooks:
	$(PYTHON) -c "from pathlib import Path; import nbformat; ps=sorted(Path('.').glob('Semana[0-9]*/*.ipynb')); assert ps, 'No hay notebooks'; [nbformat.validate(nbformat.read(str(p), as_version=4)) for p in ps]; print(f'nbformat: {len(ps)} notebooks OK')"


validate-week:
	$(PYTHON) -c "from pathlib import Path; import nbformat; ps=sorted(Path('$(WEEK_DIR)').glob('*.ipynb')); assert ps, 'No hay notebooks en $(WEEK_DIR)'; [nbformat.validate(nbformat.read(str(p), as_version=4)) for p in ps]; print(f'$(WEEK_DIR): {len(ps)} notebooks nbformat OK')"


execute-cuaderno:
	@test -f "$(CUADERNO)"
	@mkdir -p $(BUILD_DIR)
	$(PYTHON) -m nbconvert \
		--to notebook \
		--execute "$(CUADERNO)" \
		--ExecutePreprocessor.timeout=$(NOTEBOOK_TIMEOUT) \
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
	MSYS_NO_PATHCONV=1 docker run --rm \
		--shm-size=2g \
		-v "$(WORKDIR):/workspace/CC-0F4" \
		$(IMAGE) \
		python -m nbconvert \
			--to notebook \
			--execute "/workspace/CC-0F4/$(CUADERNO)" \
			--ExecutePreprocessor.timeout=$(NOTEBOOK_TIMEOUT) \
			--output "/workspace/CC-0F4/$(BUILD_DIR)/Cuaderno$(WEEK)-CC-0F4.docker.executed.ipynb"
	@echo "Cuaderno ejecutado en Docker: $(BUILD_DIR)/Cuaderno$(WEEK)-CC-0F4.docker.executed.ipynb"

clean:
	@find . -type d -name '__pycache__' -prune -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name '.ipynb_checkpoints' -prune -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name '.pytest_cache' -prune -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name '.ruff_cache' -prune -exec rm -rf {} + 2>/dev/null || true
	@rm -rf $(BUILD_DIR)


FORCE:
