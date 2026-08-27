### Semana 4 - Embeddings, chunking y dense retrieval

#### Propósito

Semana 3 convirtió la generación probabilística en una interfaz verificable y mostró que la selección de contexto afecta al sistema.

Semana 4 cambia la pregunta:

```text
Semana 3
¿qué contexto entregamos al modelo?

        ->

Semana 4
¿cómo recuperamos automáticamente
el contexto relevante?
```

La cadena conceptual es:

```text
documentos -> passages -> chunks -> embeddings -> similitud -> índice -> ranking -> top-k
```

No se construye todavía un sistema RAG.


#### Experimento principal

Pregunta:

> ¿Cómo afecta el tamaño objetivo de los chunks a la recuperación de evidencia relevante cuando las demás variables permanecen fijas?

Baseline:

```text
target_words = 180
```

Variantes:

```text
small = 80
large = 320
```

Variables fijas:

```text
corpus
queries
qrels
overlap_passages = 1
embedding model
normalización L2
similarity = inner product
index = IndexFlatIP
top-k
```

Métricas:

```text
Recall@1
Recall@3
Recall@5
```

La métrica principal para discusión es:

```text
mean Recall@3
```

#### Modelo canónico

```text
intfloat/multilingual-e5-small
```

Se usa por ser multilingüe, compacto y estar orientado a retrieval. Produce embeddings de 384 dimensiones y admite hasta 512 tokens. El cuaderno utiliza los prefijos `query:` y `passage:` y el laboratorio verifica que ninguna condición introduzca truncación.

#### Ejecución sin descarga

Para verificar el cuaderno del lunes sin descargar el encoder:

```bash
CC0F4_RUN_REAL_RETRIEVAL=0 make execute-cuaderno4
```

Para validar el laboratorio:

```bash
CC0F4_RUN_REAL_RETRIEVAL=0 \
jupyter nbconvert \
  --to notebook \
  --execute Semana4/Laboratorio4-CC-0F4.ipynb \
  --ExecutePreprocessor.timeout=600 \
  --output /tmp/Laboratorio4-validado.ipynb
```

El modo offline usa TF-IDF + SVD únicamente para validar el software. Sus métricas no son evidencia del experimento canónico.

#### Entorno

Semana 4 utiliza el entorno global del curso. No crea un `requirements.txt` propio.

El `requirements.txt` raíz ya contiene `sentence-transformers` y `faiss-cpu`.

Desde la raíz:

```bash
make check-semana4
make execute-cuaderno4
```

#### Alcance deliberado

Semana 4 incluye:

```text
embeddings
chunking
cosine / inner product
exact dense retrieval
FAISS
top-k
Recall@k mínimo
```

Semana 4 no incluye:

```text
BM25
hybrid retrieval
cross-encoder reranking
RAG generation
LangChain
Qdrant
GraphRAG
agents
```

#### Criterio de cierre

El estudiante debe poder defender:

```text
texto -> embedding -> ranking

cosine(normalizados)
==
inner product(normalizados)

documento != chunk

IndexFlatIP == exact search

index != vector store != retriever

más contexto por chunk != mejor retrieval necesariamente

resultado agregado != análisis de errores
```

y presentar:

```text
small
vs
baseline
vs
large
    ->
Recall@k
    ->
error analysis
    ->
conclusión limitada
```

#### Puente a Semana 5

```text
Semana 4
dense retrieval
      |
      v
top-k evidence

Semana 5
BM25 + dense
      |
      v
fusion
      |
      v
reranking
      |
      v
context
      |
      v
LLM
```
