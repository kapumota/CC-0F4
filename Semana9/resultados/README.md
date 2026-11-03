### Resultados de la Semana 9

Este directorio recibe archivos generados localmente. El repositorio no debe contener métricas inventadas ni ejecuciones LLM presentadas como realizadas cuando no lo fueron.

Al ejecutar `python -m Semana9.agent_benchmark` se producen:

- `runs.csv`: 48 filas, 16 preguntas humanas x 3 baselines A0/A1/B. Incluye `evidence_hit`, llamadas, pasos, latencia local, razón de parada y `context_token_proxy`.
- `traces.jsonl`: decisiones y observaciones de los tres baselines offline.
- `summary.json`: métricas agregadas, hashes SHA-256 y limitaciones explícitas.

Al ejecutar `python -m Semana9.agent_demo --policy scripted --output Semana9/resultados/demo_scripted.json` se obtiene una **simulación guionizada**, no una inferencia LLM.

Solo una ejecución explícita con `--policy llm` permite generar `demo_llm.json`; su contenido puede mostrar errores de modelo o parada sin éxito. El campo `completed_with_citations` acredita únicamente la validación operativa de citas observadas, no la corrección semántica de la respuesta.

Los datos reales se preparan en `Semana9/datos_reales/` desde SQuAD 1.1 dev; no se generan datos sintéticos. La carpeta contiene `manifest.json` y hashes de procedencia.
