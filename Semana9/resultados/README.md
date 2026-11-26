### Resultados de Semana 9: sin cifras precargadas

Antes de usar cualquier gráfico o métrica, ejecutar la preparación del SQuAD 1.1 dev completo y el benchmark offline. El programa produce `runs.csv`, `traces.jsonl` y `summary.json` con tamaños de partición, SHA256 de datos, umbral elegido **solo en calibración** y métricas de **evaluación**.

`python -m Semana9.agent_llm_eval --n 100` genera, cuando Qwen realmente se carga y ejecuta, `resultados/llm_real/comparacion_llm.csv`, `trazas_llm.jsonl` y `resumen_llm.json`. Si no se ejecutó, no debe informarse EM/F1 ni comparar agentes.

Ninguna salida de `ScriptedPolicy` demuestra autonomía del modelo. Un `completed_with_citations` significa que la cita pasó el contrato estructural; **no** que el texto esté respaldado o sea correcto.
