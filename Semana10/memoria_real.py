"""Memoria episódica verificable sobre QMSum Academic y Committee.

- No crea documentos, consultas ni anotaciones experimentales sintéticas.
- Consulta transcripciones originales; usa los spans humanos solo al evaluar.
- Persistencia SQLite idempotente sin reemplazos silenciosos.
- Evalúa recuperación de evidencia, NO calidad de respuestas de LLM.
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import math
import re
import sqlite3
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "datos"
OUT = ROOT / "resultados"
SOURCE_COMMIT = "83d7768c1f2b4dfeb091385d3dc7e239b8e5bb7e"
# SHA-1 del objeto blob Git y tamaño exacto del archivo JSONL publicado en QMSum.
BLOBS: dict[str, tuple[str, int]] = {
    "Academic/train": ("7e9e14565a53ed5114c67a39a34bfc398803346d", 4002726),
    "Academic/val": ("0300f312055c5b4346581d04c423bc524aec8013", 846571),
    "Academic/test": ("5142f78067c03e4c409bd41e29ad8cec4548e5e9", 945351),
    "Committee/train": ("36ae7deb404cb37a66e28e3dbe4b72b3c528f86c", 2381696),
    "Committee/val": ("07e51ee8b900d7be5b101a3b69646a726d06c105", 631864),
    "Committee/test": ("d085bd14652675031d942d279b192274f857e11a", 601618),
}
TOKEN_RE = re.compile(r"[a-z0-9]+", re.IGNORECASE)
DEFAULT_LIMIT = 48


def tokens(text: str) -> list[str]:
    """Tokens léxicos: NO embeddings ni comprensión semántica."""
    return TOKEN_RE.findall(text.lower())


def git_blob_sha1(raw: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


def local_path(key: str) -> Path:
    if key not in BLOBS:
        raise ValueError("No corresponde a uno de los seis archivos fijados de QMSum")
    return DATA / (key.replace("/", "_") + ".jsonl")


def check_file(key: str) -> dict[str, Any]:
    path = local_path(key)
    if not path.is_file():
        raise FileNotFoundError(
            f"Falta {path.name}. Preparar antes de clase: python -m Semana10.memoria_real --preparar"
        )
    raw = path.read_bytes()
    sha1, expected_size = BLOBS[key]
    if len(raw) != expected_size or git_blob_sha1(raw) != sha1:
        raise ValueError(f"Integridad Git inválida en {key}. No se admite corpus sustituto.")
    records = [json.loads(x) for x in raw.decode("utf-8").splitlines() if x.strip()]
    if not records or not all(
        isinstance(r.get("meeting_transcripts"), list)
        and isinstance(r.get("specific_query_list"), list)
        for r in records
    ):
        raise ValueError(f"Esquema de QMSum inesperado en {key}")
    return {
        "file": path.name,
        "meetings": len(records),
        "specific_queries": sum(len(r["specific_query_list"]) for r in records),
        "sha256": hashlib.sha256(raw).hexdigest(),
    }


def prepare() -> dict[str, Any]:
    DATA.mkdir(parents=True, exist_ok=True)
    for key in BLOBS:
        path = local_path(key)
        if path.exists():
            check_file(key)
            continue
        domain, split = key.split("/")
        url = (f"https://raw.githubusercontent.com/Yale-LILY/QMSum/{SOURCE_COMMIT}"
               f"/data/{domain}/jsonl/{split}.jsonl")
        req = urllib.request.Request(url, headers={"User-Agent": "CC0F4-QMSum-Education/1.0"})
        temp = path.with_suffix(".download")
        try:
            with urllib.request.urlopen(req, timeout=90) as source, temp.open("wb") as target:
                while True:
                    chunk = source.read(1024 * 1024)
                    if not chunk:
                        break
                    target.write(chunk)
            raw = temp.read_bytes()
            sha1, size = BLOBS[key]
            if len(raw) != size or git_blob_sha1(raw) != sha1:
                raise ValueError(f"Descarga incompleta o modificada: {key}")
            temp.replace(path)
        finally:
            temp.unlink(missing_ok=True)
        print("Descargado y verificado:", key)
    return verify()


def verify() -> dict[str, Any]:
    result = {k: check_file(k) for k in BLOBS}
    return {
        "dataset": "QMSum", "domains": ["Academic", "Committee"],
        "source_commit": SOURCE_COMMIT,
        "files": result,
        "meetings_total": sum(r["meetings"] for r in result.values()),
        "human_queries_total": sum(r["specific_queries"] for r in result.values()),
    }


def get_meetings(split: str) -> list[tuple[str, dict[str, Any]]]:
    if split not in ("train", "val", "test"):
        raise ValueError("Solo se permiten los splits oficiales train, val y test")
    result = []
    for domain in ("Academic", "Committee"):
        key = f"{domain}/{split}"
        check_file(key)
        for i, line in enumerate(local_path(key).read_text(encoding="utf-8").splitlines()):
            if line.strip():
                result.append((f"{domain}:{split}:{i:04d}", json.loads(line)))
    return result


def normalized_turns(turns: list[dict]) -> list[tuple[int, str, str]]:
    return [(i, str(x.get("speaker", "")), str(x.get("content", "")))
            for i, x in enumerate(turns)]


class MemoryStore:
    """Almacén de turnos originales. La clave de reunión nunca se sobreescribe.

    Una escritura idéntica es idempotente. Si el mismo meeting_id aparece con
    distinto contenido, se rechaza la operación y no se pierden los episodios.
    """
    def __init__(self, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(path)
        self.connection.execute(
            "CREATE TABLE IF NOT EXISTS episodes ("
            "meeting_id TEXT NOT NULL, position INTEGER NOT NULL, "
            "speaker TEXT NOT NULL, content TEXT NOT NULL, "
            "PRIMARY KEY(meeting_id, position))"
        )

    def save_meeting(self, meeting_id: str, turns: list[dict]) -> str:
        if not isinstance(meeting_id, str) or not meeting_id.strip() or not turns:
            raise ValueError("Se requieren identificador y al menos un turno")
        wanted = normalized_turns(turns)
        current = self.connection.execute(
            "SELECT position, speaker, content FROM episodes WHERE meeting_id=? ORDER BY position",
            (meeting_id,),
        ).fetchall()
        if current:
            if current != wanted:
                raise ValueError(
                    f"Conflicto: {meeting_id} ya fue almacenada con otros turnos. "
                    "Se conserva la versión existente; no se reemplaza sin auditoría."
                )
            return "already_present_identical"
        with self.connection:
            self.connection.executemany(
                "INSERT INTO episodes(meeting_id,position,speaker,content) VALUES (?,?,?,?)",
                [(meeting_id, *row) for row in wanted],
            )
        return "inserted"

    def read(self, meeting_id: str) -> list[dict[str, Any]]:
        rows = self.connection.execute(
            "SELECT position,speaker,content FROM episodes WHERE meeting_id=? ORDER BY position",
            (meeting_id,),
        ).fetchall()
        return [dict(position=i, speaker=sp, content=text) for i, sp, text in rows]

    def close(self) -> None:
        self.connection.close()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()


def bm25_rank(query: str, episodes: list[dict], limit: int = DEFAULT_LIMIT) -> list[dict]:
    """BM25 local fijo por reunión, con empates resueltos por índice de turno.

    Devuelve score para docencia; NO usa qrels ni resúmenes gold.
    """
    if limit < 1:
        raise ValueError("limit debe ser positivo")
    docs = [tokens(str(x["speaker"]) + " " + str(x["content"])) for x in episodes]
    n = len(docs)
    if not n:
        return []
    df = collections.Counter(term for doc in docs for term in set(doc))
    mean_len = sum(map(len, docs)) / n or 1.0
    terms = set(tokens(query))
    scored = []
    for i, doc in enumerate(docs):
        tf = collections.Counter(doc)
        doc_len = len(doc)
        score = 0.0
        for term in terms:
            count = tf.get(term, 0)
            if count:
                idf = math.log(1 + (n - df[term] + 0.5) / (df[term] + 0.5))
                score += idf * count * 2.2 / (count + 1.2 * (0.25 + 0.75 * doc_len / mean_len))
        scored.append(dict(position=i, score=score))
    return sorted(scored, key=lambda row: (-row["score"], row["position"]))[:min(limit, n)]


def bm25(query: str, episodes: list[dict], limit: int = DEFAULT_LIMIT) -> list[int]:
    """Interfaz de ranking; mantiene compatibilidad con la primera versión."""
    return [x["position"] for x in bm25_rank(query, episodes, limit)]


def gold_positions(query: dict, n_turns: int) -> set[int]:
    gold: set[int] = set()
    for span in query["relevant_text_span"]:
        if len(span) != 2:
            raise ValueError("Rango gold mal formado")
        first, last = map(int, span)
        if not 0 <= first <= last < n_turns:
            raise ValueError(f"Rango gold fuera de la transcripción: {span}")
        gold.update(range(first, last + 1))
    return gold


def grade_meeting(meeting_id: str, meeting: dict, store: MemoryStore,
                  limit: int = DEFAULT_LIMIT) -> list[dict]:
    store.save_meeting(meeting_id, meeting["meeting_transcripts"])
    episodes = store.read(meeting_id)
    rows = []
    for qi, q in enumerate(meeting["specific_query_list"]):
        gold = gold_positions(q, len(episodes))
        if not gold:
            continue
        recent = set(range(max(0, len(episodes) - limit), len(episodes)))
        lexical_rank = bm25_rank(q["query"], episodes, limit)
        chosen = {
            "working_recent": recent,
            "episodic_bm25": {r["position"] for r in lexical_rank},
        }
        for policy, selected in chosen.items():
            rows.append({
                "meeting": meeting_id, "query_index": qi, "policy": policy,
                "n_turns": len(episodes), "n_gold": len(gold),
                "n_selected": len(selected),
                "span_turn_recall": len(gold & selected) / len(gold),
                "any_relevant": int(bool(gold & selected)),
                "gold_outside_recent": int(bool(gold - recent)),
                "top_bm25_score": lexical_rank[0]["score"] if lexical_rank else 0.0,
            })
    return rows


def run(split: str = "val", limit: int = DEFAULT_LIMIT) -> dict[str, Any]:
    if split not in ("train", "val", "test"):
        raise ValueError("Split inválido")
    if limit < 1 or limit > 512:
        raise ValueError("limit debe estar entre 1 y 512")
    meetings = get_meetings(split)
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    with MemoryStore(DATA / "qmsum_episodic.sqlite3") as store:
        for meeting_id, meeting in meetings:
            rows.extend(grade_meeting(meeting_id, meeting, store, limit=limit))
    if not rows:
        raise ValueError("No se encontraron preguntas humanas con rangos válidos")
    # El sufijo evita sobrescribir la corrida con otra capacidad.
    suffix = f"_{limit}" if limit != DEFAULT_LIMIT else ""
    rows_path = OUT / f"qmsum_{split}{suffix}_por_consulta.jsonl"
    rows_path.write_text("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in rows), encoding="utf-8")
    metrics = {}
    for name in ("working_recent", "episodic_bm25"):
        group = [x for x in rows if x["policy"] == name]
        metrics[name] = {
            "n_queries": len(group),
            "mean_turn_recall": sum(x["span_turn_recall"] for x in group) / len(group),
            "any_relevant_rate": sum(x["any_relevant"] for x in group) / len(group),
            "mean_selected": sum(x["n_selected"] for x in group) / len(group),
        }
    summary = {
        "benchmark": "QMSum", "source_commit": SOURCE_COMMIT,
        "domains": ["Academic", "Committee"],
        "official_split": split, "limit": limit,
        "n_meetings": len(meetings), "n_evaluated_query_policy_rows": len(rows),
        "results": metrics,
        "scope": "Localización de evidencia por turno, SIN respuesta de LLM",
        "limitations": [
            "Consultas y rangos humanos no son juicios exhaustivos de relevancia",
            "La partición test es la oficial dentro del QMSum público, no un test oculto",
            "La recuperación léxica BM25 no equivale a embeddings semánticos",
            "No se mide vigencia factual, resumen ni calidad de un agente LLM",
        ],
    }
    (OUT / f"qmsum_{split}{suffix}_resumen.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return summary


def main() -> None:
    cli = argparse.ArgumentParser(description=__doc__)
    group = cli.add_mutually_exclusive_group(required=True)
    group.add_argument("--preparar", action="store_true")
    group.add_argument("--verificar", action="store_true")
    group.add_argument("--evaluar", choices=("train", "val", "test"))
    cli.add_argument("--limit", type=int, default=DEFAULT_LIMIT,
                     help="Capacidad de memoria en turnos. Por defecto 48; cambiar solo en val/train.")
    opts = cli.parse_args()
    if opts.evaluar == "test" and opts.limit != DEFAULT_LIMIT:
        cli.error("El test docente congelado utiliza --limit 48; calibra en val")
    result = prepare() if opts.preparar else verify() if opts.verificar else run(opts.evaluar, opts.limit)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
