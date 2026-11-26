### **Lectura 10: Estado, memoria de trabajo, memoria episódica y recuperación verificable**

 **Caso experimental:** QMSum, transcripciones de reuniones Academic y Committee, con consultas humanas y turnos de apoyo anotados.

#### **1. Del controlador a la memoria**

En la Semana 9, un controlador toma decisiones y acumula observaciones **durante una ejecución**. El estado `RunState` registra pasos, llamadas, evidencias vistas y razón de parada. No constituye memoria persistente. Una ejecución posterior no tiene por qué recuperar las observaciones anteriores.

En la Semana 10 distinguimos:

| Concepto | Función | Duración | Ejemplo del curso |
|---|---|---|---|
| Estado de ejecución | Controlar el paso actual | Una ejecución | `step`, `tool_calls`, `stop_reason` |
| Memoria de trabajo | Conservar contexto cercano bajo un límite | Ventana | Últimos 48 turnos de reunión |
| Memoria episódica | Conservar observaciones con identidad y procedencia | Entre ejecuciones | Turnos registrados en SQLite |
| Memoria semántica | Recuperar información a partir de representaciones de significado o hechos consolidados | Según política de vigencia | Tema y conceptos codificados en embeddings, *no implementados experimentalmente esta semana* |

Un sistema puede persistir episodios sin tener memoria semántica. Asimismo, acceder a un texto almacenado no significa que el sistema lo comprenda ni que sea cierto.

#### **2. Ciclo de memoria y frontera de confianza**

Un diseño seguro separa **escritura**, **lectura**, **recuperación**, **validación** y **olvido o actualización**. La transcripción es un dato procedente de terceros, nunca una instrucción de ejecución. La escritura debe utilizar identificadores inequívocos y conservar el origen.

En nuestro almacén, una clave es `(meeting_id, position)`. La lectura usa `ORDER BY position`. Si se repite la misma reunión con el mismo contenido, el guardado es idempotente. Si aparece el mismo `meeting_id` con otros turnos, el programa **rechaza la escritura** en vez de sobrescribir silenciosamente. Es un contrato de integridad, no un mecanismo de resolución de contradicciones semánticas.

La base SQLite se conserva como archivo `Semana10/datos/qmsum_episodic.sqlite3`; cada ejecución posterior puede volver a leer los episodios. El archivo no debe compartirse como supuesto resultado experimental ni contener claves secretas.

#### **3. QMSum: corpus, procedencia y diseño**

El conjunto QMSum contiene reuniones largas con consultas específicas y resúmenes, junto a rangos de turnos relevantes anotados por humanos. Utilizamos los dominios Academic y Committee; no utilizamos Product para no introducir reuniones de producto escenificadas como si fueran casos naturales. Conservamos **todos** los archivos oficiales `train`, `val` y `test` de esos dos dominios, sin seleccionar reuniones que favorezcan una política.

Fuente: [Yale-LILY/QMSum](https://github.com/Yale-LILY/QMSum), commit `83d7768c1f2b4dfeb091385d3dc7e239b8e5bb7e`. Cada JSONL se valida contra su tamaño y objeto Git SHA-1 publicado. La preparación requiere conexión una vez; la evaluación posterior es local. No creamos documentos, consultas, conversaciones ni etiquetas de relevancia para el experimento.

La unidad de evidencia es el **turno**. Para una consulta humana $q$, el conjunto de referencia $G_q$ agrupa los índices incluidos en `relevant_text_span`. El recuperador recibe únicamente el texto original y la pregunta; **no** recibe los resúmenes humanos ni los rangos gold.

#### **4. Memoria de trabajo frente a memoria episódica**

Sea $M$ una reunión almacenada con $N$ turnos y $K=48$ una capacidad común.

**Ventana reciente:**

$$
W_K(M)=\{\max(0,N-K),\ldots,N-1\}.
$$

**Recuperación episódica:**

$$
R_K(q,M)=\operatorname{topK}_{i\in M}\operatorname{BM25}(q,\operatorname{turno}_i).
$$

BM25 es una puntuación léxica basada en frecuencias de términos, longitud del documento e inverso de frecuencia documental; no representa semántica mediante embeddings. Ambos métodos ofrecen hasta 48 turnos, pero uno privilegia **posición reciente** y el otro **coincidencia léxica**. Ninguno garantiza encontrar toda la información relevante.

Un turno sin palabras compartidas con la consulta puede tener puntuación BM25 cero. El prototipo conserva esos empates en el ranking de tamaño fijo; una puntuación cero **no prueba** que la pregunta carezca de respuesta.

#### **5. Qué se puede medir honestamente**

Para el conjunto gold $G_q$ y la selección $S_q^P$ de la política $P$:

$$
\mathrm{TurnRecall}(q,P)=\frac{|G_q\cap S_q^P|}{|G_q|},
\qquad
\mathrm{AnyHit}(q,P)=\mathbb{1}[G_q\cap S_q^P\ne\varnothing].
$$

`AnyHit=1` puede coexistir con `TurnRecall` muy bajo: una reunión puede necesitar numerosos turnos distantes para sostener su respuesta. Estas métricas **no** son calidad de resumen, respuesta correcta, *entailment*, uso real de memoria semántica ni seguridad contra instrucciones maliciosas.

La comparación es **pareada por pregunta**. Para cada `meeting` y `query_index`, calculamos la diferencia entre `episodic_bm25` y `working_recent`. Es mejor inspeccionar los turnos gold originales de las discrepancias que confiar únicamente en un promedio.

#### 6. Vigencia, recencia y contradicciones

La posición de un turno no es una fecha de validez factual. Un participante puede corregir una afirmación anterior, expresar una hipótesis o retractarse. Seleccionar el último turno no demuestra que sea el válido; elegir el mejor score tampoco. Se requiere una política explícita que capture procedencia, fecha, versión, confirmación y relaciones de supersesión. Esta semana **no** pretendemos inferir automáticamente esos vínculos desde QMSum.

En una base de memoria, hay dos situaciones distintas:

- **Conflicto de identidad:** intentar guardar contenido distinto bajo el mismo `meeting_id`. La implementación lo rechaza; es comprobable mediante contratos de SQLite.
- **Contradicción de hechos:** dos intervenciones dicen cosas incompatibles. Detectarla y determinar cuál prevalece requeriría razonamiento, anotaciones o revisión humana. No puede inferirse de la clave primaria.

En la práctica de laboratorio, los estudiantes inspeccionarán turnos reales para **proponer** qué metadatos de validez faltan, sin generar nuevas etiquetas de verdad presentadas como gold.

#### **7. Abstención y límites de la evidencia**

Un recuperador no debería inventar citas para aparentar conocimiento. Sin embargo, QMSum ofrece consultas contestables anotadas: no hay una colección independiente de preguntas sin respuesta y sus etiquetas. Por tanto, no es legítimo afirmar una tasa de acierto de abstención. Podemos estudiar **señales diagnósticas** como `top_bm25_score=0`, y su relación con cobertura de turnos anotados, pero esa señal no es una evaluación de incertidumbre calibrada.

Asimismo, añadir una segunda llamada a un LLM o una búsqueda vectorial tendría nuevos costos y exigiría registrar modelo, revisión, recursos y métricas. Los experimentos evaluados aquí **no ejecutan un LLM**.

#### **8. Protocolo de clase y amenazas a la validez**

1. **Antes de clase:** preparar los seis JSONL oficiales y verificar hashes; ejecutar las pruebas unitarias, que no requieren Internet.
2. **Teoría:** ejecutar el cuaderno sobre `val` y discutir los contratos de persistencia y recuperación.
3. **Laboratorio:** evaluar `test` con `K=48` predeclarado, inspeccionar diferencias y preparar un reporte con IDs de reuniones y consultas.
4. **Sin ajustes a posteriori:** el test oficial no se usa para elegir K, tokenización, variantes BM25 ni ejemplos favorables. Si se exploran K alternativos, hacerlo en `val` y declararlo como exploración.

Amenazas: relevancia incompleta de los turnos gold, sesgo léxico de BM25, longitud heterogénea de reuniones, subconjunto de dos dominios, diferencias entre recuperación y respuesta. QMSum `test` es público y no es un test oculto independiente.

#### **9. Preguntas para discusión y evaluación**

- ¿Por qué incrementar K puede elevar `AnyHit` y a la vez aumentar costo de contexto?
- ¿Qué evidencia necesitarías para afirmar que memoria episódica mejora **exactitud de respuesta**, más allá de localizar turnos?
- ¿Cómo tratarías versiones contradictorias de una decisión sin sobrescribir la fuente histórica?
- ¿Por qué los identificadores y los hashes pertenecen al control de integridad y no a la semántica de las reuniones?
- ¿Por qué `top_bm25_score=0` no autoriza a declarar que un problema carece de respuesta?
- ¿Qué separa la memoria de la Semana 10 de un supervisor multiagente de la Semana 11?.

#### **Referencias**

1. Zhong et al., [QMSum: A New Benchmark for Query-based Multi-domain Meeting Summarization](https://arxiv.org/abs/2104.05938), NAACL 2021.
2. [Yale-LILY/QMSum, repositorio de datos](https://github.com/Yale-LILY/QMSum).
3. Robertson y Zaragoza, [The Probabilistic Relevance Framework: BM25 and Beyond](https://www.nowpublishers.com/article/Details/INR-019).
4. Packer et al., [MemGPT: Towards LLMs as Operating Systems](https://arxiv.org/abs/2310.08560).
5. Anthropic, [Building Effective Agents](https://www.anthropic.com/research/building-effective-agents), para separar mecanismos programados y agentes LLM.
