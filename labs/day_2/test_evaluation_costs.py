import unittest

from evaluation_utils import estimate_cost_usd


class CostEstimateTests(unittest.TestCase):
    def test_partial_or_empty_rates_are_not_complete(self):
        for rates in ({}, {"model_input_per_1m": 1.0}):
            with self.subTest(rates=rates):
                result = estimate_cost_usd(
                    {"model_input_tokens": 1000, "model_output_tokens": 500}, rates
                )
                self.assertFalse(result["rates_complete"])
                self.assertIsNone(result["components_usd"]["model_output"])

    def test_complete_rates_preserve_cost_calculation(self):
        result = estimate_cost_usd(
            {"model_input_tokens": 1000, "model_output_tokens": 500},
            {
                "model_input_per_1m": 1.0,
                "model_output_per_1m": 2.0,
                "semantic_per_1k": 0.0,
                "agentic_per_1m": 0.0,
            },
        )
        self.assertTrue(result["rates_complete"])
        self.assertEqual(result["estimated_cost_usd"], 0.002)


if __name__ == "__main__":
    unittest.main()
