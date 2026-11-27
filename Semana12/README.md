### Semana 12: optimización y presupuesto de contexto

Dos horas de teoría y cuatro horas de laboratorio. Se utilizan preguntas humanas de SQuAD v1.1 dev completo. No se requieren GPU, token, API de pago ni entrenamiento de modelos. La versión v2 amplía los análisis del material anterior sin cambiar el ranking TF-IDF ni la política adaptativa.

#### Objetivos

Comparar políticas de contexto fijo y adaptativo, estudiar el compromiso calidad-costo, calibrar sin etiquetas de prueba, calcular incertidumbre por conglomerados y analizar errores reales. Distinguir recuperación, generación, adaptación de pesos y test-time compute.

#### Instalación del paquete v2 (docente)

Extraer el ZIP en Downloads. Desde Git Bash de Windows, ejecutar `find /c/Users/kapum/Downloads -maxdepth 5 -name instalar_semana12.py`. Desde la raíz de CC-0F4, ejecutar `py -3 RUTA_AL_INSTALADOR --repo .` con la ruta devuelta (entre comillas si tiene espacios). Revisar el DRY-RUN; para aplicar añadir `--apply`. El instalador solo escribe los archivos enumerados de Semana12, respalda los reemplazados en `.ccf04/semana12-backups/` y no toca datasets, CSV de resultados, otras semanas ni Git. No es necesario instalar de nuevo si los archivos ya coinciden.

#### Datos y preparación

Fuente original: [SQuAD](https://rajpurkar.github.io/SQuAD-explorer/). Espejo del proyecto: [dev-v1.1.json](https://raw.githubusercontent.com/rajpurkar/SQuAD-explorer/master/dataset/dev-v1.1.json). El archivo debe contener 48 artículos, 2067 párrafos y 10570 preguntas. Tamaño: 4854279 bytes. SHA-256:

`95aa6a52d5d6a735563366753ca50492a658031da74f301ac5238b03966972c9`

Dependencias comunes: Python, NumPy, pandas, scikit-learn, matplotlib y Jupyter. Desde la terminal de Docker, en la raíz del repositorio:

```bash
cd /workspace/CC-0F4
python -m Semana12.retrieval_real --check
```

Si falta el archivo, buscar primero el original ya utilizado en Semana 9:

```bash
find Semana9 -type f -name dev-v1.1.json
```

Si se encuentra, ejecutar `--prepare --origen` con la ruta exacta que devuelve `find`. No utilizar los JSONL derivados. Si no existe una copia original, ejecutar:

```bash
python -m Semana12.retrieval_real --prepare
```

El programa prueba la fuente original y su espejo, comprobando tamaño y SHA-256. Si ambas fallan dentro de Docker, descargar en Git Bash de Windows:

```bash
cd /c/Users/kapum/CC-0F4
mkdir -p Semana12/datos/importacion
curl -fL --retry 2 -o Semana12/datos/importacion/dev-v1.1.json.part https://raw.githubusercontent.com/rajpurkar/SQuAD-explorer/master/dataset/dev-v1.1.json
```

Solo si curl termina correctamente, verificar y renombrar:

```bash
cd Semana12/datos/importacion
printf '%s  %s\n' '95aa6a52d5d6a735563366753ca50492a658031da74f301ac5238b03966972c9' 'dev-v1.1.json.part' | sha256sum -c - && mv dev-v1.1.json.part dev-v1.1.json
```

En Docker:

```bash
cd /workspace/CC-0F4
python -m Semana12.retrieval_real --prepare --origen Semana12/datos/importacion/dev-v1.1.json
python -m Semana12.retrieval_real --check
```

No hay modo reducido ni sustitutos. Un archivo existente incorrecto se rechaza; no se sobrescribe silenciosamente.

#### Ejecución y conservación de evidencias

```bash
python -m unittest discover -s Semana12/tests -t . -p 'test_*.py' -v
python -m Semana12.retrieval_real --run
python -m Semana12.retrieval_real --check-results
```

La primera ejecución v2 calcula TF-IDF y el ranking una sola vez para las 10570 preguntas frente a 2067 párrafos. Las políticas, remuestreos y semillas reutilizan ese ranking. Los resultados se guardan en `Semana12/resultados/v2/`, sin tocar los archivos de la versión anterior. Las siguientes ejecuciones de `--run` reutilizan las salidas completas si las huellas del código, los datos declarados y los CSV coinciden. Si el código o las salidas cambiaron, se detiene; conservar la carpeta v2 antes de regenerar deliberadamente una nueva ejecución. El comando `--check` verifica los bytes del dataset; `--check-results` verifica los artefactos almacenados, sin inferencia ni ranking.

#### Diseño experimental

- Partición principal por artículo, semilla 2026, 24 artículos para desarrollo y 24 para prueba. El índice incluye todos los párrafos y no usa etiquetas. El conjunto de prueba es interno al dev público, no el test oculto de SQuAD.
- A0 (top-1), F2 (top-2), F3 (top-3), F4 (top-4), A1 (top-5). B utiliza top-1 o top-5 según el margen entre las primeras dos similitudes. Los ocho umbrales candidatos se conservan. Para lambda = 0.025, el umbral y el mejor baseline fijo se eligen exclusivamente en desarrollo; los empates prefieren el menor umbral o k.
- Utilidad por pregunta = acierto - lambda × párrafos. Los promedios principales ponderan cada pregunta por igual. El IC95 percentil usa 2000 remuestreos de artículos completos, con denominador de preguntas recalculado en cada réplica; se informa además el estimando macro por artículo, sin confundirlo con el micro.
- Comparación a presupuesto medio igual: interpolación de las tasas top-k adyacentes con peso determinado por el costo medio de B, sin utilizar las etiquetas para escoger el peso. Es el acierto esperado de una mezcla aleatoria independiente de la pregunta, no una ejecución aleatoria ni una comparación contra el mejor algoritmo posible. En cada réplica bootstrap se iguala de nuevo el costo. La diferencia de utilidad coincide con la diferencia de acierto a igual costo.
- Sensibilidad de lambda: malla 0 a 0.100 en pasos 0.001, tanto B congelada como B recalibrada en desarrollo para cada lambda. La frontera exacta de políticas congeladas se calcula por cruces de rectas (los extremos pueden ser empates). No seleccionar la política usando el test. Las ocho semillas 2026 a 2033 son un análisis de sensibilidad, no ocho pruebas independientes ni una búsqueda de la mejor semilla.

#### Archivos de resultados

| Archivo dentro de resultados/v2 | Contenido |
|---|---|
| resumen.json | Configuración, métricas, IC, frontera, hashes, versiones |
| calibracion_solo_desarrollo.csv | Utilidades y umbrales de desarrollo |
| resultados_todas_las_consultas_test.csv | Predicciones, costos y aciertos de cada política |
| ranking_todas_las_consultas.csv | Ranking y resultados de ambas particiones |
| errores_top5_test.csv | Todos los fallos top-5 |
| muestra_errores_test.csv | Hasta tres errores reproducibles de artículos distintos cuando sea posible |
| sensibilidad_lambda.csv | Políticas congeladas y B recalibrada por lambda |
| sensibilidad_semillas.csv | Umbral, diferencia entre mejores candidatos y métricas por semilla |
| desglose_articulo.csv | Métricas y errores por artículo |
| desglose_tipo_pregunta.csv | Métricas por palabra interrogativa inicial |
| particion_articulos.csv | Asignación de artículos |

Las pruebas aritméticas de ingeniería no contienen preguntas fabricadas ni constituyen un benchmark; la prueba de integración con el dataset requiere el original instalado. No se adjuntan valores experimentales precalculados. Los resultados de la primera versión reportados por el docente motivan los análisis adicionales; las cifras v2 deben salir de los archivos generados en Docker.

#### Uso de los cuadernos

Abrir `Cuaderno12-CC-0F4.ipynb` para teoría (120 minutos) y `Laboratorio12-CC-0F4.ipynb` para actividades (240 minutos). Los cuadernos reutilizan las salidas verificadas y no descargan datos. La primera ejecución del benchmark debe realizarse desde la terminal. El laboratorio requiere programar celdas de análisis y defender decisiones con evidencia real.

#### Límites de interpretación

Las preguntas fueron redactadas por personas que tenían acceso al párrafo fuente, lo que puede favorecer la recuperación léxica. Solo hay una referencia de párrafo por pregunta; otros pasajes pueden ser válidos. El análisis secundario se diseñó después de observar resultados de la primera versión. No se evalúan respuestas LLM, tokens, costo de API, razonamiento ni LoRA. Un párrafo no tiene longitud constante; la utilidad usa un costo convencional, no un costo físico. Las bandas bootstrap son exploratorias, condicionales a las políticas ajustadas; no ajustadas por comparaciones múltiples.

#### Git

Antes de añadir archivos, verificar que el `.gitignore` general contenga estas reglas (añadirlas si faltan):

```gitignore
/Semana12/datos/dev-v1.1.json
/Semana12/datos/importacion/
/Semana12/datos/*.tmp
/Semana12/datos/*.part
```

Conservar la documentación de datos. Revisar individualmente los resultados antes de publicar; no incluir el dataset ni modificar otras semanas. El paquete no modifica `.gitignore` ni realiza operaciones Git.
