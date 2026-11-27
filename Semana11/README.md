### Semana 11: coordinación de agentes y evaluación con HotpotQA

Esta semana corresponde a dos horas de teoría y cuatro horas de laboratorio de CC-0F4.
Se mantienen tres materiales centrales: `Lectura11-CC-0F4.md`, `Cuaderno11-CC-0F4.ipynb` y `Laboratorio11-CC-0F4.ipynb`.
La implementación Python evita copiar grandes bloques de código en los cuadernos.

#### Objetivos y separación de evidencias

El curso distingue tres componentes que no deben confundirse:

1. Recuperación BM25 de oraciones sobre las 7.405 preguntas originales de HotpotQA dev distractor. Se usa el contexto suministrado con cada pregunta, no una búsqueda en toda Wikipedia.
2. Contratos y coordinación de mensajes con pizarra de solo adición. Las pruebas de corrupción de mensajes son unitarias, no un resultado empírico sobre HotpotQA.
3. Piloto opcional de agentes LLM reales, con un mismo modelo Qwen para agente único y supervisor con dos trabajadores. El supervisor es determinista y **los trabajadores seleccionan evidencia y generan respuestas con inferencias reales**.

La comparación de agentes no iguala el número de llamadas ni el presupuesto de inferencia. Sirve para analizar fallos, costos y calidad en un piloto exploratorio, no para afirmar superioridad científica.

#### Datos originales

Fuente: [HotpotQA](https://hotpotqa.github.io/), archivo público `hotpot_dev_distractor_v1.json`, 7.405 preguntas humanas y oraciones de apoyo anotadas.
El hash SHA-256 oficial aceptado por el código es `4e9ecb5c8d3b719f624d66b60f8d56bf227f03914f5f0753d6fa1b359d7104ea`.
La fuente se descarga o se copia desde el archivo oficial ya disponible; no se generan consultas sintéticas para la evaluación.
Las respuestas y los `supporting_facts` se consultan solamente después de obtener la predicción.

Las transcripciones y eventos de LangGraph revisados en el paquete anterior se aprovechan como antecedentes didácticos de contratos y fallos. Sus 23 preguntas redactadas para clase y 15 resúmenes no se utilizan como benchmark.

#### Instalación en Windows, Git Bash y Docker Desktop

Ubicaciones de trabajo confirmadas:

- ZIP y carpeta extraída: `C:\Users\kapum\Downloads`
- Repositorio local: `C:\Users\kapum\CC-0F4`
- Repositorio montado en Docker/JupyterLab: `/workspace/CC-0F4`

Después de extraer el ZIP, localiza el instalador desde Git Bash:

```bash
cd /c/Users/kapum/CC-0F4
find /c/Users/kapum/Downloads -maxdepth 5 -name instalar_semana11.py
```

Con la carpeta de descarga sugerida, primero inspecciona sin cambios y después aplica:

```bash
py -3 /c/Users/kapum/Downloads/CC0F4_Semana11_HotpotQA_Integrada/instalar_semana11.py --repo .
py -3 /c/Users/kapum/Downloads/CC0F4_Semana11_HotpotQA_Integrada/instalar_semana11.py --repo . --apply
```

El instalador crea una copia de seguridad de cualquier archivo que sustituya, no borra actividades adicionales y no realiza commits, push ni operaciones remotas. **No copies manualmente sobre una carpeta Semana11 ya modificada**.

#### Configuración de .gitignore

El repositorio tiene un `.gitignore` general. Semana11 no incorpora otro archivo `.gitignore`.
El instalador permite consolidar las exclusiones de datos generados en la raíz, con una comprobación estricta de las versiones originales. La operación es opcional y separada de la instalación docente:

```bash
py -3 /c/Users/kapum/Downloads/CC0F4_Semana11_HotpotQA_Integrada/instalar_semana11.py --repo . --consolidar-ignores
py -3 /c/Users/kapum/Downloads/CC0F4_Semana11_HotpotQA_Integrada/instalar_semana11.py --repo . --consolidar-ignores --apply
```

Esta consolidación mueve las reglas específicas de datos QMSum y HotpotQA al `.gitignore` general y solo retira `Semana10/.gitignore` si coincide exactamente con la versión auditada; no modifica datos existentes. Si el archivo general o el de Semana10 cambiaron, la operación se detiene y no fuerza nada.

#### Pruebas y evaluación en Docker

Abre Docker Desktop, tu JupyterLab habitual y `File > New > Terminal`. Ejecuta:

```bash
cd /workspace/CC-0F4
python -m unittest discover -s Semana11/tests -t . -p 'test_*.py' -v
python -m Semana11.multiagente_real --preparar
python -m Semana11.multiagente_real --verificar
python -m Semana11.multiagente_real --evaluar-recuperacion
```

La descarga se realiza una vez. Si HotpotQA ya está en otra carpeta, usa su archivo original para ahorrar descarga:

```bash
python -m Semana11.multiagente_real --preparar --origen Semana13/datos/hotpot_dev_distractor_v1.json
```

Si `--preparar` ya descargó y verificó el archivo, no ejecutes el comando alternativo. En caso de error de hash no se crea un corpus sustitutivo.

La evaluación de recuperación procesa todas las 7.405 preguntas y genera:

- `Semana11/resultados/hotpot_recuperacion_resumen.json`
- `Semana11/resultados/hotpot_recuperacion_7405_por_consulta.jsonl`

Se reportan Recall de oraciones de apoyo, tasa AnyHit y tasa AllHit, con desglose por tipo y dificultad. No se mide generación LLM en esta etapa.

#### Piloto opcional con Qwen real

Antes de clase, verifica que Docker tiene suficiente RAM o GPU. El modelo de referencia es `Qwen/Qwen2.5-1.5B-Instruct`. Requiere descargar los pesos al menos una vez y usa las dependencias comunes del curso.

```bash
python -m Semana11.multiagente_real --piloto-llm 16 --modelo Qwen/Qwen2.5-1.5B-Instruct
```

Las 16 preguntas se seleccionan con una regla de hash fijada antes de observar resultados, no con selección de casos favorables. Este tamaño es una comprobación exploratoria del procedimiento. **No constituye una evaluación generalizable de agentes multiagente**. Para realizar más inferencias reales, incrementa el número de preguntas con `--piloto-llm N` y registra el presupuesto del equipo antes de observar los resultados.

El piloto registra EM, F1 de respuesta, F1 de citas, finalizaciones válidas, llamadas al modelo, tokens y tiempos. Un JSON inválido cuenta como fallo; no se repara ni se sustituye por una respuesta artificial. La verificación de citas solo asegura procedencia, no apoyo factual.

El resultado de la Semana 9 con Qwen 0.5B fue desfavorable para el agente; eso justifica ejecutar una prueba exploratoria en la Semana 11 antes de comprometer una comparación mayor. La versión 1.5B no garantiza mejores resultados.

#### Evaluación experimental de recuperación

La evaluación utiliza las 7.405 preguntas originales de HotpotQA v1, partición dev distractor. La integridad del dataset fue comprobada mediante SHA-256 antes de iniciar los experimentos.

La recuperación selecciona hasta 14 oraciones del contexto proporcionado para cada pregunta.

Para ejecutar el benchmark:

```bash
python -m Semana11.multiagente_real --evaluar-recuperacion
```

#### Resultados de referencia

| Tipo de pregunta | Consultas | Recall medio | AnyHit | AllHit |
|---|---:|---:|---:|---:|
| Global | 7405 | 0.8190 | 0.9818 | 0.6188 |
| Bridge | 5918 | 0.8055 | 0.9816 | 0.5874 |
| Comparison | 1487 | 0.8726 | 0.9825 | 0.7438 |

Se realizaron dos ejecuciones completas con métricas agregadas idénticas. La segunda ejecución registró una duración total de 6.1 segundos en el entorno Docker utilizado por el docente. El tiempo puede variar según el equipo.

Los resultados se almacenan en:

- `resultados/hotpot_recuperacion_7405_por_consulta.jsonl`
- `resultados/hotpot_recuperacion_resumen.json`

#### Interpretación y limitaciones

El benchmark evalúa recuperación de evidencia, no generación de respuestas.

Cada pregunta dispone de su propio conjunto de párrafos distractores. No se realiza recuperación sobre un corpus documental abierto.

Las evidencias de referencia se utilizan exclusivamente para la evaluación, no para seleccionar las oraciones recuperadas.

Un valor elevado de AnyHit no garantiza la recuperación completa de la evidencia necesaria. Los resultados muestran una diferencia entre la recuperación parcial y completa, especialmente en las preguntas de tipo bridge.

Estos resultados no demuestran superioridad de una arquitectura multiagente frente a un agente único.

#### Pruebas unitarias

Se ejecutaron satisfactoriamente las 25 pruebas unitarias del módulo de Semana 11. Estas pruebas verifican el comportamiento funcional del código y son independientes de la evaluación experimental sobre HotpotQA.

#### Uso de cuadernos y entregables

Desde JupyterLab abre `Semana11/Cuaderno11-CC-0F4.ipynb` y `Semana11/Laboratorio11-CC-0F4.ipynb`. Ambos usan los módulos del repositorio y trabajan con preguntas originales.

El estudiante debe entregar una tabla de recuperación de 7.405 preguntas, análisis de trazas reales, pruebas de los contratos de coordinación y un diagnóstico de fallos. Si ejecutó Qwen, separará los resultados del piloto; si no, deberá declarar que la inferencia LLM no se realizó.

#### Limpieza y preparación para Git

La limpieza reutiliza la herramienta de la raíz del curso, sin eliminar datos ni resultados:

```bash
python scripts/limpiar_caches.py
python scripts/limpiar_caches.py --apply
```

No añadas a GitHub el archivo JSON oficial de HotpotQA; es descargable y está protegido por `.gitignore` tras la consolidación. Revisa siempre `git status --short` y `git diff --cached --name-only` antes de seleccionar archivos, para no incluir modificaciones locales de otras semanas. No hay que reconstruir la imagen Docker si el repositorio de Windows ya está montado en `/workspace/CC-0F4`.

#### Fuentes y limitaciones

- Yang et al., HotpotQA, EMNLP 2018: https://arxiv.org/abs/1809.09600
- Wu et al., AutoGen, 2023: https://arxiv.org/abs/2308.08155
- Anthropic, Building Effective Agents: https://www.anthropic.com/research/building-effective-agents
- Why Do Multi-Agent LLM Systems Fail?, 2025: https://arxiv.org/abs/2503.13657

No se distribuyen puntuaciones inventadas ni se afirma éxito del agente antes de ejecutar el modelo.
