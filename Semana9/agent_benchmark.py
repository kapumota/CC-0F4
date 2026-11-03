"""Benchmark docente A0/A1/B sobre BM25 fijo, sin LLM ni coste de API.

B es una politica heuristica, no un agente LLM. Usa una muestra real y reproducible de SQuAD 1.1, no los datos ilustrativos de Semana 4.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
import statistics
import time
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

STOPWORDS = frozenset()  # Comparacion controlada, sin preprocesamiento ajustado al benchmark.
TOKEN_RE = re.compile(r"\w+", flags=re.UNICODE)


def tokens(text: str) -> list[str]:
    """Tokenizacion lexical minima, documentada y determinista."""
    return [x for x in TOKEN_RE.findall(text.casefold()) if x not in STOPWORDS]


def find_repo_root(start: Path | None = None) -> Path:
    """Localiza CC-0F4 con Semana9, sin exigir Semana4 ni datos fabricados."""
    base = (start or Path.cwd()).resolve()
    for path in [base, *base.parents]:
        if (path / "Semana9/agent_benchmark.py").is_file():
            return path
    raise FileNotFoundError("No se encontro Semana9 en la raiz de CC-0F4")


def real_paths(root: Path) -> dict[str, Path]:
    folder = root / "Semana9/datos_reales"
    paths = {"corpus": folder / "corpus.jsonl", "queries": folder / "queries.jsonl",
             "qrels": folder / "qrels.json"}
    missing = [str(p) for p in paths.values() if not p.is_file()]
    if missing:
        raise FileNotFoundError("Faltan datos reales. Ejecuta antes: "
                                "python -m Semana9.prepare_real_data. Faltan: " + ", ".join(missing))
    return paths


def jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(row) for row in path.read_text(encoding="utf-8").splitlines() if row.strip()]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


@dataclass(frozen=True)
class Passage:
    passage_id: str
    text: str
    doc_id: str


class BM25Tool:
    """Misma herramienta determinista para las tres politicas.

    BM25 local sobre passages, no reproduce el baseline E5/FAISS de Semana7.
    """

    def __init__(self, corpus: list[dict[str, Any]]):
        self.passages = [
            Passage(passage_id=p["passage_id"], text=p["text"], doc_id=doc["doc_id"])
            for doc in corpus for p in doc["passages"]
        ]
        self.term_freqs = [Counter(tokens(p.text)) for p in self.passages]
        self.avgdl = statistics.mean(sum(tf.values()) for tf in self.term_freqs)
        df: Counter[str] = Counter()
        for tf in self.term_freqs:
            df.update(tf.keys())
        n = len(self.passages)
        self.idf = {
            term: math.log(1 + (n - f + 0.5) / (f + 0.5))
            for term, f in df.items()
        }

    def search(self, query: str, top_k: int) -> list[dict[str, Any]]:
        if top_k < 1 or top_k > 5:
            raise ValueError("top_k fuera de la allowlist [1, 5]")
        k1, b = 1.5, 0.75
        query_terms = Counter(tokens(query))
        ranked = []
        for passage, tf in zip(self.passages, self.term_freqs):
            dl = sum(tf.values())
            score = sum(
                self.idf.get(term, 0.0) * (n * (k1 + 1)) /
                (n + k1 * (1 - b + b * dl / self.avgdl))
                for term in query_terms if (n := tf.get(term, 0)) > 0
            )
            ranked.append((score, passage.passage_id, passage))
        ranked.sort(key=lambda item: (-item[0], item[1]))
        return [
            {"passage_id": p.passage_id, "doc_id": p.doc_id,
             "score": round(score, 8), "text": p.text}
            for score, _, p in ranked[:top_k]
        ]


def lexical_coverage(query: str, evidence: str) -> float:
    """Criterio de observacion NO supervisado por qrels."""
    q = set(tokens(query))
    return len(q.intersection(tokens(evidence))) / len(q) if q else 0.0


def run_workflow(query: str, tool: BM25Tool, top_k: int = 3) -> dict[str, Any]:
    """Plan fijo: una unica llamada. top_k=1 o 3 como baselines A0/A1."""
    started = time.perf_counter()
    findings = tool.search(query, top_k)
    elapsed = (time.perf_counter() - started) * 1000
    return {
        "policy": f"workflow_fixed_top{top_k}", "citations": [p["passage_id"] for p in findings],
        "answer_excerpt": findings[0]["text"] if findings else "",
        "steps": 1, "tool_calls": 1, "stop_reason": "completed",
        "latency_ms": round(elapsed, 4),
        "trace": [{"step": 1, "action": "search", "top_k": top_k,
                   "observation_ids": [p["passage_id"] for p in findings],
                   "stop": "completed"}],
    }


def run_adaptive(query: str, tool: BM25Tool, threshold: float = 0.45) -> dict[str, Any]:
    """Control adaptativo con observacion, decision y parada.

    NO es ReAct con LLM. Es una base ejecutable para reemplazar la politica
    por un modelo capaz de elegir herramientas con contratos de Semana6.
    """
    started = time.perf_counter()
    trace: list[dict[str, Any]] = []
    first = tool.search(query, 1)
    confidence = lexical_coverage(query, first[0]["text"]) if first else 0.0
    trace.append({"step": 1, "action": "search", "top_k": 1,
                  "observation_ids": [p["passage_id"] for p in first],
                  "lexical_coverage": round(confidence, 4)})
    if confidence < threshold:
        findings = tool.search(query, 3)
        trace.append({"step": 2, "action": "search", "top_k": 3,
                      "observation_ids": [p["passage_id"] for p in findings],
                      "stop": "completed_max_two_calls"})
    else:
        findings = first
        trace[-1]["stop"] = "completed_sufficient_lexical_coverage"
    elapsed = (time.perf_counter() - started) * 1000
    return {
        "policy": "adaptive_rule_based", "citations": [p["passage_id"] for p in findings],
        "answer_excerpt": findings[0]["text"] if findings else "",
        "steps": len(trace), "tool_calls": len(trace),
        "stop_reason": trace[-1]["stop"], "latency_ms": round(elapsed, 4),
        "trace": trace,
    }


def evaluate_run(root: Path, output_dir: Path | None = None,
                 threshold: float = 0.45) -> dict[str, Any]:
    if not 0 <= threshold <= 1:
        raise ValueError("threshold debe estar en [0, 1]")
    paths = real_paths(root)
    corpus = jsonl(paths["corpus"])
    queries = jsonl(paths["queries"])
    qrels = json.loads(paths["qrels"].read_text(encoding="utf-8"))
    if len(queries) != 16 or len({q["query_id"] for q in queries}) != 16:
        raise ValueError("Se requieren 16 preguntas reales con IDs unicos")
    if set(qrels) != {q["query_id"] for q in queries}:
        raise ValueError("Las claves qrels y queries no coinciden")
    tool = BM25Tool(corpus)
    if len(tool.passages) != 32:
        raise ValueError("Se requieren los 32 pasajes reales de SQuAD")
    known = {p.passage_id for p in tool.passages}
    if any(not set(rels).issubset(known) for rels in qrels.values()):
        raise ValueError("qrels contiene pasajes inexistentes")

    records: list[dict[str, Any]] = []
    traces: list[dict[str, Any]] = []
    for q in queries:
        for result in (run_workflow(q["query"], tool, 1),
                       run_workflow(q["query"], tool, 3),
                       run_adaptive(q["query"], tool, threshold)):
            relevant = set(qrels[q["query_id"]])
            record = {
                "query_id": q["query_id"], "difficulty": q.get("difficulty", ""),
                "policy": result["policy"], "evidence_hit": int(bool(relevant.intersection(result["citations"]))),
                "evidence_count": len(result["citations"]),
                "steps": result["steps"], "tool_calls": result["tool_calls"],
                "context_token_proxy": sum(len(tokens(tool_passage.text)) for tool_passage in tool.passages
                                           if tool_passage.passage_id in result["citations"]),
                "latency_ms": result["latency_ms"], "stop_reason": result["stop_reason"],
                "citations": "|".join(result["citations"]),
            }
            records.append(record)
            traces.append({"query_id": q["query_id"], "query": q["query"], **result})
    stats = {}
    for policy in ("workflow_fixed_top1", "workflow_fixed_top3", "adaptive_rule_based"):
        sub = [r for r in records if r["policy"] == policy]
        stats[policy] = {
            "queries": len(sub), "evidence_hit_rate": round(statistics.mean(r["evidence_hit"] for r in sub), 6),
            "mean_tool_calls": round(statistics.mean(r["tool_calls"] for r in sub), 6),
            "mean_steps": round(statistics.mean(r["steps"] for r in sub), 6),
            "mean_context_token_proxy": round(statistics.mean(r["context_token_proxy"] for r in sub), 6),
            "mean_latency_ms": round(statistics.mean(r["latency_ms"] for r in sub), 4),
        }
    summary = {
        "experiment": "Semana9 SQuAD REAL A0 top1 vs A1 top3 vs B adaptativo, SIN LLM",
        "sample_size": len(queries), "passages": len(tool.passages),
        "threshold_not_tuned": threshold, "metric_definition": "evidence_hit=al menos 1 passage relevante en las citas",
        "not_measured": ["correctness de respuesta", "latencia de LLM", "tokens reales de modelo", "costo API", "eficacia de agente LLM"],
        "token_proxy_note": "conteo de palabras via tokenizador lexical local, NO tokens LLM ni costo",
        "baseline_retriever": "BM25 local fijo sobre pasajes reales SQuAD; no reproduce E5/FAISS",
        "design_limit": "B usa un ranking fijo, no mejora evidence_hit sobre A1; la muestra SQuAD no es evaluacion oficial",
        "source_dataset": "SQuAD 1.1 dev, subconjunto real de 32 pasajes y 16 preguntas humanas",
        "qrels_limit": "Una respuesta anotada por pasaje original, no relevancia exhaustiva",
        "policy_labels": {"A0": "workflow_fixed_top1", "A1": "workflow_fixed_top3",
                          "B": "adaptive_rule_based"},
        "data_sha256": {k: sha256(v) for k, v in paths.items()},
        "results": stats,
    }
    if output_dir:
        output_dir.mkdir(parents=True, exist_ok=True)
        with (output_dir / "runs.csv").open("w", encoding="utf-8", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=list(records[0])); writer.writeheader(); writer.writerows(records)
        with (output_dir / "traces.jsonl").open("w", encoding="utf-8") as fh:
            for t in traces:
                fh.write(json.dumps(t, ensure_ascii=False) + "\n")
        (output_dir / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--threshold", type=float, default=0.45)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    root = find_repo_root()
    folder = args.output or root / "Semana9/resultados"
    print(json.dumps(evaluate_run(root, folder, args.threshold), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
