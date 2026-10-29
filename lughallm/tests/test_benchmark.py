"""
Unit tests for SWAHILI-BENCH dataset and evaluation logic.
Compatible with standard library unittest and pytest.
"""

import unittest
from lughallm.src.benchmark.evaluator import SwahiliEvaluator
from lughallm.src.benchmark.swahili_bench import SwahiliBenchRunner


class TestSwahiliBench(unittest.TestCase):

    def test_evaluator_positive_case(self):
        evaluator = SwahiliEvaluator()
        item = {
            "id": "test_01",
            "category": "methali",
            "expected_keywords": ["subira", "uvumilivu"],
            "negative_keywords": ["haraka"]
        }
        response = "Mtu mwenye subira na uvumilivu hufanikiwa katika shughuli zake za kila siku."
        res = evaluator.evaluate_response(item, response)
        
        self.assertTrue(res["passed"])
        self.assertEqual(res["score"], 1.0)
        self.assertIn("subira", res["matched_keywords"])
        self.assertIn("uvumilivu", res["matched_keywords"])
        self.assertEqual(len(res["violations"]), 0)

    def test_evaluator_hallucination_penalty(self):
        evaluator = SwahiliEvaluator()
        item = {
            "id": "test_02",
            "category": "hallucination_resistance",
            "expected_keywords": ["hakuna", "mlima"],
            "negative_keywords": ["ndiyo ipo", "inaongozwa"]
        }
        response = "Ndiyo ipo Jamhuri ya Kilimanjaro na nchi hii inaongozwa na rais maarufu."
        res = evaluator.evaluate_response(item, response)
        
        self.assertFalse(res["passed"])
        self.assertGreater(len(res["violations"]), 0)

    def test_benchmark_runner_simulation(self):
        runner = SwahiliBenchRunner()
        results = runner.run_mock_simulation("lughallm")
        
        self.assertGreater(results["total_items"], 0)
        self.assertGreaterEqual(results["overall_score"], 0.8)
        self.assertGreaterEqual(results["pass_rate"], 0.8)
        self.assertIn("methali", results["category_scores"])
        self.assertIn("sheng", results["category_scores"])


if __name__ == "__main__":
    unittest.main()
