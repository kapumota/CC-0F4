"""Pruebas de funciones y propiedades; no son datasets del benchmark docente."""
import unittest

from .agent_benchmark import (BM25Tool, calibrate_threshold, lexical_coverage,
                              run_adaptive, run_workflow)


class BenchmarkContractTests(unittest.TestCase):
    def setUp(self):
        # Estos registros mínimos comprueban contratos de software, NO rendimiento.
        self.tool = BM25Tool([{"doc_id": "D01", "passages": [
            {"passage_id": "D01-P01", "text": "DNS redes seguridad"},
            {"passage_id": "D01-P02", "text": "Sistema de archivos redes"},
            {"passage_id": "D01-P03", "text": "Recuperación de documentos"},
        ]}])

    def test_tool_limit(self):
        with self.assertRaises(ValueError): self.tool.search("dns", 0)
        with self.assertRaises(ValueError): self.tool.search("dns", 21)

    def test_fixed_workflow(self):
        self.assertEqual(run_workflow("DNS", self.tool, 1)["tool_calls"], 1)
        self.assertEqual(len(run_workflow("DNS", self.tool, 3)["citations"]), 3)

    def test_expansion_bounded(self):
        a = run_adaptive("pregunta que no se corresponde", self.tool, 1.01)
        self.assertEqual(a["tool_calls"], 2)
        self.assertEqual(len(a["citations"]), 3)

    def test_inclusion(self):
        for question in ("DNS redes", "documentos", "sin términos coincidentes"):
            a0 = set(run_workflow(question, self.tool, 1)["citations"])
            a1 = set(run_workflow(question, self.tool, 3)["citations"])
            b = set(run_adaptive(question, self.tool)["citations"])
            self.assertTrue(a0 <= b <= a1)

    def test_coverage(self):
        self.assertEqual(lexical_coverage("dns red", "red dns"), 1.0)
        self.assertEqual(lexical_coverage("no aparece", "red dns"), 0.0)

    def test_calibration_uses_development_only(self):
        rows = [
            {"query_id": "c", "split": "calibration", "article": "A",
             "passage_id": "D01-P01", "top_ids": ["D01-P01", "D01-P02", "D01-P03"],
             "top1_coverage": 0.6, "rank_at10": 1},
            {"query_id": "e", "split": "evaluation", "article": "B",
             "passage_id": "D01-P03", "top_ids": ["D01-P01", "D01-P02", "D01-P03"],
             "top1_coverage": 0.2, "rank_at10": 3},
        ]
        sizes = {p.passage_id: 12 for p in self.tool.passages}
        chosen, trials = calibrate_threshold(rows, sizes)
        rows[1]["top1_coverage"] = 0.99
        again, trials_again = calibrate_threshold(rows, sizes)
        self.assertEqual(chosen, again)
        self.assertEqual(trials, trials_again)


if __name__ == "__main__":
    unittest.main()
