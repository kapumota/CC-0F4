### Semana 1 - De modelos a sistemas de IA compuestos

#### Propósito

La Semana 1 establece la base conceptual y experimental de CC-0F4. El objetivo no es aprender una API ni entrenar un LLM competitivo, sino conectar:

```text
modelo -> componente -> implementación -> métrica -> evidencia -> sistema
```

Al finalizar la semana debes poder:

- distinguir un modelo de un sistema de IA compuesto,
- explicar `texto -> tokens -> IDs -> embeddings -> posición`,
- describir el papel de $Q$, $K$ y $V$,
- reconstruir scaled dot-product attention,
- explicar por qué la causalidad proviene de la máscara y no de `softmax`,
- reconocer Multi-Head Attention, residual, LayerNorm y FFN,
- distinguir encoder-only, encoder-decoder y decoder-only,
- verificar propiedades mediante invariantes,
- localizar la matemática dentro de una implementación real,
- formular una conclusión proporcional a la evidencia experimental.


#### Material de la semana

| Recurso | Función |
|---|---|
| [`Cuaderno1-CC-0F4.ipynb`](Cuaderno1-CC-0F4.ipynb) | Material canónico de clase: Transformer, posición, atención, causalidad, MHA y bloque Transformer |
| [`Laboratorio1-CC-0F4.ipynb`](Laboratorio1-CC-0F4.ipynb) | Laboratorio experimental del jueves |
| [`Lectura1-CC-0F4.md`](Lectura1-CC-0F4.md) | Lectura técnica sobre Transformer y extensiones |
| [`Resumen1-Attention-Is-All-You-Need.md`](Resumen1-Attention-Is-All-You-Need.md) | Resumen crítico guiado del paper central de la semana |

Recursos externos usados durante la semana:

- **Attention AI Lab:** https://github.com/kapumota/attentionlab-ai
- **Annotated Deep Learning Paper Implementations:** https://github.com/kapumota/annotated_deep_learning_paper_implementations
- **Attention Is All You Need:** https://arxiv.org/abs/1706.03762


#### Lunes - Fundamentos y arquitectura

El lunes se trabaja la secuencia conceptual:

```text
sistema de IA compuesto -> Transformer como componente -> tokens -> embeddings -> posición -> Q/K/V
-> atención producto-punto escalado -> máscara causal -> Multi-Head Attention -> residual + LayerNorm + FFN
-> encoder/decoder
```

Material principal:

```text
Cuaderno1-CC-0F4.ipynb
Lectura1-CC-0F4.md
Resumen1-Attention-Is-All-You-Need.md
```

Attention AI Lab se usa para observar full attention frente a causal attention y para mostrar la transición:

```text
matemática -> función -> API -> frontend -> sistema
```

#### Jueves - Laboratorio experimental

El laboratorio sigue el ciclo metodológico:

```text
BUILD -> EVALUATE -> READ -> CRITIQUE -> DEFEND
```

Las etiquetas se mantienen en inglés como nombres estables de etapas del workflow experimental del curso. Las instrucciones y la evaluación permanecen en español.

En el laboratorio se exige:

- predecir dimensiones antes de ejecutar,
- recorrer $X \to Q,K,V$,
- verificar scaling, máscara y `softmax`,
- comparar full attention y causal attention,
- calcular invariantes,
- introducir un fallo controlado,
- leer `mha.py` y `models.py`,
- diseñar una comparación controlada,
- identificar una limitación,
- defender qué conclusión sí está respaldada por la evidencia y cuál no.

#### Estándar experimental

Toda actividad experimental debe poder expresarse mediante:

```text
pregunta -> hipótesis -> baseline -> modificación controlada -> métrica -> resultado -> análisis de error
-> limitación -> conclusión
```

Una celda que ejecuta sin error no demuestra por sí sola que el componente sea correcto.



#### Entrega del laboratorio

Trabaja sobre una copia de:

```text
Laboratorio1-CC-0F4.ipynb
```

El archivo de entrega debe conservar las celdas del laboratorio y añadir las respuestas, resultados y conclusiones solicitadas.

Nombre sugerido:

```text
Laboratorio1-CC-0F4-APELLIDO.ipynb
```

La entrega se realiza mediante la plataforma de evaluación indicada por el docente. **No envíes soluciones mediante pull request al repositorio del curso.**

La defensa oral puede ser solicitada durante la sesión.



#### Prueba diagnóstica

La prueba diagnóstica de entrada se distribuye y entrega mediante una **plataforma de evaluación externa al repositorio**.

No se publica en `CC-0F4` y no forma parte de los archivos de `Semana1/`.



#### Entorno mínimo

El material es CPU-first. No requiere GPU, APIs comerciales ni servicios externos para ejecutar el cuaderno base.

Requisitos mínimos:

```text
Python 3.10+
PyTorch
JupyterLab
Matplotlib
nbformat
nbconvert
```

Para instalación local y uso de Docker consulta:

```text
docs/ENTORNO.md
```

Desde la raíz del repositorio:

```bash
make help
make check
make check-semana1
```



#### Criterio de cierre de Semana 1

La semana está cerrada cuando puedes sostener técnicamente:

$$ 
X \longrightarrow Q,K,V \longrightarrow \frac{QK^\top}{\sqrt{d_k}} \longrightarrow +M \longrightarrow \text{softmax} \longrightarrow AV \longrightarrow \text{MHA}
$$


En **causal attention**, definimos:

$$
M_{ij} = \begin{cases} 
0 & \text{si } j \leq i \\
-\infty & \text{si } j > i 
\end{cases}
$$

Esto produce:

$$
A_{ij} = \frac{\exp\left(\frac{Q_i K_j^\top}{\sqrt{d_k}} + M_{ij}\right)}{\sum_{l=1}^{n} \exp\left(\frac{Q_i K_l^\top}{\sqrt{d_k}} + M_{il}\right)} \approx 0 \quad \text{para } j > i
$$

La evidencia mínima no es "el código corre", sino:

```text
configuración registrada + propiedad definida + métrica + resultado + limitación + conclusión defendible
```
