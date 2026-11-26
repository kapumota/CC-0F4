### Resultados experimentales

Los archivos aquí se producen **solo mediante ejecuciones reales** de `python -m Semana10.memoria_real --evaluar val|test`. No se incluye ningún valor ficticio ni simulación de métricas.

Las trazas `qmsum_<split>_por_consulta.jsonl` contienen `meeting`, `query_index`, `policy`, turnos seleccionados, Recall por turnos y AnyHit. Los resúmenes agregan por política. No muestran corrección de resumen, vigencia factual ni capacidad de LLM.

Las pruebas unitarias emplean fixtures mínimas de SQLite y BM25, pero nunca crean o alteran resultados de este directorio.
