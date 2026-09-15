import unittest

from evaluation_utils import render_cited_answer, validate_cited_answer


class CitedAnswerTests(unittest.TestCase):
    def test_full_abstention_accounts_for_every_part_without_passing_quality_gates(self):
        result = validate_cited_answer(
            {"claims": [], "insufficient_evidence": ["diagnosis", "treatment"]},
            ["S1"],
            ["diagnosis", "treatment"],
        )
        for metric in (
            "answer_part_coverage",
            "citation_coverage",
            "citation_validity",
            "valid_citation_coverage",
        ):
            self.assertEqual(result[metric], 0.0)
        self.assertEqual(
            render_cited_answer(result),
            "Insufficient evidence for answer parts: diagnosis, treatment.",
        )

    def test_empty_claims_do_not_hide_unaccounted_parts(self):
        with self.assertRaisesRegex(ValueError, "unaccounted"):
            validate_cited_answer(
                {"claims": [], "insufficient_evidence": ["diagnosis"]},
                ["S1"],
                ["diagnosis", "treatment"],
            )

    def test_claim_and_partial_abstention_are_both_rendered(self):
        result = validate_cited_answer(
            {
                "claims": [
                    {
                        "answer_part_id": "diagnosis",
                        "text": "Synthetic supported statement.",
                        "source_ids": ["S1"],
                    }
                ],
                "insufficient_evidence": ["treatment"],
            },
            ["S1"],
            ["diagnosis", "treatment"],
        )
        self.assertEqual(result["answer_part_coverage"], 0.5)
        self.assertEqual(result["valid_citation_coverage"], 1.0)
        self.assertEqual(
            render_cited_answer(result),
            "- Synthetic supported statement. [S1]\n"
            "Insufficient evidence for answer parts: treatment.",
        )

    def test_claims_still_require_citations(self):
        with self.assertRaisesRegex(ValueError, "at least one source_id"):
            validate_cited_answer(
                {
                    "claims": [
                        {"answer_part_id": "diagnosis", "text": "Unsupported.", "source_ids": []}
                    ],
                    "insufficient_evidence": [],
                },
                ["S1"],
                ["diagnosis"],
            )


if __name__ == "__main__":
    unittest.main()
