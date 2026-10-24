# Methodology

## The question

At what human repair cost does a cheaper, less reliable model stop being the cheaper way to deliver accepted work?

This repository answers that from published benchmark figures. It runs no models and makes no new measurements. Everything here is arithmetic over numbers a third party published, plus one explicit, swept assumption about repair cost.

## Repair model

For each incoming task:

1. The model makes **one attempt**.
2. If the attempt fails, the failure is **always detected** and a person repairs it to the acceptance bar at a fixed cost **L** per failure.
3. **L is the same for every model.**
4. Any other cost that is **constant per task and equal across models** is excluded.

Under those assumptions every incoming task is eventually accepted, so the expected cost per incoming task equals the loaded cost per successful task:

```
loaded CPST = c + f × L
```

where `c` is API cost per attempt (failed attempts included) and `f` is the failure rate, `1 − pass rate`.

The expression is linear in L, so any two models' lines cross at most once:

```
L* = (c_b − c_a) / (f_a − f_b)
```

This is the break-even rule from the article, `ΔC > Δp × L`, solved for L. Below L\* the cheaper model has the lower loaded CPST; above it the more reliable model does. If one model is both cheaper and more reliable, there is no crossover at L ≥ 0.

Inference-only CPST, the figure benchmarks usually publish, is the special case `c / (1 − f)`, which ignores repair entirely.

### Why per-task constants can be dropped

Adding the same constant k to every model's cost per task cancels from `L*`. Infrastructure or evaluation costs that are genuinely per task and model-independent therefore do not change which model wins or where the lines cross. They do raise absolute CPST, so any dollar figure in this repository is an under-count of a real operating cost. Costs that scale with attempts, turns or wall-clock time are **not** constant across models and are not covered by this argument.

## Uncertainty

Arize reports that pass rates "carry roughly a ±6 point 95% confidence interval." The reliability gap between two models is the difference of two such rates. This repository combines them as ±6√2 ≈ ±8.5 points, which treats the two rates as independent. Both models ran the same 40 tasks, so their results are likely positively correlated and the true interval on the gap is probably narrower. The independent combination is the conservative choice.

The crossover range is L\* recomputed at the two ends of the gap's range. A crossover is reported as **resolved** only when that range excludes zero. Unresolved means the published data cannot distinguish the two models' reliability, so the crossover point should not be relied on.

Only pass-rate uncertainty is propagated. Published cost per attempt is treated as exact.

## Claims ledger

| Quantity | Status | Source |
|---|---|---|
| Pass rate per model | Published | Arize and Fireworks, results table |
| Mean API cost per attempt, including failed attempts | Published | Same |
| Cost per successful task | Published; used only to cross-check | Same |
| ±6 point 95% interval on pass rates | Published, approximate | Same |
| Grading is binary (all task tests pass) | Published | Same |
| Inference-only CPST | Derived: c / pass rate | This repository; test checks it reproduces the published column within rounding |
| Loaded CPST, crossovers, envelope | Derived | This repository |
| Interval on the reliability gap | Derived, conservative | This repository |
| One attempt per task; every failure detected and repaired; equal repair cost across models | **Assumed** | This repository |
| Repair cost L | **Swept parameter**, not a measurement | This repository |
| $80 an hour loaded labor cost, for time conversions | **Assumed**, adjustable with `--hourly` | Article's illustrative scenario |

## Sources reviewed and not used

Kept so the reasoning is auditable. Full notes in `data/sources.toml`.

**OpenAI, "Introducing GPT-6 Sol and Luna."** Publishes DeepSWE 1.1 scores for both models at max effort (68.8% and 66.6%) and per-token prices. Cost per task is published only as percentages relative to other models, and the two cost comparisons use different baselines: Sol against Claude Fable 5 with the effort level of the cost comparison not stated, Luna against Fable 5 at medium effort. No Sol to Luna cost ratio can be derived from that. The page also does not state whether the DeepSWE score is a binary pass rate or partial credit, and gives no sample sizes.

**OpenAI, "GPT-6 Sol and GPT-6 Luna: October 2026 update" (Deployment Safety Hub).** Safety and domain evaluations reported as scores, not task completion rates. The ordering between the two models varies by evaluation, so it does not support a general assumption that larger models fail less often.

## Limitations

- **Benchmark scope.** 40 selected Terminal-Bench command-line tasks. Not enterprise workflows. Failure rates on your workload can differ substantially.
- **Vendor-run.** Fireworks hosts several of the open models evaluated.
- **Repair cost is not measured.** It is swept. Real repair cost varies by failure type, and the model that fails may also influence how long a fix takes.
- **Perfect detection.** Undetected failures cost more than detected ones and are not modeled.
- **Single attempt.** No retry-before-escalation policy is modeled; retries change both cost per task and effective failure rate.
- **Point in time.** Model versions and prices change. The data file records the publication and retrieval dates.

## Roadmap

1. Retry-then-repair policies: k attempts before a person steps in.
2. Imperfect detection: a miss rate, and a cost for failures that reach production.
3. Model-dependent repair cost: separate L per model.
4. Routing policies: the cost of a cheap first attempt that escalates to a stronger model.
5. Your own measurements: the CSV format accepts any workload's pass rates and costs.
