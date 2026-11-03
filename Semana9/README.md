### Semana 9 - Workflows, agentes, ReAct, planificación y criterios de parada

#### Propósito

Las Semanas 4, 5 y 7 estudiaron recuperación y RAG, la Semana 6 construyó la frontera de confianza de una llamada a herramientas. La Semana 9 incorpora un **controlador de ejecución** que observa, decide la siguiente acción, valida, invoca herramientas y termina por una razón auditable. El eje experimental es comparar cuándo un workflow basta y cuándo la decisión de un agente justifica mayor complejidad.

```text
Semana 4/5: datos -> índices -> evidencia
Semana 6: tool call -> contrato -> ejecución -> observación
Semana 7: métricas, qrels y errores de RAG
Semana 9: múltiples decisiones, presupuesto, trazas y parada
Semana 10: memoria, persistencia y recuperación (NO implementadas aquí)
```

**Pregunta de la semana:** ¿qué ventajas y riesgos introduce permitir que un LLM seleccione acciones respecto de ejecutar una secuencia fija o una política de reglas? ¿Cómo demostrarlo con evidencia?

#### Resultados de aprendizaje comprobables

Al terminar la semana, el estudiante debe poder:

1. Diferenciar pipeline, workflow fijo, workflow con ramas, controlador heurístico y agente LLM.
2. Analizar cinco patrones de workflow y justificar cuándo utilizarlos.
3. Implementar un bucle de decisión-acción-observación que **valida** cada propuesta del modelo.
4. Explicar ReAct, planificación breve, cambios de plan y recuperación de errores.
5. Aplicar una allowlist, contratos de herramientas, `max_steps`, `max_tool_calls`, límites de tokens y deadline cooperativo.
6. Detectar repetición de acciones y distinguir éxito operativo de finalizaciones no exitosas.
7. Registrar trazas estructuradas, contrastar baselines y explicar amenazas a la validez de una comparación.


#### Delimitación frente a la Semana 10

El objeto `RunState` contiene **estado transitorio de una sola ejecución**, como contadores, observaciones y citas observadas. No crea una base de memoria, no persiste episodios y no permite recuperar hechos entre ejecuciones. `working memory`, `episodic memory` y `semantic memory` se estudiarán formalmente en la Semana 10. El patrón orchestrator-workers se presenta, pero la coordinación multiagente y los handoffs se reservarán para la Semana 11.

#### Baselines: la corrección de diseño fundamental

La edicion **usa una muestra autentica y pequena de SQuAD 1.1 dev**: 8 articulos de Wikipedia, 32 pasajes y 16 preguntas redactadas y respondidas por personas. Los qrels originales se derivan del pasaje con respuesta anotada. No se ejecuta el dataset docente creado para Semana 4. Los tres sistemas offline utilizan el **mismo BM25 local** con tokenización y ranking fijos:

- **A0** `workflow_fixed_top1`: una llamada `top_k=1`.
- **A1** `workflow_fixed_top3`: una llamada `top_k=3`.
- **B** `adaptive_rule_based`: primero `top_k=1`, amplia a `top_k=3` si la cobertura léxica es menor que el umbral 0.45, como máximo dos llamadas.

**Limitación:** al operar sobre un ranking fijo, B jamás puede superar a A1 en `evidence_hit`. Su eventual ventaja es utilizar menos contexto, no recuperar más pasajes relevantes que A1. Esta distinción impide conclusiones incorrectas sobre autonomía.

Se mide `evidence_hit`, llamadas, pasos, latencia BM25 local y `context_token_proxy` (conteo léxico de palabras). No se mide la exactitud semántica de las respuestas, costo de API, tokens del LLM ni calidad agéntica en el benchmark offline. El retriever BM25 empleado para aislar el control no sustituye el experimento con E5/FAISS o híbrido de Semana 7.

#### Instalación y ejecución desde CC-0F4

Copiar **solamente** `Semana9/` dentro de la raíz del repositorio del curso. **Paso obligatorio**: preparar una sola vez la muestra desde la fuente real, aproximadamente 4.9 MB de descarga. Luego, trabajar offline con los archivos generados en `Semana9/datos_reales/`. No se requieren APIs ni modelos grandes para A0/A1/B.

```bash
# Desde la raiz del repositorio CC-0F4:
python -m Semana9.prepare_real_data
python -m unittest Semana9.test_agent_benchmark Semana9.test_agent_loop Semana9.test_prepare_real_data -v
python -m Semana9.agent_benchmark
python -m Semana9.agent_demo --policy scripted --query-id Q01 \
  --output Semana9/resultados/demo_scripted.json
make check-week WEEK=9
make execute-cuaderno WEEK=9
```

El laboratorio se ejecuta, si se desea, mediante:

```bash
python -m jupyter nbconvert --to notebook --execute \
  Semana9/Laboratorio9-CC-0F4.ipynb \
  --ExecutePreprocessor.timeout=600 \
  --output Laboratorio9-ejecutado.ipynb
```

El modo guionizado **no es un LLM**. Se usa solo para probar la infraestructura, no para acreditar ReAct real.

#### Experimento voluntario con un LLM local

La política `LocalTransformersPolicy` utiliza el stack `torch`/`transformers` de la raíz del curso y carga un modelo instruct local o accesible en caché. El modelo canónico de referencia de las semanas anteriores es `Qwen/Qwen2.5-0.5B-Instruct`. El primer uso puede requerir descarga de pesos y suficiente RAM o GPU. No se ejecuta por defecto, no necesita claves de API y **no se ha afirmado calidad ni éxito del modelo sin una ejecución real**.

```bash
python -m Semana9.agent_demo --policy llm --query-id Q01 \
  --model-id Qwen/Qwen2.5-0.5B-Instruct \
  --output Semana9/resultados/demo_llm.json
```

Para habilitar las celdas opcionales en Jupyter:

```bash
export CC0F4_RUN_REAL_LLM=1
make execute-cuaderno WEEK=9
```

La política devuelve un JSON de acción. Respuestas mal formadas, selección de herramientas no autorizadas o terminaciones con citas inventadas son rechazadas por el controlador. Se contabilizan tokens cuando el modelo los reporta. El presupuesto global de tokens es **comprobado después de cada generación**, por lo que no es una restricción previa estricta; el deadline es cooperativo y no interrumpe forzosamente llamadas bloqueadas. Si se necesita un timeout duro de herramientas o consumo máximo estricto, se requieren mecanismos adicionales de ejecución aislada.


#### Criterios de cierre

Se presenta código ejecutable y explicable, tres baselines correctamente etiquetados, al menos cuatro trazas, un fallo de control reproducido, criterios de parada implementados y una conclusión ajustada a las métricas realmente medidas. Si ejecuta un LLM, debe registrar procedencia de la inferencia y distinguirla de los replays; si no, debe declararlo sin ambigüedad.

**Fuentes fundamentales:** Anthropic, *Building Effective Agents*; Yao et al., *ReAct*; Kapoor et al., *AI Agents That Matter*. Las direcciones y el contexto se encuentran en `Lectura9-CC-0F4.md`. No se han copiado fuentes externas completas dentro de este paquete.

#### Datos reales, reproducibilidad y honestidad experimental

La muestra deriva **sin inventar documentos, consultas ni respuestas** de
[SQuAD 1.1](https://rajpurkar.github.io/SQuAD-explorer/),
[archivo de validacion](https://github.com/rajpurkar/SQuAD-explorer/blob/master/dataset/dev-v1.1.json).
Licencia: CC BY-SA 4.0 (incluir atribucion a Wikipedia y SQuAD al redistribuir).
Se fija el Git blob SHA-1 de la version leida, se almacenan SHA-256 y se separan
respuestas humanas del corpus suministrado al recuperador.

La muestra educativa se selecciona por orden del archivo antes de medir modelos, **no** es una muestra aleatoria representativa ni evaluacion del benchmark SQuAD completo. Los qrels vinculan cada pregunta a su pasaje de origen, no anotan exhaustivamente todos los pasajes potencialmente relevantes. Una puntuacion `evidence_hit` no prueba que una respuesta generada sea verdadera.
La preparacion requiere red una vez, los experimentos posteriores no. En esta entrega no se afirma haber ejecutado el corpus real desde este entorno.
