"""
SWAHILI-BENCH Evaluation Core.
Provides metrics computation, semantic keyword verification, and hallucination checks.
"""

from typing import Dict, List, Any


class SwahiliEvaluator:
    """Evaluates Swahili LLM responses against benchmark gold standards."""

    def __init__(self):
        pass

    def evaluate_response(self, item: Dict[str, Any], response_text: str) -> Dict[str, Any]:
        """
        Evaluate a single response against an item in SWAHILI-BENCH.
        
        Returns:
            Dict containing:
                - score (0.0 to 1.0)
                - passed (bool)
                - matches (List[str])
                - violations (List[str])
                - category (str)
        """
        response_lower = response_text.lower()
        expected = item.get("expected_keywords", [])
        negative = item.get("negative_keywords", [])

        # Match expected keywords (any or ratio)
        matched_expected = [kw for kw in expected if kw.lower() in response_lower]
        keyword_recall = len(matched_expected) / len(expected) if expected else 1.0

        # Check negative/hallucinated keywords
        matched_negative = [kw for kw in negative if kw.lower() in response_lower]
        penalty = 0.5 * len(matched_negative)

        # Baseline score calculation
        raw_score = max(0.0, keyword_recall - penalty)

        # Ensure minimum length check (avoids empty or trivial single-word responses)
        if len(response_text.strip().split()) < 4:
            raw_score *= 0.5

        final_score = min(1.0, round(raw_score, 2))
        passed = final_score >= 0.6 and len(matched_negative) == 0

        return {
            "id": item.get("id"),
            "category": item.get("category"),
            "dialect": item.get("dialect"),
            "score": final_score,
            "passed": passed,
            "matched_keywords": matched_expected,
            "violations": matched_negative,
            "response_preview": response_text[:120] + ("..." if len(response_text) > 120 else "")
        }

    def aggregate_results(self, evaluations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Aggregate item evaluations into category-level and overall benchmarks."""
        if not evaluations:
            return {
                "overall_score": 0.0,
                "pass_rate": 0.0,
                "total_items": 0,
                "category_scores": {}
            }

        total_score = sum(e["score"] for e in evaluations)
        passed_count = sum(1 for e in evaluations if e["passed"])
        total_items = len(evaluations)

        categories: Dict[str, List[float]] = {}
        for e in evaluations:
            cat = e.get("category", "general")
            categories.setdefault(cat, []).append(e["score"])

        category_summary = {
            cat: {
                "avg_score": round(sum(scores) / len(scores), 3),
                "count": len(scores)
            }
            for cat, scores in categories.items()
        }

        return {
            "overall_score": round(total_score / total_items, 3),
            "pass_rate": round(passed_count / total_items, 3),
            "passed_count": passed_count,
            "total_items": total_items,
            "category_scores": category_summary
        }
