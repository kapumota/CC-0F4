### Attention Is All You Need
#### Lectura crítica guiada para CC-0F4

**Referencia:** Vaswani, A., Shazeer, N., Parmar, N., Uszkoreit, J., Jones, L., Gomez, A. N., Kaiser, L., & Polosukhin, I. (2017). *Attention Is All You Need*. Advances in Neural Information Processing Systems, 30.

**Fuente primaria:** https://arxiv.org/abs/1706.03762

#### Convención terminológica

En esta lectura se emplea español cuando existe una traducción técnica clara, pero se conservan algunos términos en inglés porque aparecen así en código y literatura: `head`, `embedding`, `softmax`, `dropout`, `query`, `key` y `value`.

| Término | Uso en esta lectura |
|---|---|
| self-attention | autoatención |
| cross-attention | atención cruzada |
| scaled dot-product attention | atención de producto punto escalado |
| causal mask | máscara causal |
| positional encoding | codificación posicional |
| residual connection | conexión residual |
| LayerNorm | normalización por capas |
| position-wise feed-forward network | red feed-forward por posición |
| baseline | línea base |
| ablation | ablación |

`Query`, `key` y `value` se mantienen cuando se habla de código; se interpretan respectivamente como consulta, clave y valor.

#### 1. Problema

Antes del Transformer, los sistemas de transducción de secuencias más competitivos se apoyaban principalmente en redes recurrentes o convolucionales dentro de arquitecturas encoder-decoder. En una red recurrente:

$$
h_t=f(h_{t-1},x_t),
$$

por lo que el cálculo de una posición depende del estado anterior. Esto introduce una cadena de operaciones secuenciales que limita el paralelismo dentro de un ejemplo y alarga el camino que debe recorrer la información entre posiciones distantes.

Los modelos convolucionales permiten mayor paralelismo, pero las posiciones alejadas se conectan mediante varias capas o kernels de mayor tamaño.

El paper plantea una pregunta arquitectónica:

> ¿Puede una arquitectura para secuencias prescindir de recurrencia y convolución como mecanismo principal y utilizar atención para conectar directamente las posiciones?

La propuesta es el **Transformer**.

La contribución no consiste simplemente en "inventar attention". Los mecanismos de attention ya existían. El cambio importante es hacer de la atención el mecanismo estructural principal del modelo.

#### 2. Arquitectura original

El Transformer de 2017 es **encoder-decoder**. No debe confundirse con los LLM decoder-only modernos.

El encoder transforma:

$$
(x_1,\ldots,x_n)
$$

en:

$$
(z_1,\ldots,z_n).
$$

El decoder genera autoregresivamente:

$P(y_1,\ldots,y_m\mid x) =\prod_{t=1}^{m}P(y_t\mid y_{<t},x).$

El modelo base utiliza:

$$
N=6,
\qquad
d_{\mathrm{model}}=512.
$$

Una vista simplificada es:

```text
tokens fuente
  ->
embeddings + posición
  ->
encoder x 6
  ->
representaciones de la fuente
  ->
decoder x 6
  ->
proyección al vocabulario
  ->
softmax
  ->
token de salida
```

El encoder combina autoatención multi-head y una red feed-forward por posición. El decoder añade autoatención causal y atención cruzada sobre las representaciones del encoder.

#### 3. Query, key y value

Para una representación $X$:

$$
Q=XW_Q,\qquad K=XW_K,\qquad V=XW_V.
$$

Una interpretación operacional es:

- **query:** representación con la que una posición busca información;
- **key:** representación contra la que se calcula compatibilidad;
- **value:** contenido que se combina según los pesos resultantes.

No son preguntas, claves o valores literales en lenguaje natural. Son proyecciones aprendidas.

El flujo es:

```text
X
  ->
Q, K, V
  ->
QK^T
  ->
scaling
  ->
máscara, si corresponde
  ->
softmax
  ->
pesos de atención
  ->
AV
```

#### 4. Atención de producto punto escalado

La ecuación central es:

$\mathrm{Attention}(Q,K,V) =\mathrm{softmax}\left(\frac{QK^\top}{\sqrt{d_k}}\right)V.$

Si:

$$
Q\in\mathbb{R}^{T_q\times d_k},
\qquad
K\in\mathbb{R}^{T_k\times d_k},
$$

entonces:

$$
QK^\top\in\mathbb{R}^{T_q\times T_k}.
$$

Cada fila corresponde a una query y cada columna a una key.

En autoatención:

$$
T_q=T_k=T,
$$

por lo que la matriz es:

$$
T\times T.
$$

Esta forma cuadrada anticipa una limitación importante: la atención densa escala cuadráticamente con la longitud de secuencia.

#### 5. Por qué se divide por $\sqrt{d_k}$

El producto punto es:

$q\cdot k=\sum_{i=1}^{d_k}q_i k_i.$

Si sus componentes tienen media cero y varianza uno, aproximadamente:

$$
\mathrm{Var}(q\cdot k)=d_k.
$$

Por ello se utiliza:

$$
\frac{q\cdot k}{\sqrt{d_k}}.
$$

El objetivo es controlar la magnitud de los logits antes de `softmax`.

Debe distinguirse:

```text
1/sqrt(d_k)
  -> controla escala

máscara causal
  -> controla acceso

softmax
  -> normaliza pesos
```

El scaling **no introduce causalidad**.

#### 6. Softmax y combinación de values

Los pesos son:

$A=\mathrm{softmax}\left(\frac{QK^\top}{\sqrt{d_k}}\right).$

Para cada query:

$$
\sum_j A_{ij}=1.
$$

La salida es:

$$
O=AV.
$$

Por tanto:

```text
QK^T
  -> compatibilidad

softmax
  -> distribución de pesos

V
  -> contenido combinado

AV
  -> representación contextualizada
```

Una invariante útil es:

$E_{\mathrm{norm}}=\max_i\left|\sum_j A_{ij}-1\right|.$

Si la normalización es correcta:

$$
E_{\mathrm{norm}}\approx 0.
$$

#### 7. Máscara causal

En el decoder, la posición $i$ no puede utilizar posiciones futuras $j>i$.

$\mathrm{Attention}_{\mathrm{causal}}(Q,K,V)=\mathrm{softmax}\left(\frac{QK^\top}{\sqrt{d_k}}+M\right)V,$

con:

$$
M_{ij}=
\begin{cases}
0, & j\le i,\\
-\infty, & j>i.
\end{cases}
$$

Como:

$$
e^{-\infty}=0,
$$

se obtiene:

$$
A_{ij}\approx 0
\qquad
\text{para }j>i.
$$

La causalidad proviene de la **máscara aplicada antes de `softmax`**.

Una métrica directa es:

$L_{\mathrm{future}}=\max_{j>i}A_{ij}.$

En atención causal correcta:

$$
L_{\mathrm{future}}\approx 0.
$$

Es posible que:

$$
E_{\mathrm{norm}}\approx 0
$$

mientras:

$$
L_{\mathrm{future}}>0.
$$

Por ejemplo, full attention puede estar perfectamente normalizada y seguir permitiendo acceso al futuro.

#### 8. Paralelismo y generación autoregresiva

Durante entrenamiento, toda la secuencia objetivo es conocida y las posiciones pueden procesarse en paralelo, siempre que la máscara bloquee el futuro.

Durante inferencia autoregresiva, los tokens futuros todavía no existen:

```text
prefijo
  ->
nuevo token
  ->
prefijo ampliado
  ->
nuevo token
```

Por ello:

> Paralelismo de cómputo durante entrenamiento no significa acceso al futuro.

Y también:

> Eliminar recurrencia del bloque Transformer no elimina la secuencialidad de la generación autoregresiva.

#### 9. Multi-Head Attention

Cada head se define como:

$\mathrm{head}_i =\mathrm{Attention}\left(QW_i^Q,KW_i^K,VW_i^V\right).$

Luego:

$\mathrm{MultiHead}(Q,K,V)=\mathrm{Concat}\left(\mathrm{head}_1,\ldots,\mathrm{head}_h\right)W^O.$

En el baseline:

$$
h=8,
\qquad
d_k=d_v=64,
$$

porque:

$\frac{d_{\mathrm{model}}}{h}=\frac{512}{8}=64.$

Cada head opera con proyecciones aprendidas propias. Eso permite diferentes patrones de interacción, pero no demuestra que cada head posea una función lingüística única y estable.

#### 10. Tres usos de atención

| Mecanismo | Queries | Keys | Values | Acceso |
|---|---|---|---|---|
| autoatención del encoder | encoder | encoder | encoder | completo |
| autoatención causal del decoder | decoder | decoder | decoder | sin futuro |
| atención cruzada | decoder | encoder | encoder | fuente completa |

La atención cruzada puede escribirse como:

$$
Q=H_DW_Q,\qquad K=H_EW_K,\qquad V=H_EW_V.
$$

Esto permite que el decoder consulte las representaciones de la secuencia fuente.

#### 11. Red feed-forward por posición

Cada posición pasa por:

$\mathrm{FFN}(x) = \max(0,xW_1+b_1)W_2+b_2.$

En el paper:

$$
d_{\mathrm{model}}=512,
\qquad
d_{\mathrm{ff}}=2048.
$$

Conceptualmente:

```text
atención
  -> mezcla información entre posiciones

FFN
  -> transforma características dentro de cada posición
```

Ambas operaciones son necesarias y cumplen funciones distintas.

#### 12. Residual, LayerNorm y dropout

El paper utiliza:

$$
\mathrm{LayerNorm}
\left(
x+\mathrm{Sublayer}(x)
\right),
$$

es decir, **post-norm**.

El cuaderno de Semana 1 utiliza **pre-norm**:

$Y = X+\mathrm{MHA}\left(\mathrm{LN}(X)\right),$

$Z= Y+\mathrm{FFN}\left(\mathrm{LN}(Y)\right).$

Por tanto, no deben presentarse como la misma arquitectura.

En el modelo base se usa:

$$
P_{\mathrm{drop}}=0.1.
$$

El dropout se aplica a las salidas de subcapas y a la suma de embeddings con codificación posicional.

#### 13. Codificación posicional

Al eliminar recurrencia y convolución, el modelo necesita representar el orden.

$PE(pos,2i) =\sin\left(\frac{pos}{10000^{2i/d_{\mathrm{model}}}}\right),$

$PE(pos,2i+1) =\cos\left(\frac{pos}{10000^{2i/d_{\mathrm{model}}}}\right).$

La entrada es:

$X_{\mathrm{entrada}}= E_{\mathrm{token}}+PE.$

El paper también prueba embeddings posicionales aprendidos y obtiene resultados muy similares.

Debe distinguirse:

```text
sinusoidal/learned absolute
  -> embeddings

RoPE
  -> Q y K

ALiBi
  -> logits de atención
```

#### 14. Por qué autoatención

El paper compara complejidad, operaciones secuenciales y longitud máxima del camino.

| Capa | Complejidad | Operaciones secuenciales | Camino máximo |
|---|---:|---:|---:|
| autoatención | $O(n^2d)$ | $O(1)$ | $O(1)$ |
| recurrente | $O(nd^2)$ | $O(n)$ | $O(n)$ |
| convolucional | $O(knd^2)$ | $O(1)$ | $O(\log_k n)$ |

La autoatención conecta directamente cualquier par de posiciones, lo que reduce la longitud del camino de información.

Sin embargo:

> Attention no es siempre más barata.

La atención densa mantiene costo cuadrático en $n$.

#### 15. Entrenamiento, regularización e inferencia

Para WMT 2014 English-German se utilizan aproximadamente 4.5 millones de pares y unas 37 000 unidades BPE.

El entrenamiento usa 8 GPU NVIDIA P100.

Modelo base:

```text
100 000 steps
aproximadamente 12 horas
```

Modelo big:

```text
300 000 steps
aproximadamente 3.5 días
```

Adam:

$$
\beta_1=0.9,
\qquad
\beta_2=0.98,
\qquad
\epsilon=10^{-9}.
$$

Learning-rate schedule:

$\mathrm{lrate} = d_{\mathrm{model}}^{-1/2}\min\left(\mathrm{step}^{-1/2},\mathrm{step}\cdot\mathrm{warmup}^{-3/2}\right),$

con:

$$
\mathrm{warmup}=4000.
$$

El modelo base usa:

$$
P_{\mathrm{drop}}=0.1
$$

y label smoothing:

$$
\epsilon_{\mathrm{ls}}=0.1.
$$

Durante inferencia, el paper usa beam search con beam size 4 y penalización de longitud:

$$
\alpha=0.6.
$$

Esto muestra que el resultado reportado depende de más que la arquitectura:

```text
modelo + entrenamiento + regularización + selección de checkpoint + decoding = resultado final
```

#### 16. Resultados

El Transformer big alcanza:

$$
28.4\ \mathrm{BLEU}
$$

en English-German.

La tabla principal reporta:

$$
41.8\ \mathrm{BLEU}
$$

en English-French.

El paper también prueba constituency parsing, aportando evidencia de que la arquitectura puede transferirse a una tarea distinta de traducción.

#### 17. Ablaciones y lectura experimental

El baseline utiliza:

| Parámetro | Valor |
|---|---:|
| $N$ | 6 |
| $d_{\mathrm{model}}$ | 512 |
| $d_{\mathrm{ff}}$ | 2048 |
| $h$ | 8 |
| $d_k=d_v$ | 64 |
| dropout | 0.1 |
| label smoothing | 0.1 |
| parámetros | aproximadamente 65 M |

Variantes del número de heads:

| Heads | $d_k=d_v$ | PPL | BLEU dev |
|---:|---:|---:|---:|
| 1 | 512 | 5.29 | 24.9 |
| 4 | 128 | 5.00 | 25.5 |
| 8 | 64 | 4.92 | 25.8 |
| 16 | 32 | 4.91 | 25.8 |
| 32 | 16 | 5.01 | 25.4 |

La evidencia no permite concluir:

> Más heads siempre es mejor.

Permite concluir que, bajo esa configuración experimental, el número de heads y la dimensión por head afectan el rendimiento.

#### 18. Nota de lectura crítica

La versión HTML de arXiv presenta una inconsistencia para English-French:

- abstract: **41.8 BLEU**;
- tabla principal: **41.8 BLEU**;
- una oración de resultados: **41.0 BLEU**.

Esta lectura usa **41.8** porque coincide con el abstract y la tabla.

La lección es:

> Una fuente primaria también debe contrastarse internamente.

#### 19. Qué demuestra y qué no demuestra

El paper aporta evidencia de que una arquitectura basada principalmente en atención puede reemplazar recurrencia y convolución en las tareas estudiadas, mejorar paralelismo y obtener resultados competitivos.

No demuestra que:

- atención densa sea siempre la opción más eficiente,
- ocho heads sean universalmente óptimos,
- más heads siempre mejoren el modelo,
- cada head tenga una interpretación lingüística causal,
- todo Transformer deba ser encoder-decoder,
- post-norm sea obligatorio,
- codificación sinusoidal sea universal,
- una matriz de atención explique por completo el razonamiento del modelo.

#### 20. Qué cambió después de 2017

```text
post-norm
  -> frecuentemente pre-norm

LayerNorm
  -> en algunas familias RMSNorm

codificación sinusoidal
  -> RoPE, ALiBi y otras variantes

MHA
  -> MQA, GQA y otras variantes

ReLU
  -> GELU, SwiGLU y otras variantes

encoder-decoder
  -> decoder-only dominante en muchos LLM generativos

attention estándar
  -> implementaciones optimizadas como FlashAttention
```

El paper debe estudiarse como fundamento arquitectónico, no como especificación de un LLM actual.

#### 21. Paper -> código -> experimento

| Concepto | Semana 1 |
|---|---|
| tokens y embeddings | `Cuaderno1-CC-0F4.ipynb` |
| $Q,K,V$ | cuaderno |
| $QK^\top/\sqrt{d_k}$ | cuaderno + `mha.py` |
| máscara causal | cuaderno + laboratorio |
| Multi-Head Attention | cuaderno + `mha.py` |
| residual + LayerNorm + FFN | cuaderno + `models.py` |
| full vs causal | Attention AI Lab |
| invariantes | `EVALUATE` |
| ablaciones | `CRITIQUE` |
| límites de evidencia | `DEFEND` |

El ciclo es:

```text
BUILD
  ->
EVALUATE
  ->
READ
  ->
CRITIQUE
  ->
DEFEND
```

#### 22. Glosario mínimo

**Autoatención:** atención donde query, key y value proceden de la misma secuencia.

**Atención causal:** autoatención que bloquea posiciones futuras.

**Atención cruzada:** atención donde las queries proceden de una representación y keys/values de otra.

**Logit de atención:** score calculado antes de `softmax`.

**Head:** una instancia de atención con proyecciones propias.

**Embedding:** representación vectorial de un token.

**Baseline:** configuración de referencia.

**Ablación:** experimento que modifica o elimina un componente para estudiar su contribución.

#### 23. Preguntas adicionales

1. ¿Qué limitación computacional de las RNN motiva el Transformer?
2. ¿Por qué la contribución no debe reducirse a "inventó attention"?
3. ¿Cuál es el papel operacional de $Q$, $K$ y $V$?
4. ¿Qué representan las filas y columnas de $QK^\top$?
5. ¿Por qué se divide por $\sqrt{d_k}$?
6. ¿Qué propiedad verifica $E_{\mathrm{norm}}$?
7. ¿Qué propiedad verifica $L_{\mathrm{future}}$?
8. ¿Qué operación introduce causalidad?
9. ¿Cómo puede el entrenamiento ser paralelo sin usar tokens futuros?
10. ¿Qué diferencia autoatención del encoder, autoatención causal y atención cruzada?
11. ¿Qué función cumple el FFN si attention ya mezcla posiciones?
12. ¿Qué diferencia post-norm de pre-norm?
13. ¿Qué permite concluir la ablación del número de heads?
14. ¿Por qué el decoding forma parte del sistema experimental y no solo del modelo?
15. ¿Qué decisiones del Transformer original no son universales en LLM modernos?.

#### 24. Cierre

*Attention Is All You Need* es importante porque reorganizó el modelado de secuencias alrededor de atención.

Para CC-0F4 la lectura no termina en comprender la ecuación:

```text
paper
  ->
ecuación
  ->
tensores
  ->
código
  ->
métrica
  ->
experimento
  ->
conclusión defendible
```

#### 25. Referencia

Vaswani, A., Shazeer, N., Parmar, N., Uszkoreit, J., Jones, L., Gomez, A. N., Kaiser, L., & Polosukhin, I. (2017). *Attention Is All You Need*. Advances in Neural Information Processing Systems, 30. https://arxiv.org/abs/1706.03762
