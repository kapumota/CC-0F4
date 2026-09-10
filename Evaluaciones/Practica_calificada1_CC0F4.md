### CC0F4 - Primera Práctica Calificada
#### Del tema de investigación a un prototipo LLM verificable

**Curso:** CC0F4 - Tópicos de Ciencia de la Computación I  
**Periodo:** 2026-2  
**Cobertura:** Semanas 1, 2 y 3  
**Duración:** 1 semana y media  
**Modalidad:** individual o por grupo según el tema registrado  
**Entregables:** repositorio GitHub + diapositivas + exposición  
**Nota máxima:** 20 puntos  

### 1. Propósito

La práctica convierte el tema de investigación de cada estudiante o grupo en un **prototipo pequeño, ejecutable y defendible**.

No se espera implementar todavía RAG, recuperación híbrida, agentes, multiagentes ni multimodalidad.

El objetivo es trabajar una primera versión:

```text
problema
-> entrada y contexto
-> LLM
-> decoding
-> salida estructurada
-> validación
-> pequeña evaluación
-> defensa
```

### 2. Relación con el curso

#### Semana 1

Explica:

- Transformer;
- tokens y representaciones;
- atención y causalidad;
- por qué un decoder causal no puede usar información futura.

#### Semana 2

Explica:

- logits y probabilidades;
- softmax;
- greedy vs sampling;
- temperature, top-k o top-p cuando corresponda;
- contexto;
- función conceptual del KV cache.

#### Semana 3

Aplica:

- separación entre instrucción, entrada y contexto;
- salida estructurada;
- JSON Schema o validación equivalente;
- diferencia entre JSON parseable, schema-valid y semánticamente correcto.

### 3. Tarea mínima

Reduce tu tema a una tarea pequeña y evaluable.

Ejemplos:

```text
riesgo de mercado
-> clasificar una señal como low / medium / high
```

```text
contrataciones públicas
-> clasificar una cláusula según riesgo
```

```text
auditor de respuestas LLM
-> clasificar una respuesta como supported / unsupported
```

Produce una salida estructurada para la tarea.

Ejemplo:

```json
{
  "label": "high",
  "confidence": 0.82,
  "reason": "..."
}
```

### 4. Requisitos mínimos

#### Modelo

Utiliza:

```text
Qwen/Qwen2.5-0.5B-Instruct
```

u otro LLM pequeño. Identifica el modelo y asegúrate de poder ejecutarlo durante la demostración.

#### Datos

Utilizar entre:

```text
6 y 10 casos
```

Usa casos públicos, sintéticos o construidos por ti.

Indica su procedencia.

#### Prompts

Puedes realizar los experimentos **mediante prompts**.

No necesitas desarrollar una aplicación compleja para experimentar. Evalúa el sistema modificando de forma controlada:

- instrucción;
- ejemplos dentro del prompt;
- contexto;
- formato de salida;
- política de decoding.

Cuando realices un experimento mediante prompts, guarda en el repositorio el **prompt exacto** utilizado.

Estructura sugerida:

```text
prompts/
├── baseline.txt
├── experimento_prompt.txt
└── experimento_contexto.txt
```

No modifiques simultáneamente varias partes del prompt si deseas atribuir el resultado a un cambio específico.

#### Decoding

Registrar la política utilizada:

```text
greedy
```

o:

```text
sampling
temperature
top_k
top_p
seed
```

según corresponda.

#### Salida estructurada

Incluye:

- un formato JSON;
- un JSON Schema o validación equivalente;
- una forma de distinguir salida válida de salida incorrecta.

### 5. Experimentos

Realiza **tres experimentos pequeños**.

Puedes hacer los experimentos con código mínimo o mediante variaciones controladas de prompts.

#### Experimento 1 - Prompt baseline vs prompt mejorado
**Experimento basado en prompts: sí**

Utiliza los mismos casos y compara:

```text
P0 = prompt baseline
P1 = prompt mejorado
```

Ejemplos de modificación:

- instrucción más precisa;
- separación explícita entre tarea y contexto;
- incorporación de criterios de decisión;
- mejor especificación del formato de salida.

Mantén constantes:

- modelo;
- casos;
- contexto;
- decoding;
- JSON Schema.

Reporta:

- `schema_valid_rate`;
- una métrica relacionada con la tarea;
- un ejemplo donde P1 mejore, empeore o no cambie la respuesta.

Explica **qué cambió exactamente en el prompt**.

#### Experimento 2 - Contexto
**Experimento basado en prompts: sí**

Compara:

```text
C0 = contexto base
C1 = contexto modificado
```

Elige uno de estos cambios:

- contexto neutral;
- contexto incompleto;
- contexto conflictivo;
- contexto más largo.

Mantén constantes:

- modelo;
- instrucción;
- decoding;
- schema;
- casos.

Reporta:

```text
schema_valid_rate
```

y una métrica semántica adecuada al tema, por ejemplo:

```text
accuracy
macro_f1
exact_match
abstention_rate
```

Incluye al menos un caso en el que el cambio de contexto afecte la respuesta.

#### Experimento 3 - Decoding
**Experimento basado únicamente en prompts: no**

En este experimento el prompt permanece igual.

Compara sobre al menos 3 casos:

```text
D0 = greedy
D1 = sampling
```

Por ejemplo:

```text
temperature = 0.8
top_p = 0.9
```

Mantén constantes:

- modelo;
- prompt;
- contexto;
- casos;
- max_new_tokens.

Observe:

- variabilidad;
- estabilidad de la etiqueta;
- validez del JSON;
- cambios cualitativos en la explicación.

No se exige demostrar que una política de decoding sea universalmente mejor.

#### Experimento opcional - Few-shot
**Experimento basado en prompts: sí**

Si deseas realizar un cuarto experimento, compara:

```text
F0 = zero-shot
F1 = few-shot
```

Agregando 1 o 2 ejemplos al prompt.

Mantén constantes:

- modelo;
- casos;
- decoding;
- schema.

Este experimento es opcional y no aumenta por sí solo la nota. Úsalo para enriquecer la exposición si aporta evidencia útil.

#### Registro de experimentos

Resume cada experimento en una tabla:

| Experimento | Variable modificada | Variable fija | Métrica | Resultado | Conclusión |
|---|---|---|---|---|---|
| Prompt | prompt | modelo, casos, contexto, decoding |  |  |  |
| Contexto | contexto | modelo, prompt, casos, decoding |  |  |  |
| Decoding | decoding | modelo, prompt, contexto, casos |  |  |  |

Formula una conclusión proporcional a la evidencia observada.

### 6. Fuentes

Utiliza como mínimo:

```text
1 fuente primaria
+
1 fuente adicional
```

Apóyate en las herramientas conocidas en la prueba de entrada:

- Elicit;
- Consensus;
- ResearchRabbit;
- Connected Papers;
- Scite;
- SciSpace.

No es obligatorio utilizar las seis.

### 7. Repositorio GitHub

#### Nombre sugerido

```text
cc0f4-pc1-<apellido-o-grupo>-<tema-corto>
```

#### Estructura mínima

```text
cc0f4-pc1-.../
├── README.md
├── requirements.txt
├── src/ o notebook/
├── data/
├── prompts/
├── results/
└── slides/
    └── PC1.pdf
```

#### README

Incluye:

```text
1. Problema
2. Tarea mínima
3. Relación con Semanas 1, 2 y 3
4. Modelo
5. Datos
6. Salida estructurada
7. Cómo ejecutar
8. Prompts utilizados
9. Experimento 1 - Prompt
10. Experimento 2 - Contexto
11. Experimento 3 - Decoding
12. Resultados
13. Un error o caso fallido
14. Limitación
15. Conclusión
16. Fuentes
```

### 8. Diapositivas

Máximo:

```text
7 diapositivas de contenido
```

Estructura sugerida:

```text
1. Problema y tarea
2. Arquitectura mínima
3. Relación con Semanas 1, 2 y 3
4. Prompt y salida estructurada
5. Experimentos
6. Resultados y caso fallido
7. Limitación y conclusión
```

Usa las diapositivas para apoyar la explicación, no para reemplazarla.

### 9. Exposición

La exposición es la parte principal de la evaluación.

#### Tiempo

```text
8 min  exposición
2 min  demostración
5 min  preguntas
-----------------
15 min máximo
```

En la demostración muestra, por ejemplo:

- una entrada;
- el prompt o contexto;
- la respuesta del modelo;
- el JSON;
- la validación;
- un resultado guardado.

### 10. Rúbrica

#### Dominio y defensa oral - 12 puntos

Se evalúa:

- comprensión del problema y de la solución;
- dominio de los conceptos de Semanas 1, 2 y 3;
- interpretación del experimento;
- capacidad de responder preguntas sobre código, configuración y resultados.

#### Experimentos y demostración - 4 puntos

Se evalúa:

- Experimento 1: prompt baseline vs prompt mejorado;
- Experimento 2: modificación controlada del contexto;
- Experimento 3: decoding;
- métricas apropiadas;
- prompts y configuraciones registradas;
- demostración funcional.

#### Contenido técnico y fuentes - 2 puntos

Se evalúa:

- fuente primaria pertinente;
- fuente adicional;
- conexión entre literatura y decisiones técnicas.

#### Claridad y organización - 2 puntos

Se evalúa:

- diapositivas;
- README;
- organización del repositorio;
- manejo del tiempo.

**Nota máxima: 20 puntos**

### 11. Temas de referencia

| Estudiante | Tema |
|---|---|
| Luis Angel Azaña Vega | Sistema multi-agente LLM para la detección de requisitos direccionados en bases de contrataciones del Estado usando registros OCDS |
| David Fernando Reeves Goñi | Sistema multi-agente LLM para la detección de requisitos direccionados en bases de contrataciones del Estado usando registros OCDS |
| Omar Romulo Quispe Santos | Multi-Agent LLM Architectures and RAG for Automated Pedagogy: A Review of Exam Generation, Scoring, and Feedback |
| Luis Antonio Rojas Huaroc | Agente de extracción y verificación estructurada de elegibilidad en ofertas laborales universitarias |
| Pedro Lautaro Quispe Ballesteros | Vigilante de riesgo de mercado con alertas tempranas |
| Germain Ronald Choquechambi Quispe | Triage inteligente de vulnerabilidades con RAG híbrido sobre CVE/CWE y agentes verificadores |
| Luiggi Sergio Gil Cardoso | Análisis de documentos regulatorios con extracción estructurada, RAG y verificación de cumplimiento |
| Frank Oliver Hinojosa Zamora | Auditor de respuestas de LLM con verificación de fuentes, grounding y análisis automático de errores |
| Jesus Diego Osorio Tello | Asistente de respuesta a incidentes DevSecOps con RAG sobre runbooks, logs y evidencia técnica |
| Cesar Augusto Sanchez Malaspina | Agente de revisión científica que identifica desacuerdos entre artículos mediante citation context y RAG |
| Carlos Sinai Unda Miguel | Sistema multimodal de inspección de documentos técnicos con recuperación de texto, tablas y figuras |

Si cambiaste tu tema después de la prueba de entrada, utiliza el **tema final declarado**.

### 12. Criterio final

La práctica no busca premiar el sistema más grande.

Busca evaluar:

```text
comprender
-> construir
-> medir
-> explicar
-> defender
```

La prioridad es que puedas demostrar qué construyó, cómo lo evaluó, dónde falla y qué evidencia respalda su conclusión.

Los experimentos basados en prompts son completamente válidos siempre que:

```text
se guarde el prompt exacto
-> se cambie una variable principal
-> se mantengan las demás condiciones
-> se mida el resultado
-> se analice al menos un caso
-> se defienda la conclusión
```
