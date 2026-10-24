"""Cost per successful task (CPST) and repair-cost crossover arithmetic.

The repair model, stated once so every function below inherits it:

* Each incoming task gets one model attempt.
* A failed attempt is always detected and repaired by a person to the
  acceptance bar, at a fixed cost L per failure, the same for every model.
* Any other cost that is constant per task and equal across models is
  excluded. It shifts every model's cost equally and cancels out of every
  crossover (but it does raise absolute CPST).

Under those assumptions every incoming task is eventually accepted, so the
expected loaded cost per incoming task equals the loaded CPST:

    loaded CPST = cost_per_attempt + failure_rate * L

That is linear in L, so two models' lines cross at most once:

    L* = (c_b - c_a) / (f_a - f_b)

which is the break-even rule  dC > dp * L  solved for L.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import inf, sqrt
from typing import Optional, Sequence

_EPS = 1e-12


@dataclass(frozen=True)
class ModelResult:
    name: str
    provider: str
    pass_rate: float  # fraction of attempts that pass, 0..1
    cost_per_attempt: float  # USD per attempt, failed attempts included
    published_cpst: Optional[float] = None  # publisher's figure, for cross-checks only

    def __post_init__(self) -> None:
        if not 0.0 <= self.pass_rate <= 1.0:
            raise ValueError(f"{self.name}: pass_rate must be in [0, 1]")
        if self.cost_per_attempt < 0:
            raise ValueError(f"{self.name}: cost_per_attempt must be >= 0")

    @property
    def failure_rate(self) -> float:
        return 1.0 - self.pass_rate


def inference_cpst(m: ModelResult) -> float:
    """Inference-only CPST: API spend per successful attempt.

    Undefined, not zero, when nothing succeeds.
    """
    if m.pass_rate <= 0:
        raise ValueError(f"{m.name}: CPST is undefined with zero successes")
    return m.cost_per_attempt / m.pass_rate


def loaded_cpst(m: ModelResult, repair_cost: float) -> float:
    """Loaded CPST under the repair model in the module docstring."""
    if repair_cost < 0:
        raise ValueError("repair_cost must be >= 0")
    return m.cost_per_attempt + m.failure_rate * repair_cost


def crossover(a: ModelResult, b: ModelResult) -> Optional[float]:
    """Repair cost at which a and b have equal loaded CPST.

    Returns None when there is no crossover at L >= 0: the lines are
    parallel, or one model is at least as cheap and at least as reliable,
    so it is never more expensive.
    """
    df = a.failure_rate - b.failure_rate
    dc = b.cost_per_attempt - a.cost_per_attempt
    if abs(df) < _EPS:
        return None
    L = dc / df
    return L if L >= 0 else None


@dataclass(frozen=True)
class CrossoverEstimate:
    cheaper: ModelResult  # lower cost per attempt
    more_reliable: ModelResult  # lower failure rate
    point: float  # L* at the published pass rates
    low: float  # L* if the reliability gap is at the top of its range
    high: float  # L* if the gap is at the bottom of its range; inf if unbounded
    gap: float  # failure-rate gap, cheaper minus more_reliable
    gap_halfwidth: float
    resolved: bool  # True if the gap's range excludes zero


def crossover_estimate(
    a: ModelResult, b: ModelResult, pass_rate_halfwidth: float
) -> Optional[CrossoverEstimate]:
    """Crossover with an approximate range from pass-rate uncertainty.

    The gap's half-width is sqrt(2) * pass_rate_halfwidth, which treats the
    two pass rates as independent. Both models ran the same tasks, so the
    true uncertainty of the difference is likely smaller; this is the
    conservative choice. Only pass-rate uncertainty is propagated; cost per
    attempt is treated as exact.

    Returns None when one model dominates (no tradeoff to estimate).
    """
    cheaper, reliable = sorted((a, b), key=lambda m: m.cost_per_attempt)
    gap = cheaper.failure_rate - reliable.failure_rate
    dc = reliable.cost_per_attempt - cheaper.cost_per_attempt
    if gap <= _EPS or dc < 0:
        return None
    hw = sqrt(2.0) * pass_rate_halfwidth
    lo_gap, hi_gap = gap - hw, gap + hw
    return CrossoverEstimate(
        cheaper=cheaper,
        more_reliable=reliable,
        point=dc / gap,
        low=dc / hi_gap,
        high=dc / lo_gap if lo_gap > _EPS else inf,
        gap=gap,
        gap_halfwidth=hw,
        resolved=lo_gap > _EPS,
    )


@dataclass(frozen=True)
class Regime:
    start: float
    end: float
    model: ModelResult


def lower_envelope(models: Sequence[ModelResult], l_max: float) -> list[Regime]:
    """Which model has the lowest loaded CPST, as repair cost runs 0..l_max.

    Point estimates only. Neighbouring regimes whose reliability gap is not
    resolved should be read as ties; see crossover_estimate.
    """
    if not models:
        return []

    def key_at(L: float):
        # Lowest cost wins; at an exact tie the more reliable model wins,
        # because it stays cheaper as L grows.
        return lambda m: (round(loaded_cpst(m, L), 12), m.failure_rate)

    regimes: list[Regime] = []
    L = 0.0
    current = min(models, key=key_at(L))
    # Each step moves to a strictly more reliable model, so this terminates.
    while True:
        candidates = []
        for m in models:
            if m.failure_rate >= current.failure_rate - _EPS:
                continue
            Lc = crossover(current, m)
            if Lc is not None and Lc >= L - _EPS:
                candidates.append((Lc, m))
        if not candidates:
            regimes.append(Regime(L, l_max, current))
            return regimes
        nxt_L = min(Lc for Lc, _ in candidates)
        nxt = min(
            (m for Lc, m in candidates if Lc - nxt_L <= _EPS),
            key=lambda m: m.failure_rate,
        )
        if nxt_L >= l_max:
            regimes.append(Regime(L, l_max, current))
            return regimes
        if nxt_L > L + _EPS:
            regimes.append(Regime(L, nxt_L, current))
        L, current = max(L, nxt_L), nxt
