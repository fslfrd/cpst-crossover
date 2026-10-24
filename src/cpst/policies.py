"""Retry and escalation policies, priced with a human repair cost.

Uses per-run results (one row per attempt) rather than published averages.

A policy is an ordered list of (model, max_attempts) steps. For each task:
try the first model up to its attempt limit, stopping at the first pass;
if every attempt fails, move to the next step; if every step fails, a
person repairs the task at cost L. Every task ends up accepted.

Assumptions, in addition to those in model.py:

* Failures are detected reliably and for free, so a retry or escalation is
  triggered only by a real failure. In production that needs a check that
  can tell a failed output from a good one; its cost is excluded here.
* Within a task, a model's attempts are draws from that model's observed
  trials on that task. Default: with replacement, so pass probability is
  p = passes / trials and each attempt costs the cell's mean cost. Task
  difficulty is captured per task rather than averaged away.
  `replacement=False` draws distinct observed trials instead (sensitivity).
* Different models' attempts on the same task are independent given the task.
* Latency is not priced.

Expected cost of one task under a policy:

    sum over steps:  P(reach step) * E[machine cost of step]
    + P(every step fails) * L

Loaded CPST of the policy is the mean of that over tasks.
"""

from __future__ import annotations

import json
from collections import defaultdict
from dataclasses import dataclass
from functools import lru_cache
from itertools import permutations
from math import inf
from pathlib import Path
from typing import Iterable, Optional, Sequence

Step = tuple[str, int]  # (model_key, max attempts)


@dataclass(frozen=True)
class Policy:
    name: str
    steps: tuple[Step, ...]

    def label(self, short: dict[str, str]) -> str:
        parts = [f"{short.get(m, m)} ×{k}" if k > 1 else short.get(m, m) for m, k in self.steps]
        return " → ".join(parts + ["person"])

    @property
    def models(self) -> set[str]:
        return {m for m, _ in self.steps}


@dataclass(frozen=True)
class Cell:
    """Observed trials for one (model, task)."""

    passes: tuple[bool, ...]
    costs: tuple[float, ...]

    @property
    def p(self) -> float:
        return sum(self.passes) / len(self.passes)

    @property
    def mean_cost(self) -> float:
        return sum(self.costs) / len(self.costs)


@dataclass(frozen=True)
class Runs:
    """Per-run results indexed by model and task."""

    cells: dict[str, dict[str, Cell]]  # model -> task -> Cell

    @property
    def models(self) -> list[str]:
        return sorted(self.cells)

    @property
    def tasks(self) -> list[str]:
        return sorted(next(iter(self.cells.values())))


def load_runs(path: Path) -> Runs:
    """Load an Arize-format JSONL file.

    Matches the publisher's own accounting, which reproduces their published
    table: every row is an attempt, a row passes only if `passed` is true, and
    a missing cost (harness or provider errors) counts as zero.
    """
    acc: dict[str, dict[str, list]] = defaultdict(lambda: defaultdict(lambda: [[], []]))
    with open(path) as fh:
        for line in fh:
            r = json.loads(line)
            c = acc[r["model_key"]][r["task_id"]]
            c[0].append(bool(r["passed"]))
            c[1].append(float(r["cost_usd"] or 0.0))
    cells = {m: {t: Cell(tuple(v[0]), tuple(v[1])) for t, v in ts.items()} for m, ts in acc.items()}
    if len({frozenset(ts) for ts in cells.values()}) != 1:
        raise ValueError("every model must have results for the same tasks")
    return Runs(cells)


# ------------------------------------------------------------------ one step

def _step_with_replacement(cell: Cell, k: int) -> tuple[float, float]:
    q = 1.0 - cell.p
    reach, cost = 1.0, 0.0
    for _ in range(k):
        cost += reach * cell.mean_cost
        reach *= q
    return cost, reach


@lru_cache(maxsize=None)
def _step_without_replacement(cell: Cell, k: int) -> tuple[float, float]:
    n = len(cell.passes)
    k = min(k, n)
    total_cost = fails = 0.0
    count = 0
    for order in permutations(range(n), k):
        c, passed = 0.0, False
        for j in order:
            c += cell.costs[j]
            if cell.passes[j]:
                passed = True
                break
        total_cost += c
        fails += not passed
        count += 1
    return total_cost / count, fails / count


def step_stats(cell: Cell, k: int, replacement: bool = True) -> tuple[float, float]:
    """(expected machine cost, probability all k attempts fail) for one model on one task."""
    if k < 1:
        raise ValueError("a step needs at least one attempt")
    return _step_with_replacement(cell, k) if replacement else _step_without_replacement(cell, k)


def task_cost(policy: Policy, cells_for_task: dict[str, Cell], replacement: bool = True) -> tuple[float, float]:
    """Expected (machine cost, probability a person repairs it) for one task."""
    reach, machine = 1.0, 0.0
    for model, k in policy.steps:
        c, fail = step_stats(cells_for_task[model], k, replacement)
        machine += reach * c
        reach *= fail
        if reach == 0.0:
            break
    return machine, reach


# ------------------------------------------------------------------ policies

@dataclass(frozen=True)
class PolicyResult:
    policy: Policy
    machine_cost: float  # mean API cost per incoming task
    human_share: float  # expected share of tasks a person repairs

    def loaded(self, repair_cost: float) -> float:
        return self.machine_cost + self.human_share * repair_cost

    @property
    def inference_cpst(self) -> float:
        """API cost per task the models complete (the benchmark-style figure)."""
        done = 1.0 - self.human_share
        return self.machine_cost / done if done > 0 else inf


def evaluate(policy: Policy, runs: Runs, tasks: Optional[Sequence[str]] = None,
             replacement: bool = True) -> PolicyResult:
    tasks = list(tasks) if tasks is not None else runs.tasks
    m_sum = h_sum = 0.0
    for t in tasks:
        m, h = task_cost(policy, {mk: runs.cells[mk][t] for mk in policy.models}, replacement)
        m_sum += m
        h_sum += h
    return PolicyResult(policy, m_sum / len(tasks), h_sum / len(tasks))


def crossover(a: PolicyResult, b: PolicyResult) -> Optional[float]:
    """Repair cost at which two policies cost the same; None if no crossover at L >= 0."""
    dh = a.human_share - b.human_share
    dm = b.machine_cost - a.machine_cost
    if abs(dh) < 1e-12:
        return None
    L = dm / dh
    return L if L >= 0 else None


def cheapest(results: Iterable[PolicyResult], repair_cost: float) -> PolicyResult:
    return min(results, key=lambda r: (round(r.loaded(repair_cost), 12), r.human_share))


def envelope(results: Sequence[PolicyResult], l_max: float) -> list[tuple[float, float, PolicyResult]]:
    """Cheapest policy over 0..l_max, as exact (start, end, result) bands."""
    bands: list[tuple[float, float, PolicyResult]] = []
    L = 0.0
    current = cheapest(results, 0.0)
    while True:
        cands = []
        for r in results:
            if r.human_share >= current.human_share - 1e-12:
                continue
            x = crossover(current, r)
            if x is not None and x >= L - 1e-12:
                cands.append((x, r.human_share, r))
        if not cands:
            bands.append((L, l_max, current))
            return bands
        x, _, nxt = min(cands, key=lambda c: (c[0], c[1]))
        if x >= l_max:
            bands.append((L, l_max, current))
            return bands
        if x > L + 1e-12:
            bands.append((L, x, current))
        L, current = max(L, x), nxt


# ------------------------------------------------------------------ uncertainty

def threshold(a: PolicyResult, b: PolicyResult) -> float:
    """Repair cost above which policy b is cheaper than policy a, for every larger L.

    0 if b is at least as cheap at every L >= 0; inf if b is never cheaper for
    large L (it sends at least as many tasks to a person and costs more).
    """
    dm = b.machine_cost - a.machine_cost
    dh = a.human_share - b.human_share
    if dh > 1e-12:
        return max(0.0, dm / dh)
    if abs(dh) <= 1e-12:
        return 0.0 if dm <= 0 else inf
    return inf


@dataclass(frozen=True)
class ThresholdEstimate:
    point: float
    low: float  # 2.5th percentile
    median: float
    high: float  # 97.5th percentile; inf if not bounded
    share_b_dominates: float  # replicates where b is cheaper at every L >= 0
    share_never: float  # replicates where b is never cheaper at high L
    replicates: int

    @property
    def resolved(self) -> bool:
        """True if, in at least 97.5% of replicates, b does become cheaper at some finite L."""
        return self.high != inf


def resample(runs: Runs, rng, models: Sequence[str]) -> tuple[Runs, list[str]]:
    """Two-stage bootstrap sample: tasks with replacement, then trials within each cell."""
    tasks = runs.tasks
    cells: dict[str, dict[str, Cell]] = {m: {} for m in models}
    keys = []
    for i in range(len(tasks)):
        t = tasks[rng.randrange(len(tasks))]
        key = f"{t}#{i}"
        keys.append(key)
        for m in models:
            c = runs.cells[m][t]
            idx = [rng.randrange(len(c.passes)) for _ in c.passes]
            cells[m][key] = Cell(tuple(c.passes[j] for j in idx), tuple(c.costs[j] for j in idx))
    return Runs(cells), keys


def bootstrap_threshold(a: Policy, b: Policy, runs: Runs, n: int = 2000,
                        seed: int = 20261024) -> ThresholdEstimate:
    """Paired bootstrap of threshold(a, b): both policies see the same resampled data.

    Resampling tasks captures that attempts on the same task are correlated;
    resampling trials captures within-task noise. Cost per attempt varies
    across replicates too.
    """
    import random

    rng = random.Random(seed)
    models = sorted(a.models | b.models)
    xs = []
    for _ in range(n):
        rr, keys = resample(runs, rng, models)
        xs.append(threshold(evaluate(a, rr, keys), evaluate(b, rr, keys)))
    xs.sort()
    q = lambda f: xs[min(n - 1, int(f * n))]
    return ThresholdEstimate(
        point=threshold(evaluate(a, runs), evaluate(b, runs)),
        low=q(0.025), median=q(0.5), high=q(0.975),
        share_b_dominates=sum(1 for x in xs if x == 0.0) / n,
        share_never=sum(1 for x in xs if x == inf) / n,
        replicates=n,
    )


def single(model_key: str, attempts: int = 1) -> Policy:
    return Policy(f"{model_key} x{attempts}", ((model_key, attempts),))
