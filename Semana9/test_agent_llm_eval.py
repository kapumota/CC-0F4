"""Pruebas de evaluación sobre textos mínimos, NO inferencia artificial."""
import unittest
from .agent_llm_eval import exact_match, normalize_answer, token_f1, select_evaluation_questions


class HumanAnswerMetricTests(unittest.TestCase):
    def test_exact_match_normalizes_articles(self):
        self.assertEqual(exact_match("The Canadian Parliament.", ["Canadian Parliament"]), 1.0)
        self.assertEqual(exact_match("Ottawa", ["Toronto"]), 0.0)

    def test_f1_non_exact(self):
        self.assertGreater(token_f1("Canadian parliament", ["the parliament of Canada"]), 0)
        self.assertLess(token_f1("Canadian parliament", ["the parliament of Canada"]), 1)

    def test_answer_missing_rejected(self):
        with self.assertRaises(ValueError): exact_match("respuesta", [])

    def test_pilot_only_evaluation(self):
        qs = [{"source_question_id":"a","split":"calibration"},
              {"source_question_id":"b","split":"evaluation"}]
        self.assertEqual(len(select_evaluation_questions(qs, 1)), 1)
        with self.assertRaises(ValueError):select_evaluation_questions(qs, 2)


if __name__ == "__main__":
    unittest.main()
