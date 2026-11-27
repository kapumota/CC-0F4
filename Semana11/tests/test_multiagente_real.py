"""Pruebas de ingeniería con entradas mínimas, NO benchmark experimental."""
from __future__ import annotations

import copy
import unittest

from Semana11.contratos import Blackboard, ContractError, evidence_hash, make_message, validate_selection
from Semana11.multiagente_real import (
    answer_f1, grade_row, gold_facts, normalize_answer, parse_json_strict,
    ranked_evidence, retrieval_rows, select_pilot, summarize_retrieval,
    support_recall, validate_answer,
)


def example():
    # Estos textos son entradas de prueba del contrato, no resultados de HotpotQA.
    return {"_id": "prueba-con-enunciado-minimo", "question": "Which city hosted the event?",
            "answer": "Lima", "supporting_facts": [["Articulo B", 0]],
            "type": "bridge", "level": "medium", "context": [
                ["Articulo A", ["The venue is in Lima.", "Information about another city."]],
                ["Articulo B", ["Lima hosted the event.", "The event took place outdoors."]],
            ]}


class CoordinationTests(unittest.TestCase):
    def setUp(self):
        self.ex = example()
        self.evidence = ranked_evidence(self.ex, 4)

    def test_ranked_evidence_is_repeatable(self):
        self.assertEqual(self.evidence, ranked_evidence(self.ex, 4))

    def test_ranked_evidence_returns_original_sentences(self):
        all_texts = {sentence for _, sentences in self.ex["context"] for sentence in sentences}
        self.assertEqual({x["text"] for x in self.evidence}, all_texts)

    def test_topk_invalid_rejected(self):
        with self.assertRaises(ValueError):
            ranked_evidence(self.ex, 0)

    def test_empty_context_rejected(self):
        bad = example()
        bad["context"] = []
        with self.assertRaises(ValueError):
            ranked_evidence(bad)

    def test_gold_facts_are_not_retrieval_arguments(self):
        changed = example()
        changed["supporting_facts"] = [["Articulo A", 1]]
        self.assertEqual(ranked_evidence(self.ex), ranked_evidence(changed))

    def test_gold_recall_from_original_annotation(self):
        self.assertEqual(support_recall(self.ex, self.evidence), 1.0)
        self.assertEqual(support_recall(self.ex, []), 0.0)

    def test_retrieval_rows_preserve_id(self):
        rows = retrieval_rows([self.ex], top_k=2)
        self.assertEqual(rows[0]["question_id"], self.ex["_id"])
        self.assertEqual(rows[0]["n_observed"], 2)

    def test_summary_has_groups(self):
        result = summarize_retrieval(retrieval_rows([self.ex], top_k=4), 4)
        self.assertEqual(result["questions"], 1)
        self.assertIn("bridge", result["by_type"])

    def test_evidence_digest_detects_alteration(self):
        corrupt = copy.deepcopy(self.evidence[0])
        corrupt["text"] += " altered"
        self.assertNotEqual(evidence_hash(self.evidence[0]), evidence_hash(corrupt))

    def test_selection_rejects_unknown_ids(self):
        with self.assertRaises(ContractError):
            validate_selection(["E98"], self.evidence)

    def test_selection_rejects_duplicates(self):
        with self.assertRaises(ContractError):
            validate_selection(["E00", "E00"], self.evidence)

    def test_selection_rejects_bad_types(self):
        with self.assertRaises(ContractError):
            validate_selection("E00", self.evidence)

    def test_selection_rejects_empty(self):
        with self.assertRaises(ContractError):
            validate_selection([], self.evidence)

    def test_blackboard_preserves_provenance(self):
        board = Blackboard(self.ex["_id"])
        msg = make_message(self.ex["_id"], "evidence_worker", ["E00"], self.evidence)
        board.append(msg, self.evidence)
        msg["selected_ids"].clear()
        self.assertEqual(board.messages[0]["selected_ids"], ["E00"])

    def test_blackboard_rejects_other_question(self):
        board = Blackboard(self.ex["_id"])
        msg = make_message("otra-pregunta", "evidence_worker", ["E00"], self.evidence)
        with self.assertRaises(ContractError):
            board.append(msg, self.evidence)

    def test_blackboard_rejects_tampered_content(self):
        board = Blackboard(self.ex["_id"])
        msg = make_message(self.ex["_id"], "evidence_worker", ["E00"], self.evidence)
        msg["evidence_sha256"]["E00"] = "fake"
        with self.assertRaises(ContractError):
            board.append(msg, self.evidence)

    def test_blackboard_rejects_unknown_role(self):
        with self.assertRaises(ContractError):
            make_message(self.ex["_id"], "superuser", ["E00"], self.evidence)

    def test_json_parser_is_strict(self):
        self.assertIsNone(parse_json_strict('texto {"answer":"Lima"}'))
        self.assertEqual(parse_json_strict('{"answer":"Lima"}')["answer"], "Lima")

    def test_answer_requires_observed_citation(self):
        ok, reason, _, _ = validate_answer({"answer": "Lima", "cited_ids": ["E99"]}, self.evidence)
        self.assertFalse(ok)
        self.assertEqual(reason, "CITA_NO_OBSERVADA")

    def test_answer_rejects_duplicate_citations(self):
        ok, _, _, _ = validate_answer({"answer": "Lima", "cited_ids": ["E00", "E00"]}, self.evidence)
        self.assertFalse(ok)

    def test_answer_has_exact_schema(self):
        ok, _, _, _ = validate_answer({"answer": "Lima", "cited_ids": ["E00"], "extra": 1}, self.evidence)
        self.assertFalse(ok)

    def test_answer_metrics_distinguish_invalid_finish(self):
        base = {"valid": False, "answer": "Lima", "cited_ids": ["E00"],
                "observed": self.evidence, "stop_reason": "JSON_INVALIDO",
                "model_calls": 1, "prompt_tokens": 1, "generated_tokens": 1, "elapsed_s": 0}
        scored = grade_row(self.ex, base)
        self.assertEqual(scored["answer_em"], 0)
        self.assertEqual(scored["answer_f1"], 0.0)
        self.assertEqual(scored["valid_finish"], 0)

    def test_answer_f1_for_identity(self):
        self.assertEqual(answer_f1("The Lima", "Lima"), 1.0)
        self.assertEqual(normalize_answer("The Lima"), "lima")

    def test_selection_independent_of_labels_and_input_order(self):
        a, b = example(), example()
        b["_id"] = "otro-id"
        first = select_pilot([a, b], 1)
        second = select_pilot([b, a], 1)
        self.assertEqual(first[0]["_id"], second[0]["_id"])

    def test_selection_rejects_more_than_total(self):
        with self.assertRaises(ValueError):
            select_pilot([example()], 2)


if __name__ == "__main__":
    unittest.main()
