# Methodology

## The question

At what human repair cost does a cheaper, less reliable model stop being the cheaper way to deliver accepted work? And once retries and escalation to a stronger model are allowed, which policy is cheapest?

This repository answers both from published benchmark results: Arize's summary table, and the per-run results Arize published alongside it (one row per attempt, downloaded at a pinned commit, not redistributed). It runs no models and makes no new measurements. Everything here is arithmetic over numbers a third party published, plus one explicit, swept assumption about repair cost.

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

**Preferred: paired bootstrap on the per-run results.** Each replicate resamples the 40 tasks with replacement, then resamples each model's six trials within each chosen task, and recomputes the crossover for both models on the same resampled data. 2,000 replicates; the reported range is the 2.5th to 97.5th percentile. This captures three things the approximation below misses: attempts on the same task are related, cost per attempt varies, and the two models are compared on the same tasks.

**Fallback: approximation from the published table.** Arize reports that pass rates "carry roughly a ±6 point 95% confidence interval." Combining two such rates as ±6√2 ≈ ±8.5 points and recomputing L\* at the ends gives a quick range. **It understates the uncertainty.** An earlier version of this repository described it as conservative; that was wrong. It treats all 240 attempts per model as independent when they cluster within 40 tasks, and it treats cost per attempt as exact. For the headline crossover the approximation gives $1.12 to $2.15; the bootstrap gives $0.86 to $3.18.

A crossover is **resolved** if its range is bounded: in at least 97.5% of replicates the more reliable option becomes cheaper at some finite repair cost. Unresolved means the data cannot distinguish the two options' reliability, so the crossover point should not be relied on.

Point estimates in RESULTS.md section 2 come from the published table, which rounds pass rates to whole points. The bootstrap point estimates use the per-run results, so they differ slightly (for example $1.52 against $1.47).

## Retry and escalation policies

POLICIES.md extends the repair model from one attempt to a **policy**: an ordered list of (model, maximum attempts) steps. For each task, the first model tries up to its limit and stops at the first pass; if every attempt fails, the next step runs; if every step fails, a person repairs the task at cost L. Every task ends accepted, so:

```
loaded CPST = API cost per task + share of tasks left for a person × L
```

This is still linear in L, so the crossover arithmetic above applies unchanged. The two terms are computed per task, then averaged:

- For one model on one task, attempts are drawn from that model's six observed trials on that task, with replacement: pass probability `p = passes / 6`, and each attempt costs the cell's mean cost. Task difficulty is kept per task instead of being averaged away, which matters because the cheap models' failures concentrate on particular tasks.
- Different models' attempts on the same task are treated as independent given the task.
- A sensitivity check draws distinct observed trials instead (without replacement). It makes retries look somewhat better; see POLICIES.md section 5.

The policy set is fixed in code (`default_policies`): each of four models alone with up to 1, 2 or 3 attempts; three two-model ladders; and the four-model escalation ladder Arize published. No search over policies is run, so the cheapest policy is not the product of picking the best of many noisy estimates.

**Reproduction checks.** The per-run file reproduces Arize's published pass rate, cost per attempt and cost per successful task for all ten models (one cost figure differs by $0.0005, Claude Sonnet 5). Arize's escalation ladder computes to $0.521 per task the models complete, against $0.525 published. Tests enforce both.

**Accounting for errors.** 23 of 2,400 rows are harness or provider errors with no cost recorded. Following Arize, they count as failed attempts costing $0; that is the accounting that reproduces their table.

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
| Interval on the reliability gap (approximation) | Derived; understates uncertainty | This repository |
| Bootstrap range on crossovers | Derived from per-run results | This repository |
| Per-run results: pass or fail, cost, per attempt | Published, pinned commit | [Arize-ai/fireworks-cost-benchmark](https://github.com/Arize-ai/fireworks-cost-benchmark) |
| Retry and escalation policy costs | Derived | This repository |
| Failures detected reliably and for free; attempts independent given the task | **Assumed** | This repository |
| One attempt per task; every failure detected and repaired; equal repair cost across models | **Assumed** | This repository |
| Repair cost L | **Swept parameter**, not a measurement | This repository |
| $80 an hour loaded labor cost, for time conversions | **Assumed**, adjustable with `--hourly` | Article's illustrative scenario |

## Sources reviewed and not used

Kept so the reasoning is auditable. Full notes in `data/sources.toml`.

**OpenAI, "Introducing GPT-6 Sol and Luna."** Publishes DeepSWE 1.1 scores for both models at max effort (68.8% and 66.6%) and per-token prices. Cost per task is published only as percentages relative to other models, and the two cost comparisons use different baselines: Sol against Claude Fable 5 with the effort level of the cost comparison not stated, Luna against Fable 5 at medium effort. No Sol to Luna cost ratio can be derived from that. The page also does not state whether the DeepSWE score is a binary pass rate or partial credit, and gives no sample sizes.

**OpenAI, "GPT-6 Sol and GPT-6 Luna: October 2026 update" (Deployment Safety Hub).** Safety and domain evaluations reported as scores, not task completion rates. The ordering between the two models varies by evaluation, so it does not support a general assumption that larger models fail less often.

## Limitations

- **Comparability.** A CPST is only comparable with another computed on the same tasks and the same definition of success. Every figure here comes from one benchmark with one acceptance bar (all of a task's tests pass). Figures from other benchmarks, provider scorecards or your own workload define success differently and should not be mixed into the same dataset. This is also why the OpenAI DeepSWE figures are excluded: different tasks and unstated scoring, in addition to the mismatched cost baselines.
- **Benchmark scope.** 40 selected Terminal-Bench command-line tasks. Not enterprise workflows. Failure rates on your workload can differ substantially.
- **Vendor-run.** Fireworks hosts several of the open models evaluated.
- **Repair cost is not measured.** It is swept. Real repair cost varies by failure type, and the model that fails may also influence how long a fix takes.
- **Perfect detection.** Undetected failures cost more than detected ones and are not modeled.
- **Failure detection.** Retries and escalation assume every failure is caught, for free. On this benchmark the task's tests do that. In production you need a check that can tell a failed output from a good one, and its cost and miss rate are not modeled. Without such a check, the policy results do not apply.
- **Latency.** Retries and escalation add time, which is not priced.
- **Fixed policy set.** Sixteen policies, chosen in advance. Others, including ladders with retries at each step, may do better.
- **Third-party data.** The per-run results have no license file at the pinned commit. They are downloaded for local analysis by `python -m cpst fetch` and are not redistributed here.
- **Point in time.** Model versions and prices change. The data file records the publication and retrieval dates.

## Roadmap

1. Imperfect detection: a miss rate, and a cost for failures that reach production.
2. Model-dependent repair cost: separate L per model.
3. Effort levels as policy steps: the same model at different reasoning effort, which needs new runs.
4. Your own measurements: the CSV format accepts any workload's pass rates and costs; the policy code accepts any per-run file in the same format.
