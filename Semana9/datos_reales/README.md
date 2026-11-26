### Datos reales completos de Semana 9

Los archivos derivados se generan **solo** ejecutando `python -m Semana9.prepare_real_data` o con `--source-json` y el archivo oficial `dev-v1.1.json`.

Se admiten únicamente 48 artículos, 2.067 pasajes y 10.570 preguntas originales de SQuAD 1.1 dev; no se generan preguntas, distractores ni respuestas. Los `qrels` indican el pasaje de origen, no juicios de relevancia exhaustivos.

`manifest.json` documenta SHA256 original, Git blob SHA1, cantidades, hash por archivo derivado y partición fija de 12 artículos de calibración y 36 de evaluación. Las respuestas humanas se almacenan aparte y no se usan para indexar ni seleccionar documentos.

Fuente: https://github.com/rajpurkar/SQuAD-explorer/blob/master/dataset/dev-v1.1.json (CC BY-SA 4.0; atribuir Stanford SQuAD y artículos Wikipedia).
