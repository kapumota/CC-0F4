"""Prepara íntegra la partición dev de SQuAD 1.1 para Semana 9.

No crea preguntas, pasajes, respuestas ni resultados artificiales. Los test
unitarios pueden usar estructuras mínimas, pero NO son datos experimentales.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import urllib.request
from pathlib import Path
from typing import Any

SOURCE_URL = "https://raw.githubusercontent.com/rajpurkar/SQuAD-explorer/master/dataset/dev-v1.1.json"
EXPECTED_GIT_BLOB_SHA1 = "e9a3f913ad1468ebe105b891334ca7b0bc0e2510"
EXPECTED_SOURCE_SHA256 = "95aa6a52d5d6a735563366753ca50492a658031da74f301ac5238b03966972c9"
EXPECTED_SOURCE_BYTES = 4_854_279
EXPECTED_ARTICLES = 48
EXPECTED_PASSAGES = 2067
EXPECTED_QUESTIONS = 10570
CALIBRATION_ARTICLES = 12
PARTITION_SEED = "CC0F4-Semana9-2026-v2"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git_blob_sha1(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def load_source(path: Path | None = None) -> tuple[dict[str, Any], bytes]:
    """Carga el original completo y falla sin sustituirlo por un subconjunto."""
    if path is not None:
        raw = path.read_bytes()
    else:
        try:
            with urllib.request.urlopen(
                urllib.request.Request(SOURCE_URL, headers={"User-Agent": "CC0F4-docencia/2026"}),
                timeout=60,
            ) as response:
                raw = response.read(EXPECTED_SOURCE_BYTES + 1)
        except Exception as exc:
            raise RuntimeError(
                "No se pudo obtener SQuAD completo. Descarga dev-v1.1.json y "
                "usa --source-json /ruta/dev-v1.1.json. Sin datos de reemplazo."
            ) from exc
    actual_git = git_blob_sha1(raw)
    actual_sha = sha256_bytes(raw)
    if (len(raw) != EXPECTED_SOURCE_BYTES or
            actual_git != EXPECTED_GIT_BLOB_SHA1 or
            actual_sha != EXPECTED_SOURCE_SHA256):
        raise ValueError(
            f"SQuAD no coincide con la fuente esperada: bytes={len(raw)}, "
            f"git_sha1={actual_git}, sha256={actual_sha}"
        )
    source = json.loads(raw)
    if source.get("version") != "1.1" or not isinstance(source.get("data"), list):
        raise ValueError("La fuente no es SQuAD dev versión 1.1")
    return source, raw


def choose_calibration_titles(titles: list[str]) -> set[str]:
    """Selecciona 12 artículos antes de medir resultados; sin mirar qrels."""
    if len(set(titles)) != EXPECTED_ARTICLES:
        raise ValueError("Se requieren 48 artículos con títulos únicos")
    ordered = sorted(titles, key=lambda t: hashlib.sha256(
        f"{PARTITION_SEED}\t{t}".encode("utf-8")
    ).hexdigest())
    return set(ordered[:CALIBRATION_ARTICLES])


def extract_dataset(source: dict[str, Any]) -> tuple[list[dict], list[dict], dict, list[dict], dict]:
    """Conserva todos los pasajes y preguntas originales, sin muestreo."""
    articles = source["data"]
    if len(articles) != EXPECTED_ARTICLES:
        raise ValueError(f"Cantidad de artículos inesperada: {len(articles)}")
    calibration = choose_calibration_titles([a["title"] for a in articles])
    corpus: list[dict] = []
    queries: list[dict] = []
    qrels: dict[str, list[str]] = {}
    answers: list[dict] = []
    seen_questions: set[str] = set()
    passage_count = 0
    annotation_mismatches: list[str] = []

    for article_idx, article in enumerate(articles, start=1):
        title = article["title"]
        split = "calibration" if title in calibration else "evaluation"
        doc_id = f"SQ{article_idx:03d}"
        doc = {"doc_id": doc_id, "title": title, "passages": []}
        for paragraph_idx, paragraph in enumerate(article["paragraphs"], start=1):
            passage_id = f"{doc_id}-P{paragraph_idx:04d}"
            context = paragraph["context"]
            if not isinstance(context, str) or not context.strip():
                raise ValueError(f"Pasaje vacío: {passage_id}")
            doc["passages"].append({"passage_id": passage_id, "text": context})
            passage_count += 1
            for qa in paragraph["qas"]:
                original_id = qa["id"]
                if original_id in seen_questions:
                    raise ValueError(f"ID de pregunta duplicado: {original_id}")
                seen_questions.add(original_id)
                original_answers = qa.get("answers", [])
                human_answers = [a["text"] for a in original_answers]
                if not human_answers:
                    raise ValueError(f"Pregunta sin respuesta humana: {original_id}")
                # Se preservan las anotaciones originales aunque sus offsets tengan
                # alguna anomalía. Nunca se corrigen silenciosamente con IA.
                for answer in original_answers:
                    at = answer.get("answer_start")
                    if (not isinstance(at, int) or
                            context[at:at + len(answer["text"])] != answer["text"]):
                        annotation_mismatches.append(original_id)
                query_id = f"Q{len(queries)+1:02d}"
                queries.append({
                    "query_id": query_id, "query": qa["question"],
                    "source_question_id": original_id, "source_title": title,
                    "passage_id": passage_id, "split": split,
                })
                qrels[query_id] = [passage_id]
                answers.append({
                    "query_id": query_id, "source_question_id": original_id,
                    "passage_id": passage_id, "human_answers": human_answers,
                })
        corpus.append(doc)
    if (passage_count, len(queries), len(answers)) != (
            EXPECTED_PASSAGES, EXPECTED_QUESTIONS, EXPECTED_QUESTIONS):
        raise ValueError(
            "SQuAD incompleto: "
            f"{passage_count} pasajes, {len(queries)} preguntas. "
            f"Se requieren {EXPECTED_PASSAGES} y {EXPECTED_QUESTIONS}."
        )
    splits = {s: sum(q["split"] == s for q in queries) for s in ("calibration", "evaluation")}
    if min(splits.values()) <= 0:
        raise ValueError("La partición por artículos está vacía")
    assert not (calibration & {q["source_title"] for q in queries if q["split"] == "evaluation"})
    counts = {"articles": len(corpus), "passages": passage_count,
              "queries": len(queries), "split_queries": splits,
              "calibration_articles": CALIBRATION_ARTICLES,
              "evaluation_articles": EXPECTED_ARTICLES - CALIBRATION_ARTICLES,
              "annotations_with_offset_mismatch": len(set(annotation_mismatches)),
              "annotation_issue_ids_sample": sorted(set(annotation_mismatches))[:10]}
    return corpus, queries, qrels, answers, counts


def write_jsonl(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def prepare(source_json: Path | None = None, output_dir: Path | None = None) -> dict:
    """Escribe archivos reales y un manifiesto de procedencia."""
    source, raw = load_source(source_json)
    corpus, queries, qrels, answers, counts = extract_dataset(source)
    folder = output_dir or Path(__file__).resolve().parent / "datos_reales"
    folder.mkdir(parents=True, exist_ok=True)
    paths = {
        "corpus": folder / "corpus.jsonl",
        "queries": folder / "queries.jsonl",
        "qrels": folder / "qrels.json",
        "answers": folder / "respuestas_humanas.jsonl",
    }
    write_jsonl(paths["corpus"], corpus)
    write_jsonl(paths["queries"], queries)
    paths["qrels"].write_text(json.dumps(qrels, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    write_jsonl(paths["answers"], answers)
    manifest = {
        "dataset": "SQuAD 1.1 dev, conjunto COMPLETO, no test oculto oficial",
        "dataset_source": SOURCE_URL,
        "source_bytes": len(raw), "source_sha256": sha256_bytes(raw),
        "source_git_blob_sha1": git_blob_sha1(raw), "license": "CC BY-SA 4.0",
        "split_rule": "12 artículos de calibración por hash de título; otros 36 para evaluación",
        "split_seed": PARTITION_SEED,
        **counts,
        "sha256_files": {name: sha256_bytes(path.read_bytes()) for name, path in paths.items()},
        "limits": [
            "SQuAD dev público no es el test oculto del benchmark",
            "Qrels indican el pasaje original con respuesta; no son juicios exhaustivos de relevancia",
            "Las respuestas humanas se almacenan aparte y nunca se incorporan al recuperador",
        ],
    }
    path = folder / "manifest.json"
    path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return manifest


def verify(output_dir: Path | None = None) -> dict:
    folder = output_dir or Path(__file__).resolve().parent / "datos_reales"
    manifest_path = folder / "manifest.json"
    if not manifest_path.exists():
        raise FileNotFoundError("No existe el manifiesto; ejecuta primero --prepare")
    m = json.loads(manifest_path.read_text(encoding="utf-8"))
    if (m.get("articles"), m.get("passages"), m.get("queries")) != (
            EXPECTED_ARTICLES, EXPECTED_PASSAGES, EXPECTED_QUESTIONS):
        raise ValueError("Manifiesto no contiene el conjunto completo")
    for name, sha in m["sha256_files"].items():
        path = folder / {"corpus": "corpus.jsonl", "queries": "queries.jsonl",
                         "qrels": "qrels.json", "answers": "respuestas_humanas.jsonl"}[name]
        if not path.exists() or sha256_bytes(path.read_bytes()) != sha:
            raise ValueError(f"Archivo ausente o modificado: {path}")
    return m


def main() -> None:
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--source-json", type=Path, help="Fuente SQuAD descargada previamente")
    cli.add_argument("--output-dir", type=Path, help="Destino opcional")
    cli.add_argument("--check", action="store_true", help="Valida manifiesto y datos completos")
    args = cli.parse_args()
    result = verify(args.output_dir) if args.check else prepare(args.source_json, args.output_dir)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
