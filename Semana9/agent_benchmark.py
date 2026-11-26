"""Semana 9: tres políticas sobre SQuAD dev completo, sin LLM en el benchmark.

A0 top-1, A1 top-3 y B expansión condicionada. El umbral de B se calibra
solo con artículos de desarrollo. La evaluación usa otros artículos.
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
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .prepare_real_data import EXPECTED_PASSAGES, EXPECTED_QUESTIONS, verify

TOKEN_RE = re.compile(r"\w+", re.UNICODE)
CANDIDATE_THRESHOLDS = (0.0, 0.15, 0.25, 0.35, 0.45, 0.55, 0.65, 0.75, 0.85, 1.01)
MAX_ALLOWED_LOSS = 0.02  # Dos puntos porcentuales absolutos frente a top-3, en calibración.


def tokens(text: str) -> list[str]:
    return TOKEN_RE.findall(text.casefold())


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as stream:
        return [json.loads(line) for line in stream if line.strip()]


def find_repo_root(start: Path | None = None) -> Path:
    base = (start or Path.cwd()).resolve()
    for ancestor in (base, *base.parents):
        if (ancestor / "Semana9" / "agent_benchmark.py").is_file():
            return ancestor
    raise FileNotFoundError("No se encontró Semana9 en la raíz de CC-0F4")


def real_paths(root: Path) -> dict[str, Path]:
    folder = root / "Semana9" / "datos_reales"
    verify(folder)
    return {"corpus": folder / "corpus.jsonl", "queries": folder / "queries.jsonl",
            "qrels": folder / "qrels.json", "answers": folder / "respuestas_humanas.jsonl"}


@dataclass(frozen=True)
class Passage:
    passage_id: str
    text: str
    doc_id: str


class BM25Tool:
    """BM25 invertido: recupera en todo el corpus sin hacer scan por consulta.

    Las puntuaciones cero se ordenan por ID. La herramienta de agente sigue
    restringiendo top_k a 1..5 en agent_loop.py.
    """
    def __init__(self, corpus: list[dict[str, Any]]):
        self.passages = [
            Passage(p["passage_id"], p["text"], document["doc_id"])
            for document in corpus for p in document["passages"]
        ]
        if not self.passages:
            raise ValueError("No hay pasajes que indexar")
        self.by_id = {p.passage_id: p for p in self.passages}
        if len(self.by_id) != len(self.passages):
            raise ValueError("IDs de pasajes duplicados")
        self.passages.sort(key=lambda p: p.passage_id)
        self.sizes = [len(tokens(p.text)) for p in self.passages]
        self.avgdl = statistics.mean(self.sizes)
        self.postings: dict[str, list[tuple[int, int]]] = defaultdict(list)
        for i, passage in enumerate(self.passages):
            for term, frequency in Counter(tokens(passage.text)).items():
                self.postings[term].append((i, frequency))
        n = len(self.passages)
        self.idf = {term: math.log(1 + (n - len(posting) + 0.5) /
                                    (len(posting) + 0.5))
                    for term, posting in self.postings.items()}

    def search(self, query: str, top_k: int) -> list[dict[str, Any]]:
        if type(top_k) is not int or not (1 <= top_k <= 20):
            raise ValueError("top_k debe estar en el rango [1, 20]")
        if not isinstance(query, str) or not query.strip():
            raise ValueError("La consulta debe ser texto no vacío")
        scores: dict[int, float] = defaultdict(float)
        k1, b = 1.5, 0.75
        for term in set(tokens(query)):
            idf = self.idf.get(term, 0.0)
            for i, freq in self.postings.get(term, ()):
                denom = freq + k1 * (1 - b + b * self.sizes[i] / self.avgdl)
                scores[i] += idf * freq * (k1 + 1) / denom
        order = sorted(range(len(self.passages)), key=lambda i: (-scores.get(i, 0.0), self.passages[i].passage_id))[:top_k]
        return [{"passage_id": self.passages[i].passage_id,
                 "doc_id": self.passages[i].doc_id,
                 "score": round(scores.get(i, 0.0), 8),
                 "text": self.passages[i].text} for i in order]


def lexical_coverage(query: str, evidence: str) -> float:
    words = set(tokens(query))
    return len(words & set(tokens(evidence))) / len(words) if words else 0.0


def run_workflow(query: str, tool: BM25Tool, top_k: int = 3) -> dict[str, Any]:
    if top_k not in (1, 3):
        raise ValueError("La política fija admite solo top-1 o top-3")
    tic = time.perf_counter()
    ranking = tool.search(query, top_k)
    ids = [p["passage_id"] for p in ranking]
    return {"policy": f"workflow_fixed_top{top_k}", "citations": ids,
            "answer_excerpt": ranking[0]["text"] if ranking else "",
            "steps": 1, "tool_calls": 1, "stop_reason": "completed",
            "latency_ms": round((time.perf_counter()-tic)*1000, 3),
            "trace": [{"step": 1, "action": "search", "top_k": top_k,
                       "observation_ids": ids, "stop": "completed"}]}


def run_adaptive(query: str, tool: BM25Tool, threshold: float = 0.45) -> dict[str, Any]:
    if not 0 <= threshold <= 1.01:
        raise ValueError("Umbral de confianza fuera de rango")
    tic = time.perf_counter()
    first = tool.search(query, 1)
    coverage = lexical_coverage(query, first[0]["text"])
    trace = [{"step": 1, "action": "search", "top_k": 1,
              "observation_ids": [p["passage_id"] for p in first],
              "lexical_coverage": round(coverage, 4)}]
    if coverage < threshold:
        found = tool.search(query, 3)
        trace.append({"step": 2, "action": "search", "top_k": 3,
                      "observation_ids": [p["passage_id"] for p in found],
                      "stop": "completed_after_expansion"})
    else:
        found = first
        trace[-1]["stop"] = "completed_without_expansion"
    return {"policy": "adaptive_rule_based", "citations": [p["passage_id"] for p in found],
            "answer_excerpt": found[0]["text"] if found else "",
            "steps": len(trace), "tool_calls": len(trace),
            "stop_reason": trace[-1]["stop"],
            "latency_ms": round((time.perf_counter()-tic)*1000, 3), "trace": trace}


def _precompute(queries: list[dict], qrels: dict, tool: BM25Tool) -> list[dict]:
    """Ranking común por pregunta para evitar repetir BM25 tres veces."""
    rows = []
    for q in queries:
        ranked = tool.search(q["query"], 10)
        ids = [x["passage_id"] for x in ranked]
        gold = set(qrels[q["query_id"]])
        rank = next((i for i, value in enumerate(ids, start=1) if value in gold), None)
        rows.append({"query_id": q["query_id"], "query": q["query"],
                     "split": q["split"], "article": q["source_title"],
                     "passage_id": q["passage_id"], "top_ids": ids,
                     "top1_coverage": lexical_coverage(q["query"], ranked[0]["text"]),
                     "rank_at10": rank, "hit_top1": int(rank == 1),
                     "hit_top3": int(rank is not None and rank <= 3),
                     "hit_top5": int(rank is not None and rank <= 5)})
    return rows


def _policy_for(row: dict, threshold: float, size_by_id: dict[str, int]) -> list[dict]:
    ids = row["top_ids"]
    policies = (("workflow_fixed_top1", 1, 1, "completed"),
                ("workflow_fixed_top3", 3, 1, "completed"))
    expanded = row["top1_coverage"] < threshold
    conditions = list(policies) + [("adaptive_rule_based", 3 if expanded else 1,
                                    2 if expanded else 1,
                                    "completed_after_expansion" if expanded else "completed_without_expansion")]
    result = []
    for name, k, calls, stop in conditions:
        citations = ids[:k]
        hit = int(row["passage_id"] in citations)
        result.append({
            "query_id": row["query_id"], "split": row["split"], "article": row["article"],
            "policy": name, "evidence_hit": hit, "evidence_count": k,
            "tool_calls": calls, "steps": calls,
            "context_word_proxy": sum(size_by_id[pid] for pid in citations),
            "stop_reason": stop, "top1_coverage": round(row["top1_coverage"], 4),
            "citations": "|".join(citations),
            "gold_passage_id": row["passage_id"],
            "rank_at10": row["rank_at10"] if row["rank_at10"] else "",
        })
    return result


def calibrate_threshold(rows: list[dict], sizes: dict[str, int]) -> tuple[float, list[dict]]:
    """Optimiza compromiso usando solo calibración, nunca evaluación."""
    development = [x for x in rows if x["split"] == "calibration"]
    if not development:
        raise ValueError("Sin preguntas de calibración")
    trials = []
    for threshold in CANDIDATE_THRESHOLDS:
        results = [_policy_for(row, threshold, sizes)[2] for row in development]
        baseline = [_policy_for(row, threshold, sizes)[1] for row in development]
        loss = statistics.mean(b["evidence_hit"] - a["evidence_hit"] for a, b in zip(results, baseline))
        saved_words = statistics.mean(b["context_word_proxy"] - a["context_word_proxy"] for a, b in zip(results, baseline))
        extra_calls = statistics.mean(a["tool_calls"] - b["tool_calls"] for a, b in zip(results, baseline))
        # Escala docente explicita: 40 palabras de ahorro equivalen a una búsqueda adicional.
        utility = saved_words - 40 * extra_calls
        trials.append({"threshold": threshold, "absolute_hit_loss": round(loss, 8),
                       "mean_words_saved": round(saved_words, 5),
                       "mean_extra_calls": round(extra_calls, 5),
                       "selection_utility": round(utility, 5),
                       "meets_loss_limit": loss <= MAX_ALLOWED_LOSS + 1e-12})
    eligible = [x for x in trials if x["meets_loss_limit"]]
    chosen = (max(eligible, key=lambda x: (x["selection_utility"], -x["threshold"]))
              if eligible else
              min(trials, key=lambda x: (x["absolute_hit_loss"], -x["selection_utility"])))
    return chosen["threshold"], trials


def _summary(rows: list[dict]) -> dict:
    answer = {}
    for policy in ("workflow_fixed_top1", "workflow_fixed_top3", "adaptive_rule_based"):
        sub = [r for r in rows if r["policy"] == policy]
        answer[policy] = {"queries": len(sub),
                          "evidence_hit_rate": round(statistics.mean(r["evidence_hit"] for r in sub), 6),
                          "mean_tool_calls": round(statistics.mean(r["tool_calls"] for r in sub), 6),
                          "mean_context_words": round(statistics.mean(r["context_word_proxy"] for r in sub), 2)}
    return answer


def evaluate_run(root: Path, output_dir: Path | None = None,
                 threshold: float | None = None) -> dict[str, Any]:
    paths = real_paths(root)
    corpus = jsonl(paths["corpus"])
    queries = jsonl(paths["queries"])
    qrels = json.loads(paths["qrels"].read_text(encoding="utf-8"))
    if len(queries) != EXPECTED_QUESTIONS or len({q["query_id"] for q in queries}) != EXPECTED_QUESTIONS:
        raise ValueError("No están presentes las 10.570 preguntas originales")
    if set(qrels) != {q["query_id"] for q in queries}:
        raise ValueError("Consultas y qrels no coinciden")
    tool = BM25Tool(corpus)
    if len(tool.passages) != EXPECTED_PASSAGES:
        raise ValueError("Se requieren todos los 2.067 pasajes")
    if any(not set(v).issubset(tool.by_id) for v in qrels.values()):
        raise ValueError("Hay referencias a pasajes inexistentes")
    size_by_id = {p.passage_id: len(tokens(p.text)) for p in tool.passages}
    t0 = time.perf_counter()
    ranked = _precompute(queries, qrels, tool)
    calibrated_threshold, trials = calibrate_threshold(ranked, size_by_id)
    selected = calibrated_threshold if threshold is None else threshold
    if not 0 <= selected <= 1.01:
        raise ValueError("Umbral fuera de rango")
    records = [item for row in ranked for item in _policy_for(row, selected, size_by_id)]
    calibration_rows = [r for r in records if r["split"] == "calibration"]
    evaluation_rows = [r for r in records if r["split"] == "evaluation"]
    if set(r["article"] for r in calibration_rows) & set(r["article"] for r in evaluation_rows):
        raise AssertionError("Fuga entre artículos de calibración y evaluación")
    retrieval_evaluation = [r for r in ranked if r["split"] == "evaluation"]
    result = {
        "experiment": "Semana9 SQuAD 1.1 dev COMPLETO, BM25 y controlador sin LLM",
        "source": "SQuAD 1.1 dev, párrafos de Wikipedia y preguntas originales",
        "sample_size": len(queries), "passages": len(tool.passages),
        "calibration_queries": sum(q["split"] == "calibration" for q in queries),
        "evaluation_queries": len(retrieval_evaluation),
        "evaluation_articles": len({r["article"] for r in retrieval_evaluation}),
        "selected_threshold": selected, "threshold_origin": "calibration" if threshold is None else "manual_override_not_confirmatory",
        "calibration_trials": trials,
        "calibration_results": _summary(calibration_rows),
        "evaluation_results": _summary(evaluation_rows),
        "retrieval_evaluation": {
            "recall_at_1": round(statistics.mean(r["hit_top1"] for r in retrieval_evaluation), 6),
            "recall_at_3": round(statistics.mean(r["hit_top3"] for r in retrieval_evaluation), 6),
            "recall_at_5": round(statistics.mean(r["hit_top5"] for r in retrieval_evaluation), 6),
            "mrr_at_10": round(statistics.mean(1/r["rank_at10"] if r["rank_at10"] else 0 for r in retrieval_evaluation), 6),
        },
        "seconds_local_bm25_and_processing": round(time.perf_counter()-t0, 3),
        "data_sha256": {k: sha256(v) for k, v in paths.items()},
        "not_measured": ["corrección semántica de respuestas", "eficacia de un agente LLM", "precio de API"],
        "limitations": [
            "Qrels identifican pasaje con respuesta, no relevancia exhaustiva",
            "Los 48 artículos pertenecen a SQuAD dev público, no a su test oculto",
            "B usa el mismo ranking y por construcción no supera top-3 en hit",
            "No confundir la simulación offline de políticas con inferencia LLM",
        ],
    }
    if output_dir:
        output_dir.mkdir(parents=True, exist_ok=True)
        with (output_dir / "runs.csv").open("w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(records[0])); writer.writeheader(); writer.writerows(records)
        with (output_dir / "traces.jsonl").open("w", encoding="utf-8") as stream:
            for row in records:
                stream.write(json.dumps({"query_id": row["query_id"], "policy": row["policy"],
                                         "observed_ids": row["citations"].split("|"),
                                         "gold_id_not_used_by_policy": row["gold_passage_id"],
                                         "stop_reason": row["stop_reason"],
                                         "tool_calls": row["tool_calls"]}, ensure_ascii=False) + "\n")
        (output_dir / "summary.json").write_text(json.dumps(result, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    return result


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--threshold", type=float, help="Solo para análisis exploratorio, no calibración confirmatoria")
    p.add_argument("--output", type=Path)
    args = p.parse_args()
    root = find_repo_root()
    print(json.dumps(evaluate_run(root, args.output or root / "Semana9" / "resultados", args.threshold),
                     ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
