# Fuentes de datos QMSum

En este directorio se guardan **únicamente** los seis archivos JSONL oficiales tras ejecutar:

```bash
python -m Semana10.memoria_real --preparar
python -m Semana10.memoria_real --verificar
```

Fuente: https://github.com/Yale-LILY/QMSum, commit `83d7768c1f2b4dfeb091385d3dc7e239b8e5bb7e`.

Se verifica cada tamaño y SHA-1 de objeto Git. Si los archivos están presentes pero modificados, el programa rechaza su uso. No sustituyas datos por fixtures de tests ni ejemplos inventados. La base local `qmsum_episodic.sqlite3` se crea al ejecutar la evaluación y se puede conservar entre sesiones.
