"""Pruebas sin LLM ni acceso a red para las políticas de Semana 9."""

import unittest
from .agent_benchmark import BM25Tool, lexical_coverage, run_adaptive, run_workflow


class AgentBenchmarkTests(unittest.TestCase):
    def setUp(self):
        self.tool = BM25Tool([{
            "doc_id": "D01", "passages": [
                {"passage_id": "D01-P01", "text": "DNS nombres resolución redes"},
                {"passage_id": "D01-P02", "text": "Acceso redes y seguridad"},
                {"passage_id": "D01-P03", "text": "Laboratorio GPUs y memoria"},
            ]
        }])

    def test_tool_contract(self):
        with self.assertRaises(ValueError):
            self.tool.search("dns", 0)
        with self.assertRaises(ValueError):
            self.tool.search("dns", 6)

    def test_workflow_is_fixed(self):
        r = run_workflow("DNS redes", self.tool)
        self.assertEqual(r["tool_calls"], 1)
        self.assertEqual(len(r["citations"]), 3)
        self.assertEqual(r["policy"], "workflow_fixed_top3")
        self.assertEqual(len(run_workflow("DNS redes", self.tool, top_k=1)["citations"]), 1)

    def test_adaptive_loop_is_bounded(self):
        r = run_adaptive("pregunta externa sin coincidencias", self.tool, threshold=0.45)
        self.assertEqual(r["tool_calls"], 2)
        self.assertEqual(len(r["trace"]), 2)
        self.assertIn("stop", r["trace"][-1])

    def test_rank_monotonicity(self):
        queries = ["DNS redes", "laboratorio", "sin coincidencia"]
        for q in queries:
            a0 = set(run_workflow(q, self.tool, 1)["citations"])
            a1 = set(run_workflow(q, self.tool, 3)["citations"])
            b = set(run_adaptive(q, self.tool)["citations"])
            self.assertTrue(a0.issubset(b))
            self.assertTrue(b.issubset(a1))

    def test_coverage(self):
        self.assertEqual(lexical_coverage("red dns", "dns red"), 1.0)
        self.assertEqual(lexical_coverage("término", "distinto"), 0.0)


if __name__ == "__main__":
    unittest.main()
