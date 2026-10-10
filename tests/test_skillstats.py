"""Checks skillstats against published reference values and the numbers quoted in the guide.

    python3 -m unittest discover tests
"""

import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "skill-eval-statistics", "scripts"))

import skillstats as s  # noqa: E402


class Intervals(unittest.TestCase):
    def test_wilson_reference_values(self):
        # Newcombe (1998), Table I: 81/263 -> 0.2553 to 0.3662.
        lo, hi = s.wilson(81, 263)
        self.assertAlmostEqual(lo, 0.2553, places=4)
        self.assertAlmostEqual(hi, 0.3662, places=4)

    def test_wilson_all_pass_is_not_degenerate(self):
        lo, hi = s.wilson(3, 3)
        self.assertAlmostEqual(lo, 0.4385, places=4)
        self.assertEqual(hi, 1.0)

    def test_rule_of_three(self):
        self.assertAlmostEqual(s.zero_failures_bound(100), 0.0295, places=4)
        self.assertAlmostEqual(s.zero_failures_bound(300), 3 / 300, places=3)

    def test_newcombe_difference(self):
        # Newcombe (1998), Table II example (a): 56/70 vs 48/80 -> 0.0524 to 0.3339.
        d, lo, hi, _ = s.diff_test(56, 70, 48, 80)
        self.assertAlmostEqual(d, 0.2, places=6)
        self.assertAlmostEqual(lo, 0.0524, places=4)
        self.assertAlmostEqual(hi, 0.3339, places=4)


class Planning(unittest.TestCase):
    def test_runs_for_margin(self):
        self.assertEqual(s.runs_for_margin(0.05), 385)

    def test_runs_per_arm(self):
        self.assertEqual(s.runs_per_arm(0.7, 0.8), 294)

    def test_design_effect_ceiling(self):
        # 20 queries, ICC 0.5: effective n approaches 20 / 0.5 = 40 as runs grow.
        n_eff = 20 * 1000 / s.design_effect(1000, 0.5)
        self.assertLess(n_eff, 40)
        self.assertGreater(n_eff, 39.9)

    def test_threshold(self):
        self.assertAlmostEqual(s.p_pass_threshold(0.6, 3), 0.648, places=6)
        self.assertAlmostEqual(s.p_pass_threshold(0.5, 3), 0.5, places=6)


class Judge(unittest.TestCase):
    def test_perfect_judge_is_identity(self):
        self.assertAlmostEqual(s.judge_corrected(0.7, 1.0, 1.0), 0.7)

    def test_lenient_judge(self):
        self.assertAlmostEqual(s.judge_corrected(0.8, 0.95, 0.5), 0.3 / 0.45)

    def test_useless_judge_rejected(self):
        with self.assertRaises(ValueError):
            s.judge_corrected(0.5, 0.5, 0.5)


class Clustered(unittest.TestCase):
    def test_icc_extremes(self):
        self.assertAlmostEqual(s.icc_anova([[1, 1, 1], [0, 0, 0], [1, 1, 1], [0, 0, 0]]), 1.0)
        self.assertEqual(s.icc_anova([[1, 0], [0, 1], [1, 0], [0, 1]]), 0.0)

    def test_analyze_paired(self):
        rows = []
        for q in range(12):
            for run in range(3):
                rows.append({"query": q, "variant": "old", "pass": q < 4})
                rows.append({"query": q, "variant": "new", "pass": q < 10})
        with tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False) as fh:
            fh.write("\n".join(json.dumps(r) for r in rows))
        try:
            out = s.analyze(fh.name, reps=2000)
        finally:
            os.unlink(fh.name)
        paired = out[2]
        self.assertIn("+50%", paired)
        self.assertIn("6 queries improved, 0 got worse", paired)
        self.assertIn("sign test p = 0.031", paired)


if __name__ == "__main__":
    unittest.main()
