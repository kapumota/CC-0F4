### Coleccion REAL de Semana 9

Este directorio se genera con `python -m Semana9.prepare_real_data`.

**Fuente:** SQuAD 1.1 dev (Stanford), pasajes de Wikipedia, preguntas y respuestas anotadas por personas, CC BY-SA 4.0. Se emplea una **muestra pequena de 32 pasajes y 16 preguntas** distribuida en 8 articulos. No se inventa contenido, no se traducen preguntas ni se generan qrels artificialmente.

La primera preparacion requiere obtener el archivo fuente de aproximadamente 4.9 MB. El dataset mini generado se usa localmente sin Internet.

URL: https://github.com/rajpurkar/SQuAD-explorer/blob/master/dataset/dev-v1.1.json

La funcion de preparacion comprueba el SHA-1 Git blob de la fuente y conserva SHA-256 de los cuatro archivos derivados. No incluye los textos originales en el ZIP inicial porque en este entorno no fue posible descargar el dataset.

Los qrels vinculan cada pregunta a su **pasaje de origen** con respuesta humana,
pero otros pasajes del subconjunto podrian ser relevantes sin estar anotados.
Por tanto, `evidence_hit` mide recuperacion de la evidencia identificada, no
relevancia completa ni exactitud de la respuesta. No es un benchmark oficial
ni permite generalizar resultados a SQuAD completo.

**Cita:** Rajpurkar et al. (2016), SQuAD, arXiv:1606.05250.

**Licencia y atribucion:** CC BY-SA 4.0, atribucion a SQuAD y a Wikipedia;
consultar `manifest.json` tras la preparacion.
