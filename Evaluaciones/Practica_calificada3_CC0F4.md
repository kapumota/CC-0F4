### CC0F4 - Tercera Práctica Calificada
#### De sistemas RAG evaluables a workflows, agentes controlados y memoria verificable

**Curso:** CC0F4 - Tópicos de Ciencia de la Computación I  
**Periodo:** 2026-2  
**Cobertura:** Semanas 9 y 10, con reutilización de las semanas 1 a 7  
**Duración propuesta:** 10 días calendario  
**Modalidad:** individual, excepto el grupo de dos estudiantes previamente autorizado  
**Entregables:** repositorio GitHub + diapositivas + demostración y defensa oral  
**Nota máxima:** 20 puntos

### 1. Propósito

Esta práctica continúa el mismo tema de investigación desarrollado en la PC1, PC2 y el examen parcial.

El examen parcial dejó un baseline de recuperación, RAG, evaluación y contratos de herramientas. Ahora corresponde estudiar dos problemas que no podían resolverse únicamente mediante un pipeline de recuperación y generación:

1. Cómo coordinar varias operaciones para completar una tarea, controlando las decisiones, los errores y las condiciones de terminación.
2. Cómo conservar y recuperar información de ejecuciones anteriores sin confundir recuerdos con hechos actuales.

El objetivo no es construir un sistema multiagente completo ni incorporar bibliotecas por acumulación. Debes desarrollar una extensión pequeña, ejecutable y medible que permita comprobar **si la autonomía y la memoria aportan una mejora real frente a alternativas más sencillas**.

Se evaluará la adaptación razonada de los conceptos del curso a tu proyecto y no la cantidad de herramientas, agentes o componentes incorporados.

### 2. Relación con las semanas 9 y 10

#### Semana 9. Workflows, planificación y ReAct

Debes comprender y aplicar:

- Diferencias entre pipeline, workflow determinista y agente controlado por un LLM.
- Patrones `prompt chaining`, `routing`, `parallelization`, `evaluator-optimizer` y `orchestrator-workers`.
- Arquitectura de un agente: modelo, controlador, estado, herramientas, acciones y observaciones.
- Ciclo `Perceive -> Decide -> Act -> Observe`.
- ReAct como intercalación de decisiones, acciones y observaciones.
- Planificación, descomposición y replanning.
- Control mediante `max_steps`, límites de tokens, timeouts y criterios de parada.
- Detección de llamadas repetidas, ciclos, progreso insuficiente y terminación incorrecta.
- Instrumentación y comparación experimental de ejecución.

Debes poder explicar qué decisiones son del LLM y cuáles pertenecen al controlador determinista.

Una secuencia fija de llamadas a herramientas no constituye, por sí misma, un agente autónomo.

#### Semana 10. Estado y memoria de agentes

Debes distinguir:

- Estado de ejecución y contexto conversacional.
- Working memory y límites de contexto.
- Memoria episódica de tareas, acciones y observaciones.
- Memoria semántica de conocimiento recuperable.
- Memoria procedimental como instrucciones y políticas reutilizables.
- Persistencia entre ejecuciones o sesiones.
- Escritura, lectura, actualización, invalidación y eliminación.
- Selección por relevancia, recencia e importancia.
- Recuperación de recuerdos incorrectos u obsoletos.
- Costos, privacidad y trazabilidad de memoria.

No basta con guardar mensajes en un archivo y denominarlos memoria episódica. Debes demostrar qué se almacena, cómo se recupera, cuándo se utiliza y qué ocurre cuando deja de ser válido.

### 3. Tarea mínima

Selecciona una tarea multi-paso relacionada directamente con el proyecto que vienes desarrollando.

La tarea debe requerir **al menos dos operaciones diferentes** de recuperación, análisis, validación o consulta mediante herramientas.

El sistema debe producir una respuesta estructurada, con evidencia y un estado de terminación verificable.

La arquitectura mínima tendrá dos variantes:

**A. Workflow determinista**

```text
entrada validada
-> plan fijo
-> recuperación de evidencia
-> llamada a herramienta
-> evaluación de resultados
-> respuesta estructurada
-> validación final
```

**B. Agente controlado por LLM**

```text
entrada validada
-> estado inicial
-> decisión del modelo
-> acción mediante herramienta
-> observación validada
-> actualización del estado
-> nueva decisión o terminación
-> respuesta estructurada
```

El agente debe poder seleccionar entre al menos dos herramientas u operaciones, decidir continuar o terminar y justificar sus decisiones mediante información contenida en las trazas.

Las herramientas se ejecutarán exclusivamente a través de un controlador con contratos y políticas de seguridad. No se permite que el modelo ejecute comandos arbitrarios.

### 4. Requisitos mínimos

#### Reutilización del proyecto

Conserva los siguientes elementos del examen parcial:

- Corpus real y sus identificadores.
- Consultas y `qrels` cuando correspondan.
- Recuperador y arquitectura RAG seleccionada.
- Modelo generador y configuración.
- Contratos y validadores de herramientas.
- Métricas y registros experimentales.

Puedes corregir errores demostrados, pero documenta cada corrección. No modifiques silenciosamente los resultados originales ni reemplaces el baseline anterior.

#### Benchmark de tareas

Define **al menos 10 tareas multi-paso**, con resultados esperados independientes de las respuestas del agente.

Incluye:

- Al menos 6 tareas ordinarias que requieren dos o más operaciones.
- Al menos 2 tareas donde una herramienta falla, devuelve un error o no encuentra evidencia.
- Al menos 2 tareas donde corresponde detenerse, abstenerse o rechazar una conclusión no sustentada.

Las tareas pueden reutilizar documentos y casos del examen parcial. Deben incorporar nuevas condiciones multi-paso, sin exigir un corpus nuevo.

Cada tarea incluirá:

```text
task_id
objetivo
entrada
operaciones necesarias
fuentes permitidas
resultado esperado
criterio de éxito
condición de terminación
```

Fija las tareas y sus criterios antes de ejecutar las comparaciones.

Utiliza datos reales y pequeños. Se permiten fallos inyectados y escenarios controlados, siempre que se identifiquen como tales. No presentes resultados simulados como ejecuciones reales de un LLM.

#### Herramientas y controlador

Reutiliza al menos una herramienta del examen parcial y añade, si fuera necesario, una operación auxiliar pequeña.

El controlador debe implementar:

```text
max_steps
max_tool_calls
timeout_per_tool
total_deadline
max_input_tokens o presupuesto de contexto
max_output_tokens
stop_reason
```

Los límites deben fijarse antes del experimento.

La ejecución debe distinguir:

```text
SUCCESS
ABSTAIN
MAX_STEPS
TIMEOUT
TOOL_ERROR
INVALID_OUTPUT
NO_PROGRESS
REPEATED_ACTION
```

Los nombres pueden adaptarse, pero los estados deben tener definiciones verificables.

Los fallos de herramientas no deben convertirse automáticamente en nuevas instrucciones para el agente. Las observaciones se tratarán como datos y se validarán antes de introducirse en el contexto.

### 5. Experimentos obligatorios

#### Experimento 1. Workflow determinista frente a agente controlado

**Pregunta experimental:** ¿Permitir que un LLM seleccione herramientas y determine el siguiente paso aumenta el éxito en tareas multi-paso respecto de un workflow fijo?

Compara:

```text
W0 = workflow determinista
W1 = agente con selección de herramientas y control de terminación
```

Mantén constantes:

- Benchmark y respuestas esperadas.
- Corpus y versión de documentos.
- Modelo generador y decoding.
- Herramientas disponibles y contratos.
- Recuperador y configuración RAG.
- Presupuestos máximos de pasos, tiempo y llamadas.
- Condición de memoria: sin memoria persistente.

La única diferencia principal debe ser **la política que controla la secuencia de acciones**.

El workflow seguirá reglas predefinidas. El agente utilizará el LLM para seleccionar la siguiente acción y decidir cuándo detenerse, pero ambos estarán sujetos a los mismos límites.

Registra:

| Métrica | Definición |
|---|---|
| `task_success` | Proporción de tareas con resultado final correcto |
| `steps` | Número de iteraciones del controlador |
| `tool_calls` | Llamadas reales a herramientas |
| `tool_errors` | Errores observados por tarea |
| `latency_ms` | Tiempo de ejecución |
| `tokens` | Tokens de entrada y salida |
| `termination_correct` | Terminación apropiada según el caso |
| `repeated_actions` | Acciones repetidas sin progreso |

Reporta el costo de inferencia si utilizas una API con precios conocidos. En ejecución local, registra tokens y tiempos, sin inventar un costo monetario.

Conserva las trazas originales, incluyendo acciones equivocadas, reintentos, observaciones y razones de terminación.

**Análisis obligatorio:** selecciona una tarea donde W1 supere a W0 y otra donde no mejore, falle o incurra en un costo mayor. Si ambas variantes producen los mismos resultados, explica qué evidencia permite o impide justificar el uso de un agente.

#### Experimento 2. Estado y memoria del agente

**Pregunta experimental:** ¿Qué mejora aporta cada mecanismo de memoria a tareas encadenadas y qué errores introduce?

Compara cuatro configuraciones del mismo agente:

```text
M0 = Agent without memory
M1 = Agent with working memory
M2 = Agent with episodic memory
M3 = Agent with retrieval-backed semantic memory
```

Las diferencias deben estar definidas operacionalmente:

**M0. Sin memoria:** cada tarea empieza con el prompt base y la entrada actual. No recibe historial previo.

**M1. Working memory:** conserva información de pasos anteriores dentro de la sesión actual. Se reinicia al comenzar una nueva sesión.

**M2. Episodic memory:** conserva un registro persistente de tareas anteriores, acciones, observaciones, resultados y errores. Recupera episodios pertinentes al ejecutar nuevas tareas.

**M3. Semantic memory:** recupera hechos o conocimientos consolidados desde una memoria semántica persistente, con procedencia y fecha o versión. Puede reutilizar FAISS y el encoder de la semana 4.

La comparación debe conservar modelo, herramientas, controlador, tareas, decoding y límites de ejecución. Define el mismo presupuesto máximo de contexto para todas las condiciones y registra su consumo.

**No se exige incorporar MemGPT, Letta ni Mem0.** Se permite implementar estas memorias mediante Python, JSONL, archivos e índices FAISS existentes.

Prepara al menos **tres secuencias de tareas encadenadas**, con un mínimo de tres interacciones por secuencia. Las tareas deben utilizar información que ya existe en el proyecto y que pueda evaluarse de forma independiente.

Las secuencias deben incluir:

1. Recuperación correcta de información anterior.
2. Recuperación de información de otra sesión.
3. Actualización o invalidación de un recuerdo antiguo.
4. Un caso de interferencia entre recuerdos similares.

Los cambios de estado pueden introducirse de manera controlada, pero deben identificarse como actualizaciones del escenario. No inventes hechos sobre las fuentes reales.

Reporta:

```text
task_success
memory_recall_accuracy
cross_session_retention
stale_memory_error_rate
wrong_memory_use_rate
context_tokens
latency_ms
```

Define los denominadores de cada métrica. No contabilices una respuesta correcta por casualidad como recuperación correcta de memoria si el agente no utilizó el recuerdo correspondiente.

**Análisis obligatorio:** presenta un caso en que la memoria ayude, otro en que no produzca una mejora y uno en que recupere información equivocada, desactualizada o irrelevante.

#### Pruebas de robustez y terminación

Como parte de los experimentos anteriores, ejecuta pruebas controladas de:

- Herramienta que devuelve un error transitorio.
- Herramienta que devuelve una salida inválida.
- Acción repetida sin avance.
- Agotamiento del número máximo de pasos.
- Evidencia insuficiente para responder.
- Recuerdo obsoleto que contradice una fuente más reciente.

Comprueba que el controlador termina correctamente, preserva la traza y no transforma el error en una respuesta aparentemente válida.

No se exige un tercer experimento independiente. Estas pruebas deben incorporarse al registro de los experimentos 1 y 2.

### 6. Adaptación a los temas de investigación

Debes conservar el tema registrado en la PC1 y continuado en el examen parcial.

Los siguientes ejemplos delimitan tareas pequeñas adecuadas para cada proyecto. No constituyen proyectos nuevos.

| Proyecto | Tarea multi-paso propuesta | Memoria que debe evaluarse |
|---|---|---|
| Riesgo de mercado | Recuperar evidencia de riesgo, calcular señal, contrastarla y decidir si emitir alerta | Episodios de alertas anteriores, cambios de condiciones y señales obsoletas |
| Contrataciones públicas OCDS | Recuperar cláusula, consultar indicadores del proceso, contrastar evidencia y producir alerta fundamentada | Historial por proceso e ítem, observaciones anteriores y versiones actualizadas |
| Contradicciones normativas | Recuperar artículos, contrastar regla y excepción, verificar contexto y decidir si existe contradicción aparente | Interpretaciones previas, artículos vinculados y vigencia de la evidencia |
| Revisión científica | Recuperar publicaciones, contrastar afirmaciones y comprobar validez temporal de citas | Historial de afirmaciones, relaciones entre artículos y nuevas publicaciones |
| Pedagogía automatizada | Recuperar criterios de evaluación, analizar respuesta y contrastar retroalimentación con rúbrica | Errores conceptuales previos y progreso entre sesiones |
| Elegibilidad laboral | Extraer requisitos, verificar evidencia y emitir decisión sustentada | Condiciones verificadas previamente y convocatorias actualizadas |
| Vulnerabilidades CVE/CWE | Recuperar CVE, consultar relaciones CWE y contrastar evidencia de mitigación | Incidentes previos, versiones afectadas y mitigaciones obsoletas |
| Documentos regulatorios | Recuperar obligación, comprobar excepción y generar resultado de revisión | Versiones normativas y hallazgos anteriores |
| Auditoría de respuestas LLM | Recuperar fuentes, descomponer afirmaciones y verificar respaldo | Historial de verificaciones y correcciones de citas |
| Incidentes DevSecOps | Recuperar runbook, consultar evidencia de incidente y seleccionar acción permitida | Historial de incidentes, acciones ejecutadas y procedimientos actualizados |

Cada estudiante debe formular sus propias tareas y criterios de éxito según el estado real de su repositorio.

No se permite inventar datos o resultados para completar artificialmente los experimentos.

### 7. Registro experimental y reproducibilidad

Para cada experimento registra:

```text
pregunta experimental
hipótesis
baseline
variables fijas
variable modificada
tareas y resultados esperados
configuración y modelo
ejecuciones
métricas
errores
limitaciones
conclusión
```

Guarda tanto los resultados agregados como los resultados por tarea y las trazas individuales.

El registro de cada paso del agente incluirá, como mínimo:

```json
{
  "task_id": "T01",
  "step": 2,
  "selected_tool": "nombre_herramienta",
  "arguments": {},
  "observation_status": "ok",
  "state_updated": true,
  "tokens": 0,
  "latency_ms": 0,
  "stop_reason": null
}
```

Los valores deben proceder de ejecuciones reales. Los ejemplos de formato no sustituyen trazas.

En los experimentos de memoria registra adicionalmente el identificador, tipo, procedencia y versión del recuerdo recuperado, y si su utilización fue correcta.

Si utilizas episodios de entrenamiento, ejemplos de desarrollo o ajustes de prompts, sepáralos de las tareas destinadas a evaluación final. No modifiques el benchmark de evaluación después de inspeccionar los resultados sin declarar ese cambio.

### 8. Fuentes

Utiliza al menos dos fuentes técnicas primarias y una fuente pertinente al dominio del proyecto.

Lecturas principales:

- Yao et al. (2023), *ReAct: Synergizing Reasoning and Acting in Language Models*. https://arxiv.org/abs/2210.03629
- Packer et al. (2023), *MemGPT: Towards LLMs as Operating Systems*. https://arxiv.org/abs/2310.08560
- Park et al. (2023), *Generative Agents: Interactive Simulacra of Human Behavior*. https://arxiv.org/abs/2304.03442

Fuentes complementarias:

- Shinn et al. (2023), *Reflexion: Language Agents with Verbal Reinforcement Learning*. https://arxiv.org/abs/2303.11366
- Anthropic, *Building Effective Agents*. https://www.anthropic.com/research/building-effective-agents
- Hugging Face, *AI Agents Course*. https://huggingface.co/learn/agents-course/unit1/introduction
- Documentación de Letta, Mem0 y OpenAI Agents SDK.

Debes identificar qué concepto o decisión concreta respalda cada fuente. No basta con incluir una bibliografía sin relación con la implementación.

La matriz de trazabilidad de la PC3 tendrá dos filas principales, correspondientes a las semanas 9 y 10. Cada fila incluirá recurso estudiado, concepto, archivo o función, evidencia de ejecución y limitación propia. Agrega referencias a las semanas 4, 6 y 7 cuando reutilices recuperación, contratos y métricas.

### 9. Repositorio GitHub

Continúa el repositorio del mismo proyecto, sin eliminar PC1, PC2 ni el examen parcial.

Organiza esta entrega en una carpeta:

```text
pc3/
├── README.md
├── requirements.txt
├── src/
│   ├── workflow.py
│   ├── agent.py
│   ├── controller.py
│   ├── memory.py
│   └── evaluation.py
├── data/
│   ├── tasks.jsonl
│   ├── expected_results.jsonl
│   └── memory_scenarios.jsonl
├── prompts/
├── results/
│   ├── exp1/
│   ├── exp2/
│   └── traces/
├── tests/
└── slides/
    └── PC3_CC0F4.pdf
```

La estructura es orientativa, especialmente para proyectos organizados mediante notebooks. Puedes reutilizar módulos anteriores, pero debes indicar dónde están y cómo ejecutarlos.

El README incluirá:

1. Problema y continuidad con las entregas anteriores.
2. Tarea multi-paso seleccionada.
3. Arquitectura del workflow y del agente.
4. Herramientas, contratos y controlador.
5. Modelo y configuración.
6. Benchmark de tareas y criterios de éxito.
7. Experimento 1.
8. Experimento 2.
9. Pruebas de robustez y terminación.
10. Resultados comparativos.
11. Análisis de trazas y errores.
12. Limitaciones.
13. Fuentes y trazabilidad.
14. Instrucciones de reproducción y commit evaluado.

En el único grupo de dos estudiantes, añade contribuciones individuales verificables. Ambos integrantes deberán comprender y defender la arquitectura completa.

### 10. Diapositivas

Máximo **7 diapositivas de contenido**.

Estructura sugerida:

1. Problema y continuidad con el examen parcial.
2. Arquitectura comparada: workflow y agente.
3. Controlador, herramientas y límites.
4. Experimento 1 y resultados.
5. Arquitecturas de memoria y experimento 2.
6. Trazas, errores y casos de memoria obsoleta.
7. Conclusiones, limitaciones y decisión técnica.

Prioriza evidencia de ejecución, diferencias entre sistemas y análisis de fallos.

### 11. Exposición y defensa

**Individual:**

```text
8 min  exposición
2 min  demostración
5 min  preguntas
-----------------
15 min máximo
```

**Grupo de dos:**

```text
10 min  exposición
3 min   demostración
7 min   preguntas
------------------
20 min máximo
```

La demostración debe mostrar:

- Una tarea que requiera varios pasos.
- La ejecución del workflow.
- La ejecución del agente sobre la misma tarea.
- Una decisión y una observación registradas.
- Una recuperación de memoria.
- Un error controlado o recuerdo obsoleto.
- Una métrica comprobable y la condición de terminación.

No es necesario ejecutar los experimentos completos durante la exposición. Debe existir evidencia reproducible de sus resultados.

La defensa comprobará el conocimiento de las semanas 9 y 10 y los fundamentos anteriores necesarios para justificar el funcionamiento del sistema.

### 12. Rúbrica

#### Dominio técnico y defensa oral - 12 puntos

Se evalúa:

- **3 puntos:** comprensión de workflows, patrones, arquitectura de agentes y ReAct.
- **3 puntos:** diseño del controlador, selección de herramientas, planificación, manejo de errores y terminación.
- **3 puntos:** distinción entre estado, working memory, memoria episódica y semántica, persistencia y tratamiento de información obsoleta.
- **3 puntos:** interpretación de resultados, explicación de trazas, fundamentación de decisiones y respuestas individuales.

No se otorgará el puntaje completo por mostrar código funcional si no puedes explicar sus decisiones y fallos.

#### Experimentos y demostración - 4 puntos

- **1,5 puntos:** comparación controlada workflow frente a agente.
- **1,5 puntos:** comparación de las cuatro configuraciones de memoria.
- **1 punto:** trazas, pruebas de robustez, métricas y demostración funcional.

#### Contenido técnico y fuentes - 2 puntos

Pertinencia de las fuentes, corrección conceptual y relación demostrable entre las lecturas, el proyecto y las decisiones técnicas.

#### Claridad y organización - 2 puntos

README, datos, tareas, reproducibilidad, diapositivas, organización del repositorio y manejo del tiempo.

**Nota máxima: 20 puntos.**

Se mantiene la distribución de las evaluaciones anteriores:

```text
Dominio técnico y defensa   12
Experimentos y demostración  4
Contenido y fuentes          2
Claridad y organización      2
                            --
Total                       20
```

### 13. Restricciones

No se exige:

- Un sistema multiagente completo.
- Incorporar obligatoriamente LangGraph, LangChain, CrewAI, AutoGen, MemGPT, Letta o Mem0.
- Utilizar servicios pagados.
- Construir una interfaz gráfica.
- Desplegar en producción.
- Entrenar o ajustar un LLM.
- Crear un corpus nuevo si el anterior es suficiente.
- Agregar herramientas externas sin relación con el problema.
- Construir un sistema autónomo sin límites de ejecución.

Si incorporas una biblioteca de agentes, debes poder explicar su controlador, estado, política de herramientas y mecanismo de memoria. Utilizar una biblioteca no demuestra, por sí solo, dominio de esos conceptos.

### 14. Criterio final

Una buena solución no es necesariamente la que utiliza un agente más autónomo ni la que almacena más recuerdos.

Debe demostrar experimentalmente:

```text
mismo problema
-> dos políticas de ejecución
-> medición y comparación
-> análisis de decisiones y errores

mismo agente
-> cuatro configuraciones de memoria
-> tareas encadenadas
-> recuperación y actualización
-> medición de beneficios y fallos
```

La evaluación debe permitir responder cuatro preguntas:

1. ¿Cuándo resulta suficiente un workflow fijo?
2. ¿Cuándo aporta valor que el LLM controle las acciones?
3. ¿Qué clase de memoria mejora el desempeño?
4. ¿Cuándo la autonomía o la memoria aumentan el costo, el riesgo de error o la complejidad?

**Se evaluará la capacidad de implementar, controlar, medir, explicar y defender.** Se conservarán los resultados negativos y no se aceptarán afirmaciones de superioridad sin evidencia reproducible.

