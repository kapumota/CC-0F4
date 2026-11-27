"""Contratos mínimos de coordinación y pizarra inmutable por pregunta.

Estas funciones permiten pruebas controladas de fallos de ingeniería.
No constituyen un segundo dataset experimental.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import Any


class ContractError(ValueError):
    """Mensaje, cita o procedencia que incumple el contrato."""


def evidence_hash(entry: dict[str, Any]) -> str:
    content = f"{entry['title']}\0{entry['sent_id']}\0{entry['text']}"
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def validate_selection(ids: Any, observed: list[dict[str, Any]],
                       max_items: int = 6) -> list[str]:
    if not isinstance(ids, list) or not 1 <= len(ids) <= max_items:
        raise ContractError("SELECCION_VACIA_O_EXCESIVA")
    if any(not isinstance(value, str) for value in ids):
        raise ContractError("ID_NO_TEXTO")
    if len(set(ids)) != len(ids):
        raise ContractError("ID_DUPLICADO")
    known = {entry["id"] for entry in observed}
    if not set(ids).issubset(known):
        raise ContractError("CITA_NO_OBSERVADA")
    return list(ids)


def make_message(question_id: str, role: str, ids: list[str],
                 observed: list[dict[str, Any]]) -> dict[str, Any]:
    if role not in {"evidence_worker", "answer_worker"}:
        raise ContractError("ROL_NO_AUTORIZADO")
    valid_ids = validate_selection(ids, observed, max_items=14)
    lookup = {entry["id"]: entry for entry in observed}
    return {"question_id": question_id, "role": role,
            "selected_ids": valid_ids,
            "evidence_sha256": {identifier: evidence_hash(lookup[identifier])
                                for identifier in valid_ids}}


@dataclass
class Blackboard:
    """Una pizarra no permite sobrescribir mensajes anteriores."""
    question_id: str
    messages: list[dict[str, Any]] = field(default_factory=list)

    def append(self, message: dict[str, Any], observed: list[dict[str, Any]]) -> None:
        if not isinstance(message, dict) or set(message) != {
            "question_id", "role", "selected_ids", "evidence_sha256"
        }:
            raise ContractError("ESQUEMA_MENSAJE")
        if message["question_id"] != self.question_id:
            raise ContractError("PREGUNTA_EQUIVOCADA")
        actual = make_message(self.question_id, message["role"],
                              message["selected_ids"], observed)
        if actual != message:
            raise ContractError("PROCEDENCIA_ALTERADA")
        # Se conserva una copia independiente del mensaje aceptado.
        self.messages.append({"question_id": message["question_id"],
                              "role": message["role"],
                              "selected_ids": list(message["selected_ids"]),
                              "evidence_sha256": dict(message["evidence_sha256"])})
