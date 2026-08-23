### CC0F4 - TOPICOS DE CIENCIA DE LA COMPUTACION I

Repositorio público del curso **CC0F4 - TOPICOS DE CIENCIA DE LA COMPUTACION I**.

**Tema del periodo 2026-2:** Sistemas de IA con Agentes y Recuperación Multimodal.

Este curso estudia, con un enfoque de Ciencia de la Computación, cómo diseñar, implementar y evaluar sistemas contemporáneos de inteligencia artificial que combinan modelos fundacionales, contexto, recuperación de información, herramientas, estado, memoria, agentes y multimodalidad.

El énfasis no está solamente en utilizar modelos de lenguaje o frameworks disponibles, sino en **comprender los componentes del sistema, construir líneas base, formular experimentos, medir resultados, analizar errores y defender técnicamente las decisiones de diseño**.

> **Lenguaje principal del curso:** Python 3.x  
> **Entorno principal:** Jupyter Notebook / JupyterLab  
> **Periodo académico:** 2026-2  
> **Créditos:** 4  
> **Horas semanales:** 6 horas  
> **Teoría:** lunes de 6:00 p. m. a 8:00 p. m.  
> **Laboratorio:** jueves de 4:00 p. m. a 8:00 p. m.

#### Descripción del curso

Asignatura teórico-práctica orientada al diseño, implementación, evaluación y sustentación de **sistemas de IA compuestos**.

El curso parte de los fundamentos de transformers y modelos de lenguaje para avanzar hacia:

- inferencia autoregresiva
- generación estructurada
- ingeniería de contexto
- embeddings y recuperación de información
- RAG
- herramientas tipadas
- workflows
- agentes
- estado y memoria
- coordinación multiagente
- evaluación de agentes
- recuperación multimodal
- generación condicionada por evidencia

Los frameworks y tecnologías de rápida evolución pueden emplearse como ejemplos, pero no constituyen el objeto central del curso.

La intención es estudiar principios que continúen siendo relevantes aunque cambien los modelos, APIs, librerías o protocolos utilizados para implementarlos.

#### Idea central del curso

Un modelo fundacional no constituye por sí solo un sistema completo.

El curso estudia progresivamente los siguientes componentes:

- modelo
- contexto
- retrieval
- herramientas
- estado y memoria
- agentes
- evaluación
- multimodalidad

Todo el recorrido está atravesado por:

- baseline
- hipótesis
- experimento
- métrica
- resultado
- análisis de error
- conclusión

Una ejecución correcta no constituye, por sí sola, evidencia de que un sistema sea mejor.

#### Competencia del curso

Diseñar, implementar, evaluar y sustentar sistemas contemporáneos de inteligencia artificial compuestos, justificando con rigor conceptual y evidencia experimental las decisiones relacionadas con representación, contexto, recuperación, herramientas, control, memoria, evaluación y multimodalidad.

El estudiante deberá ser capaz de distinguir cuándo una arquitectura más compleja aporta valor frente a una línea base más simple.

#### Resultados de aprendizaje

Al finalizar el curso, el estudiante deberá ser capaz de:

1. Explicar la mecánica de un modelo transformer causal desde tokenización y embeddings hasta logits, decodificación, ventana de contexto y KV cache.
2. Diseñar interacciones robustas con modelos mediante instrucciones, generación estructurada, validación de esquemas y administración explícita del contexto.
3. Implementar y comparar recuperación léxica, densa, híbrida y con reranking.
4. Construir sistemas RAG evaluables sobre corpus controlados.
5. Diseñar herramientas tipadas y workflows con entradas, salidas y errores verificables.
6. Construir agentes con estado, memoria, planificación, verificación, criterios de parada y trazas auditables.
7. Comparar sistemas single-agent y multi-agent mediante métricas de desempeño, costo y complejidad.
8. Diseñar benchmarks pequeños y reproducibles para sistemas RAG y agentes.
9. Comparar graders deterministas, evaluación humana y LLM-as-Judge.
10. Implementar y evaluar recuperación multimodal mediante modelos contrastivos tipo CLIP.
11. Diseñar generación condicionada por evidencia y analizar grounding y alucinaciones.
12. Sustentar oralmente decisiones de arquitectura, resultados experimentales, ablaciones y análisis de errores.

#### Prerrequisitos esperados

Se asume que el estudiante llega con bases razonables en:

- programación en Python o capacidad para adaptarse rápidamente al lenguaje
- estructuras de datos y algoritmos
- álgebra lineal
- probabilidad básica
- aprendizaje automático
- redes neuronales
- fundamentos de inteligencia artificial
- programación concurrente y distribuida
- lectura de documentación técnica y artículos científicos

Durante la primera semana se realizará una **prueba diagnóstica de entrada** para identificar el nivel real del grupo y ajustar los repasos necesarios.

La prueba es diagnóstica y busca observar especialmente:

- programación
- razonamiento algorítmico
- álgebra lineal aplicada
- fundamentos de machine learning
- comprensión básica de transformers
- capacidad de análisis experimental

#### Enfoque metodológico

El curso adopta un enfoque de **ingeniería experimental de sistemas de IA**.

Cada semana combina:

- fundamentos conceptuales
- implementación
- experimentación
- métricas
- análisis de errores
- exposiciones técnicas
- defensa oral

Los lunes se priorizan principios relativamente estables. Los jueves esos principios se convierten en experimentos reproducibles.

La estructura mínima esperada de una práctica es:

```text
baseline
modificación
experimento
métrica
resultado
error analysis
conclusión
```

No se calificará principalmente la cantidad de código ni la sofisticación visual de una aplicación.

Se calificará la capacidad para responder preguntas como:

- ¿Cuál es la línea base?
- ¿Qué cambió?
- ¿Qué hipótesis se está probando?
- ¿Qué métrica corresponde a la pregunta?
- ¿Cuánto mejoró o empeoró?
- ¿Cuál fue el costo adicional?
- ¿Qué casos fallaron?
- ¿Qué evidencia respalda la conclusión?

#### Uso de herramientas de inteligencia artificial

Se permite utilizar herramientas de IA generativa durante el curso para:

- estudiar conceptos
- producir ejemplos
- programar
- depurar
- explorar alternativas
- generar variantes de prompts
- contrastar explicaciones
- apoyar la documentación

El uso de estas herramientas no reemplaza la comprensión del estudiante.

Toda entrega debe poder ser defendida oralmente.

Cuando corresponda, el estudiante deberá explicar:

- qué parte fue producida o sugerida por una herramienta
- cómo verificó el resultado
- qué errores encontró
- qué sugerencias rechazó
- qué decisiones técnicas tomó personalmente

#### Contenido general

#### Unidad I - Modelos fundacionales e interfaces estructuradas

- transformer causal
- embeddings
- queries, keys y values
- self-attention
- multi-head attention
- causal masking
- tokenización
- logits y softmax
- generación autoregresiva
- greedy decoding
- temperature
- top-k y top-p
- ventana de contexto
- KV cache
- prompting
- structured generation
- JSON Schema
- validación de salidas
- context engineering

#### Unidad II - Recuperación, contexto y RAG evaluable

- embeddings para retrieval
- similitud
- chunking
- vector stores
- dense retrieval
- BM25
- sparse retrieval
- recuperación híbrida
- fusión de rankings
- reranking
- cross-encoders
- RAG
- grounding
- evaluación de retrieval
- Recall@k
- MRR
- nDCG
- evaluación de generación
- benchmarks
- ablaciones
- análisis de errores

#### Unidad III - Herramientas, agentes y evaluación

- tool calling
- contratos de herramientas
- entradas y salidas estructuradas
- validación
- retries
- timeouts
- workflows
- estado
- control loops
- planificación
- ReAct
- verificación
- guardrails básicos
- criterios de parada
- memoria de trabajo
- memoria episódica
- memoria semántica
- trazas
- auditabilidad
- multiagentes
- supervisor-worker
- handoffs
- blackboard
- optimización en tiempo de inferencia
- evaluación de agentes
- LLM-as-Judge
- pass@k
- pass^k

#### Unidad IV - Recuperación y generación multimodal

- aprendizaje contrastivo
- dual encoders
- CLIP y OpenCLIP
- embeddings texto-imagen
- similitud multimodal
- recuperación image-to-text
- recuperación text-to-image
- R@1, R@5 y R@10
- MRR
- hard negatives
- error analysis multimodal
- multimodal RAG
- generación grounded
- trazabilidad de evidencia
- análisis de afirmaciones no soportadas
- ablaciones multimodales

#### Programación semanal

| Semana | Tema central | Resultado esperado |
|---|---|---|
| 1 | Presentación del curso. De modelos a sistemas de IA compuestos. Transformer, atención, causalidad, tokens y modelo fundacional. Prueba diagnóstica de entrada | Distingue un modelo fundacional de un sistema compuesto y comprende el estándar experimental del curso. |
| 2 | LLMs para construcción de sistemas: embeddings, logits, softmax, decoding, ventana de contexto y KV cache | Explica cómo se genera un token y relaciona contexto y KV cache con costo y latencia. |
| 3 | Prompting, structured generation, JSON Schema, validación y context engineering | Diseña una interfaz estructurada entre un LLM y un programa. |
| 4 | Embeddings para retrieval, chunking, similitud, vector stores, dense retrieval y FAISS | Construye un retriever denso y evalúa decisiones de representación y chunking. |
| 5 | BM25, recuperación híbrida, reranking y RAG | Compara experimentalmente retrievers y demuestra el efecto de un reranker. |
| 6 | Tools, function calling, contratos, validación, errores, retries y timeouts | Modela una herramienta como una interfaz verificable para un sistema con LLM. |
| 7 | Evaluación de retrieval y RAG: benchmark, Recall@k, MRR, nDCG, grounding y error analysis | Construye un benchmark reproducible y separa errores de retrieval, contexto y generación. |
| 8 | Examen parcial | Integra modelos fundacionales, structured generation, contexto, retrieval, RAG, tools y evaluación básica. |
| 9 | Workflows, agentes, planificación, ReAct, verificación y criterios de parada | Distingue workflow y agente y justifica cuándo la autonomía aporta valor. |
| 10 | Estado y memoria: working, episodic, semantic y external memory | Evalúa mediante ablaciones cuándo la memoria mejora o degrada un sistema. |
| 11 | Sistemas multiagente, supervisor-worker, handoffs, blackboard y análisis de trayectorias | Analiza coordinación y propagación de errores en sistemas multiagente. |
| 12 | Optimización: prompt, contexto, retrieval, tools, test-time compute, SFT, LoRA y QLoRA | Compara distintas formas de mejorar un sistema mediante una frontera calidad-costo. |
| 13 | Evaluación de agentes, graders, LLM-as-Judge, pass@k, pass^k, sesgos y desacuerdo | Diseña evaluaciones reproducibles y analiza limitaciones de evaluadores automáticos. |
| 14 | Aprendizaje contrastivo, CLIP/OpenCLIP y recuperación multimodal | Evalúa retrieval texto-imagen mediante métricas de ranking y hard negatives. |
| 15 | Multimodal RAG, generación grounded, trazabilidad, integración y demos finales | Integra recuperación multimodal y generación condicionada por evidencia. |
| 16 | Examen final | Integra modelos, contexto, retrieval, herramientas, estado, agentes, evaluación y multimodalidad. |

#### Exposiciones técnicas

Durante parte de los laboratorios de los jueves se desarrollarán exposiciones breves sobre temas contemporáneos que complementan el núcleo estable del curso.

El tiempo total destinado a exposiciones no deberá superar las dos horas de una sesión de laboratorio.

Entre los temas posibles se encuentran:

- atención eficiente y contexto largo
- FlashAttention
- GQA
- late interaction
- ColBERT
- GraphRAG
- structured generation
- constrained decoding
- MCP
- interoperabilidad entre agentes y herramientas
- memoria persistente
- sistemas multiagente
- automatic prompt optimization
- test-time compute
- LLM-as-Judge
- modelos multimodales modernos
- VLM
- Document AI
- multimodal agents

Cada exposición deberá incluir como mínimo:

1. problema abordado
2. fuente primaria
3. idea fundamental
4. arquitectura o método
5. limitaciones
6. pequeño experimento, reproducción o demostración
7. análisis crítico
8. conclusión sobre cuándo usar y cuándo no usar el enfoque

Las exposiciones no deben limitarse a resumir documentación o producir diapositivas mediante herramientas generativas.

#### Proyecto integrador

El proyecto del curso desarrolla progresivamente un sistema de IA compuesto.

No se exige construir un chatbot.

Son válidos, entre otros:

- sistemas de consulta documental
- asistentes para literatura científica
- sistemas para análisis de código
- agentes sobre datos
- asistentes educativos
- herramientas de análisis técnico
- sistemas multimodales
- aplicaciones con recuperación de evidencia

El proyecto deberá contener:

```text
problema
baseline
arquitectura propuesta
dataset o benchmark
experimentos
métricas
ablaciones
failure analysis
conclusiones
```

La interfaz gráfica es secundaria.

La calidad del proyecto depende principalmente de la solidez de la pregunta experimental, la implementación, las métricas, la reproducibilidad y la defensa técnica.

#### Hitos del proyecto

| Semana | Hito |
|---|---|
| 5 | Propuesta de una página: problema, corpus o entorno, baseline, métrica e hipótesis |
| 10 | Midpoint demo con baseline ejecutable, resultado preliminar y al menos un fallo reproducible |
| 13 | Evaluación formal del componente agéntico o equivalente |
| 15 | Sistema final, ablación, error analysis, demostración y defensa |

#### Sistema de evaluación

El curso considera:

- **5 prácticas calificadas**
- **1 examen parcial**
- **1 examen final**

Las prácticas corresponden a:

```text
C1 = inferencia y structured generation
C2 = retrieval y RAG evaluable
C3 = tools y agentes
C4 = evaluación de agentes
C5 = integración multimodal y proyecto
```

Se elimina la menor nota de las cinco prácticas:

```text
PP = promedio de las cuatro mejores notas entre C1, C2, C3, C4 y C5
PF = (PP + EP + EF) / 3
```

Criterios generales para las prácticas:

- Sustentación oral individual o verificación oral focalizada: **60%**
- Implementación, corrección técnica y reproducibilidad: **10%**
- Análisis experimental, métricas, interpretación y discusión de errores: **20%**
- Claridad expositiva, organización de evidencia y reporte técnico: **10%**

La sustentación oral es parte central de la evaluación.

Una práctica no obtiene una calificación alta solamente porque el notebook ejecuta correctamente.

#### Estándar experimental esperado

Todo experimento relevante debe identificar, cuando corresponda:

- pregunta
- hipótesis
- línea base
- variable modificada
- datos
- métrica
- configuración
- resultado
- costo
- errores
- limitaciones
- conclusión

Ejemplo:

```text
Baseline: dense retrieval
Modificación: dense retrieval + BM25
Evaluación: Recall@5 y MRR
Resultado: comparación cuantitativa
Análisis: errores observados
Conclusión: decisión respaldada por evidencia
```

Se espera evitar comparaciones donde cambien simultáneamente múltiples variables sin control.

#### Reproducibilidad

Los laboratorios y proyectos deberán registrar información suficiente para reconstruir los experimentos.

Cuando corresponda se deberá registrar:

- modelo
- versión o checkpoint
- dataset
- partición evaluada
- seed
- parámetros de generación
- prompts relevantes
- configuración de retrieval
- top-k
- métricas
- latencia
- hardware relevante
- errores observados

La reproducibilidad forma parte de la calidad técnica del trabajo.

#### Bibliografía principal

- **Chip Huyen** - *AI Engineering: Building Applications with Foundation Models*. O'Reilly Media, 2025.
- **Suhas Pai** - *Designing Large Language Model Applications: A Holistic Approach to LLMs*. O'Reilly Media, 2025.
- **Jay Alammar y Maarten Grootendorst** - *Hands-On Large Language Models: Language Understanding and Generation*. O'Reilly Media, 2024.
- **Anjanava Biswas y Wrick Talukdar** - *Building Agentic AI Systems*. Packt Publishing, 2025.
- **Vaswani et al.** - *Attention Is All You Need*. NeurIPS, 2017.
- **Lewis et al.** - *Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks*. NeurIPS, 2020.
- **Yao et al.** - *ReAct: Synergizing Reasoning and Acting in Language Models*. ICLR, 2023.
- **Radford et al.** - *Learning Transferable Visual Models From Natural Language Supervision*. ICML, 2021.

La documentación técnica y los artículos de frontera se actualizarán durante cada periodo académico sin modificar los principios fundamentales del curso.

#### Herramientas y entorno

El curso utilizará principalmente:

- Python 3.x
- PyTorch
- Hugging Face Transformers
- Hugging Face Datasets
- sentence-transformers
- FAISS
- rank-bm25
- Pydantic o JSON Schema
- OpenCLIP
- Jupyter Notebook / JupyterLab

Frameworks como LangChain, LangGraph, smolagents o protocolos como MCP pueden utilizarse como ejemplos o extensiones.

No se evaluará la memorización de APIs ni el uso mecánico de frameworks.

#### Recomendaciones de uso para estudiantes

1. Revisar el `README.md` general antes de iniciar el curso.
2. Leer el material correspondiente antes de cada sesión.
3. Ejecutar los notebooks base antes del laboratorio cuando se indique.
4. Mantener registro de configuraciones y resultados experimentales.
5. No modificar simultáneamente varias variables cuando se busca atribuir una mejora.
6. Conservar líneas base durante todo el desarrollo.
7. Analizar los casos donde el sistema falla, no únicamente los promedios.
8. Prepararse para defender oralmente cualquier parte de una entrega.
9. Utilizar herramientas de IA como apoyo, no como sustituto de comprensión.
10. Consultar papers y documentación primaria para afirmaciones técnicas importantes.

#### Estándar esperado de implementación

En este curso se espera que el código:

- tenga responsabilidades claramente separadas
- utilice entradas y salidas explícitas
- valide datos cuando corresponda
- registre errores y estados relevantes
- permita reproducir experimentos
- diferencie código experimental de infraestructura accesoria
- facilite la comparación contra una línea base
- produzca resultados que puedan analizarse cuantitativamente

El objetivo no es producir la arquitectura más compleja.

El objetivo es construir el **sistema más simple que permita responder rigurosamente la pregunta planteada**.

#### Defensa oral

El estudiante debe poder explicar, entre otras cosas:

- por qué eligió un modelo
- por qué utilizó determinada representación
- qué constituye su baseline
- por qué escogió una métrica
- qué ocurre al retirar un componente
- qué parte del resultado depende del prompt
- qué ocurre si una tool falla
- cómo termina un agente
- qué información mantiene la memoria
- cuánto cuesta agregar otro agente
- qué error aparece con mayor frecuencia
- qué afirmación puede respaldar con los experimentos realizados

No poder explicar una parte central de una implementación afecta directamente la evaluación, aunque el código funcione.

#### Integridad académica

Este repositorio puede contener notebooks, ejemplos, esqueletos, datasets, evaluaciones públicas y código de referencia.

La disponibilidad del material no reemplaza el trabajo intelectual del estudiante.

Se permite utilizar asistentes de programación y modelos generativos, pero el estudiante es responsable de:

- comprender el código entregado
- verificar afirmaciones
- revisar resultados
- reconocer fuentes
- detectar errores
- sustentar decisiones
- identificar limitaciones

Toda reutilización de código, ideas, textos o material externo debe realizarse con honestidad académica y comprensión efectiva.

#### Organización sugerida del repositorio

La organización sigue el patrón semanal usado en el repositorio MCC225, manteniendo la raíz pequeña y agregando material conforme avanza el curso.

```text
CC-0F4/
README.md
LICENSE
.gitignore
.gitattributes
Makefile
Semana1/
Semana2/
Semana3/
...
Semana16/
```

Cada semana puede contener solamente los elementos que realmente necesite:

```text
SemanaX/
README.md
CuadernoX-CC0F4.ipynb
ActividadX-CC0F4.md
Proyecto/
papers/
```

No se crea una carpeta de sílabo dentro del repositorio. Tampoco se exige que todas las semanas tengan la misma estructura.

La estructura debe mantenerse tan pequeña como resulte razonable.

#### Relación con cursos posteriores

CC0F4 introduce una perspectiva de sistemas de IA que conecta aprendizaje automático, recuperación de información, sistemas de software y evaluación experimental.

La base desarrollada es útil para asignaturas posteriores relacionadas con:

- sistemas distribuidos para IA
- computación eficiente
- serving de modelos
- seguridad de sistemas de IA
- confiabilidad
- evaluación adversarial
- aprendizaje multimodal
- agentes
- investigación en sistemas inteligentes

El curso no pretende agotar ninguno de esos campos.

Su función es proporcionar una base rigurosa para comprender cómo se integran sus componentes dentro de un sistema contemporáneo de inteligencia artificial.

#### Principio del curso

El objetivo final puede resumirse en cinco acciones:

```text
construir
medir
comparar
analizar
defender
```

**CC0F4** no evalúa quién puede producir el sistema más llamativo, sino quién puede **explicar qué construyó, por qué lo construyó de esa manera, cómo sabe si funciona, qué costo tiene, dónde falla y qué evidencia respalda sus conclusiones**.
