### Lectura 9 - Workflows, agentes, planificación, ReAct y criterios de parada

#### Propósito y delimitación

Hasta la Semana 7, el curso había estudiado cómo transformar documentos en representaciones recuperables, combinar BM25 y recuperación densa, construir contexto para RAG y evaluar rankings y respuestas. La Semana 6 había introducido algo igualmente decisivo: la diferencia entre una propuesta de llamada generada por un modelo y la ejecución que el programa puede autorizar. En la Semana 9 pasamos de **una llamada controlada** a **una secuencia de decisiones controladas**. La pregunta ya no es únicamente si una herramienta es correcta, sino quién decide utilizarla, cuándo se repite, qué se hace ante un error y qué evidencia justifica terminar.

El objetivo no es construir una plataforma completa de agentes, ni agregar memoria persistente, ni coordinar múltiples agentes. Es comprender el **control de flujo observable** de sistemas que combinan modelos, herramientas y datos. En esta lectura usaremos *estado transitorio* para contar pasos, mantener las últimas observaciones y registrar una ejecución. La representación, persistencia y recuperación de *working memory*, *episodic memory* y *semantic memory* corresponden a la Semana 10.

#### 1. Un problema de ingeniería: responder no siempre equivale a resolver

Considérese una consulta del corpus institucional de la Semana 4: un equipo recibe IP y puede acceder a direcciones numéricas, pero no resuelve nombres de dominio. Un sistema RAG tradicional sigue un procedimiento reconocible: recuperar pasajes, construir contexto, generar respuesta y, cuando corresponde, evaluar sus citas. Esta arquitectura puede ser suficiente. No es razonable incorporar autonomía si el problema se resuelve mediante una única recuperación conocida y un generador bien controlado.

Ahora imagine una consulta incompleta: "La VPN dice conectada, pero un servicio interno no funciona". El sistema podría necesitar diferenciar resolución DNS, rutas de red y permisos. Una aplicación puede programar una secuencia fija de diagnósticos. Otra puede evaluar un resultado intermedio y elegir qué prueba aplicar después. Una tercera podría pedir a un LLM que seleccione la próxima acción de entre herramientas autorizadas. Las tres pueden producir respuestas correctas, pero tienen superficies de fallo y costos diferentes.

El criterio técnico no es si la interfaz parece conversar de manera autónoma. Importan **la política de selección**, **el espacio de acciones**, **las observaciones que modifican la política** y **el mecanismo de terminación**. La autonomía no es un atributo visual del chatbot: es una propiedad de la arquitectura de control.

#### 2. Pipeline, workflow y agente: diferencias operativas

Un *pipeline* transforma información mediante etapas cuyos enlaces están predefinidos. Por ejemplo:

```text
consulta -> BM25 -> fusión con dense -> reranking -> contexto -> respuesta
```

Es común que las etapas contengan módulos estadísticos o modelos de lenguaje. Esto no convierte automáticamente al sistema en un agente. Un *workflow* prescribe un grafo de operaciones y las condiciones que determinan sus rutas. Puede contener ramas, paralelismo y bucles con reglas explícitas. Un workflow no significa necesariamente una sola secuencia lineal.

En un **controlador heurístico adaptativo**, la siguiente acción depende de una observación, pero la función de decisión está determinada por el programador. Por ejemplo, ampliar la búsqueda cuando una cobertura léxica cae bajo un umbral fijado previamente. La decisión es sensible a los datos, aunque no esté generada por un LLM.

En un **agente dirigido por LLM**, el modelo participa realmente en la elección de la acción y de sus argumentos. El programa, sin embargo, conserva la autoridad de validar la acción, ejecutar o rechazar la herramienta y detener la ejecución. Esta separación es crítica: *seleccionar* una operación no equivale a *autorizarla*.

| Arquitectura | ¿Quién define el siguiente paso? | Ejemplo | Ventaja | Riesgo |
|---|---|---|---|---|
| Pipeline fijo | Código | Buscar, rerankear, responder | Reproducible y fácil de auditar | Poco flexible |
| Workflow con ramas | Condiciones programadas | Ruta de FAQ o soporte técnico | Predecible y adaptable | Reglas incompletas |
| Control heurístico | Política explícita sobre observaciones | Expandir top-1 a top-3 | Bajo costo de decisión | Umbrales frágiles |
| Agente LLM | Modelo propone, controlador autoriza | Elegir búsqueda, lectura o finalización | Flexibilidad ante variación de tareas | Decisiones erróneas y costo variable |

No debe asumirse que la última fila siempre es superior. La ingeniería consiste en comparar el incremento de capacidad con el incremento de riesgo, latencia, costo e incertidumbre.

#### 3. Cinco patrones de workflows

La clasificación difundida en *Building Effective Agents* distingue cinco patrones particularmente útiles. No constituyen una secuencia de madurez ni exigen un framework.

##### 3.1 Prompt chaining

Divide una tarea en subtareas encadenadas. Un paso produce un artefacto que otro consume. Ejemplo: extraer entidades de una consulta, validar su estructura y construir una búsqueda. El código decide el orden, aunque cada transformación pueda usar un LLM. Un control de esquema entre pasos evita que una salida incorrecta contamine toda la cadena.

```text
consulta -> extraer entidades -> validar JSON -> recuperar evidencia
```

El costo tiende a crecer con el número de invocaciones. Si cada paso introduce una probabilidad independiente de fallo, la probabilidad de éxito de la cadena disminuye con su longitud. La independencia suele ser una aproximación, no una propiedad garantizada.

##### 3.2 Routing

Clasifica una solicitud y elige un procedimiento especializado. En soporte universitario, una consulta podría ir a rutas de red, repositorio o biblioteca. El clasificador puede ser determinista o un modelo. La clasificación incorrecta afecta todo el recorrido, por eso se requiere una ruta de incertidumbre, no solamente rutas para casos conocidos.

```text
consulta -> clasificar tipo
                  |-- red -> retriever de conectividad
                  |-- Git -> retriever de seguridad
                  `-- incierto -> recuperar en índice general
```

##### 3.3 Parallelization

Ejecuta operaciones independientes en paralelo y agrega resultados. Dos estrategias comunes son *sectioning*, que divide una tarea en partes no superpuestas, y *voting*, que obtiene varias estimaciones. La reducción de latencia no es automática: la agregación, los límites de concurrencia y la lentitud de la rama más lenta pueden anularla. No debe paralelizarse una operación que depende del resultado de otra.

##### 3.4 Evaluator-optimizer

Produce una salida, la evalúa respecto de criterios explícitos y, solo si aporta valor, solicita una revisión. El ciclo requiere un máximo de iteraciones y un criterio de aceptación. Sin una función de evaluación estable, el sistema puede oscilar entre versiones sin progreso. Una evaluación basada en un LLM no debe presentarse como verdad objetiva.

```text
candidato -> evaluar criterios -> aprobado
                 |
                 `-> corregir -> reevaluar (máximo N veces)
```

##### 3.5 Orchestrator-workers

Un orquestador descompone un problema y asigna subtareas a trabajadores especializados. En Semana 9 se estudia como **patrón arquitectónico**: qué información debe asignarse y cómo reconocer dependencias. No se implementa todavía el sistema multiagente completo con handoffs y estado compartido; ese desarrollo se reserva a Semana 11. El nombre del patrón no justifica introducir múltiples modelos cuando funciones ordinarias bastan.

#### 4. Anatomía del agente: responsabilidades distintas

Una arquitectura básica tiene una tarea, un controlador, una política de decisión, herramientas y observaciones. También requiere límites. El modelo de lenguaje es un posible módulo de decisión, no el sistema entero.

```text
Tarea de usuario
    |
    v
Controlador [autoridad, presupuestos, validación]
    |
    +--> Política LLM: propone {action, arguments}
    |
    +--> Validador: contrato, allowlist, presupuesto
    |
    +--> Herramienta: lectura o búsqueda autorizada
    |
    <--- Observación (datos potencialmente no confiables)
    |
    +--> Nueva decisión o terminación explícita
```

Una herramienta debe exponer un nombre inequívoco, un contrato de entrada, un contrato de salida y una política de errores. La Semana 6 estudió validación estructural, de dominio, retries y timeouts en una llamada; ahora el controlador debe conservar esas garantías **en cada iteración**. La existencia de `max_steps` no reemplaza el timeout de una herramienta, ni el timeout de un intento reemplaza el deadline de toda la tarea.

No confundamos las **observaciones** con instrucciones. Un documento recuperado puede contener una frase como "ignora las reglas anteriores". Esa frase es información de una fuente no confiable. No puede cambiar la allowlist, conceder permisos o levantar un presupuesto. El controlador trata la observación como datos y separa estrictamente las instrucciones del sistema de los resultados externos.

#### 5. Perceive, Decide, Act, Observe: un ciclo ejecutable

Podemos describir la operación mediante el estado transitorio $s_t$, una observación $o_t$, una acción $a_t$ y una política $\pi$. Conceptualmente:

$$
 a_t = \pi(task, s_t, o_{\le t})
$$

La acción no se ejecuta inmediatamente. Primero pasa por una función de validación $V(a_t, s_t, B)$ con un presupuesto restante $B$. Si $V$ rechaza la acción, se registra el rechazo y se aplica la política de recuperación o parada. Si la acepta, una herramienta genera una nueva observación. El estado evoluciona para reflejar contadores, identificadores recuperados y el resultado de la última acción:

$$
 s_{t+1} = update(s_t, a_t, observation_t)
$$

En esta semana $s_t$ es únicamente un registro operativo de **la ejecución actual**. No constituye memoria semántica, episódica ni una memoria de trabajo general reutilizable entre sesiones.

##### Invariantes del controlador

- Toda acción tiene un nombre presente en una allowlist.
- Una acción inválida no dispara efectos externos.
- El número de llamadas a herramientas nunca supera `max_tool_calls`.
- Toda ejecución termina por éxito validado o por una razón de parada reconocible.
- La acción `finish` solo puede citar identificadores recuperados por la propia ejecución.
- Un resultado de herramienta no amplía permisos por su contenido.
- La traza distingue acciones propuestas, aceptadas, rechazadas y ejecutadas.

Estos invariantes son comprobables con pruebas unitarias; no dependen de la calidad lingüística del LLM.

#### 6. ReAct: seleccionar acciones a partir de observaciones

El artículo *ReAct: Synergizing Reasoning and Acting in Language Models*, de Yao y colaboradores, propone intercalar razonamiento y acción para tareas en las que la información disponible cambia durante la ejecución. En un sistema docente no necesitamos registrar cadenas internas de razonamiento. Sí necesitamos exponer y comprobar la decisión estructurada, su autorización y la observación producida por cada herramienta.

Una traza simplificada, **ilustrativa y no medida**, podría ser:

```text
Paso 1: modelo propone search_documents(query="DNS sin resolución", top_k=3)
Controlador: valida contrato y presupuesto, ejecuta
Observación: se recuperaron D01-P03, D02-P04, D01-P02
Paso 2: modelo propone read_passage(passage_id="D01-P03")
Controlador: valida que ese identificador fue observado
Observación: se lee el pasaje pertinente
Paso 3: modelo propone finish(answer="...", citations=["D01-P03"])
Controlador: valida citas observadas y longitud de respuesta
Salida: completed_with_citations
```

La selección ha sido propuesta por el modelo, pero un programa puede denegarla. Si usamos una lista de acciones predefinida, tenemos un *replay* o *scripted policy*: sirve para probar la infraestructura, pero **no constituye evidencia de capacidad ReAct del LLM**. Por eso el paquete separa `ScriptedPolicy` y `LocalTransformersPolicy`.

La denominación "ReAct" es útil cuando existe interacción modelo-observación-acción. No debe asignarse automáticamente a un algoritmo que contiene un `while` o una regla `if score < threshold`.

#### 7. Planificación, descomposición y replanning

Una tarea compuesta puede descomponerse en subtareas con dependencias. Ejemplo: para responder una incidencia de conectividad, primero identificar el síntoma observable, recuperar las políticas relevantes, comprobar si la evidencia permite distinguir hipótesis y producir una respuesta con citas. La planificación explicita qué se quiere lograr y qué datos faltan; no obliga a construir un plan largo antes de cada consulta.

- **Plan fijo**: las subtareas se ejecutan siempre en orden.
- **Plan-and-execute**: se propone un plan breve y luego se ejecutan subtareas.
- **Replanning**: ante una observación inesperada se actualiza el plan y se evita repetir pasos inútiles.

En un caso de error controlado, `read_passage` devuelve un rechazo porque el modelo propone un identificador que nunca fue recuperado. El controlador no debe ejecutar la lectura. Puede comunicar el error como observación y permitir una decisión alternativa, siempre dentro del límite de pasos. Si el mismo modelo repite la petición prohibida, el sistema puede terminar por acción repetida o límite de acciones inválidas.

Planificar no significa concederle autoridad al plan. Las acciones siguen validadas una por una. La modificación del plan debe poder reconstruirse desde la traza, de lo contrario no sería posible explicar por qué el agente cambió su estrategia.

#### 8. Límites, costos y condiciones de parada

Un agente que puede decidir volver a usar una herramienta debe tener presupuestos explícitos. Los límites no deben depender exclusivamente de la buena voluntad del modelo.

| Límite | Qué controla | Qué no garantiza |
|---|---|---|
| `max_steps` | Cantidad máxima de decisiones | No garantiza un costo monetario fijo |
| `max_tool_calls` | Número de ejecuciones de herramientas | No limita por sí solo el costo de cada herramienta |
| `deadline_seconds` | Tiempo total cooperativo del controlador | No interrumpe necesariamente una llamada ya iniciada |
| `max_invalid_actions` | Intentos rechazados | No determina calidad de respuestas |
| `max_new_tokens` | Longitud de la generación local | No incluye todos los tokens de entrada |
| Detección de repetición | Una acción idéntica sin avance | No detecta todos los ciclos semánticos |

La **terminación correcta** exige una condición verificable. `completed_with_citations` significa que se aceptó una respuesta con citas ya observadas, no que se haya demostrado automáticamente su corrección semántica. `max_steps`, `max_tool_calls`, `deadline_exceeded`, `repeated_action` e `invalid_action_limit` son terminaciones controladas, pero no éxitos de tarea.

Una acción puede repetirse legítimamente si cambian sus argumentos o si la fuente ha cambiado. Para el ejemplo docente, bloquear una firma exacta repetida permite visualizar un fallo recurrente; un sistema real necesitaría detectar progreso insuficiente mediante señales de utilidad adicionales.

##### Análisis de complejidad

Si el controlador permite a lo sumo `S` decisiones y `T` llamadas, su número de iteraciones es `O(S)` y el número de herramientas invocadas está acotado por `T`. Si una llamada al LLM cuesta `C_m` y una herramienta `C_h`, un presupuesto simple es `O(S*C_m + T*C_h)`. No representa una igualdad monetaria: los costos reales dependen de tokens de entrada, salida, cachés, latencia de red y el tipo de herramienta. La latencia extremo a extremo no es necesariamente la suma simple cuando hay paralelismo, y una herramienta bloqueada puede romper un deadline cooperativo.

#### 9. Instrumentación: qué debe mostrar una traza

Una traza debe permitir contestar quién propuso la acción, cuál fue validada, qué argumentos utilizó, qué observación produjo, qué presupuesto quedaba y por qué terminó la ejecución. Para proteger datos sensibles no debe guardar credenciales ni textos completos de documentos si no son necesarios. Una entrada puede contener `step`, `action`, `arguments`, `status`, `observation_ids`, `error_type`, contadores y `stop_reason`.

En este paquete, `agent_benchmark.py` produce tablas reproducibles del controlador heurístico, mientras `agent_demo.py` produce trazas individuales de un replay o de un modelo local. Es fundamental distinguir ambas procedencias. Que una traza tenga aspecto de agente no demuestra que haya intervenido un modelo.

#### 10. Diseño experimental: comparar sin favorecer inadvertidamente a una política

Usamos un subconjunto fijo de SQuAD 1.1 dev: ocho articulos reales de Wikipedia, 32 pasajes originales, 16 preguntas humanas y sus pasajes de origen anotados. Los qrels de esta muestra no son juicios exhaustivos de relevancia. Para aislar la política de control utilizamos la **misma implementación de BM25** en las condiciones offline. No estamos reemplazando el baseline de recuperación densa o híbrida de la Semana 7; la herramienta BM25 local es un instrumento para estudiar decisiones y pasos.

Se proponen tres condiciones offline:

```text
A0 workflow_fixed_top1:       una búsqueda top-1
A1 workflow_fixed_top3:       una búsqueda top-3
B  adaptive_rule_based:       primera búsqueda top-1;
                             si cobertura léxica < 0.45, ampliar a top-3
```

A0 proporciona el extremo de contexto mínimo y A1 el extremo de mayor contexto entre estos dos valores. B intenta ahorrar contexto cuando la primera observación parece suficiente. **Con un ranking BM25 inmutable, los pasajes top-1 son un subconjunto de top-3**. Por ello, para cualquier consulta y el mismo conjunto de relevantes:

$$
 Hit_{A0}(q) \le Hit_B(q) \le Hit_{A1}(q)
$$

Esta desigualdad no mide la utilidad total: B puede gastar dos llamadas, consumir menos pasajes o terminar prematuramente. La mejora de B no puede declararse como una mayor cobertura que A1 bajo este diseño. Su posible valor es un compromiso entre cobertura y presupuesto de contexto. Además, el indicador `context_token_proxy` solo cuenta palabras obtenidas por el tokenizador léxico del benchmark; **no es el número de tokens reales del modelo ni un costo API**.

Un verdadero agente LLM constituye una **cuarta condición exploratoria**, C. Si puede reformular búsquedas o abrir pasajes selectivamente, tiene capacidades diferentes de A0/A1/B; el experimento debe declararlo y no atribuir causalmente sus diferencias únicamente a la autonomía. Para comparar respuestas semánticas, hacen falta anotaciones y evaluación aparte, que se profundizarán en otras semanas.

##### Métricas que sí podemos interpretar

- `evidence_hit`: al menos un pasaje citado pertenece al conjunto relevante de la consulta.
- `mean_tool_calls`: promedio de invocaciones de herramientas.
- `mean_steps`: promedio de acciones registradas.
- `mean_context_token_proxy`: longitud léxica del contexto citado, no tokens del LLM.
- `mean_latency_ms`: tiempo local observado de la ejecución del script, dependiente de la máquina y sin inferencia LLM.
- `stop_reason`: cómo terminó, separado del éxito de la tarea.

La tasa de acierto de evidencia no equivale a `answer correctness`, `faithfulness` ni éxito funcional. Conviene inspeccionar consulta por consulta y registrar paradas equivocadas, ampliaciones inútiles y citas no pertinentes. El artículo *AI Agents That Matter* advierte sobre interpretaciones de desempeño que ignoran costos y debilidades de evaluación; el benchmark docente sirve para formular hipótesis, no para generalizarlas a toda tarea agéntica.

#### 11. Caso de estudio completo y preguntas de análisis

Tome las consultas Q01 (resolución de DNS), Q07 (token publicado en Git) y Q15 (solicitud MFA inesperada). Primero ejecute A0/A1/B sin LLM y observe qué identificadores aparecen como relevantes. Después, mediante `ScriptedPolicy`, recorra una secuencia de búsqueda, lectura y finalización con citas permitidas. Por último, si dispone del modelo local, conecte `LocalTransformersPolicy` y compruebe si puede producir decisiones JSON válidas. El último paso **no está garantizado**: modelos compactos pueden devolver JSON incorrecto, elegir una herramienta innecesaria o terminar antes de tiempo. Esos fallos son parte del experimento, no resultados que deban ocultarse.

Preguntas para responder con evidencia:

1. ¿Qué clase de decisión diferencia el workflow fijo del adaptativo, y por qué ninguna de las dos políticas offline es un LLM agent?
2. Si B recupera un solo pasaje, ¿se puede afirmar que es más eficiente? Considere tiempo, llamadas y longitud de contexto.
3. ¿Por qué cualquier parrafo recuperado de Wikipedia debe tratarse como dato, y no como instruccion ejecutable del controlador?
4. ¿Qué distingue un error de esquema, un error de dominio, una falla de herramienta y una parada prematura?
5. ¿Cuándo debería detenerse el agente en vez de intentar una tercera reformulación de la consulta?
6. ¿Cómo demostraría que una nueva política mejora respecto de A1 sin ajustar reglas sobre las mismas 16 preguntas humanas?
7. ¿Por qué `completed_with_citations` no es una prueba de veracidad de la respuesta?
8. ¿Qué información falta para comparar costo monetario de dos modelos distintos?.

#### 12. Alcance hacia las semanas posteriores

La Semana 9 finaliza con un bucle observable, un estado transitorio mínimo y terminación controlada. No implementa memoria persistente, recuperación de episodios, bases vectoriales de recuerdos o aprendizaje acumulativo. Tampoco requiere múltiples agentes con handoffs. Esa frontera permite profundizar esta semana en **control**, la próxima en **memoria** y después en **coordinación y evaluación avanzada**, sin confundir los niveles arquitectónicos.

#### Referencias y lectura técnica

1. Anthropic, *Building Effective Agents*. Arquitecturas, cinco patrones y elección de complejidad: https://www.anthropic.com/research/building-effective-agents
2. Shunyu Yao et al., *ReAct: Synergizing Reasoning and Acting in Language Models*, ICLR 2023: https://arxiv.org/abs/2210.03629
3. S. Kapoor et al., *AI Agents That Matter*, 2024: https://arxiv.org/abs/2407.01502
4. Anthropic, notebooks de patrones mínimos: https://github.com/anthropics/claude-cookbooks/tree/main/patterns/agents
5. Jules White, ejemplos de agentes Python y MCP: https://github.com/juleswhite/python-agents-mcp-course
6. Stanford CS329Z, *Engineering AI Agents*: https://cs329z.stanford.edu/
7. Attention AI Lab, ejemplos de trazas y depuración: https://github.com/kapumota/attentionlab-ai
8. OWASP, *LLM Prompt Injection Prevention Cheat Sheet*: https://cheatsheetseries.owasp.org/cheatsheets/LLM_Prompt_Injection_Prevention_Cheat_Sheet.html



#### Anexo: procedencia de los datos reales

La muestra del laboratorio proviene de SQuAD 1.1, un conjunto de preguntas realizadas por personas sobre parrafos de Wikipedia con respuestas anotadas (Rajpurkar et al., 2016). Se seleccionan 8 articulos, cuatro parrafos por articulo y una pregunta del primer y tercer parrafo. La seleccion se fija antes de ejecutar los baselines. No se fabrican preguntas ni resultados.
Las etiquetas indican el pasaje original que contiene la respuesta humana, no todos los pasajes que podrian responder la pregunta. El ingles de las fuentes se conserva para evitar introducir alteraciones mediante traduccion.
La pregunta cientifica de Semana 9 no es superar el benchmark SQuAD, sino comparar politicas de ejecucion bajo el mismo retriever y presupuesto.
