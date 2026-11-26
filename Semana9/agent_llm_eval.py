"""Evaluación REAL de Qwen local frente a un workflow fijo, en preguntas SQuAD.

No admite respuestas prefabricadas. Si no hay modelo, se detiene con error.
Usa las MISMAS preguntas y el MISMO modelo en las dos condiciones.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import string
import time
from pathlib import Path
from statistics import mean

from .agent_benchmark import BM25Tool, find_repo_root, jsonl, real_paths
from .agent_loop import Limits, RestrictedTools, run_agent
from .agent_policy import LocalTransformersPolicy


def normalize_answer(text: str) -> str:
    """Normalización SQuAD en inglés: minúsculas, puntuación, artículos y espacios."""
    t = text.lower()
    t = "".join(ch for ch in t if ch not in string.punctuation)
    t = re.sub(r"\b(a|an|the)\b", " ", t)
    return " ".join(t.split())


def exact_match(prediction: str, ground_truths: list[str]) -> float:
    if not ground_truths:
        raise ValueError("Se requieren anotaciones humanas originales")
    return float(any(normalize_answer(prediction) == normalize_answer(ref) for ref in ground_truths))


def token_f1(prediction: str, ground_truths: list[str]) -> float:
    if not ground_truths:
        raise ValueError("Se requieren anotaciones humanas originales")
    from collections import Counter
    a = normalize_answer(prediction).split()
    def score(reference: str) -> float:
        b = normalize_answer(reference).split()
        common = sum((Counter(a) & Counter(b)).values())
        if not a or not b:
            return float(a == b)
        if not common:
            return 0.0
        precision, recall = common / len(a), common / len(b)
        return 2 * precision * recall / (precision + recall)
    return max(score(r) for r in ground_truths)


def select_evaluation_questions(queries: list[dict], n: int) -> list[dict]:
    """Muestra determinista de test; se selecciona sin usar respuestas ni qrels."""
    test = [q for q in queries if q["split"] == "evaluation"]
    if len(test) < n or n < 1:
        raise ValueError("Solicita 1..N consultas disponibles exclusivamente de evaluación")
    return sorted(test, key=lambda q: hashlib.sha256(q["source_question_id"].encode()).hexdigest())[:n]


def fixed_answer(policy: LocalTransformersPolicy, question: str,
                 retrieved: list[dict], max_new_tokens: int = 96) -> tuple[str, int, int]:
    """Generación con el MISMO modelo que decide acciones en el otro sistema."""
    tokenizer, model, torch = policy.tokenizer, policy.model, policy.torch
    context = "\n\n".join(
        f"[{r['passage_id']}] {r['text'][:1000]}" for r in retrieved
    )
    user = ("Contesta brevemente la pregunta en inglés usando solo los pasajes. "
            "Si no aparece la respuesta, di 'I do not know'.\n"
            f"Pregunta: {question}\n\nEvidencia:\n{context}\n\nRespuesta:")
    messages = [{"role": "user", "content": user}]
    raw = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    inputs = tokenizer(raw, return_tensors="pt").to(model.device)
    prompt_length = int(inputs["input_ids"].shape[1])
    with torch.no_grad():
        out = model.generate(**inputs, max_new_tokens=max_new_tokens, do_sample=False,
                             pad_token_id=tokenizer.eos_token_id)
    return (tokenizer.decode(out[0, prompt_length:], skip_special_tokens=True).strip(),
            prompt_length, int(len(out[0]) - prompt_length))


def run_real_pilot(root: Path, n: int = 100,
                   model_id: str = "Qwen/Qwen2.5-0.5B-Instruct",
                   output_dir: Path | None = None) -> dict:
    """Requiere pesos Qwen reales, no usa una política guionizada."""
    paths = real_paths(root)
    corpus, queries, human = jsonl(paths["corpus"]), jsonl(paths["queries"]), jsonl(paths["answers"])
    if len(queries) != 10570:
        raise ValueError("Solo se admite SQuAD dev completo")
    answer_map = {x["query_id"]: x["human_answers"] for x in human}
    selected = select_evaluation_questions(queries, n)
    bm25 = BM25Tool(corpus)
    tools = RestrictedTools(bm25)
    # Si faltan transformers/pesos no se generan métricas ni se inventa un reemplazo.
    model = LocalTransformersPolicy(model_id=model_id)
    output_dir = output_dir or root / "Semana9" / "resultados" / "llm_real"
    output_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    tracefile = output_dir / "trazas_llm.jsonl"
    tic = time.time()
    with tracefile.open("w", encoding="utf-8") as traces:
        for idx, q in enumerate(selected, start=1):
            question, qid = q["query"], q["query_id"]
            references = answer_map[qid]
            retrieved = bm25.search(question, 3)
            started = time.perf_counter()
            answer_fixed, input_length, output_length = fixed_answer(model, question, retrieved)
            fixed_elapsed = round(time.perf_counter()-started, 3)
            # Control de agente: Qwen elige acciones y genera la respuesta.
            started = time.perf_counter()
            agent = run_agent(question, model, tools, Limits(
                max_steps=6, max_tool_calls=3, max_invalid_actions=2,
                deadline_seconds=180, max_observation_chars=1200,
                max_total_tokens=12000))
            agent_elapsed = round(time.perf_counter()-started, 3)
            for policy_name, answer, citations, elapsed, reason, calls in (
                ("fixed_qwen_top3", answer_fixed,
                 [p["passage_id"] for p in retrieved], fixed_elapsed, "completed", 1),
                ("agent_qwen", agent["answer"], agent["citations"],
                 agent_elapsed, agent["stop_reason"], agent["tool_calls"]),
            ):
                rows.append({
                    "query_id": qid, "source_question_id": q["source_question_id"],
                    "condition": policy_name, "exact_match": exact_match(answer, references),
                    "f1": round(token_f1(answer, references), 6),
                    "gold_passage_cited": int(q["passage_id"] in citations),
                    "citations_count": len(citations),
                    "elapsed_s": elapsed, "tool_calls": calls,
                    "stop_reason": reason, "answer": answer,
                    "citations": "|".join(citations),
                })
            traces.write(json.dumps({"query_id": qid, "question": question,
                "fixed_answer": answer_fixed, "fixed_prompt_tokens": input_length,
                "fixed_generated_tokens": output_length,
                "agent": agent}, ensure_ascii=False) + "\n")
            if idx % 10 == 0:
                print(f"Procesadas {idx}/{len(selected)} consultas de evaluación real")
    with (output_dir / "comparacion_llm.csv").open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)
    result = {"dataset": "SQuAD 1.1 dev, evaluación por artículos",
              "queries": len(selected), "conditions": ["fixed_qwen_top3", "agent_qwen"],
              "model_id": model_id, "model_revision": getattr(model.model.config, "_commit_hash", None),
              "source_sha256": json.loads((root/"Semana9"/"datos_reales"/"manifest.json").read_text(encoding="utf-8"))["source_sha256"],
              "started_epoch_s": tic,
              "limitations": [
                  "Piloto sobre un subconjunto de evaluación, no estimador de toda SQuAD",
                  "EM/F1 comparan respuesta con respuestas humanas; no miden entailment de citas",
                  "No incluye evaluación humana de apoyo factual, necesaria para conclusiones de grounding",
                  "Los pasajes citados se comprueban contra el origen; otras evidencias podrían ser suficientes",
              ],
              "metrics": {}}
    for name in result["conditions"]:
        sub = [r for r in rows if r["condition"] == name]
        result["metrics"][name] = {
            "exact_match": round(mean(r["exact_match"] for r in sub), 6),
            "token_f1": round(mean(r["f1"] for r in sub), 6),
            "gold_passage_cited": round(mean(r["gold_passage_cited"] for r in sub), 6),
            "mean_tool_calls": round(mean(r["tool_calls"] for r in sub), 4),
            "mean_elapsed_s": round(mean(r["elapsed_s"] for r in sub), 3),
        }
    (output_dir / "resumen_llm.json").write_text(json.dumps(result, indent=2, ensure_ascii=False)+"\n", encoding="utf-8")
    return result


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--n", type=int, default=100, help="Número de consultas reales, solo test, piloto")
    p.add_argument("--model-id", default="Qwen/Qwen2.5-0.5B-Instruct")
    p.add_argument("--output", type=Path)
    a = p.parse_args()
    root = find_repo_root()
    print(json.dumps(run_real_pilot(root, a.n, a.model_id, a.output), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
