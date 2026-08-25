### Entorno de ejecución de CC-0F4

#### Objetivo

CC-0F4 debe poder ejecutarse en CPU y, cuando exista hardware NVIDIA compatible, en GPU. El material base de Semana 1 es **CPU-first**.

#### Versiones fijadas para 2026-2

```text
Python 3.10+
PyTorch 2.11.0
CUDA de referencia: 12.8
JupyterLab 4.x
```

`requirements.txt` contiene las dependencias de alto nivel. PyTorch se instala por separado porque CPU y CUDA usan índices distintos.

#### Instalación local CPU

Linux o WSL:

```bash
python3 -m venv .ccf04
source .ccf04/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install torch==2.11.0 \
  --index-url https://download.pytorch.org/whl/cpu

make doctor
make check
```

Windows PowerShell:

```powershell
py -m venv .ccf04
.ccf04\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install torch==2.11.0 `
  --index-url https://download.pytorch.org/whl/cpu
```

#### Instalación local GPU NVIDIA

```bash
python -m pip install -r requirements.txt
python -m pip install torch==2.11.0 \
  --index-url https://download.pytorch.org/whl/cu128
```

Comprueba:

```bash
python -c "import torch; print(torch.__version__); print(torch.cuda.is_available()); print(torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU')"
```

#### Docker

Se usa una única imagen:

```text
pytorch/pytorch:2.11.0-cuda12.8-cudnn9-runtime
```

Construye:

```bash
make docker-build
```

o:

```bash
docker build --pull -t cc0f4:2026-2 .
```

#### Docker CPU

```bash
make docker-run-cpu
```

La imagen incluye runtime CUDA, pero si no se expone una GPU, PyTorch ejecuta las operaciones compatibles en CPU.

Comprueba:

```bash
make docker-check-cpu
```

#### Docker GPU NVIDIA en Linux

Requiere Docker Engine, driver NVIDIA y NVIDIA Container Toolkit.

Después de instalar el toolkit:

```bash
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker
```

Verifica:

```bash
docker run --rm --gpus all \
  nvidia/cuda:12.8.0-base-ubuntu22.04 \
  nvidia-smi
```

Luego:

```bash
make docker-check-gpu
make docker-run-gpu
```

#### Docker GPU NVIDIA en Windows

La imagen sigue siendo un **Linux container**. En Windows debe ejecutarse mediante Docker Desktop con backend WSL2.

Se requiere:

- Windows 10/11 compatible,
- WSL2 actualizado,
- GPU NVIDIA,
- driver NVIDIA compatible con WSL2,
- Docker Desktop con WSL2.

PowerShell:

```powershell
docker build --pull -t cc0f4:2026-2 .

docker run --rm -it `
  --gpus all `
  --shm-size=2g `
  -p 8888:8888 `
  -v "${PWD}:/workspace/CC-0F4" `
  cc0f4:2026-2
```

Para CPU elimina `--gpus all`.

#### Validación de Semana 1

Desde la raíz:

```bash
make check
```

Esto verifica los archivos obligatorios y la estructura `nbformat` de los dos notebooks.

Para ejecutar el cuaderno canónico:

```bash
make execute-cuaderno1
```

Salida:

```text
.build/Cuaderno1-CC-0F4.executed.ipynb
```

El laboratorio no se ejecuta automáticamente de inicio a fin porque contiene ejercicios y `TODO` intencionales.

También puedes comprobar el cuaderno dentro de Docker:

```bash
make docker-test-cuaderno1-cpu
```

#### Reproducibilidad

Cuando reportes un experimento registra, cuando corresponda:

```text
Python
PyTorch
CPU/GPU
modelo
seed
datos
configuración
métrica
resultado
```

#### Referencias oficiales

- PyTorch: https://pytorch.org/get-started/
- PyTorch Docker: https://hub.docker.com/r/pytorch/pytorch
- Docker Desktop GPU: https://docs.docker.com/desktop/features/gpu/
- NVIDIA Container Toolkit: https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html
