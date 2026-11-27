"""Semana 11: recuperación HotpotQA y comparación local de agentes.

La recuperación usa las 7.405 preguntas originales, con evidencia humana.
El piloto LLM es opcional y sus resultados solo existen después de inferencia real.
La búsqueda se limita al contexto distractor provisto para cada pregunta.
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import math
import re
import shutil
import string
import time
import urllib.request
from pathlib import Path
from typing import Any

from .contratos import Blackboard, ContractError, make_message, validate_selection

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "datos" / "hotpot_dev_distractor_v1.json"
OUT = ROOT / "resultados"
URLS = (
    "https://curtis.ml.cmu.edu/datasets/hotpot/hotpot_dev_distractor_v1.json",
    "http://curtis.ml.cmu.edu/datasets/hotpot/hotpot_dev_distractor_v1.json",
)
OFFICIAL_SHA256 = "4e9ecb5c8d3b719f624d66b60f8d56bf227f03914f5f0753d6fa1b359d7104ea"
MODEL_ID = "Qwen/Qwen2.5-1.5B-Instruct"
TOKEN = re.compile(r"[a-z0-9]+", re.IGNORECASE)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def check_dataset(path: Path = DATA) -> list[dict[str, Any]]:
    """Comprueba integridad y esquema sin fabricar valores ausentes."""
    if not path.is_file():
        raise FileNotFoundError(f"No existe {path}. Ejecuta --preparar antes de clase.")
    observed = sha256_file(path)
    if observed != OFFICIAL_SHA256:
        raise ValueError(f"SHA-256 HotpotQA incorrecto: {observed}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list) or len(data) != 7405:
        raise ValueError("HotpotQA no contiene las 7.405 preguntas esperadas")
    ids = set()
    required = {"_id", "question", "answer", "supporting_facts", "context"}
    for item in data:
        if not isinstance(item, dict) or not required.issubset(item):
            raise ValueError("Ejemplo HotpotQA con esquema incompleto")
        if item["_id"] in ids:
            raise ValueError("ID HotpotQA duplicado")
        ids.add(item["_id"])
        if not isinstance(item["context"], list) or not isinstance(item["supporting_facts"], list):
            raise ValueError("Contexto o evidencia humana malformada")
    return data


def prepare(origin: str | None = None) -> dict[str, Any]:
    """Descarga una sola vez el archivo oficial, con hash completo."""
    DATA.parent.mkdir(parents=True, exist_ok=True)
    if DATA.exists():
        data = check_dataset()
        return {"status": "YA_VERIFICADO", "questions": len(data), "sha256": OFFICIAL_SHA256}
    temp = DATA.with_suffix(".part")
    temp.unlink(missing_ok=True)
    try:
        if origin:
            shutil.copyfile(origin, temp)
            check_dataset(temp)
        else:
            last_error: Exception | None = None
            for url in URLS:
                try:
                    request = urllib.request.Request(url, headers={"User-Agent": "CC0F4-docente"})
                    with urllib.request.urlopen(request, timeout=120) as response, temp.open("wb") as target:
                        shutil.copyfileobj(response, target)
                    check_dataset(temp)
                    last_error = None
                    break
                except Exception as exc:
                    last_error = exc
                    temp.unlink(missing_ok=True)
            if last_error is not None:
                raise RuntimeError("No se pudo descargar HotpotQA. Usa --origen con el archivo oficial. No se usan datos sustitutos.") from last_error
        temp.replace(DATA)
        return {"status": "PREPARADO", "questions": 7405, "sha256": OFFICIAL_SHA256}
    finally:
        temp.unlink(missing_ok=True)


def words(value: str) -> list[str]:
    return TOKEN.findall(str(value).casefold())


def ranked_evidence(example: dict[str, Any], top_k: int = 14) -> list[dict[str, Any]]:
    """BM25 por oración sobre el contexto de la propia pregunta, sin gold."""
    if not 1 <= top_k <= 50:
        raise ValueError("top_k debe estar entre 1 y 50")
    entries = [(str(title), index, str(sentence))
               for title, sentences in example["context"]
               for index, sentence in enumerate(sentences)]
    if not entries:
        raise ValueError("Pregunta sin oraciones disponibles")
    tokenized = [words(text) for _, _, text in entries]
    df: collections.Counter[str] = collections.Counter()
    for tokens in tokenized:
        df.update(set(tokens))
    n = len(entries)
    avgdl = sum(map(len, tokenized)) / n or 1.0
    query = set(words(example["question"]))
    scored = []
    for index, tokens in enumerate(tokenized):
        tf = collections.Counter(tokens)
        dl = len(tokens)
        score = sum(
            math.log(1.0 + (n - df[term] + 0.5) / (df[term] + 0.5))
            * tf[term] * 2.2 / (tf[term] + 1.2 * (0.25 + 0.75 * dl / avgdl))
            for term in query if tf[term]
        )
        scored.append((score, index))
    scored.sort(key=lambda value: (-value[0], value[1]))
    return [{"id": f"E{rank:02d}", "title": entries[index][0],
             "sent_id": entries[index][1], "text": entries[index][2],
             "bm25": round(score, 6)}
            for rank, (score, index) in enumerate(scored[:top_k])]


def gold_facts(example: dict[str, Any]) -> set[tuple[str, int]]:
    return {(str(title), int(index)) for title, index in example["supporting_facts"]}


def support_recall(example: dict[str, Any], evidence: list[dict[str, Any]]) -> float:
    gold = gold_facts(example)
    predicted = {(entry["title"], entry["sent_id"]) for entry in evidence}
    return len(gold & predicted) / len(gold) if gold else 0.0


def retrieval_rows(data: list[dict[str, Any]], top_k: int = 14) -> list[dict[str, Any]]:
    rows = []
    for example in data:
        evidence = ranked_evidence(example, top_k)
        gold = gold_facts(example)
        found = {(x["title"], x["sent_id"]) for x in evidence}
        common = len(gold & found)
        rows.append({
            "question_id": example["_id"], "level": example.get("level", ""),
            "type": example.get("type", ""), "n_gold": len(gold),
            "n_observed": len(evidence), "n_support_found": common,
            "support_recall": common / len(gold) if gold else 0.0,
            "any_support": int(common > 0),
            "all_support": int(bool(gold) and common == len(gold)),
        })
    return rows


def summarize_retrieval(rows: list[dict[str, Any]], top_k: int = 14) -> dict[str, Any]:
    if not rows:
        raise ValueError("No hay preguntas para resumir")
    def aggregate(subset: list[dict[str, Any]]) -> dict[str, Any]:
        size = len(subset)
        return {"questions": size,
                "mean_support_recall": sum(x["support_recall"] for x in subset) / size,
                "any_support_rate": sum(x["any_support"] for x in subset) / size,
                "all_support_rate": sum(x["all_support"] for x in subset) / size}
    by_type = {k: aggregate([r for r in rows if r["type"] == k])
               for k in sorted({r["type"] for r in rows})}
    by_level = {k: aggregate([r for r in rows if r["level"] == k])
                for k in sorted({r["level"] for r in rows})}
    return {"benchmark": "HotpotQA dev distractor original", "questions": len(rows),
            "source_sha256": OFFICIAL_SHA256, "top_k": top_k,
            "retrieval": aggregate(rows), "by_type": by_type, "by_level": by_level,
            "scope": "Recuperación de oraciones del contexto provisto; SIN generación de respuestas",
            "limitations": [
                "Cada pregunta trae su propio conjunto de párrafos distractores; no es recuperación sobre un corpus abierto",
                "No se utiliza el gold para recuperar, solo para calificar",
                "La presencia de evidencia no equivale a una respuesta correcta",
            ]}


def evaluate_retrieval(top_k: int = 14) -> dict[str, Any]:
    examples = check_dataset()
    rows = retrieval_rows(examples, top_k)
    summary = summarize_retrieval(rows, top_k)
    OUT.mkdir(parents=True, exist_ok=True)
    filename = OUT / f"hotpot_recuperacion_{len(examples)}_por_consulta.jsonl"
    with filename.open("w", encoding="utf-8") as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False) + "\n")
    (OUT / "hotpot_recuperacion_resumen.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return summary


def parse_json_strict(raw: str) -> dict[str, Any] | None:
    """No repara errores de formato del modelo de manera silenciosa."""
    try:
        parsed = json.loads(raw.strip())
    except (json.JSONDecodeError, TypeError):
        return None
    return parsed if isinstance(parsed, dict) else None


class LocalLLM:
    """El mismo checkpoint real se usa para las dos condiciones."""
    def __init__(self, model_id: str = MODEL_ID, max_input_tokens: int = 4096):
        try:
            import torch
            from transformers import AutoModelForCausalLM, AutoTokenizer
        except ImportError as exc:
            raise RuntimeError("Se requiere torch y transformers en Docker; no hay respuestas simuladas") from exc
        self.torch = torch
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model_id = model_id
        self.max_input_tokens = max_input_tokens
        self.tokenizer = AutoTokenizer.from_pretrained(model_id)
        self.model = AutoModelForCausalLM.from_pretrained(model_id).to(self.device)
        self.model.eval()
        try:
            self.revision = self.model.config._commit_hash
        except AttributeError:
            self.revision = None
        torch.manual_seed(2026)
        print("Modelo cargado:", model_id, "| dispositivo:", self.device)

    def ask(self, system: str, user: str, max_new_tokens: int = 192) -> dict[str, Any]:
        turns = [{"role": "system", "content": system}, {"role": "user", "content": user}]
        formatted = self.tokenizer.apply_chat_template(turns, tokenize=False, add_generation_prompt=True)
        encoded = self.tokenizer(formatted, return_tensors="pt")
        prompt_tokens = int(encoded["input_ids"].shape[1])
        if prompt_tokens > self.max_input_tokens:
            return {"raw": "", "parsed": None, "prompt_tokens": prompt_tokens,
                    "generated_tokens": 0, "error": "PRESUPUESTO_CONTEXTO"}
        encoded = encoded.to(self.device)
        with self.torch.inference_mode():
            result = self.model.generate(**encoded, max_new_tokens=max_new_tokens,
                                         do_sample=False,
                                         pad_token_id=self.tokenizer.eos_token_id)
        generated = result[0, prompt_tokens:]
        raw = self.tokenizer.decode(generated, skip_special_tokens=True)
        return {"raw": raw, "parsed": parse_json_strict(raw),
                "prompt_tokens": prompt_tokens, "generated_tokens": int(generated.shape[0]),
                "error": None}


def evidence_text(observed: list[dict[str, Any]]) -> str:
    return "\n".join(f"{item['id']} [{item['title']}#{item['sent_id']}]: {item['text']}"
                     for item in observed)


def validate_answer(parsed: dict[str, Any] | None,
                    observed: list[dict[str, Any]]) -> tuple[bool, str, str, list[str]]:
    if parsed is None:
        return False, "JSON_INVALIDO", "", []
    if set(parsed) != {"answer", "cited_ids"}:
        return False, "ESQUEMA_RESPUESTA", "", []
    answer, citations = parsed["answer"], parsed["cited_ids"]
    if not isinstance(answer, str) or not answer.strip():
        return False, "RESPUESTA_VACIA", "", []
    if not isinstance(citations, list) or not citations or any(not isinstance(x, str) for x in citations):
        return False, "CITAS_MALFORMADAS", "", []
    if len(set(citations)) != len(citations):
        return False, "CITAS_DUPLICADAS", "", []
    available = {item["id"] for item in observed}
    if not set(citations).issubset(available):
        return False, "CITA_NO_OBSERVADA", "", []
    return True, "FINALIZACION_ESTRUCTURAL", answer.strip(), citations


def agent_single(llm: LocalLLM, example: dict[str, Any],
                 observed: list[dict[str, Any]]) -> dict[str, Any]:
    start = time.perf_counter()
    output = llm.ask(
        'Answer using only observed evidence. Return one strict JSON object with exactly: {"answer":"...","cited_ids":["E00"]}.',
        "Question: " + example["question"] + "\nEvidence:\n" + evidence_text(observed))
    ok, reason, answer, citations = validate_answer(output["parsed"], observed)
    return {"valid": ok, "stop_reason": output["error"] or reason,
            "answer": answer, "cited_ids": citations, "observed": observed,
            "model_calls": 1, "prompt_tokens": output["prompt_tokens"],
            "generated_tokens": output["generated_tokens"],
            "elapsed_s": time.perf_counter() - start,
            "trace": [{"role": "single", "raw": output["raw"], "error": output["error"]}]}


def agent_supervisor_workers(llm: LocalLLM, example: dict[str, Any],
                             observed: list[dict[str, Any]]) -> dict[str, Any]:
    start = time.perf_counter()
    question_id = example["_id"]
    blackboard = Blackboard(question_id)
    first = llm.ask(
        'You are evidence worker. Select 1 to 6 observed IDs. Return strict JSON with exactly: {"selected_ids":["E00"]}.',
        "Question: " + example["question"] + "\nEvidence:\n" + evidence_text(observed), 100)
    calls, prompt_tokens, generated_tokens = 1, first["prompt_tokens"], first["generated_tokens"]
    trace = [{"role": "evidence_worker", "raw": first["raw"], "error": first["error"]}]
    try:
        if first["parsed"] is None:
            raise ContractError("WORKER_JSON_INVALIDO")
        if set(first["parsed"]) != {"selected_ids"}:
            raise ContractError("WORKER_ESQUEMA_INVALIDO")
        selected_ids = validate_selection(first["parsed"]["selected_ids"], observed, max_items=6)
        message = make_message(question_id, "evidence_worker", selected_ids, observed)
        blackboard.append(message, observed)
        selection = [entry for entry in observed if entry["id"] in selected_ids]
    except (ContractError, TypeError, KeyError) as exc:
        return {"valid": False, "stop_reason": first["error"] or str(exc), "answer": "",
                "cited_ids": [], "observed": observed, "model_calls": calls,
                "prompt_tokens": prompt_tokens, "generated_tokens": generated_tokens,
                "elapsed_s": time.perf_counter() - start, "trace": trace,
                "blackboard": blackboard.messages}
    second = llm.ask(
        'You are answer worker. Use only selected evidence. Return strict JSON with exactly: {"answer":"...","cited_ids":["E00"]}.',
        "Question: " + example["question"] + "\nSelected evidence:\n" + evidence_text(selection))
    calls += 1
    prompt_tokens += second["prompt_tokens"]
    generated_tokens += second["generated_tokens"]
    trace.append({"role": "answer_worker", "raw": second["raw"], "error": second["error"]})
    ok, reason, answer, citations = validate_answer(second["parsed"], selection)
    if ok:
        message = make_message(question_id, "answer_worker", citations, observed)
        blackboard.append(message, observed)
    return {"valid": ok, "stop_reason": second["error"] or reason,
            "answer": answer, "cited_ids": citations, "observed": observed,
            "model_calls": calls, "prompt_tokens": prompt_tokens,
            "generated_tokens": generated_tokens,
            "elapsed_s": time.perf_counter() - start, "trace": trace,
            "blackboard": blackboard.messages}


def normalize_answer(text: str) -> str:
    text = str(text).casefold().translate(str.maketrans("", "", string.punctuation))
    return " ".join(re.sub(r"\b(a|an|the)\b", " ", text).split())


def answer_f1(predicted: str, gold: str) -> float:
    """F1 de tokens con tratamiento específico de yes/no/noanswer."""
    pred_text, gold_text = normalize_answer(predicted), normalize_answer(gold)
    categorical = {"yes", "no", "noanswer"}
    if pred_text in categorical or gold_text in categorical:
        return float(pred_text == gold_text)
    a, b = collections.Counter(pred_text.split()), collections.Counter(gold_text.split())
    overlap = sum((a & b).values())
    return 2 * overlap / (sum(a.values()) + sum(b.values())) if overlap else float(not a and not b)


def grade_row(example: dict[str, Any], result: dict[str, Any]) -> dict[str, Any]:
    """Una respuesta de contrato inválido no se computa como acierto."""
    lookup = {entry["id"]: (entry["title"], entry["sent_id"]) for entry in result["observed"]}
    citations = {lookup[cite] for cite in result["cited_ids"] if cite in lookup} if result["valid"] else set()
    gold = gold_facts(example)
    overlap = len(citations & gold)
    precision = overlap / len(citations) if citations else 0.0
    recall = overlap / len(gold) if gold else 0.0
    support_f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    answer = result["answer"] if result["valid"] else ""
    return {"question_id": example["_id"], "answer_em": int(bool(result["valid"]) and normalize_answer(answer) == normalize_answer(example["answer"])),
            "answer_f1": answer_f1(answer, example["answer"]) if result["valid"] else 0.0,
            "support_f1": support_f1, "valid_finish": int(result["valid"]),
            "stop_reason": result["stop_reason"], "model_calls": result["model_calls"],
            "prompt_tokens": result["prompt_tokens"],
            "generated_tokens": result["generated_tokens"],
            "elapsed_s": result["elapsed_s"]}


def select_pilot(data: list[dict[str, Any]], size: int) -> list[dict[str, Any]]:
    if not 1 <= size <= len(data):
        raise ValueError("n fuera del tamaño real de HotpotQA")
    # Se fija por hash de ID, sin consultar respuestas ni resultados.
    return sorted(data, key=lambda x: (hashlib.sha256(("CC0F4-S11-2026|" + x["_id"]).encode()).hexdigest(), x["_id"]))[:size]


def pilot(size: int = 16, model_id: str = MODEL_ID) -> dict[str, Any]:
    data = check_dataset()
    chosen = select_pilot(data, size)
    llm = LocalLLM(model_id)
    OUT.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, Any]] = []
    trace_path = OUT / f"hotpot_piloto_{size}_trazas.jsonl"
    with trace_path.open("w", encoding="utf-8") as output:
        for index, item in enumerate(chosen, 1):
            observations = ranked_evidence(item)
            for name, runner in (("single", agent_single), ("supervisor_workers", agent_supervisor_workers)):
                run = runner(llm, item, observations)
                metrics = grade_row(item, run)
                metrics["architecture"] = name
                metrics["retrieval_support_recall"] = support_recall(item, observations)
                rows.append(metrics)
                output.write(json.dumps({"question_id": item["_id"], "architecture": name,
                                         "question": item["question"], "trace": run,
                                         "metrics": metrics}, ensure_ascii=False) + "\n")
            print(f"Consultas procesadas: {index}/{size}", flush=True)
    summary = {"source": "HotpotQA dev distractor", "dataset_sha256": OFFICIAL_SHA256,
               "model_id": model_id, "model_revision": getattr(llm, "revision", None),
               "questions": size, "total_public_questions": len(data),
               "sampling": "Orden fijo por SHA-256 de ID, sin selección por resultado",
               "status": "PILOTO_REAL_EXPLORATORIO", "architectures": {},
               "limitations": [
                   "Una y dos llamadas al modelo no igualan presupuesto de inferencia",
                   "Ambas arquitecturas usan los mismos 14 fragmentos recuperados; no comparan recuperación abierta",
                   "EM y F1 sobre respuestas humanas no prueban soporte factual de las citas",
                   "Piloto sin potencia estadística ni afirmaciones de superioridad",
               ]}
    for name in ("single", "supervisor_workers"):
        subset = [row for row in rows if row["architecture"] == name]
        summary["architectures"][name] = {
            "answer_em": sum(x["answer_em"] for x in subset) / size,
            "answer_f1": sum(x["answer_f1"] for x in subset) / size,
            "support_f1": sum(x["support_f1"] for x in subset) / size,
            "valid_finish_rate": sum(x["valid_finish"] for x in subset) / size,
            "mean_model_calls": sum(x["model_calls"] for x in subset) / size,
            "mean_prompt_tokens": sum(x["prompt_tokens"] for x in subset) / size,
            "mean_generated_tokens": sum(x["generated_tokens"] for x in subset) / size,
            "mean_elapsed_s": sum(x["elapsed_s"] for x in subset) / size,
            "stop_reasons": dict(collections.Counter(x["stop_reason"] for x in subset))}
    (OUT / f"hotpot_piloto_{size}_resumen.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Semana 11: HotpotQA real, contratos y agentes LLM")
    command = parser.add_mutually_exclusive_group(required=True)
    command.add_argument("--preparar", action="store_true")
    command.add_argument("--verificar", action="store_true")
    command.add_argument("--evaluar-recuperacion", action="store_true")
    command.add_argument("--piloto-llm", type=int, metavar="N")
    parser.add_argument("--origen", help="Archivo oficial HotpotQA ya descargado")
    parser.add_argument("--modelo", default=MODEL_ID)
    parser.add_argument("--top-k", type=int, default=14)
    args = parser.parse_args()
    if args.preparar:
        value = prepare(args.origen)
    elif args.verificar:
        value = {"questions": len(check_dataset()), "sha256": OFFICIAL_SHA256,
                 "status": "VERIFICADO"}
    elif args.evaluar_recuperacion:
        value = evaluate_retrieval(args.top_k)
    else:
        value = pilot(args.piloto_llm, args.modelo)
    print(json.dumps(value, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
