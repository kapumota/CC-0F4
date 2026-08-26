### Entorno global de CC-0F4

#### Principio

CC-0F4 utiliza **un solo entorno de software para todo el semestre**.

Las semanas contienen material académico:

```text
SemanaN/
  ->
README
cuaderno
laboratorio
lecturas
material de exposición
```

La infraestructura vive únicamente en la raíz:

```text
requirements.txt
Makefile
Dockerfile
ENTORNO.md
```

No se crean entornos, Dockerfiles, requirements ni Makefiles por semana.

#### Entorno Python

El entorno local recomendado es:

```text
.ccf04
```

Se crea una sola vez:

```bash
make setup
```

Linux/WSL:

```bash
source .ccf04/bin/activate
```

Windows PowerShell:

```powershell
.ccf04\Scripts\Activate.ps1
```

#### Stack del semestre

El archivo `requirements.txt` contiene las dependencias comunes para:

- notebooks y experimentación,
- Transformers y datasets,
- retrieval denso y sparse,
- structured generation y validación,
- evaluación,
- adaptación eficiente,
- recuperación multimodal.

PyTorch se mantiene fuera de `requirements.txt` porque la build depende del entorno de ejecución.

#### Instalación CPU

```bash
make install-cpu
```

El orden es intencional:

```text
PyTorch CPU -> requirements.txt
```

Esto evita que una dependencia de alto nivel seleccione automáticamente otra build de PyTorch.

#### Instalación NVIDIA GPU

```bash
make install-gpu
```

El flujo es:

```text
PyTorch CUDA 12.8 -> requirements.txt
```

#### Validación global

```bash
make check
```

`make check` descubre automáticamente las carpetas `SemanaN/` existentes y valida cada una.

No se modifica el Makefile cuando se agrega una semana nueva.

#### Validación de una semana

Ambas formas son equivalentes:

```bash
make check-week WEEK=2
make check-semana2
```

La segunda funciona mediante una regla patrón y seguirá funcionando con semanas futuras:

```bash
make check-semana3
make check-semana10
make check-semana16
```

sin editar `Makefile`.

#### Ejecución de un cuaderno canónico

Forma explícita:

```bash
make execute-cuaderno WEEK=2
```

Forma abreviada:

```bash
make execute-cuaderno2
```

El mismo Makefile resuelve automáticamente:

```text
Semana2/Cuaderno2-CC-0F4.ipynb
```

y para otra semana:

```text
SemanaN/CuadernoN-CC-0F4.ipynb
```

#### Docker

Se utiliza una sola imagen para todo el curso.

El `Dockerfile` de la raíz instala el `requirements.txt` global y no necesita cambiar cuando se añade una semana.

Construcción:

```bash
make docker-build
```

CPU:

```bash
make docker-run-cpu
```

NVIDIA:

```bash
make docker-run-gpu
```

Prueba de un cuaderno:

```bash
make docker-test-cuaderno2
```

Las reglas patrón permiten usar el mismo comando con cualquier semana futura.

#### Modelos y datasets externos

`requirements.txt` instala librerías, no pesos de modelos ni datasets grandes.

Los notebooks deben distinguir:

```text
dependencia de software != artefacto descargable
```

Un modelo de Hugging Face, un dataset o un checkpoint puede:

- estar precargado,
- descargarse explícitamente,
- omitirse cuando una sección sea opcional.

No debe ser razón para crear un entorno distinto por semana.

#### Reproducibilidad

Todo experimento debe registrar, cuando corresponda:

```text
Python
PyTorch
librerías relevantes
CPU/GPU
modelo
seed
datos o prompt
configuración
métrica
resultado
```

Para inferencia:

```text
decoding
context length
batch
precision
KV heads
unidad de memoria
supuestos del estimador
```

#### Regla para el resto del semestre

Al crear `Semana3/`, `Semana4/`, ..., `Semana16/`:

```text
se agregan materiales
```

pero no:

```text
nuevo entorno
nuevo Makefile
nuevo Dockerfile
requirements de la semana
```

Si una dependencia realmente nueva fuera imprescindible y no pudo preverse en el stack global, se trata como una **modificación excepcional de infraestructura del curso**, no como parte rutinaria de una semana.
