"""Contratos del controlador sin red, GPU ni memoria persistente."""
import unittest

from .agent_benchmark import BM25Tool
from .agent_loop import Limits, RestrictedTools, ScriptedPolicy, run_agent
from .agent_policy import parse_json_object


class AgentLoopTests(unittest.TestCase):
    def setUp(self):
        tool = BM25Tool([{"doc_id": "D01", "passages": [
            {"passage_id": "D01-P01", "text": "Red DNS resuelve nombres del campus"},
            {"passage_id": "D01-P02", "text": "VPN autorizaciones para servicios"},
            {"passage_id": "D01-P03", "text": "Repositorio y seguridad de tokens"},
        ]}])
        self.tools = RestrictedTools(tool)
        self.search = {"action": "search_documents", "arguments": {"query": "DNS", "top_k": 1}}
        self.finish = {"action": "finish", "arguments": {
            "answer": "Consulte la guia DNS.", "citations": ["D01-P01"]}}

    def run_actions(self, *actions, limits=None):
        return run_agent("Como diagnosticar DNS?", ScriptedPolicy(list(actions)),
                         self.tools, limits or Limits())

    def test_completed_with_verified_citation(self):
        r = self.run_actions(self.search, self.finish)
        self.assertEqual(r["stop_reason"], "completed_with_citations")
        self.assertEqual(r["tool_calls"], 1)
        self.assertEqual(r["citations"], ["D01-P01"])

    def test_unobserved_citation_rejected(self):
        r = self.run_actions({"action": "finish", "arguments": {
            "answer": "Falso", "citations": ["D01-P03"]}} ,
            {"action": "finish", "arguments": {
            "answer": "Falso", "citations": ["D01-P03"]}})
        self.assertEqual(r["stop_reason"], "invalid_action_limit")
        self.assertEqual(r["tool_calls"], 0)

    def test_invalid_tool_blocked(self):
        a = {"action": "run_shell", "arguments": {"command": "echo hola"}}
        r = self.run_actions(a, a)
        self.assertEqual(r["stop_reason"], "invalid_action_limit")
        self.assertEqual(r["tool_calls"], 0)

    def test_repeated_action_detected(self):
        r = self.run_actions(self.search, self.search)
        self.assertEqual(r["stop_reason"], "repeated_action")
        self.assertEqual(r["tool_calls"], 1)

    def test_step_budget(self):
        r = self.run_actions(self.search, self.finish, limits=Limits(max_steps=1))
        self.assertEqual(r["stop_reason"], "max_steps")

    def test_calls_budget_allows_finish(self):
        r = self.run_actions(self.search, self.finish, limits=Limits(max_tool_calls=1))
        self.assertEqual(r["stop_reason"], "completed_with_citations")

    def test_calls_budget_blocks_second_tool(self):
        second = {"action": "read_passage", "arguments": {"passage_id": "D01-P01"}}
        r = self.run_actions(self.search, second, limits=Limits(max_tool_calls=1))
        self.assertEqual(r["stop_reason"], "max_tool_calls")

    def test_unseen_passage_fails(self):
        bad = {"action": "read_passage", "arguments": {"passage_id": "D01-P03"}}
        r = self.run_actions(bad, bad)
        self.assertEqual(r["stop_reason"], "repeated_action")
        self.assertEqual(r["observations"][0]["status"], "error")

    def test_bad_top_k_contract(self):
        bad = {"action": "search_documents", "arguments": {"query": "dns", "top_k": 0}}
        r = self.run_actions(bad, self.search, self.finish)
        self.assertEqual(r["invalid_actions"], 1)
        self.assertEqual(r["stop_reason"], "completed_with_citations")

    def test_empty_task_rejected(self):
        with self.assertRaises(ValueError):
            self.run_actions(self.search, limits=Limits(max_steps=0))
        with self.assertRaises(ValueError):
            run_agent("", ScriptedPolicy([self.search]), self.tools)

    def test_llm_json_parser(self):
        self.assertEqual(parse_json_object('{"action":"finish","arguments":{}}')["action"], "finish")
        with self.assertRaises(Exception):
            parse_json_object('Introduccion {"action":"finish"}')

    def test_invalid_model_output_still_counts_tokens(self):
        a = {"action": "__invalid_json__", "arguments": {},
             "usage": {"prompt_tokens": 25, "generated_tokens": 12}}
        r = self.run_actions(a, self.search, self.finish)
        self.assertEqual(r["invalid_actions"], 1)
        self.assertEqual(r["prompt_tokens"], 25)
        self.assertEqual(r["generated_tokens"], 12)
        self.assertEqual(r["stop_reason"], "completed_with_citations")

    def test_model_usage_budget(self):
        a = {**self.search, "usage": {"prompt_tokens": 200, "generated_tokens": 100}}
        r = self.run_actions(a, self.finish, limits=Limits(max_total_tokens=200))
        self.assertEqual(r["stop_reason"], "token_budget_exhausted")
        self.assertEqual(r["tool_calls"], 0)


if __name__ == "__main__":
    unittest.main()
