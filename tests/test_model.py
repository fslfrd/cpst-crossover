import sys
import unittest
from math import inf, isclose
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from cpst.data import load_dataset  # noqa: E402
from cpst.model import (  # noqa: E402
    ModelResult,
    crossover,
    crossover_estimate,
    inference_cpst,
    loaded_cpst,
    lower_envelope,
)

CHEAP = ModelResult("cheap", "x", pass_rate=0.5, cost_per_attempt=0.10)
RELIABLE = ModelResult("reliable", "x", pass_rate=0.9, cost_per_attempt=0.50)
DOMINANT = ModelResult("dominant", "x", pass_rate=0.9, cost_per_attempt=0.05)


class ArithmeticTests(unittest.TestCase):
    def test_inference_cpst(self):
        self.assertAlmostEqual(inference_cpst(CHEAP), 0.20)

    def test_cpst_undefined_with_zero_successes(self):
        with self.assertRaises(ValueError):
            inference_cpst(ModelResult("none", "x", 0.0, 1.0))

    def test_loaded_cpst(self):
        # 0.10 + 0.5 * 2.00
        self.assertAlmostEqual(loaded_cpst(CHEAP, 2.0), 1.10)

    def test_crossover_matches_break_even_rule(self):
        # dC = 0.40, dp = 0.40  ->  L* = 1.00
        L = crossover(CHEAP, RELIABLE)
        self.assertAlmostEqual(L, 1.0)
        self.assertAlmostEqual(loaded_cpst(CHEAP, L), loaded_cpst(RELIABLE, L))
        self.assertEqual(crossover(CHEAP, RELIABLE), crossover(RELIABLE, CHEAP))

    def test_dominated_pair_has_no_crossover(self):
        self.assertIsNone(crossover(DOMINANT, RELIABLE))
        self.assertIsNone(crossover_estimate(DOMINANT, RELIABLE, 0.06))

    def test_constant_per_task_cost_cancels(self):
        k = 0.37
        a = ModelResult("a", "x", CHEAP.pass_rate, CHEAP.cost_per_attempt + k)
        b = ModelResult("b", "x", RELIABLE.pass_rate, RELIABLE.cost_per_attempt + k)
        self.assertAlmostEqual(crossover(a, b), crossover(CHEAP, RELIABLE))

    def test_estimate_range_brackets_point(self):
        e = crossover_estimate(CHEAP, RELIABLE, 0.06)
        self.assertTrue(e.resolved)
        self.assertLess(e.low, e.point)
        self.assertLess(e.point, e.high)

    def test_small_gap_is_unresolved(self):
        a = ModelResult("a", "x", 0.40, 0.01)
        b = ModelResult("b", "x", 0.45, 0.20)
        e = crossover_estimate(a, b, 0.06)
        self.assertFalse(e.resolved)
        self.assertEqual(e.high, inf)

    def test_envelope_switches_at_crossover(self):
        env = lower_envelope([CHEAP, RELIABLE], 5.0)
        self.assertEqual([r.model.name for r in env], ["cheap", "reliable"])
        self.assertAlmostEqual(env[0].end, 1.0)
        self.assertAlmostEqual(env[1].start, 1.0)

    def test_envelope_skips_dominated_models(self):
        env = lower_envelope([CHEAP, RELIABLE, DOMINANT], 5.0)
        self.assertEqual([r.model.name for r in env], ["dominant"])

    def test_envelope_is_minimum_everywhere(self):
        models = load_dataset("arize_terminalbench_2026_07").models
        env = lower_envelope(models, 20.0)
        for r in env:
            for L in (r.start + 1e-6, (r.start + r.end) / 2, r.end - 1e-6):
                best = min(loaded_cpst(m, L) for m in models)
                self.assertTrue(isclose(loaded_cpst(r.model, L), best, abs_tol=1e-9))


class PublishedDataTests(unittest.TestCase):
    """The data file must reproduce the publisher's own CPST column.

    Pass rates are published rounded to whole points and costs to tenths of a
    cent, so each derived CPST must fall inside the range those roundings allow.
    """

    def test_derived_cpst_within_rounding_of_published(self):
        ds = load_dataset("arize_terminalbench_2026_07")
        self.assertEqual(len(ds.models), 10)
        for m in ds.models:
            lo = (m.cost_per_attempt - 0.0005) / (m.pass_rate + 0.005)
            hi = (m.cost_per_attempt + 0.0005) / (m.pass_rate - 0.005)
            with self.subTest(model=m.name):
                self.assertLessEqual(lo, m.published_cpst + 0.0005)
                self.assertGreaterEqual(hi, m.published_cpst - 0.0005)

    def test_source_metadata_present(self):
        ds = load_dataset("arize_terminalbench_2026_07")
        for key in ("url", "published", "retrieved", "grading", "pass_rate_ci95_halfwidth"):
            self.assertIn(key, ds.meta)


if __name__ == "__main__":
    unittest.main()
