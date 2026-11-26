"""Pruebas de infraestructura con fixtures mínimas SOLO para contratos.

No son consultas ni reuniones experimentales; los resultados de QMSum se generan
exclusivamente después de verificar los seis JSONL originales.
"""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from Semana10 import memoria_real as m


class MemoryContractTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / "episodios.sqlite3"
        self.turns = [
            {"speaker": "a", "content": "Una fuente verificable"},
            {"speaker": "b", "content": "El comité revisó la propuesta"},
            {"speaker": "c", "content": "Se confirma la propuesta"},
        ]

    def tearDown(self):
        self.temp.cleanup()

    def test_persistence_across_connection(self):
        with m.MemoryStore(self.path) as db:
            self.assertEqual(db.save_meeting("reunion", self.turns), "inserted")
        with m.MemoryStore(self.path) as db:
            self.assertEqual([r["content"] for r in db.read("reunion")],
                             [x["content"] for x in self.turns])

    def test_repeat_write_idempotent(self):
        with m.MemoryStore(self.path) as db:
            db.save_meeting("reunion", self.turns)
            self.assertEqual(db.save_meeting("reunion", self.turns), "already_present_identical")
            self.assertEqual(len(db.read("reunion")), 3)

    def test_conflict_refused_without_data_loss(self):
        with m.MemoryStore(self.path) as db:
            db.save_meeting("reunion", self.turns)
            altered = [dict(x) for x in self.turns]
            altered[1]["content"] = "Texto deliberadamente distinto para comprobar el contrato"
            with self.assertRaisesRegex(ValueError, "Conflicto"):
                db.save_meeting("reunion", altered)
            self.assertEqual(db.read("reunion")[1]["content"], self.turns[1]["content"])

    def test_different_ids_do_not_share_context(self):
        with m.MemoryStore(self.path) as db:
            db.save_meeting("uno", self.turns)
            db.save_meeting("dos", self.turns[:1])
            self.assertEqual(len(db.read("uno")), 3)
            self.assertEqual(len(db.read("dos")), 1)

    def test_empty_rejected(self):
        with m.MemoryStore(self.path) as db:
            with self.assertRaises(ValueError):
                db.save_meeting("", self.turns)
            with self.assertRaises(ValueError):
                db.save_meeting("r", [])

    def test_bm25_order_and_budget(self):
        episodes = [{"speaker": x["speaker"], "content": x["content"]} for x in self.turns]
        ranking = m.bm25_rank("propuesta", episodes, limit=2)
        self.assertEqual(len(ranking), 2)
        self.assertTrue(all(r["score"] >= 0 for r in ranking))
        self.assertEqual(m.bm25("propuesta", episodes, 2), [r["position"] for r in ranking])

    def test_bm25_no_input(self):
        self.assertEqual(m.bm25_rank("consulta", []), [])
        with self.assertRaises(ValueError):
            m.bm25("consulta", [], limit=0)

    def test_zero_overlap_does_not_claim_abstention_accuracy(self):
        episodes = [{"speaker": x["speaker"], "content": x["content"]} for x in self.turns]
        rank = m.bm25_rank("zzzzzz", episodes, 2)
        self.assertEqual(rank[0]["score"], 0.0)
        self.assertEqual(rank[0]["position"], 0)

    def test_gold_span_inclusive(self):
        self.assertEqual(m.gold_positions({"relevant_text_span": [[0, 1], [2, 2]]}, 3), {0, 1, 2})

    def test_gold_span_outside(self):
        for spans in ([[1, 3]], [[2, 1]], [[-1, 0]]):
            with self.assertRaises(ValueError):
                m.gold_positions({"relevant_text_span": spans}, 3)

    def test_grade_uses_real_schema_not_gold_for_retrieval(self):
        # Esta estructura mínima prueba los contratos, no constituye un benchmark.
        mock = {"meeting_transcripts": self.turns,
                "specific_query_list": [{"query": "propuesta", "relevant_text_span": [[1, 2]]}]}
        with m.MemoryStore(self.path) as db:
            first = m.grade_meeting("contrato", mock, db, limit=1)
            second = m.grade_meeting("contrato", mock, db, limit=1)
        self.assertEqual(first, second)
        self.assertEqual({r["policy"] for r in first}, {"working_recent", "episodic_bm25"})
        self.assertTrue(all(0 <= r["span_turn_recall"] <= 1 for r in first))

    def test_pin_declares_six_revisions(self):
        self.assertEqual(len(m.BLOBS), 6)
        self.assertTrue(all(size > 0 and len(sha) == 40 for sha, size in m.BLOBS.values()))
        self.assertIn("Academic/val", m.BLOBS)
        self.assertIn("Committee/test", m.BLOBS)


if __name__ == "__main__":
    unittest.main()
