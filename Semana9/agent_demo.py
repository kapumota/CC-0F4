"""Demostración de agente acotado. Scripted es una prueba, no un LLM."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from .agent_benchmark import BM25Tool, find_repo_root, jsonl, real_paths
from .agent_loop import Limits, RestrictedTools, ScriptedPolicy, run_agent


def demo(root: Path, policy_name: str = "scripted", query_id: str = "Q01",
         model_id: str = "Qwen/Qwen2.5-0.5B-Instruct") -> dict:
    paths = real_paths(root)
    queries = jsonl(paths["queries"])
    corpus = jsonl(paths["corpus"])
    q = next((q for q in queries if q["query_id"] == query_id), None)
    if q is None:
        raise ValueError(f"query_id no encontrado: {query_id}")
    tools = RestrictedTools(BM25Tool(corpus))
    if policy_name == "scripted":
        expected_id = tools.bm25.search(q["query"], 3)[0]["passage_id"]
        policy = ScriptedPolicy([
            {"action": "search_documents", "arguments": {"query": q["query"], "top_k": 3}},
            {"action": "read_passage", "arguments": {"passage_id": expected_id}},
            {"action": "finish", "arguments": {
                "answer": "Se recupero un fragmento de la fuente real para revision humana.",
                "citations": [expected_id]}},
        ])
    elif policy_name == "llm":
        from .agent_policy import LocalTransformersPolicy
        policy = LocalTransformersPolicy(model_id=model_id)
    else:
        raise ValueError("Politica invalida")
    result = run_agent(q["query"], policy, tools,
                       Limits(max_steps=6, max_tool_calls=3, deadline_seconds=180 if policy_name == "llm" else 20))
    result["policy_name"] = policy_name
    result["model_id"] = model_id if policy_name == "llm" else None
    result["query_id"] = query_id
    result["not_measured"] = ["correccion semantica automatica", "costo monetario"]
    return result


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--policy", choices=("scripted", "llm"), default="scripted")
    p.add_argument("--query-id", default="Q01")
    p.add_argument("--model-id", default="Qwen/Qwen2.5-0.5B-Instruct")
    p.add_argument("--output", type=Path)
    args = p.parse_args()
    result = demo(find_repo_root(), args.policy, args.query_id, args.model_id)
    result_json = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(result_json + "\n", encoding="utf-8")
    print(result_json)


if __name__ == "__main__":
    main()
