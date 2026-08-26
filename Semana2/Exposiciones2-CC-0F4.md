### Semana 2 - Exposiciones de refuerzo y búsqueda académica asistida

#### Propósito

Las exposiciones de Semana 2 forman parte del bloque final del Laboratorio 2.

No son una actividad adicional ni sustituyen la evaluación formal E1 de Semana 3.

El objetivo tiene dos partes:

```text
aprender a buscar y contrastar literatura -> comprender una técnica de inferencia -> defender un claim con evidencia
```

Esta es la primera actividad del curso que utiliza de manera explícita:

```text
Elicit
ResearchRabbit
Connected Papers
Scite
SciSpace
Consensus
```

Por ello, no se espera que el estudiante ya domine estas herramientas.

Antes de preparar la exposición se realiza una ruta guiada común para aprender qué hace cada herramienta, qué no hace y qué evidencia debe conservarse.

#### Relación con el Laboratorio 2

El Laboratorio 2 reserva al final:

```text
110-210 min
EXPOSE/DEFEND
```

El bloque máximo disponible para exposiciones es de 100 minutos.

Cada grupo dispone de:

```text
7 min exposición

3 min
defensa

total
10 min por grupo
```

Por tanto:

```text
hasta 10 grupos -> 100 min
```

Si existen menos grupos, la sesión termina antes.

La búsqueda bibliográfica y la preparación se realizan antes del jueves.

Durante el bloque final del laboratorio se presenta y defiende el trabajo ya preparado.

#### Qué se evalúa realmente

La exposición no consiste en resumir un paper ni en mostrar una respuesta generada por IA.

Debe reconstruir:

```text
problema -> pregunta -> paper primario -> baseline -> mecanismo -> recurso afectado -> evidencia experimental
-> limitación -> conexión con Laboratorio 2
```

El estudiante debe poder distinguir:

```text
lo que afirma una herramienta != lo que demuestra el paper != lo que concluye el grupo
```

#### Regla principal de uso de herramientas

Las seis herramientas no realizan la misma función.

| Rol | Herramientas recomendadas | Pregunta que ayudan a responder |
|---|---|---|
| Descubrimiento y síntesis inicial | Elicit, SciSpace, Consensus | ¿Qué papers podrían ser relevantes? |
| Exploración de red | ResearchRabbit, Connected Papers | ¿Qué trabajos anteriores, relacionados o posteriores debo revisar? |
| Contexto de citación | Scite | ¿Cómo ha sido citado un claim o paper por trabajos posteriores? |
| Verificación | arXiv, DOI, conferencia, journal, repositorio oficial | ¿Qué dice realmente la fuente primaria? |

Regla:

```text
herramienta -> orienta

fuente primaria -> sustenta
```

No se acepta como evidencia final:

```text
"lo dijo Elicit"
"lo dijo SciSpace"
"lo dijo Consensus"
"Scite dice que está supported"
"aparece cerca en Connected Papers"
```

#### Primera vez - tutorial guiado común

Antes de que cada grupo investigue su tema, todos realizan el mismo recorrido.

Caso de práctica:

```text
Tema:
Grouped-Query Attention

Pregunta:
How does grouped-query attention change decoder inference compared with multi-head attention?

Seed paper:
GQA: Training Generalized Multi-Query Transformer Models
from Multi-Head Checkpoints
Ainslie et al., 2023

Fuente:
https://arxiv.org/abs/2305.13245
```

Objetivo del tutorial:

```text
misma pregunta -> seis herramientas -> seis funciones diferentes
```

No se busca producir una revisión exhaustiva.

Se busca entender el workflow.

#### Paso 0 - Crear el registro de búsqueda

Antes de abrir una herramienta crea esta tabla.

| Campo | Registro |
|---|---|
| Fecha | |
| Tema | GQA |
| Pregunta | How does grouped-query attention change decoder inference compared with multi-head attention? |
| Seed paper | Ainslie et al. (2023) |
| Herramienta | |
| Query o acción | |
| Paper encontrado | |
| Por qué parece relevante | |
| Claim | |
| Evidencia verificada | |
| Limitación | |

Cada vez que cambies de herramienta registra la acción realizada.

La trazabilidad forma parte de la actividad.

#### Paso 1 - Elicit: descubrir papers

Sitio:

```text
https://elicit.com/
```

Uso en esta actividad:

```text
pregunta en lenguaje natural -> búsqueda semántica -> papers candidatos -> selección inicial
```

Procedimiento de primera vez:

1. abre Elicit,
2. inicia una búsqueda de papers,
3. escribe una pregunta, no un párrafo largo,
4. revisa título, año, abstract y tipo de publicación,
5. identifica el paper primario,
6. selecciona uno o dos papers relacionados,
7. registra por qué cada paper parece relevante,
8. abre la fuente original antes de aceptar un claim.

Query de práctica:

```text
How does grouped-query attention affect inference speed,
KV-cache requirements and model quality compared with
multi-head attention in autoregressive Transformers?
```

Qué debes obtener:

```text
paper primario + 1 paper relacionado + 1 claim candidato
```

Qué NO debes hacer:

```text
copiar el resumen de Elicit -> ponerlo en la diapositiva -> llamarlo evidencia
```

Pregunta de control:

> ¿El paper que Elicit mostró es el trabajo que propone el método, una evaluación posterior o solo un paper que lo menciona?.

#### Paso 2 - ResearchRabbit: navegar desde un seed paper

Sitio:

```text
https://www.researchrabbit.ai/
```

ResearchRabbit se usa principalmente para explorar literatura mediante relaciones entre papers.

Procedimiento:

1. crea un proyecto o búsqueda,
2. busca el seed paper por título o DOI/arXiv,
3. selecciona uno o más seed papers,
4. genera la red de trabajos relacionados,
5. inspecciona `Similar Work`,
6. inspecciona referencias o trabajos anteriores,
7. inspecciona trabajos que citan al seed,
8. guarda solo los papers cuya relación puedas explicar.

Para GQA intenta localizar:

```text
antecedente -> Multi-Query Attention

seed -> GQA

trabajo posterior -> modelo o sistema que adopte GQA
```

Producto mínimo:

| Tipo | Paper | Relación con el seed |
|---|---|---|
| Anterior | | |
| Similar | | |
| Posterior | | |

Error típico:

> "Está conectado en ResearchRabbit, entonces demuestra lo mismo."

Eso es incorrecto.

Una conexión sirve para descubrir qué leer, no para sustituir la lectura.

#### Paso 3 - Connected Papers: observar el vecindario conceptual

Sitio:

```text
https://www.connectedpapers.com/
```

Busca el mismo seed paper.

Connected Papers construye un grafo de similitud.

Importante:

```text
grafo de Connected Papers != árbol de citaciones
```

Papers próximos pueden ser similares porque comparten referencias o patrones de citación aunque no se citen directamente.

Procedimiento:

1. introduce el título, DOI o identificador del seed,
2. construye el grafo,
3. localiza el paper origen,
4. inspecciona los clusters cercanos,
5. identifica un paper que no habías encontrado,
6. revisa `Prior Works`,
7. revisa `Derivative Works`,
8. abre el paper seleccionado en su fuente original.

Producto mínimo:

```text
1 prior work + 1 paper del grafo + 1 derivative work
```

Para cada uno responde:

> ¿Por qué este paper cambia, amplía o contextualiza mi comprensión del seed?.

No se acepta:

> "Lo seleccioné porque estaba cerca en el grafo."

#### Paso 4 - Scite: revisar el contexto de citación

Sitio:

```text
https://scite.ai/
```

Scite no se usa aquí para contar simplemente citas.

Se usa para inspeccionar cómo aparece citado un trabajo.

Busca el seed paper por:

```text
título
DOI
arXiv
autor
```

Cuando existan Smart Citations, revisa contextos clasificados como:

```text
supporting
mentioning
contrasting
```

Procedimiento:

1. abre el reporte del paper,
2. revisa los citation statements,
3. selecciona una cita relevante para tu claim,
4. lee el contexto completo disponible,
5. abre el paper citante,
6. determina si realmente apoya, limita o contradice el claim que estás investigando.

Importante:

```text
supporting != paper correcto

contrasting != paper incorrecto
```

La clasificación es una señal para navegar la evidencia, no un score de calidad.

Producto mínimo:

| Campo | Registro |
|---|---|
| Claim investigado | |
| Paper citante | |
| Tipo de cita mostrado | |
| Contexto | |
| Interpretación del grupo | |
| ¿Fue necesario reducir el claim? | |

Si no existe una cita `contrasting`, no debes inventarla ni forzar una.

#### Paso 5 - SciSpace: leer y extraer evidencia del paper

Sitio:

```text
https://scispace.com/
```

En esta actividad se usan dos funciones:

```text
Literature Review + Chat with PDF
```

Primero puedes buscar el tema en Literature Review.

Después abre o carga el paper primario en Chat with PDF.

No preguntes solamente:

```text
Summarize this paper.
```

Haz preguntas estructurales.

Prompt recomendado:

```text
Using only this paper, identify:

1. the inference problem being addressed,
2. the baseline,
3. the architectural or algorithmic modification,
4. the variable changed,
5. the resource affected,
6. the evaluation metrics,
7. the main experimental result,
8. one limitation stated or directly supported by the paper.

For every answer, indicate the section, table or figure that should be checked in the original paper.

Do not add claims that are not supported by this paper.
```

Después:

```text
respuesta SciSpace -> abrir sección /tabla/figura -> verificar -> registrar evidencia
```

Producto mínimo:

| Campo | Evidencia verificada |
|---|---|
| Problema | |
| Baseline | |
| Método | |
| Métrica | |
| Resultado | |
| Tabla/figura/sección | |
| Limitación | |

#### Paso 6 - Consensus: contrastar una pregunta de investigación

Sitio:

```text
https://consensus.app/
```

Consensus es un buscador académico asistido por IA.

Úsalo para una pregunta científica concreta.

Para esta práctica:

```text
What evidence compares grouped-query attention with multi-head attention for inference efficiency and model quality?
```

Puedes usar `Paper Search` si quieres explorar papers sin depender primero de una síntesis.

Si la pregunta es verdaderamente binaria y existen suficientes trabajos relevantes, Consensus puede mostrar su Consensus Meter.

No fuerces una pregunta técnica compleja a formato `yes/no` solo para obtener un meter.

Procedimiento:

1. formula una pregunta concreta,
2. revisa qué papers recupera,
3. identifica si aparece el paper primario,
4. selecciona un paper que también haya aparecido en otra herramienta,
5. compara la síntesis con el abstract y la fuente primaria,
6. registra una discrepancia, limitación o coincidencia.

Producto mínimo:

```text
1 paper coincidente con otra herramienta + 1 observación sobre la síntesis + 1 verificación en la fuente primaria
```

Pregunta de control:

> ¿Consensus encontró evidencia nueva o solamente sintetizó papers que ya habíamos localizado?.

#### Qué aprendiste de las seis herramientas

Al terminar la práctica guiada deberías poder explicar:

| Herramienta | Uso principal en CC-0F4 | No confundir con |
|---|---|---|
| Elicit | descubrimiento semántico y screening inicial | fuente primaria |
| ResearchRabbit | navegación iterativa por red de literatura | prueba de un claim |
| Connected Papers | mapa visual de similitud, prior y derivative works | árbol exacto de citaciones |
| Scite | contexto de citaciones | score universal de calidad |
| SciSpace | búsqueda, lectura y extracción asistida | lectura final del paper |
| Consensus | búsqueda y síntesis de evidencia académica | consenso definitivo del campo |

La idea central es:

```text
Elicit/SciSpace/Consensus -> encontrar y orientar

ResearchRabbit/Connected Papers -> expandir el espacio de literatura

Scite -> contrastar cómo se cita

paper original -> verificar
```

#### Workflow obligatorio para la exposición real

Después del tutorial, cada grupo investiga su tema.

No es obligatorio usar las seis herramientas en profundidad.

Sí es obligatorio cubrir tres roles:

```text
1 herramienta de descubrimiento + 1 herramienta de red + Scite o revisión explícita de citas + fuente primaria
```

Ejemplo válido:

```text
Elicit -> ResearchRabbit -> Scite -> arXiv/conferencia
```

Otro ejemplo válido:

```text
SciSpace -> Connected Papers -> Scite -> DOI/conferencia
```

Consensus puede utilizarse como contraste adicional.

#### Temas de exposición

La asignación depende del número de grupos.

| # | Tema | Seed paper sugerido | Pregunta central |
|---:|---|---|---|
| 1 | FlashAttention | Dao et al. (2022), arXiv:2205.14135 | ¿Cómo puede attention exacta reducir IO sin cambiar su resultado matemático? |
| 2 | MQA / GQA | Ainslie et al. (2023), arXiv:2305.13245 | ¿Qué cambia al reducir KV heads y cuál es el trade-off? |
| 3 | MLA | DeepSeek-V2 (2024), arXiv:2405.04434 | ¿Qué significa comprimir K/V en una representación latente? |
| 4 | SWA y contexto largo | Mistral 7B (2023), arXiv:2310.06825 | ¿Qué se gana y qué se restringe al limitar el rango visible? |
| 5 | PagedAttention / vLLM | Kwon et al. (2023), arXiv:2309.06180 | ¿Por qué administrar KV cache es también un problema de sistemas? |
| 6 | Speculative Decoding | Leviathan et al. (2022/2023), arXiv:2211.17192 | ¿Cómo reducir pasos seriales preservando la distribución objetivo? |
| 7 | RoPE vs ALiBi | RoFormer, arXiv:2104.09864, ALiBi, arXiv:2108.12409 | ¿Cómo incorporan posición y qué evidencia existe sobre extrapolación? |
| 8 | KV Cache Quantization | KIVI, arXiv:2402.02750 | ¿Qué cambia al cuantizar K/V y qué costos adicionales aparecen? |
| 9 | Prefill vs Decode | DistServe, arXiv:2401.09670 | ¿Por qué prefill y decode tienen objetivos y cuellos de botella diferentes? |
| 10 | Decoding y Neural Text Degeneration | Holtzman et al., arXiv:1904.09751 | ¿Cómo cambia el comportamiento con greedy, sampling, top-k y top-p? |

Si existen menos grupos se utilizan los primeros temas necesarios.

Si existen más de diez grupos, se puede repetir un tema, pero los grupos deben estudiar claims diferentes, papers posteriores diferentes o limitaciones diferentes.

#### Pregunta de investigación por tema

No uses como pregunta:

```text
What is FlashAttention?
```

Usa una pregunta que permita comparar y defender.

Ejemplos:

```text
FlashAttention
->
Under what hardware and sequence-length conditions does
FlashAttention reduce runtime or memory traffic compared with
a standard exact-attention implementation?
```

```text
GQA
->
What inference resource changes when the number of KV heads is
reduced, and what evidence exists about the quality trade-off?
```

```text
PagedAttention
->
How does paging the KV cache address fragmentation and batching
problems in LLM serving?
```

```text
Speculative Decoding
->
How can a draft model reduce serial target-model decoding while
preserving the target distribution?
```

#### Registro obligatorio de búsqueda

Cada grupo entrega esta tabla.

| Campo | Contenido |
|---|---|
| Tema | |
| Pregunta | |
| Herramienta de descubrimiento | |
| Query exacta | |
| Herramienta de red | |
| Seed paper | |
| Paper anterior | |
| Paper posterior o relacionado | |
| Scite / contexto de citación | |
| Fuente primaria verificada | |
| Claim principal | |
| Evidencia | |
| Tabla/figura/sección | |
| Limitación | |
| Claim después de la auditoría | |

La diferencia entre `Claim principal` y `Claim después de la auditoría` es intencional.

Un buen proceso de investigación puede terminar con un claim más pequeño pero mejor defendido.

#### Prompt base para descubrimiento

Puede utilizarse en Elicit, SciSpace o Consensus, adaptándolo a la interfaz.

```text
Research question:

[QUESTION]

Find primary research papers relevant to this question.

For each candidate identify:
1. title and year,
2. whether it is a primary method paper or later evaluation,
3. baseline,
4. proposed mechanism,
5. resource affected,
6. evaluation metric,
7. main reported result,
8. stated limitation.

Prioritize original papers and sources that can be verified
through arXiv, DOI, conference proceedings or publisher pages.

Do not strengthen a claim beyond what the paper reports.
```

#### Prompt para leer el paper primario

```text
Using only the supplied primary paper, extract:

1. problem,
2. baseline,
3. method,
4. variable modified,
5. resource affected,
6. experimental setup,
7. metric,
8. main quantitative result,
9. limitation,
10. one claim that would be unsafe to generalize.

For items 6-9, indicate the section, table or figure that
should be verified manually.

If the paper does not support an item, write:
NOT ESTABLISHED BY THIS PAPER.
```

#### Prompt de auditoría final

```text
Audit this technical claim:

[CLAIM]

Evidence supplied:
- primary paper,
- one earlier or related paper,
- one later or citing paper.

Return:
1. what the primary paper demonstrates,
2. experimental conditions,
3. what it does not demonstrate,
4. whether later literature supports, limits or contradicts it,
5. assumptions required to transfer the claim to another model,
   runtime or hardware setting,
6. a narrower defensible version of the claim.

Do not strengthen the claim beyond the supplied evidence.
```

#### Producto de la exposición

La presentación tiene como máximo cuatro bloques conceptuales.

```text
1. problema + baseline
2. mecanismo
3. evidencia
4. limitación + conexión con Laboratorio 2
```

Debe contener una tabla final:

| Campo | Contenido |
|---|---|
| Problema | |
| Baseline | |
| Método | |
| Variable modificada | |
| Nivel del sistema | arquitectura/kernel/runtime/decoding |
| Recurso afectado | |
| Métrica | |
| Resultado principal | |
| Condiciones experimentales | |
| Limitación | |
| Paper relacionado | |
| Claim auditado | |
| Relación con Experimento A o B | |

#### Diapositiva obligatoria de trazabilidad

Una diapositiva debe mostrar:

```text
pregunta -> query -> herramienta 1 -> seed paper -> herramienta 2 -> paper relacionado
-> Scite/cita -> fuente primaria -> claim final
```

No hace falta mostrar capturas de todas las interfaces.

Lo importante es que la búsqueda pueda reconstruirse.

#### Preguntas que se debe tener en cuenta

1. ¿Por qué elegiste ese seed paper?
2. ¿Qué encontró Elicit, SciSpace o Consensus que no sabías al comenzar?
3. ¿Qué añadió ResearchRabbit o Connected Papers?
4. ¿Qué significa una conexión en Connected Papers?
5. ¿Qué significa una Smart Citation de Scite y qué NO significa?
6. ¿Qué claim cambió después de leer el paper?
7. ¿Qué tabla, figura o sección respalda tu resultado principal?
8. ¿Contra qué baseline se compara?
9. ¿La mejora es analítica, estimada o medida?
10. ¿El método cambia arquitectura, kernel, runtime o decoding?
11. ¿El resultado depende del hardware?
12. ¿La técnica reduce compute, IO, KV cache, fragmentación o más de uno?
13. ¿Qué paper posterior limita o amplía el trabajo original?
14. ¿Qué afirmación no podrías defender solo con el abstract?
15. ¿Qué parte conecta directamente con Experimento A o Experimento B?
16. ¿Qué herramienta fue menos útil para tu pregunta y por qué?.

#### Criterio de calidad

Una exposición fuerte muestra:

```text
pregunta precisa + búsqueda trazable + seed paper justificado + fuente primaria + red de literatura + contexto de citación
+ mecanismo entendido + evidencia cuantitativa + limitación + claim proporcional a la evidencia
```

No se considera suficiente:

```text
prompt -> respuesta de IA -> diapositiva
```

Tampoco:

```text
muchos papers -> sin pregunta -> sin baseline -> sin evidencia verificable
```

#### Checklist antes de exponer

El grupo debe poder responder "sí" a estas preguntas:

- ¿Tenemos una pregunta concreta?
- ¿Identificamos el paper primario?
- ¿Sabemos por qué es primario?
- ¿Registramos las queries utilizadas?
- ¿Usamos una herramienta de descubrimiento?
- ¿Usamos una herramienta de red?
- ¿Revisamos contexto de citación o literatura citante?
- ¿Abrimos la fuente original?
- ¿Podemos señalar tabla, figura o sección?
- ¿Tenemos un baseline?
- ¿Podemos nombrar la métrica?
- ¿Conocemos al menos una limitación?
- ¿Nuestro claim final es más preciso que un eslogan?
- ¿Podemos conectarlo con el Laboratorio 2?.

#### Regla final

Las herramientas aceleran partes distintas del proceso.

No reemplazan el juicio científico.

```text
buscar != leer

leer != verificar

verificar != generalizar

muchas citas != evidencia suficiente
```

La responsabilidad final del grupo es poder defender:

> Esta es nuestra afirmación, esta es la fuente que la sustenta, estas son las condiciones bajo las que se obtuvo y esta es la limitación que impide generalizarla sin más evidencia.
