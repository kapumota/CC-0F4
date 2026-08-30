### Semana 6 - Herramientas (tools), llamada de funciones (function calling), contratos, validación, errores, reintentos (retries) y límites de tiempo (timeouts)

#### Propósito

Semana 5 terminó en una arquitectura donde el LLM recibe evidencia recuperada.

Semana 6 cambia la frontera del sistema:

```text
Semana 5
LLM + evidencia recuperada
        ->
Semana 6
LLM + herramientas con contratos verificables
```

La pregunta central es:

> ¿Cómo convertir una propuesta probabilística de llamada a una herramienta en una ejecución controlada, validable, observable y temporalmente acotada?

La cadena conceptual de la semana es:

```text
usuario
   |
   v
LLM + especificaciones de herramientas (tool specifications)
   |
   v
ToolCall
{name, arguments}
   |
   v
análisis sintáctico (`parse`)
   |
   v
lista de herramientas permitidas (allowlist)
   |
   v
contrato de entrada (input contract)
   |
   v
validación de dominio (domain validation)
   |
   v
política de ejecución (execution policy)
   |
   +-> reintento selectivo (retry)
   +-> espera progresiva entre reintentos (backoff)
   +-> tiempo de espera por intento (timeout)
   +-> límite temporal total (deadline)
   |
   v
implementación de la herramienta (tool implementation)
   |
   v
contrato de salida (output contract)
   |
   v
ToolResult / ToolError
   |
   v
observación (observation)
```

La tesis pedagógica de la semana es:

```text
Semana 6 no estudia agentes.

Semana 6 estudia la frontera de confianza
entre un LLM probabilístico y una función determinista.
```

Semana 6 contiene una exposición técnica de refuerzo, como ocurre en otras semanas no evaluadas.

#### Resultados de aprendizaje

Al finalizar la semana el estudiante debe poder:

- distinguir salida estructurada (structured output), llamada de funciones (function calling) y ejecución de funciones (function execution),
- explicar por qué la salida de un LLM no constituye entrada confiable,
- diseñar un contrato de entrada tipado,
- separar validación estructural de validación de dominio,
- diseñar contratos de salida,
- representar errores como datos estructurados,
- clasificar errores usando los códigos `protocol`, `validation`, `domain`, `transient`, `timeout`, `execution` y `output_contract`, comprendiendo su significado en español,
- decidir qué errores son reintentables (`retryable`),
- distinguir reintento (`retry`) de reparación (`repair`),
- distinguir tiempo de espera agotado por intento (`timeout`) de límite temporal total (`deadline`),
- medir resultados correctos aunque el resultado esperado sea un error,
- auditar llamadas a herramientas (`tool calls`) mediante trazas reproducibles,
- evaluar por separado selección de herramienta, análisis sintáctico (`parsing`), validez del esquema (`schema`), semántica de argumentos y resultado de extremo a extremo (`end-to-end`).

#### La llamada de herramientas (tool calling) no es ejecución

```text
llamada de funciones (function calling) != ejecución de funciones (function execution)
```

El modelo propone:

```json
{
  "name": "catalog.lookup_stock",
  "arguments": {
    "sku": "SKU001"
  }
}
```

La aplicación conserva la autoridad para:

```text
aceptar/rechazar
validar
ejecutar
reintentar
cancelar
registrar
```

#### Herramientas canónicas

La semana utiliza tres herramientas locales:

```text
calculator.calculate_total
catalog.lookup_stock
shipping.get_quote
```

No se necesita una API externa para el Experimento A.

#### Niveles de contrato

##### Especificación de herramienta (tool specification)

Es la descripción que ve el modelo.

```text
name
description
parameters
```

##### Contrato de entrada (input contract)

Valida forma y tipos.

```text
Pydantic/JSON Schema
```

##### Contrato de dominio (domain contract)

Valida reglas que no pertenecen al tipo.

Ejemplo:

```text
"SKU999"
```

puede ser un `str` válido y satisfacer el esquema (`schema`), pero no existir en el catálogo.

Por ello:

```text
válido por tipo (`type-valid`) != válido por esquema (`schema-valid`) != válido para el dominio (`domain-valid`)
```

##### Contrato de salida (output contract)

Una herramienta también debe cumplir la forma de salida prometida.

```text
herramienta ejecutada != salida válida
```

#### Errores estructurados

La interfaz canónica utiliza:

```text
ToolResult
ToolError
```

y no depende solamente de excepciones.

```text
excepción (`exception`) != contrato de error (`error contract`)
```

Taxonomía:

```text
protocol        -> protocolo
validation      -> validación
domain          -> dominio
transient       -> transitorio
timeout         -> tiempo de espera agotado
execution       -> ejecución
output_contract -> contrato de salida
```

Política inicial:

```text
protocol        -> sin reintento automático
validation      -> sin reintento automático
domain          -> sin reintento automático
transient       -> reintento acotado
timeout         -> reintento solo si queda presupuesto
execution       -> sin reintento por defecto
output_contract -> sin reintento automático
```

#### Reintento (retry) no es reparación (repair)

```text
reintento (`retry`) != reparación (`repair`)
```

Reintento (`retry`):

```text
mismos argumentos ya validados + fallo transitorio
->
nuevo intento
```

Reparación (`repair`):

```text
argumentos inválidos
->
cambiar la llamada
```

La reparación automática mediante un nuevo ciclo LLM no se implementa en Semana 6 porque introduce decisión iterativa y se acerca a flujos de trabajo (`workflows`) y agentes.

#### Tiempo de espera (timeout) y límite temporal total (deadline)

Se distinguen:

```text
per_attempt_timeout
`max_attempts` (máximo de intentos)
`overall_deadline` (límite temporal total)
```

Un reintento (`retry`) puede mejorar la recuperación ante fallos transitorios, pero consume tiempo.

```text
más reintentos (`retries`) != mejor sistema en todos los casos
```

#### Experimento A - Entorno de ejecución determinista (runtime)

Pregunta:

> ¿Qué efecto tiene agregar progresivamente validación, errores estructurados, retries y límites temporales cuando las entradas y los fallos permanecen fijos?.

Condiciones:

```text
A = despacho directo ingenuo (`dispatch`)

B = A
  + contrato tipado de entrada

C = B
  + ToolResult/ToolError
  + contrato de salida

D = C
  + reintento selectivo (`retry`)
  + espera progresiva (`backoff`)

E = D
  + tiempo de espera por intento (`timeout`)
  + límite temporal total (`deadline`)
```

Comparaciones:

```text
A vs B
-> efecto de la validación de entrada (`input validation`)

B vs C
-> efecto de los errores estructurados (`structured errors`) y del contrato de salida (`output contract`)

C vs D
-> efecto de los reintentos (`retries`)

D vs E
-> efecto de límites temporales
```

Los fallos se inyectan de forma determinista:

```text
none
transient_once
transient_twice
always_transient
slow_once
always_slow
internal_error
malformed_output
```

No se espera que Internet falle casualmente.

#### Métricas del Experimento A

```text
correct_outcome_rate
uncaught_exception_rate
error_classification_accuracy
invalid_execution_rate
transient_recovery_rate
mean_attempts
latency_mean_ms
latency_p95_ms
deadline_overrun_rate
```

`correct_outcome_rate` es la métrica principal.

Ejemplo:

```text
SKU inexistente
->
resultado correcto = error domain
```

Por tanto:

```text
success_rate
```

por sí sola sería engañosa.

#### Experimento B - Llamada de funciones (function calling) con un LLM

El entorno de ejecución (`runtime`) se fija antes de medir al modelo.

Cada solicitud permite:

```text
0 o 1 llamada a herramienta (`tool call`)
```

No se permite:

```text
llamadas paralelas a herramientas (`parallel tool calling`)
cadenas de múltiples herramientas (`multi-tool chains`)
reparación automática (`auto-repair`)
ciclo de agente (`agent loop`)
ReAct
```

Benchmark:

```text
24 casos

6 calculator.calculate_total
6 catalog.lookup_stock
6 shipping.get_quote
6 casos sin herramienta (`no_tool`)
```

Métricas:

```text
tool_choice_accuracy
arguments_parse_rate
arguments_schema_valid_rate
arguments_semantic_accuracy
no_tool_accuracy
end_to_end_task_accuracy
```

Distinciones:

```text
llamada a herramienta válida (`tool call`) != llamada a herramienta correcta (`tool call`)

éxito de la herramienta (`tool success`) != éxito de la tarea (`task success`)
```

#### Análisis sintáctico (parsing) de la respuesta del modelo real

El cuaderno usa dos niveles:

```text
1. tokenizer.parse_response(...)
   cuando el tokenizer/modelo proporciona una plantilla de respuesta (`response template`) compatible

2. parser explícito de <tool_call> ... </tool_call>
   como mecanismo alternativo (`fallback`) transparente
```

Esto evita asumir que toda la generación es JSON puro.

El parser exige como máximo una llamada porque esa es una restricción experimental de Semana 6.

#### Modelo real opcional

Modelo docente por defecto:

```text
Qwen/Qwen3-1.7B
```

Ejecución:

```bash
CC0F4_RUN_REAL_TOOL_LLM=1 make execute-cuaderno6
```

El experimento fija:

```text
do_sample=False
enable_thinking=False
```

cuando el chat template acepta `enable_thinking`.

El modelo real es opcional. El Experimento A no depende de él.

#### Ejecución offline

```bash
CC0F4_RUN_REAL_TOOL_LLM=0 make execute-cuaderno6
```

En modo sin conexión (`offline`):

```text
Experimento A
-> ejecución real del entorno local (`runtime`)

Experimento B
-> casos prefijados (`fixtures`) de `ToolCall` deterministas
```

Por ello:

```text
offline
= valida software, contratos, análisis sintáctico (`parsing`) y métricas

modo sin conexión (`offline`)
!=
evidencia del comportamiento de un LLM real
```

#### Laboratorio

El laboratorio profundiza tres puntos:

```text
JSON Schema como segunda representación del contrato
reintento manual (`retry`) vs Tenacity
tiempo de espera (`timeout`), límite temporal (`deadline`) y observabilidad
```

La clase teórica implementa el mecanismo a mano para hacerlo visible.

En el laboratorio se muestra Tenacity como abstracción equivalente para retries selectivos.

#### Dependencias

Semana 6 utiliza el entorno global del curso.

Dependencias del entorno relacionadas:

```text
pydantic
jsonschema
tenacity
httpx
pytest
transformers
pandas
```

Uso directo en la semana:

```text
pydantic
-> contratos tipados

jsonschema
-> verificación cruzada en el laboratorio

tenacity
-> comparación en el laboratorio

transformers
-> llamada de funciones (`function calling`) real opcional

pandas
-> métricas y análisis
```

`httpx` y `pytest` permanecen disponibles en el entorno global para extensiones y pruebas del curso, pero no son necesarios para ejecutar el camino canónico de Semana 6.

La decisión de implementar primero reintento (`retry`), espera progresiva (`backoff`) y tiempo de espera (`timeout`) manualmente con `asyncio` es deliberada:

```text
comprender el mecanismo -> medirlo -> recién después delegarlo a una librería
```

#### Exposición de refuerzo

Archivo:

```text
Exposiciones6-CC-0F4.md
```

Formato de cuatro grupos:

```text
15 min exposición
5 min preguntas x 4 grupos = 80 min
```

Temas:

```text
1. Toolformer y aprendizaje de uso de herramientas
2. Gorilla y conexión de LLM con APIs
3. Esquemas de herramientas (`tool schemas`), interfaces restringidas (`constrained interfaces`) y análisis de respuestas (`response parsing`)
4. MCP como protocolo actual de interoperabilidad
```

MCP se estudia como tecnología y arquitectura.

```text
MCP como exposición != MCP como dependencia estructural de Semana 6
```

#### Material de referencia

Se aprovechan patrones de:

```text
kapumota/CC-0F4
-> metodología experimental

kapumota/MCC225
-> estilo cuaderno + evidencia

kapumota/CC-0C2
-> evaluación y defensa técnica

kapumota/CMCC-1
-> contexto conceptual de herramientas (`tools`)

kapumota/attentionlab-ai
-> contratos Pydantic + trazas de herramientas (`tool traces`) + fallos reproducibles

kapumota/CC-0F5
-> asyncio + coordinación + timeout

juleswhite/python-agents-mcp-course
-> recuperación guiada ante fallos (`failing forward`) + errores accionables + validación en la fuente (`validate at source`)

labmlai/annotated_deep_learning_paper_implementations
-> implementaciones pequeñas y explícitas

kapumota/sentinelOps
-> disciplina de validación reproducible
```

No se reutilizan:

```text
ciclos de agentes (`agent loops`)
planificación (`planning`)
memoria (`memory`)
transporte de MCP (`MCP transport`)
microservicios (`microservices`)
Kubernetes
orquestación distribuida (`distributed orchestration`)
```

#### Reproducibilidad

El cuaderno genera:

```text
Semana6/resultados/latest_run.json
```

Registra:

```text
hashes SHA-256
seed
versiones
modo offline/real
modelo
programación de fallos (`fault schedule`)
políticas A/B/C/D/E
`max_attempts` (máximo de intentos)
`backoff` (espera progresiva)
`timeouts` (límites de espera)
`deadline` (límite temporal total)
métricas
limitaciones
```

El programación de fallos (`fault schedule`) es parte del experimento y queda incluido en el hash del benchmark.

#### Validación

Desde la raíz del repositorio:

```bash
make check-semana6
```

Cuaderno:

```bash
CC0F4_RUN_REAL_TOOL_LLM=0 make execute-cuaderno6
```

Laboratorio:

```bash
CC0F4_RUN_REAL_TOOL_LLM=0 \
jupyter nbconvert \
  --to notebook \
  --execute Semana6/Laboratorio6-CC-0F4.ipynb \
  --ExecutePreprocessor.timeout=600 \
  --output /tmp/Laboratorio6-validado.ipynb
```

No se modifica el `Makefile`.

La razón es que Semana 6 ahora **sí tiene laboratorio canónico** y el `Makefile` actual ya valida automáticamente:

```text
SemanaN/README.md
CuadernoN-CC-0F4.ipynb
LaboratorioN-CC-0F4.ipynb
```

para toda semana no incluida en `NO_LAB_WEEKS`.

#### Alcance deliberado

Semana 6 incluye:

```text
especificación de herramienta (`tool specification`)
llamada de funciones (`function calling`)
ejecución de funciones (`function execution`)
lista permitida (`allowlist`)
Pydantic
JSON Schema
contrato de entrada (input contract)
validación de dominio (domain validation)
contrato de salida (output contract)
errores estructurados (`structured errors`)
inyección de fallos (`fault injection`)
reintento (`retry`)
`backoff` (espera progresiva)
Tenacity como comparación
tiempo de espera (`timeout`) con `asyncio`
límite temporal total (`overall deadline`)
trazas (`traces`)
latencia
análisis de errores (`error analysis`)
banco de pruebas (`benchmark`) de llamada de funciones (`function calling`)
MCP como exposición
```

Semana 6 no incluye:

```text
agentes
ReAct
planificación (`planning`)
memoria (`memory`)
LangGraph
LangChain
MCP como entorno de ejecución (`runtime`) del curso
ciclos de múltiples herramientas (`multi-tool loops`)
llamadas paralelas a herramientas (`parallel tool calling`)
ciclos automáticos de reparación con LLM (`automatic LLM repair loops`)
```

#### Criterio de cierre

El estudiante debe poder defender:

```text
salida estructurada (`structured output`) != llamada de herramientas (`tool calling`)

llamada de herramientas (`tool calling`) != ejecución de herramientas (`tool execution`)

especificación de herramienta (`tool specification`) != implementación

válido por tipo (`type-valid`) != válido por esquema (`schema-valid`) != válido para el dominio (`domain-valid`)

contrato de entrada (input contract) != contrato de salida (output contract)

salida del LLM (`LLM output`) != entrada confiable (`trusted input`)

excepción (`exception`) != error estructurado de herramienta

reintento (`retry`) != reparación (`repair`)

reintentable (`retryable`) != fallido (`failed`)

tiempo de espera agotado (`timeout`) != reintento (`retry`)

tiempo de espera por intento (`per-attempt timeout`) != límite temporal total (`overall deadline`)

llamada a herramienta válida (`tool call`) != llamada a herramienta correcta (`tool call`)

éxito de la herramienta (`tool success`) != éxito de la tarea (`task success`)

llamada de funciones (`function calling`) != agente

MCP != llamada de funciones (`function calling`)
```

#### Puente a la Semana 7

```text
Semana 6
acción individual verificable
        ->
Semana 7
evaluación sistemática de retrieval/RAG
```

Los flujos de trabajo (`workflows`), la planificación, ReAct y los agentes permanecen reservados para la Semana 9.
