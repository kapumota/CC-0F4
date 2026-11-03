"""Prepara una coleccion docente REAL desde SQuAD 1.1, validacion.

No genera preguntas, textos ni etiquetas sinteticas. Conserva los contextos, preguntas y respuestas humanos publicados. Solo selecciona una muestra fija
por orden de aparicion, sin ajustar por el rendimiento de los recuperadores.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import urllib.request
from pathlib import Path
from typing import Any

URL = "https://raw.githubusercontent.com/rajpurkar/SQuAD-explorer/master/dataset/dev-v1.1.json"
EXPECTED_GIT_BLOB_SHA1 = "e9a3f913ad1468ebe105b891334ca7b0bc0e2510"
ARTICLES = 8
PARAGRAPHS_PER_ARTICLE = 4
QUESTIONS_PER_ARTICLE = 2


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git_blob_sha1(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def load_source(path: Path | None) -> tuple[dict[str, Any], bytes]:
    if path is not None:
        data = path.read_bytes()
    else:
        try:
            with urllib.request.urlopen(URL, timeout=45) as response:
                data = response.read()
        except Exception as exc:
            raise RuntimeError(
                "No fue posible descargar SQuAD. Descarga dev-v1.1.json desde "
                f"{URL} y utiliza --source-json /ruta/dev-v1.1.json"
            ) from exc
    sha1 = git_blob_sha1(data)
    if sha1 != EXPECTED_GIT_BLOB_SHA1:
        raise ValueError(f"Fuente no reconocida. Git blob SHA1 recibido={sha1}, esperado={EXPECTED_GIT_BLOB_SHA1}")
    try:
        obj = json.loads(data)
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError("El archivo fuente no es JSON valido") from exc
    if obj.get("version") != "1.1" or not isinstance(obj.get("data"), list):
        raise ValueError("Se requiere SQuAD 1.1 dev con data[]")
    return obj, data


def select_subset(source: dict[str, Any]) -> tuple[list[dict], list[dict], dict, list[dict]]:
    corpus: list[dict] = []
    questions: list[dict] = []
    qrels: dict[str, list[str]] = {}
    answers: list[dict] = []
    used_question_ids: set[str] = set()
    for article in source["data"]:
        if len(corpus) == ARTICLES:
            break
        paragraphs = [p for p in article["paragraphs"]
                      if isinstance(p.get("context"), str) and p.get("qas")]
        if len(paragraphs) < PARAGRAPHS_PER_ARTICLE:
            continue
        docid = f"SQ{len(corpus)+1:03d}"
        doc = {"doc_id": docid, "title": article["title"], "passages": []}
        for pi, paragraph in enumerate(paragraphs[:PARAGRAPHS_PER_ARTICLE], 1):
            pid = f"{docid}-P{pi:02d}"
            context = paragraph["context"]
            doc["passages"].append({"passage_id": pid, "text": context})
            # Primeras dos preguntas humanas: de pasajes 1 y 3, uno por pasaje.
            if pi not in (1, 3):
                continue
            qa = paragraph["qas"][0]
            sid = qa["id"]
            if not qa.get("answers") or sid in used_question_ids:
                raise ValueError("Pregunta sin respuesta anotada o ID duplicado")
            original_answers = [a["text"] for a in qa["answers"]]
            if not all(a in context for a in original_answers):
                raise ValueError(f"Respuesta fuera del pasaje original: {sid}")
            qid = f"Q{len(questions)+1:02d}"
            questions.append({"query_id": qid, "query": qa["question"],
                              "source_question_id": sid, "source_title": article["title"]})
            qrels[qid] = [pid]
            answers.append({"query_id": qid, "source_question_id": sid,
                            "passage_id": pid, "human_answers": original_answers})
            used_question_ids.add(sid)
        corpus.append(doc)
    if (len(corpus), sum(len(x["passages"]) for x in corpus), len(questions)) != (8,32,16):
        raise ValueError("La fuente no produjo la muestra esperada 8/32/16")
    return corpus, questions, qrels, answers


def write_jsonl(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def prepare(source_json: Path | None = None, output_dir: Path | None = None) -> dict:
    source, raw = load_source(source_json)
    corpus, queries, qrels, answers = select_subset(source)
    folder = output_dir or Path(__file__).resolve().parent / "datos_reales"
    folder.mkdir(parents=True, exist_ok=True)
    paths = {"corpus": folder / "corpus.jsonl", "queries": folder / "queries.jsonl",
             "qrels": folder / "qrels.json", "answers": folder / "respuestas_humanas.jsonl"}
    write_jsonl(paths["corpus"], corpus)
    write_jsonl(paths["queries"], queries)
    paths["qrels"].write_text(json.dumps(qrels, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_jsonl(paths["answers"], answers)
    manifest = {
        "dataset": "SQuAD 1.1, desarrollo (dev), seleccion didactica real",
        "dataset_source": URL, "git_blob_sha1_expected": EXPECTED_GIT_BLOB_SHA1,
        "source_sha256": sha256_bytes(raw),
        "license": "CC BY-SA 4.0", "origin": "Wikipedia, preguntas y respuestas anotadas por personas",
        "selection": "primeros 8 articulos con >=4 parrafos utilizables, primeros 4 parrafos por articulo, primera pregunta del parrafo 1 y del 3",
        "documents": len(corpus), "passages": 32, "queries": len(queries),
        "limitations": ["Subconjunto docente intencional, no resultado oficial SQuAD",
                        "qrels a nivel de pasaje observado, no anotacion exhaustiva de los 32 pasajes",
                        "ninguna muestra se selecciono despues de medir el modelo"],
        "sha256_files": {k: hashlib.sha256(path.read_bytes()).hexdigest() for k, path in paths.items()},
    }
    (folder / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return manifest


def main() -> None:
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--source-json", type=Path, help="Archivo dev-v1.1.json original descargado previamente")
    cli.add_argument("--output-dir", type=Path, help="Directorio de salida opcional")
    opts = cli.parse_args()
    print(json.dumps(prepare(opts.source_json, opts.output_dir), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
