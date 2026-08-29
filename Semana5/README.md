### Semana 5 - BM25, recuperación híbrida, reranking y RAG

#### Propósito

Semana 4 respondió:

```text
¿cómo recuperar automáticamente evidencia relevante?
        ->
embeddings -> segmentación -> similitud -> FAISS -> top-k
```

Semana 5 mantiene el mismo corpus, las mismas consultas, los mismos qrels y la misma segmentación de referencia, pero añade señales y etapas de recuperación:

```text
                         +-> BM25 ----------------+
                         |                        |
consulta ----------------+                        +-> RRF -> Cross-Encoder -> contexto -> LLM
                         |                        |
                         +-> E5 + FAISS ----------+
```

La pregunta experimental es:

> ¿Cómo cambia la recuperación de evidencia cuando se compara BM25, recuperación densa, recuperación híbrida mediante RRF y recuperación híbrida con reranking, manteniendo constantes corpus, consultas, qrels, segmentación y top-k?.

#### Continuidad con Semana 4

Se reutiliza el benchmark de:

```text
Semana4/datos/
```

con:

```text
12 documentos
72 passages
24 consultas
qrels definidos sobre passage_id
```

La condición de segmentación queda fija en:

```text
target_words = 180
overlap_passages = 1
```

La recuperación densa conserva:

```text
modelo = intfloat/multilingual-e5-small
normalización = L2
similitud = producto interno
índice = FAISS IndexFlatIP
```

Por tanto, Semana 5 no vuelve a estudiar qué tamaño de fragmento es mejor. Esa variable ya fue estudiada en Semana 4.

#### Condiciones del experimento

```text
A = BM25
B = dense E5 + FAISS
C = BM25 + dense + RRF
D = BM25 + dense + RRF + Cross-Encoder
```

Se fija:

```text
candidate_depth = 10
top-k in {1, 3, 5}
RRF rank_constant = 60
```

Métrica principal:

```text
mean Recall@3
```

También se reportan:

```text
Recall@1
Recall@5
```

La evaluación exhaustiva mediante MRR, nDCG, grounding y análisis sistemático de RAG queda para Semana 7.

Nota metodológica sobre atribución:

```text
BM25 vs dense
-> comparación de familias de recuperación

dense vs hybrid
-> incorpora BM25 y la fusión; no aísla el efecto de un único componente

hybrid vs hybrid + reranker
-> comparación incremental que aísla de forma más limpia el efecto del reranker
```

#### Reranker canónico

```text
cross-encoder/mmarco-mMiniLMv2-L12-H384-v1
```

El Cross-Encoder se aplica solo al conjunto pequeño de candidatos producido por la fusión. No se utiliza para puntuar todo el corpus.

#### Generador canónico para la demostración RAG

Se reutiliza el modelo pequeño de Semana 3:

```text
Qwen/Qwen2.5-0.5B-Instruct
```

El objetivo no es comparar modelos generativos. Se mantiene fijo para mostrar la transición:

```text
ranking -> evidencia -> contexto -> LLM
```

Una mejora de Recall@k no demuestra automáticamente una mejora de calidad final de RAG.


#### Ejecución sin descargar modelos

El cuaderno permite validar estructura, segmentación, BM25, fusión, métricas y flujo de RAG mediante sustitutos deterministas:

```bash
CC0F4_RUN_REAL_RETRIEVAL=0 \
CC0F4_RUN_REAL_RERANKER=0 \
CC0F4_RUN_REAL_LLM=0 \
make execute-cuaderno5
```

Los resultados del modo offline sirven únicamente para validar software y no constituyen evidencia del experimento canónico.

#### Entorno

Semana 5 utiliza el entorno global del curso. El `requirements.txt` de la raíz ya contiene:

```text
sentence-transformers
faiss-cpu
rank-bm25
transformers
```

No se crea un entorno por semana.

#### Alcance deliberado

Semana 5 incluye:

```text
BM25
recuperación dispersa
recuperación densa heredada de Semana 4
RRF
recuperación híbrida
Cross-Encoder
retrieve-then-rerank
construcción mínima de contexto
RAG mínimo
Recall@k para comparación controlada
```

Semana 5 no convierte todavía en objetivo principal:

```text
MRR
nDCG
RAGAS
LLM-as-Judge
grounding exhaustivo
GraphRAG
agentic RAG
LangChain
LangGraph
MCP
agentes
```

#### Criterio de cierre

La semana está cerrada cuando el estudiante puede defender:

```text
sparse retrieval != dense retrieval

BM25 score != dense score

fusionar rankings != promediar scores sin calibración

retriever != reranker

bi-encoder != cross-encoder

candidate generation != final ranking

mejor Recall@k != mejor respuesta RAG necesariamente

RAG = retrieval + contexto + generación
```

y explicar el pipeline:

```text
BM25 -------+
             +-> RRF -> Cross-Encoder -> top-k -> contexto -> LLM
E5 + FAISS --+
```

#### Puente a la Semana 6

Semana 5 termina con un sistema donde el LLM recibe contexto recuperado. Semana 6 cambia el tipo de capacidad externa:

```text
Semana 5
LLM + evidencia recuperada
        ->
Semana 6
LLM + herramientas con contratos, validación, retries y timeouts
```

#### Evidencia empírica adicional

El cuaderno registra:

```text
latencia media y p95
bootstrap pareado de Recall@3
closed-book vs RAG
auditoría de chunk_id citados
control negativo sin evidencia esperada
manifiesto reproducible de corrida
```

Estas mediciones complementan Recall@k sin adelantar la evaluación completa de grounding, MRR y nDCG reservada para Semana 7.

El benchmark de Semana 4 se conserva sin modificaciones post hoc. No se asume que haya sido diseñado como benchmark adversarial de distractores léxicos duros.
