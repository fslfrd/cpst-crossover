import random
import sys
import unittest
from math import inf
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from cpst.data import load_dataset, model_keys, runs_file  # noqa: E402
from cpst.policies import (  # noqa: E402
    Cell, Policy, PolicyResult, Runs, envelope, evaluate, load_runs, single, step_stats, threshold,
)


def cell(passes, costs):
    return Cell(tuple(passes), tuple(costs))


class StepTests(unittest.TestCase):
    def test_with_replacement(self):
        c = cell([True, False], [1.0, 1.0])  # p = 0.5, mean cost 1
        self.assertEqual(step_stats(c, 1), (1.0, 0.5))
        cost, fail = step_stats(c, 2)
        self.assertAlmostEqual(cost, 1.5)
        self.assertAlmostEqual(fail, 0.25)

    def test_without_replacement(self):
        c = cell([True, False], [1.0, 3.0])
        # orders: (pass) cost 1; (fail, pass) cost 3 + 1
        cost, fail = step_stats(c, 2, replacement=False)
        self.assertAlmostEqual(cost, (1.0 + 4.0) / 2)
        self.assertEqual(fail, 0.0)

    def test_never_solved_always_reaches_person(self):
        c = cell([False] * 6, [0.1] * 6)
        self.assertAlmostEqual(step_stats(c, 3)[1], 1.0)


class PolicyTests(unittest.TestCase):
    def setUp(self):
        # two tasks: cheap model solves the easy one, strong model solves both
        self.runs = Runs({
            "cheap": {"easy": cell([True] * 2, [0.01] * 2), "hard": cell([False] * 2, [0.01] * 2)},
            "strong": {"easy": cell([True] * 2, [0.50] * 2), "hard": cell([True] * 2, [0.50] * 2)},
        })

    def test_ladder_cost(self):
        r = evaluate(Policy("l", (("cheap", 1), ("strong", 1))), self.runs)
        # easy: 0.01; hard: 0.01 + 0.50
        self.assertAlmostEqual(r.machine_cost, (0.01 + 0.51) / 2)
        self.assertAlmostEqual(r.human_share, 0.0)

    def test_threshold_semantics(self):
        a = PolicyResult(single("x"), 0.1, 0.5)
        b = PolicyResult(single("y"), 0.5, 0.1)
        self.assertAlmostEqual(threshold(a, b), 1.0)
        self.assertEqual(threshold(b, a), inf)
        self.assertEqual(threshold(a, PolicyResult(single("z"), 0.05, 0.1)), 0.0)

    def test_envelope_is_minimum_everywhere(self):
        pols = [single("cheap"), single("strong"), Policy("l", (("cheap", 1), ("strong", 1)))]
        res = [evaluate(p, self.runs) for p in pols]
        for a, b, r in envelope(res, 10.0):
            for L in (a + 1e-6, (a + b) / 2, b - 1e-6):
                self.assertAlmostEqual(r.loaded(L), min(x.loaded(L) for x in res))

    def test_closed_form_matches_simulation(self):
        rng = random.Random(3)
        runs = Runs({m: {t: cell([rng.random() < q for _ in range(6)], [rng.random() for _ in range(6)])
                         for t in "abcdefgh"} for m, q in (("m1", 0.3), ("m2", 0.7))})
        pol = Policy("p", (("m1", 2), ("m2", 1)))
        want = evaluate(pol, runs)
        n, m_sum, h_sum = 200_000, 0.0, 0
        for _ in range(n):
            t = rng.choice(runs.tasks)
            done = False
            for mk, k in pol.steps:
                c = runs.cells[mk][t]
                for _ in range(k):
                    j = rng.randrange(6)
                    m_sum += c.costs[j]
                    if c.passes[j]:
                        done = True
                        break
                if done:
                    break
            h_sum += not done
        self.assertAlmostEqual(m_sum / n, want.machine_cost, delta=0.01)
        self.assertAlmostEqual(h_sum / n, want.human_share, delta=0.01)


@unittest.skipIf(runs_file(load_dataset("arize_terminalbench_2026_07")) is None,
                 "per-run results not fetched (python -m cpst fetch)")
class ArizeReproductionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ds = load_dataset("arize_terminalbench_2026_07")
        cls.runs = load_runs(runs_file(cls.ds))
        cls.keys = model_keys(cls.ds)

    def test_shape(self):
        self.assertEqual(len(self.runs.models), 10)
        self.assertEqual(len(self.runs.tasks), 40)
        for m in self.runs.models:
            for t in self.runs.tasks:
                self.assertEqual(len(self.runs.cells[m][t].passes), 6)

    def test_reproduces_published_table(self):
        for m in self.ds.models:
            r = evaluate(single(self.keys[m.name]), self.runs)
            with self.subTest(model=m.name):
                self.assertLessEqual(abs((1 - r.human_share) - m.pass_rate), 0.005 + 1e-9)
                # Published to 3 decimals; Claude Sonnet 5 is $0.4945 in the runs vs $0.494 published.
                self.assertLessEqual(abs(r.machine_cost - m.cost_per_attempt), 0.001)
                self.assertAlmostEqual(r.machine_cost / (1 - r.human_share), m.published_cpst, delta=0.0006)

    def test_reproduces_published_ladder(self):
        k = self.keys
        ladder = Policy("l", ((k["gpt-oss-120b"], 1), (k["gemini-3.1-flash-lite"], 1),
                              (k["Kimi K2.6"], 1), (k["GPT-5.5"], 1)))
        self.assertAlmostEqual(evaluate(ladder, self.runs).inference_cpst, 0.525, delta=0.525 * 0.02)


if __name__ == "__main__":
    unittest.main()
