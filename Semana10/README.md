### Semana 10: Memoria de agentes, persistencia y recuperación sobre QMSum

**Dos horas de teoría y cuatro de laboratorio.** Mantiene los tres recursos centrales del curso: `Lectura10-CC-0F4.md`, `Cuaderno10-CC-0F4.ipynb` y `Laboratorio10-CC-0F4.ipynb`. Los módulos de Python son apoyos para no copiar implementaciones extensas dentro de cada cuaderno.

#### Datos y alcance

Benchmark: [QMSum](https://github.com/Yale-LILY/QMSum), **Academic + Committee**, `train/val/test` íntegros; datos originales sin preguntas inventadas. El commit y los hashes de los seis archivos están congelados en `memoria_real.py`. Se excluye el dominio Product (reuniones de producto escenificadas). Las anotaciones humanas `relevant_text_span` se usan para evaluación, nunca como características de recuperación.

**Qué se compara:** ventana de los 48 turnos recientes (`working_recent`) frente a memoria persistente SQLite + BM25 top-48 (`episodic_bm25`). Ambas usan el mismo presupuesto de turnos. Se reporta Recall por turnos y AnyHit, por pregunta y global. **No hay evaluación de LLM, resumen generativo ni memoria semántica neuronal.**

#### Instalación desde Windows y Git Bash

Entorno utilizado en el curso:

- Descargas de Windows: `C:\Users\kapum\Downloads`.
- Repositorio Git local: `C:\Users\kapum\CC-0F4`.
- Repositorio montado en Docker/JupyterLab: `/workspace/CC-0F4`.

El ZIP trae `instalar_semana10.py` **en su raíz**, fuera de la carpeta `Semana10/`.
Descarga el ZIP en `Downloads`, utiliza **Extraer todo** y comprueba que allí estén
`instalar_semana10.py` y la carpeta `Semana10`. El instalador se ejecuta en Git Bash
con Python de Windows; **no copies manualmente encima de una Semana10 existente**.

Desde **Git Bash de Windows**:

```bash
cd /c/Users/kapum/CC-0F4
find /c/Users/kapum/Downloads -maxdepth 5 -type f -name instalar_semana10.py
```

Si has descomprimido el ZIP en una carpeta con el mismo nombre, los comandos son:

```bash
# Inspección sin cambios (DRY-RUN)
py -3 /c/Users/kapum/Downloads/CC0F4_Semana10_QMSum_Integrada_Sin_Guia/instalar_semana10.py --repo .

# Solo si la inspección muestra los cambios esperados: instalación con respaldo
py -3 /c/Users/kapum/Downloads/CC0F4_Semana10_QMSum_Integrada_Sin_Guia/instalar_semana10.py --repo . --apply

git status --short -- Semana10/
```

Si el nombre de la carpeta extraída es diferente, **sustituye la ruta del script
por la que devolvió `find`**. Si Windows no reconoce `py -3`, comprueba si
`python --version` está disponible y usa `python` en su lugar.

El instalador respalda los archivos que sustituya en una carpeta hermana de
`CC-0F4`, conserva cualquier actividad o archivo local adicional y no toca otras semanas.
La reinstalación de archivos idénticos no requiere otro respaldo. No realiza commits,
`push` ni cambios remotos. Si Git tiene modificaciones pendientes en otras semanas,
**no las elimines**.

#### Ejecución desde Docker Desktop y JupyterLab

Abre el **JupyterLab habitual** y selecciona `File > New > Terminal`.
Estos comandos se ejecutan **dentro de Docker**, no en Git Bash de Windows:

```bash
cd /workspace/CC-0F4
pwd
ls Semana10/

# Pruebas de ingeniería, no resultados experimentales
python -m unittest discover -s Semana10/tests -t . -p 'test_*.py' -v

# Descargar las seis fuentes originales de QMSum y verificar integridad
python -m Semana10.memoria_real --preparar
python -m Semana10.memoria_real --verificar

# Evaluación real: primero validación y luego prueba
python -m Semana10.memoria_real --evaluar val
python -m Semana10.memoria_real --evaluar test
```

Las pruebas unitarias deben terminar en `OK`; en el entorno de preparación pasaron 12 pruebas. **No hay resultados de QMSum pregrabados**. Si falla la descarga, no se reemplaza QMSum por datos sintéticos. Revisa los resultados reales en `Semana10/resultados/` después de ejecutar.

Abre luego desde el explorador de JupyterLab:

- `Semana10/Cuaderno10-CC-0F4.ipynb` (teoría).
- `Semana10/Laboratorio10-CC-0F4.ipynb` (laboratorio).

El laboratorio es autónomo respecto del cuaderno, pero requiere los seis archivos originales. Si JupyterLab sigue mostrando una versión antigua, cierra su pestaña **sin sobrescribir el archivo actualizado**, refresca el explorador y vuelve a abrir.
No necesitas reconstruir la imagen Docker mientras el volumen de Windows ya esté montado en `/workspace/CC-0F4`.

Para comprobar el contenido en Docker:

```bash
python -c "import json,pathlib; n=json.loads(pathlib.Path('Semana10/Cuaderno10-CC-0F4.ipynb').read_text(encoding='utf-8')); print('Celdas:',len(n['cells']),'Dataset:',n['metadata']['cc0f4']['data'])"
```

Debe indicar 29 celdas y `QMSum Academic/Committee original, train/val/test`.

#### Limpieza y preparación de Git

Después de guardar los notebooks puedes borrar **solo cachés regenerables** con
la herramienta ya instalada en la Semana 9:

```bash
python scripts/limpiar_caches.py           # vista previa
python scripts/limpiar_caches.py --apply   # eliminación segura
```

No utilices `make clean` si quieres conservar `.build`, que puede contener notebooks ejecutados. El limpiador preserva datos, resultados, SQLite, notebooks y modelos.

**No subas todavía la Semana 10**: primero ejecuta los tests y las evaluaciones en Docker y revisa los resultados. Para preparar un commit selectivo desde Git Bash, usa `git status --short -- Semana10/` y `git diff --cached --name-only`, **no uses `git add .`, `git clean -fd` ni `git reset --hard`**, porque otras semanas tienen trabajo local pendiente. No añadas los seis JSONL originales ni la base SQLite.

#### Archivos generados

- `datos/{Academic,Committee}_{train,val,test}.jsonl`: archivos reales originales, no subirlos como código.
- `datos/qmsum_episodic.sqlite3`: SQLite persistente, creado al evaluar.
- `resultados/qmsum_val_resumen.json`, `qmsum_test_resumen.json`: resultados reales, **solo después de ejecutar**.
- `resultados/qmsum_*_por_consulta.jsonl`: trazabilidad por consulta.

`.gitignore` de la semana excluye únicamente grandes fuentes originales y la base SQLite. No se incluyen puntuaciones experimentales prefabricadas.

#### Mejoras didácticas integradas

Se trabajan las ideas de conflicto de escritura, persistencia idempotente, diferencia entre recencia y vigencia, abstención no verificable sin negativos, contratos de integridad y errores recuperativos observados en reuniones reales. No se convierten resúmenes de incidencias de software en un segundo benchmark.


