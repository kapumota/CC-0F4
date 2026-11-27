### Semana 11: sistemas multiagente, supervisor y contratos de coordinación

**Curso:** CC-0F4, Tópicos de Ciencia de la Computación I.

**Dedicación:** dos horas de teoría y cuatro de laboratorio.

**Pregunta central:** ¿qué añade la separación en trabajadores a un sistema de recuperación y respuesta, y cómo se mide su utilidad sin confundir la corrección de los contratos con la calidad de la respuesta?

#### 1. Objetivos de aprendizaje

Al terminar la semana, el estudiante podrá distinguir un agente único de un supervisor con trabajadores, describir un contrato de mensajes y su autoridad, registrar trazas de coordinación, verificar la procedencia de evidencia y diseñar una comparación empírica sin filtrar anotaciones humanas en la entrada.

Se espera también que pueda justificar cuándo una solución con un solo agente resulta preferible. Delegar una tarea no es siempre una mejora. Produce nuevas llamadas, mensajes, validaciones y oportunidades de fallo.

#### 2. De la Semana 9 a la Semana 11

En la Semana 9 se implementó un controlador que admite acciones, observaciones, límites y motivos de terminación. El experimento utilizó SQuAD completo y una comparación exploratoria con un modelo local. El código del controlador podía verificar que una cita procediera de un pasaje observado, pero esa comprobación no validaba el contenido de la respuesta.

La Semana 10 introdujo SQLite y recuperación de memoria a partir de transcripciones QMSum. Allí se comparó una ventana reciente con una memoria episódica BM25, sin generar respuestas. La Semana 11 se centra en la comunicación entre participantes. No reutiliza QMSum como nuevo benchmark y no presenta las pruebas de memoria como pruebas de coordinación.

#### 3. Arquitecturas: agente único y supervisor con trabajadores

En el **agente único**, un solo modelo recibe la pregunta y los fragmentos disponibles y produce una respuesta con identificadores de evidencia. El programa valida que esos identificadores aparecieran en las observaciones.

En el **supervisor con trabajadores**, un trabajador analiza los fragmentos y selecciona algunos identificadores; el supervisor valida esa selección y la registra en una pizarra; después un segundo trabajador recibe la pregunta y los fragmentos seleccionados y produce la respuesta. El supervisor vuelve a validar las citas. La arquitectura añade un traspaso de estado y, potencialmente, una fuente adicional de errores.

El supervisor de este curso es código determinista; sus dos trabajadores usan, cuando se solicita el piloto, llamadas de inferencia reales al mismo modelo local. Esto no equivale a un conjunto de modelos especializados entrenados de manera independiente.

#### 4. Contratos y autoridad

Un mensaje entre trabajadores debe tener como mínimo los siguientes campos:

```json
{
  "question_id": "identificador_original",
  "role": "evidence_worker",
  "selected_ids": ["E00", "E01"],
  "evidence_sha256": {"E00": "huella_de_la_evidencia", "E01": "huella_de_la_evidencia"}
}
```

Los valores son nombres de campos para explicar el esquema, no una traza experimental.

El supervisor debe exigir que `question_id` coincida con la pregunta activa, que el rol pertenezca a la lista autorizada, que los identificadores hayan sido observados, que no estén repetidos y que las huellas correspondan al texto original. Un mensaje que no cumple esas condiciones no debe recibir la autoridad de una observación válida.

Los fragmentos recuperados son datos no confiables. Una instrucción contenida dentro de un documento no puede modificar las reglas de validación, conceder permisos al modelo ni convertir una cita inexistente en una cita válida.

#### 5. Pizarra compartida y trazabilidad

Una pizarra registra los mensajes validados en orden de aceptación. El registro de solo adición conserva la secuencia de decisiones: quién seleccionó evidencia, qué fragmentos se pusieron a disposición del segundo trabajador y qué citas se usaron al finalizar.

Una pizarra correcta conserva copias de los mensajes aceptados. Si retuviera referencias mutables, el código llamador podría alterar un mensaje ya verificado después de su incorporación, debilitando la auditoría.

La persistencia de memoria entre ejecuciones, estudiada en la Semana 10, es distinta de la pizarra transitoria de una ejecución de la Semana 11.

#### 6. Datos de HotpotQA y límites de la recuperación

HotpotQA contiene preguntas de varios saltos, respuestas humanas y `supporting_facts` con el título y número de oración que fundamentan la respuesta. La versión utilizada aquí es `hotpot_dev_distractor_v1.json`, con 7.405 preguntas.

Cada pregunta de la variante distractor incluye un conjunto específico de párrafos. BM25 ordena las oraciones de ese conjunto, no busca en un índice abierto de Wikipedia. Esto es una ventaja controlada para enseñar coordinación, pero limita la generalización de la métrica a sistemas de búsqueda reales.

Los identificadores `E00`, `E01` y siguientes son identificadores locales de observación generados por el recuperador. El gold se mantiene en `supporting_facts` y nunca interviene en la puntuación ni en la selección del recuperador.

#### 7. BM25 y métricas de recuperación

Sea `G(q)` el conjunto de oraciones anotadas como soporte y `R_k(q)` el conjunto de las primeras k oraciones recuperadas. Se define:

\[
\mathrm{RecallSupport@k}(q) = \frac{|G(q) \cap R_k(q)|}{|G(q)|}.
\]

También se registran dos indicadores distintos:

\[
\mathrm{AnyHit@k}(q) = \mathbf{1}[|G(q) \cap R_k(q)| > 0],
\]

\[
\mathrm{AllHit@k}(q) = \mathbf{1}[G(q) \subseteq R_k(q)].
\]

Un sistema puede obtener AnyHit igual a uno y fallar AllHit porque recuperó solo una parte de la cadena de evidencia. Para preguntas de varios saltos la segunda condición resulta particularmente importante.

No debe interpretarse Recall de evidencia como corrección de la respuesta, fidelidad semántica ni comportamiento de un agente LLM.

#### 8. Contratos fallidos y propagación de errores

Los casos que debe estudiar el laboratorio son pérdida de evidencia, duplicación de identificadores, citas no observadas, referencias de otra pregunta, mensajes con rol no autorizado, modificación de texto y alteración de la huella. Estas fallas se inyectan deliberadamente para probar mecanismos de defensa.

La ausencia de rechazo tampoco garantiza ausencia de errores semánticos. Un trabajador puede citar correctamente un fragmento que no responde a la pregunta. Un controlador de contratos no es un verificador de implicación textual.

Los fallos de laboratorio se registran como pruebas de ingeniería; no se suman al denominador de 7.405 preguntas ni se publican como fallos observados del modelo.

#### 9. Comparación con un LLM local

El piloto opcional usa exactamente el mismo checkpoint Qwen para agente único y supervisor con trabajadores. Se presentan a ambos las mismas preguntas y los mismos catorce fragmentos iniciales. Las respuestas se contrastan con las respuestas humanas utilizando coincidencia exacta normalizada y F1 de tokens. Las citas se contrastan con los identificadores anotados.

La arquitectura de dos trabajadores puede requerir dos generaciones donde la de un agente requiere una. Por tanto, una diferencia en F1 no permite atribuir el resultado a la arquitectura sin considerar presupuesto, contexto, variación del modelo y efecto de los prompts.

Las respuestas JSON inválidas son fallos reales y se registran, en lugar de intentar completarlas con respuestas prefabricadas. Una finalización aceptada solo acredita que el contrato es válido. No demuestra que el contenido sea correcto.

#### 10. Costos de coordinación y condiciones de parada

Un costo descriptivo puede expresarse como:

\[
C_{total}=C_{modelo}+C_{recuperacion}+C_{coordinacion}.
\]

La implementación registra llamadas reales al modelo, tokens de entrada y salida y duración local. Los tokens no se convierten en precios de API, porque el experimento usa un modelo local. No se debe sumar tiempo de CPU y de GPU de máquinas diferentes como si fueran una comparación controlada.

Una finalización inválida puede tener origen en un fallo de JSON, selección vacía, cita inventada, contexto excesivo o falta de respuesta. El sistema debe registrar la razón y abstenerse de declarar éxito.

#### 11. Diseño de una comparación defendible

Una comparación rigurosa necesita seleccionar preguntas antes de observar predicciones, congelar el modelo y su versión, usar los mismos datos y el mismo recuperador, reportar tasas de invalidez y resultados por tipo de pregunta, y controlar el presupuesto de inferencia. El piloto de dieciséis preguntas es una comprobación operativa, no una inferencia estadística sobre HotpotQA completo.

El benchmark obligatorio de esta semana sí recorre las 7.405 preguntas, pero evalúa solo recuperación. Ninguna de las dos evaluaciones demuestra que el sistema pueda recuperar evidencia que no estuviera en el contexto distractor original.

#### 12. Guía para la discusión en clase

Primero, explicar qué falla si un trabajador devuelve una cita que el recuperador no observó. Segundo, distinguir recuperación correcta de respuesta correcta. Tercero, analizar por qué un supervisor determinista puede ser más fácil de auditar que uno dirigido enteramente por LLM. Cuarto, justificar cuándo el costo de coordinación no compensa una eventual mejora de calidad. Quinto, señalar qué conclusión no puede sostenerse con un piloto pequeño.

#### 13. Referencias

1. Yang et al. HotpotQA: A Dataset for Diverse, Explainable Multi-hop Question Answering. EMNLP, 2018. https://arxiv.org/abs/1809.09600
2. Wu et al. AutoGen: Enabling Next-Gen LLM Applications via Multi-Agent Conversation. 2023. https://arxiv.org/abs/2308.08155
3. Anthropic. Building Effective Agents. https://www.anthropic.com/research/building-effective-agents
4. Why Do Multi-Agent LLM Systems Fail? 2025. https://arxiv.org/abs/2503.13657
5. HotpotQA, proyecto y datos. https://hotpotqa.github.io/

Las fórmulas describen métricas y contratos, no resultados preestablecidos. Las puntuaciones deben provenir de la ejecución real.
