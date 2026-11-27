### Lectura 12: optimización y presupuesto de inferencia

#### 1. Calidad frente a recursos

La optimización requiere un objetivo y una restricción de recursos. En recuperación de información se mide el acierto del párrafo de origen y el número de párrafos entregados. El segundo es un proxy de contexto, no de tokens ni de latencia. Para una consulta y un párrafo, la similitud coseno de los vectores TF-IDF normalizados es:

$$s(q,d)=\frac{\mathbf v_q^\top\mathbf v_d}{\|\mathbf v_q\|_2\|\mathbf v_d\|_2}.$$

Se ordenan los párrafos por similitud. Los baselines fijos entregan los primeros $k$ párrafos con $k\in\{1,2,3,4,5\}$. A0 y A1 corresponden a los extremos. B usa el margen entre las dos primeras similitudes:

$$m(q)=s(q,d_1)-s(q,d_2).$$

$$k_B(q)=\begin{cases}5 & m(q)<\tau,\\1 & \text{en otro caso.}\end{cases}$$

El margen no es una probabilidad calibrada. Si hay un único párrafo anotado, el acierto es un indicador de pertenencia al conjunto recuperado. Con el mismo ranking, ampliar el contexto no puede reducir ese acierto.

#### 2. Utilidad y frontera

$$U_\lambda(\pi)=\frac{1}{n}\sum_{i=1}^{n}\left[H_i(\pi)-\lambda k_i(\pi)\right].$$

Lambda representa la penalización por cada párrafo. El valor principal 0.025 es convencional; no se presenta como universal. Cada política congelada define una recta con intercepto igual al acierto y pendiente igual al negativo del contexto medio. Si dos políticas tienen costos distintos, su punto de cruce es:

$$\lambda^*=\frac{\overline H_a-\overline H_b}{\overline k_a-\overline k_b}.$$

La envolvente superior identifica qué política obtiene mayor utilidad observada para cada costo. Es un análisis descriptivo del test, no una regla para elegir retrospectivamente la política. Se distingue de recalibrar B en desarrollo para cada lambda.

Una comparación adicional iguala el presupuesto medio de B. Si el costo medio es $c$ entre $j$ y $j+1$, se compara con una mezcla independiente de la pregunta que usa top-$j+1$ con probabilidad $c-j$. El acierto esperado es la interpolación de ambos aciertos. Esta comparación no utiliza etiquetas para fijar el peso ni simula nuevos datos.

#### 3. Calibración y estimación estadística

Las preguntas de un artículo están correlacionadas. La separación se hace por artículo: 24 de desarrollo, 24 de prueba. El índice TF-IDF utiliza todos los textos sin etiquetas, como catálogo de búsqueda. Solo desarrollo se usa para optimizar el umbral o escoger el baseline fijo principal. En un empate exacto se prefiere el menor umbral o k. Un margen pequeño entre utilidades de desarrollo indica una decisión sensible.

El promedio micro por pregunta es el estimando principal. El promedio macro por artículo asigna el mismo peso a cada artículo y puede diferir. Para el IC95 micro, se remuestrean artículos con reemplazo y se divide la suma de diferencias de sus preguntas entre el total de preguntas de los artículos seleccionados en esa réplica. No se remuestrean preguntas aisladas. El intervalo percentil refleja variabilidad entre artículos, no corrige comparaciones múltiples ni incluye toda la incertidumbre de calibración.

Ocho semillas predefinidas muestran sensibilidad a la partición. Las evaluaciones se superponen y no representan experimentos independientes. No elegir la semilla que favorezca a B. Como el test de la primera versión fue observado, los análisis secundarios son exploratorios.

#### 4. Test-time compute, SFT, LoRA y QLoRA

Test-time compute es cómputo adicional durante la inferencia, por ejemplo considerar alternativas o verificar resultados. Nuestra política modifica solo cuántos párrafos se entregan; no mide razonamiento de un modelo. SFT actualiza pesos a partir de ejemplos supervisados. LoRA propone $W'=W+BA$, donde $B\in\mathbb R^{d\times r}$, $A\in\mathbb R^{r\times k}$ y $r\ll\min(d,k)$. La actualización tiene $r(d+k)$ parámetros entrenables en lugar de $dk$ para esa matriz. QLoRA utiliza pesos base cuantizados y adaptadores entrenables. No se ejecuta entrenamiento ni inferencia LLM en el benchmark.

#### 5. Fallos y amenazas a la validez

Si el párrafo de origen no aparece entre los cinco primeros, ampliar hasta cinco no resuelve el fallo. Si aparece en top-5 pero B entrega solo top-1, el fallo corresponde a la decisión de presupuesto. Inspeccionar preguntas reales, sus textos fuente y los párrafos recuperados, evitando seleccionar ejemplos convenientes. Clasificar por palabra interrogativa inicial ofrece un desglose léxico, no una anotación semántica. Los anotadores de SQuAD vieron el párrafo al redactar preguntas, lo que puede favorecer TF-IDF. Otros párrafos podrían contener la respuesta; recuperar el origen no demuestra respuesta correcta ni evidencia factual completa.

#### Referencias

- [SQuAD, Rajpurkar et al.](https://arxiv.org/abs/1606.05250).
- [Scaling LLM Test-Time Compute Optimally](https://arxiv.org/abs/2408.03314).
- [LoRA](https://arxiv.org/abs/2106.09685).
- [QLoRA](https://arxiv.org/abs/2305.14314).
- [CC-0F4, Semana 9](https://github.com/kapumota/CC-0F4/tree/main/Semana9).
