### Semana 9: workflows, agentes, ReAct, planificación y parada

#### Objetivo

Aprender a distinguir un workflow fijo, un controlador adaptativo y un agente que toma decisiones con un LLM **sin confundir pruebas del controlador con resultados de un agente**. La teoría incluye ReAct, planificación, recuperación ante errores, validación de herramientas y trazas.

#### Datos reales y condiciones

- **Fuente:** SQuAD 1.1 dev, Wikipedia y preguntas/respuestas humanas originales.
- **Alcance obligatorio:** 48 artículos, 2.067 pasajes y 10.570 preguntas. No se permite sustituir por 16 preguntas.
- **Calibración:** 12 artículos seleccionados mediante hash de título antes de observar resultados. **Evaluación:** otros 36 artículos. No comparten artículos.
- **Recuperador:** BM25 idéntico en las tres políticas, indexa los 2.067 pasajes.
- **Políticas A0 / A1 / B:** top-1; top-3; top-1 y expansión a top-3 si la cobertura léxica es insuficiente. El umbral se selecciona solo en calibración.
- **Evaluación de recuperación:** Recall@1/3/5, MRR@10, acierto por política, contexto transportado, llamadas, errores por consulta. Los qrels identifican el **pasaje original** de cada respuesta, no son relevancia exhaustiva.
- **Evaluación LLM separada:** `agent_llm_eval.py` utiliza Qwen local, igual para el workflow fijo con LLM y el agente que decide herramientas. Calcula exact match (EM), F1 contra respuestas humanas, pasaje original citado, llamadas y paradas. Es un piloto, no un resultado general de toda SQuAD.

**Advertencia:** el ranking de B siempre está contenido en top-3; no puede tener mayor `evidence_hit` que A1. La comparación investiga compromisos de contexto y llamadas. Además, una cita observada no demuestra por sí sola fidelidad semántica.

#### Preparación antes de clase (una vez, con Internet)

Desde la raíz del repositorio `CC-0F4`:

```bash
python -m Semana9.prepare_real_data
python -m Semana9.prepare_real_data --check
```

Se descarga únicamente el archivo oficial público `dev-v1.1.json`, verificado con SHA256 y Git blob SHA1, sin claves, tokens de API ni datos prefabricados. Si ya se dispone de ese archivo, puede evitarse la descarga:

```bash
python -m Semana9.prepare_real_data --source-json /ruta/dev-v1.1.json
```

Los resultados de las semanas 9 y 12 se deben mantener separados. Ambos pueden leer la **misma fuente original**, pero no comparten calibración ni afirman resultados idénticos.

#### Laboratorio: políticas reales, sin LLM (obligatorio)

```bash
python -m unittest Semana9.test_prepare_real_data Semana9.test_agent_benchmark Semana9.test_agent_loop -v
python -m Semana9.agent_benchmark
```

El segundo comando calcula todas las preguntas: escribe `Semana9/resultados/runs.csv`, `traces.jsonl`, `summary.json`. Nunca crea filas de resultados sin procesar el corpus. Las métricas principales se reportan **solo en evaluación**. La calibración se publica por separado para auditar la elección de umbral.

Abre en JupyterLab:

1. `Semana9/Cuaderno9-CC-0F4.ipynb`, cuaderno explicativo.
2. `Semana9/Laboratorio9-CC-0F4.ipynb`, actividad integrada.

#### Agentes con LLM real (piloto docente, requiere pesos Qwen locales)

```bash
python -m Semana9.agent_llm_eval --n 100 --model-id Qwen/Qwen2.5-0.5B-Instruct
```

El piloto compara dos condiciones en las **mismas** 100 preguntas reales de la partición de evaluación: un workflow top-3 con Qwen y un agente que usa Qwen para decidir acciones. El código no simula el modelo si faltan los pesos. Para ampliar el piloto, cambie `--n` y registre el tamaño antes de inspeccionar resultados. La inferencia no forma parte de los tests offline obligatorios.

**La ausencia de una GPU o del modelo no se reemplaza por respuestas guionizadas.** En tal caso, la comparación LLM queda `NO EJECUTADA` y se puede completar la práctica de recuperación y control, sin concluir nada sobre capacidades de Qwen.

#### Qué debe entregar el estudiante

- Resultados de recuperación del conjunto completo, con tamaño de datos y hashes.
- Un ejemplo real donde B amplía y otro donde no; si alguno no existe, indicarlo.
- Dos casos de error real obtenidos del CSV, con IDs y pasajes relevantes.
- Traza de una acción rechazada, explicando el contrato aplicado. Los errores de seguridad inducidos en pruebas son **pruebas unitarias del controlador**, no datos de benchmark.
- Si se ejecutó Qwen, tabla EM/F1 pareada; si no, declaración explícita de no ejecución.

#### Alcance y procedencia

[Proyecto oficial de SQuAD](https://rajpurkar.github.io/SQuAD-explorer/) · [Fuente original SQuAD 1.1 dev](https://github.com/rajpurkar/SQuAD-explorer/blob/master/dataset/dev-v1.1.json). Licencia del conjunto SQuAD 1.1: CC BY-SA 4.0, con atribución al proyecto SQuAD y Wikipedia.

No se reclama puntuación oficial en el test oculto de SQuAD. La partición interna de `dev` evita fuga por artículo al calibrar B, pero no equivale a un benchmark independiente de una competición.
