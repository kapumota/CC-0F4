"""Control de un agente de Semana 9: acciones, observaciones, presupuestos y parada.

Un controlador no es un LLM. Solo se considera agente dirigido por LLM cuando
la politica conectada usa realmente un modelo para elegir las acciones.
Este modulo no persiste memoria ni ejecuta herramientas fuera de su allowlist.
"""
from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass, field
from typing import Any, Protocol

from .agent_benchmark import BM25Tool


@dataclass(frozen=True)
class Limits:
    max_steps: int = 6
    max_tool_calls: int = 3
    max_invalid_actions: int = 2
    deadline_seconds: float = 20.0
    max_observation_chars: int = 1200
    max_total_tokens: int = 12000  # tope contable, comprobado tras cada generacion

    def __post_init__(self) -> None:
        if min(self.max_steps, self.max_tool_calls, self.max_invalid_actions,
               self.max_observation_chars, self.max_total_tokens) < 1 or self.deadline_seconds <= 0:
            raise ValueError("Todos los presupuestos deben ser positivos")


@dataclass
class RunState:
    task: str
    step: int = 0
    tool_calls: int = 0
    invalid_actions: int = 0
    observed_ids: list[str] = field(default_factory=list)
    observations: list[dict[str, Any]] = field(default_factory=list)
    trace: list[dict[str, Any]] = field(default_factory=list)
    stop_reason: str | None = None
    answer: str = ""
    citations: list[str] = field(default_factory=list)
    prompt_tokens: int | None = None
    generated_tokens: int | None = None


class Policy(Protocol):
    def decide(self, task: str, observations: list[dict[str, Any]],
               observed_ids: list[str]) -> dict[str, Any]: ...


class ScriptedPolicy:
    """Secuencia controlada para tests y docencia. NO es un agente LLM."""

    def __init__(self, actions: list[dict[str, Any]]):
        self.actions = list(actions)
        self.cursor = 0

    def decide(self, task: str, observations: list[dict[str, Any]],
               observed_ids: list[str]) -> dict[str, Any]:
        if self.cursor >= len(self.actions):
            return {"action": "finish", "arguments": {
                "answer": "Ejecucion de demostracion finalizada.",
                "citations": observed_ids[:1],
            }}
        action = self.actions[self.cursor]
        self.cursor += 1
        return action


class RestrictedTools:
    """Herramientas locales de solo lectura, con contratos comprobados."""

    def __init__(self, bm25: BM25Tool):
        self.bm25 = bm25
        self.by_id = {p.passage_id: p for p in bm25.passages}

    def execute(self, name: str, args: dict[str, Any], seen: list[str],
                max_chars: int) -> dict[str, Any]:
        if name == "search_documents":
            if set(args) != {"query", "top_k"}:
                raise ValueError("search_documents requiere query y top_k")
            query = args["query"]
            top_k = args["top_k"]
            if not isinstance(query, str) or not (1 <= len(query.strip()) <= 400):
                raise ValueError("query debe ser texto de 1 a 400 caracteres")
            if type(top_k) is not int or not (1 <= top_k <= 5):
                raise ValueError("top_k debe ser un entero entre 1 y 5")
            results = self.bm25.search(query, top_k)
            return {"results": [
                {"passage_id": x["passage_id"], "score": x["score"],
                 "excerpt": x["text"][:max_chars]}
                for x in results
            ]}
        if name == "read_passage":
            if set(args) != {"passage_id"} or not isinstance(args.get("passage_id"), str):
                raise ValueError("read_passage requiere passage_id como texto")
            passage_id = args["passage_id"]
            if passage_id not in seen:
                raise ValueError("Solo pueden abrirse pasajes previamente recuperados")
            return {"passage_id": passage_id,
                    "text": self.by_id[passage_id].text[:max_chars]}
        raise ValueError("Herramienta no autorizada")


def _parse_decision(raw: Any) -> tuple[str, dict[str, Any]]:
    if not isinstance(raw, dict) or set(raw) - {"action", "arguments", "usage"}:
        raise ValueError("La decision debe ser un objeto con action y arguments")
    action, args = raw.get("action"), raw.get("arguments")
    if not isinstance(action, str) or not isinstance(args, dict):
        raise ValueError("action debe ser texto y arguments un objeto")
    if action not in {"search_documents", "read_passage", "finish"}:
        raise ValueError("Accion fuera de la allowlist")
    return action, args


def run_agent(task: str, policy: Policy, tools: RestrictedTools,
              limits: Limits | None = None) -> dict[str, Any]:
    """Ejecuta un bucle acotado. Deadline es cooperativo, no interrumpe llamadas.

    Las observaciones son datos no confiables. El controlador nunca interpreta
    su contenido como instrucciones y no ejecuta comandos del sistema.
    """
    if not isinstance(task, str) or not task.strip():
        raise ValueError("La tarea no puede estar vacia")
    lim = limits or Limits()
    state = RunState(task=task)
    begin = time.monotonic()
    signatures: set[str] = set()

    def stop(reason: str) -> dict[str, Any]:
        state.stop_reason = reason
        return {**asdict(state), "elapsed_ms": round((time.monotonic() - begin) * 1000, 3)}

    while True:
        if time.monotonic() - begin >= lim.deadline_seconds:
            return stop("deadline_exceeded")
        if state.step >= lim.max_steps:
            return stop("max_steps")
        if (state.prompt_tokens or 0) + (state.generated_tokens or 0) >= lim.max_total_tokens:
            return stop("token_budget_exhausted")
        state.step += 1
        try:
            decision = policy.decide(task, list(state.observations), list(state.observed_ids))
            usage = decision.get("usage", {}) if isinstance(decision, dict) else {}
            # Contabilizar tokens incluso si el modelo propuso una accion invalida.
            if isinstance(usage, dict):
                for key in ("prompt_tokens", "generated_tokens"):
                    value = usage.get(key)
                    if type(value) is int and value >= 0:
                        old = getattr(state, key) or 0
                        setattr(state, key, old + value)
            action, args = _parse_decision(decision)
        except Exception as exc:
            state.invalid_actions += 1
            state.trace.append({"step": state.step, "status": "rejected",
                                "error_type": "policy_or_schema", "error": str(exc)[:200]})
            state.observations.append({"type": "error", "error": "invalid_decision"})
            if state.invalid_actions >= lim.max_invalid_actions:
                return stop("invalid_action_limit")
            continue

        if time.monotonic() - begin >= lim.deadline_seconds:
            return stop("deadline_exceeded")
        if (state.prompt_tokens or 0) + (state.generated_tokens or 0) > lim.max_total_tokens:
            return stop("token_budget_exhausted")

        if action == "finish":
            answer = args.get("answer")
            citations = args.get("citations")
            if (set(args) != {"answer", "citations"}
                    or not isinstance(answer, str) or not (1 <= len(answer.strip()) <= 1500)
                    or not isinstance(citations, list)
                    or not citations
                    or any(not isinstance(c, str) or c not in state.observed_ids for c in citations)):
                state.invalid_actions += 1
                state.trace.append({"step": state.step, "action": "finish", "status": "rejected",
                                    "error_type": "unverified_finish"})
                state.observations.append({"type": "error", "error": "unverified_finish"})
                if state.invalid_actions >= lim.max_invalid_actions:
                    return stop("invalid_action_limit")
                continue
            state.answer = answer
            state.citations = list(dict.fromkeys(citations))
            state.trace.append({"step": state.step, "action": "finish", "status": "accepted",
                                "citations": state.citations})
            return stop("completed_with_citations")

        if state.tool_calls >= lim.max_tool_calls:
            state.trace.append({"step": state.step, "action": action, "status": "denied_budget"})
            return stop("max_tool_calls")
        signature = json.dumps({"action": action, "arguments": args},
                               ensure_ascii=False, sort_keys=True)
        if signature in signatures:
            state.trace.append({"step": state.step, "action": action,
                                "arguments": args, "status": "repeated_without_progress"})
            return stop("repeated_action")
        signatures.add(signature)
        state.tool_calls += 1
        try:
            observation = tools.execute(action, args, state.observed_ids,
                                        lim.max_observation_chars)
            for item in observation.get("results", []):
                if item["passage_id"] not in state.observed_ids:
                    state.observed_ids.append(item["passage_id"])
            item = {"step": state.step, "action": action, "arguments": args,
                    "status": "success", "observation": observation}
            state.trace.append(item)
            state.observations.append({"type": "tool_result", **item})
        except Exception as exc:
            state.invalid_actions += 1
            item = {"step": state.step, "action": action, "arguments": args,
                    "status": "error", "error": str(exc)[:200]}
            state.trace.append(item)
            state.observations.append({"type": "tool_error", **item})
            if state.invalid_actions >= lim.max_invalid_actions:
                return stop("invalid_action_limit")


__all__ = ["Limits", "RunState", "Policy", "ScriptedPolicy", "RestrictedTools", "run_agent"]
