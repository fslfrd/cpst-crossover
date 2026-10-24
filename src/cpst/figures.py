"""Charts. Requires matplotlib (pip install -e '.[figures]')."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from .data import Dataset, model_keys  # noqa: E402
from .model import crossover_estimate, loaded_cpst, lower_envelope  # noqa: E402

# Validated categorical slots 1-4 (pass CVD and normal-vision checks on the
# light surface). Slots 3-4 sit below 3:1 contrast, so every highlighted line
# is directly labeled. See README "Chart palette".
SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK_2 = "#52514e"
MUTED = "#8a8983"
GRID = "#e4e3df"
CONTEXT = "#cfcec8"
BAND = "#efeeea"
SLOTS = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100"]


def _style() -> None:
    plt.rcParams.update({
        "font.family": ["Inter", "Helvetica Neue", "Arial", "DejaVu Sans"],
        "font.size": 11,
        "text.parse_math": False,
        "axes.edgecolor": GRID,
        "axes.labelcolor": INK_2,
        "xtick.color": INK_2,
        "ytick.color": INK_2,
    })


def crossover_chart(ds: Dataset, out: Path, l_max: float = 4.0, hourly: float = 80.0, runs=None) -> None:
    _style()
    env = lower_envelope(ds.models, l_max)
    highlighted = []
    for r in env:
        if r.model not in highlighted:
            highlighted.append(r.model)
    highlighted = highlighted[:3]
    color = {m.name: SLOTS[i] for i, m in enumerate(highlighted)}

    fig, ax = plt.subplots(figsize=(12, 6.75), dpi=200)
    fig.patch.set_facecolor(SURFACE)
    ax.set_facecolor(SURFACE)
    xs = [l_max * i / 400 for i in range(401)]

    # Uncertainty band for the last crossover on the envelope: the per-run
    # bootstrap if available, otherwise the approximation from the table.
    if len(env) >= 2:
        a, b = env[-2].model, env[-1].model
        lo = hi = None
        if runs is not None:
            from .policies import bootstrap_threshold, single
            keys = model_keys(ds)
            bt = bootstrap_threshold(single(keys[a.name]), single(keys[b.name]), runs)
            if bt.resolved:
                lo, hi, label = bt.low, bt.high, "95% bootstrap range\nfor this crossover"
        else:
            e = crossover_estimate(a, b, ds.pass_rate_halfwidth)
            if e is not None and e.resolved:
                lo, hi, label = e.low, e.high, "approx. 95% range\nfor this crossover"
        if lo is not None:
            ax.axvspan(lo, min(hi, l_max), color=BAND, lw=0, zorder=0)
            ax.text((lo + min(hi, l_max)) / 2, 0.02, label,
                    transform=ax.get_xaxis_transform(), ha="center", va="bottom",
                    fontsize=9.5, color=MUTED)

    # Context models first, thin and gray
    for m in ds.models:
        if m.name in color:
            continue
        ax.plot(xs, [loaded_cpst(m, x) for x in xs], color=CONTEXT, lw=1.1, zorder=1,
                solid_capstyle="round")
    ax.plot([], [], color=CONTEXT, lw=1.1,
            label=f"Other models in the benchmark ({len(ds.models) - len(color)})")

    # Highlighted models
    for m in highlighted:
        ys = [loaded_cpst(m, x) for x in xs]
        ax.plot(xs, ys, color=color[m.name], lw=2.2, zorder=3, solid_capstyle="round",
                label=f"{m.name}  ({m.pass_rate:.0%} pass, ${m.cost_per_attempt:.3f}/attempt)")
        ax.annotate(m.name, (xs[-1], ys[-1]), xytext=(8, 0), textcoords="offset points",
                    va="center", fontsize=11, color=INK, fontweight="medium")

    # Crossover markers along the envelope
    for a, b in zip(env, env[1:]):
        x = b.start
        y = loaded_cpst(b.model, x)
        ax.scatter([x], [y], s=70, color=INK, edgecolors=SURFACE, linewidths=2, zorder=5)
        ax.annotate(f"${x:.2f}", (x, y), xytext=(0, 12), textcoords="offset points",
                    ha="center", fontsize=10.5, color=INK, fontweight="semibold")

    ax.set_xlim(0, l_max)
    ax.set_ylim(0, None)
    ax.grid(axis="y", color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.tick_params(length=0)
    ax.xaxis.set_major_formatter(lambda v, _: f"${v:.2f}")
    ax.yaxis.set_major_formatter(lambda v, _: f"${v:.2f}")
    per_min = hourly / 60
    ax.set_xlabel(f"Human repair cost per failed task   (at ${hourly:.0f}/hr loaded, ${per_min:.2f} ≈ 1 minute)",
                  labelpad=10)
    ax.set_ylabel("Loaded cost per accepted task", labelpad=10)

    fig.text(0.065, 0.955, "Once a failure takes about a minute to fix, the most reliable models become the cheapest",
             fontsize=15.5, fontweight="semibold", color=INK, ha="left")
    fig.text(0.065, 0.918,
             "Loaded cost per accepted task = API cost per attempt + failure rate × repair cost.  "
             "One attempt per task; every failure repaired.",
             fontsize=11, color=INK_2, ha="left")
    footer = [
        f"Source: {ds.meta['publisher']}, “{ds.meta['title']},” {ds.meta['published']}.",
        f"{ds.meta['benchmark']}, {ds.meta['total_runs']:,} runs. "
        "Benchmark API cost only; excludes infrastructure and evaluation.",
        "Derived analysis, not a new measurement: github.com/fslfrd/cpst-crossover",
    ]
    for i, line in enumerate(footer):
        fig.text(0.065, 0.068 - i * 0.025, line, fontsize=9, color=MUTED, ha="left")

    leg = ax.legend(loc="upper left", frameon=False, fontsize=10, handlelength=2.2)
    for t in leg.get_texts():
        t.set_color(INK_2)

    fig.subplots_adjust(left=0.065, right=0.85, top=0.86, bottom=0.19)
    fig.savefig(out, facecolor=SURFACE)
    plt.close(fig)


def policy_chart(ds: Dataset, runs, out: Path, l_max: float = 5.0, hourly: float = 80.0) -> None:
    """Loaded cost per task for the fixed policy set; four policies highlighted."""
    from .policies import Policy, bootstrap_threshold, envelope, evaluate, single
    from .policy_report import default_policies

    _style()
    keys = model_keys(ds)
    oss, fl, k26, g55 = (keys[n] for n in ("gpt-oss-120b", "gemini-3.1-flash-lite", "Kimi K2.6", "GPT-5.5"))
    ladder = Policy("arize-ladder", ((oss, 1), (fl, 1), (k26, 1), (g55, 1)))
    hi = [  # (policy, label, color); fixed order, so colors follow the policy
        (ladder, "Escalation ladder", SLOTS[0]),
        (single(fl), "flash-lite once", SLOTS[1]),
        (single(g55), "GPT-5.5 once", SLOTS[2]),
        (single(fl, 3), "flash-lite up to 3 tries", SLOTS[3]),
    ]
    hi_names = {p.name for p, _, _ in hi}
    results = {p.name: evaluate(p, runs) for p in default_policies(keys)}

    fig, ax = plt.subplots(figsize=(12, 6.75), dpi=200)
    fig.patch.set_facecolor(SURFACE)
    ax.set_facecolor(SURFACE)
    xs = [l_max * i / 400 for i in range(401)]

    # Bootstrap band where the ladder overtakes cheap retries
    bt = bootstrap_threshold(single(fl, 3), ladder, runs)
    if bt.resolved:
        ax.axvspan(bt.low, min(bt.high, l_max), color=BAND, lw=0, zorder=0)
        ax.text((bt.low + min(bt.high, l_max)) / 2, 0.02, "95% bootstrap range\nfor this crossover",
                transform=ax.get_xaxis_transform(), ha="center", va="bottom", fontsize=9.5, color=MUTED)

    others = [r for n, r in results.items() if n not in hi_names]
    for r in others:
        ax.plot(xs, [r.loaded(x) for x in xs], color=CONTEXT, lw=1.1, zorder=1, solid_capstyle="round")
    ax.plot([], [], color=CONTEXT, lw=1.1, label=f"Other policies tested ({len(others)})")

    for p, label, c in hi:
        r = results[p.name]
        ys = [r.loaded(x) for x in xs]
        ax.plot(xs, ys, color=c, lw=2.2, zorder=3, solid_capstyle="round",
                label=f"{label}: {r.human_share:.0%} of tasks left for a person, ${r.machine_cost:.3f} API cost per task")
        ax.annotate(label, (xs[-1], ys[-1]), xytext=(8, 0), textcoords="offset points",
                    va="center", fontsize=11, color=INK, fontweight="medium")

    # Mark where the ladder becomes the cheapest policy overall
    env = envelope(list(results.values()), l_max)
    for a, b, r in env:
        if r.policy.name == ladder.name and a > 0:
            y = r.loaded(a)
            ax.scatter([a], [y], s=70, color=INK, edgecolors=SURFACE, linewidths=2, zorder=5)
            ax.annotate(f"${a:.2f}", (a, y), xytext=(0, -20), textcoords="offset points",
                        ha="center", fontsize=10.5, color=INK, fontweight="semibold")

    ax.set_xlim(0, l_max)
    ax.set_ylim(0, None)
    ax.grid(axis="y", color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    ax.tick_params(length=0)
    ax.xaxis.set_major_formatter(lambda v, _: f"${v:.2f}")
    ax.yaxis.set_major_formatter(lambda v, _: f"${v:.2f}")
    ax.set_xlabel(f"Human repair cost per task left for a person   (at ${hourly:.0f}/hr loaded, "
                  f"${hourly / 60:.2f} ≈ 1 minute)", labelpad=10)
    ax.set_ylabel("Cost per accepted task", labelpad=10)

    fig.text(0.065, 0.955, "Retry the cheap model while fixes are cheap. Past about a minute, escalate.",
             fontsize=15.5, fontweight="semibold", color=INK, ha="left")
    fig.text(0.065, 0.918,
             "Escalation ladder: gpt-oss-120b → flash-lite → Kimi K2.6 → GPT-5.5 → person, one try each. "
             "Failures assumed detected; every task ends accepted.",
             fontsize=11, color=INK_2, ha="left")
    rm = ds.meta["runs"]
    footer = [
        f"Data: per-run results from {ds.meta['publisher']}, {ds.meta['published']} "
        f"({rm['repo'].removeprefix('https://github.com/')} at commit {rm['commit'][:7]}).",
        f"{ds.meta['benchmark']}, {ds.meta['total_runs']:,} runs. API cost only; failure detection, "
        "infrastructure and latency not priced.",
        "Derived analysis, not a new measurement: github.com/fslfrd/cpst-crossover",
    ]
    for i, line in enumerate(footer):
        fig.text(0.065, 0.068 - i * 0.025, line, fontsize=9, color=MUTED, ha="left")

    leg = ax.legend(loc="upper left", frameon=False, fontsize=10, handlelength=2.2)
    for t in leg.get_texts():
        t.set_color(INK_2)
    fig.subplots_adjust(left=0.065, right=0.83, top=0.86, bottom=0.19)
    fig.savefig(out, facecolor=SURFACE)
    plt.close(fig)
