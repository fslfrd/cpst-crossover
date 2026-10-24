"""The crossover chart. Requires matplotlib (pip install -e '.[figures]')."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from .data import Dataset  # noqa: E402
from .model import crossover_estimate, loaded_cpst, lower_envelope  # noqa: E402

# Validated categorical slots 1-3 (pass all-pairs CVD and normal-vision checks
# on the light surface) plus neutral roles. See README "Chart palette".
SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK_2 = "#52514e"
MUTED = "#8a8983"
GRID = "#e4e3df"
CONTEXT = "#cfcec8"
BAND = "#efeeea"
SLOTS = ["#2a78d6", "#eb6834", "#1baf7a"]


def crossover_chart(ds: Dataset, out: Path, l_max: float = 4.0, hourly: float = 80.0) -> None:
    plt.rcParams.update({
        "font.family": ["Inter", "Helvetica Neue", "Arial", "DejaVu Sans"],
        "font.size": 11,
        "text.parse_math": False,
        "axes.edgecolor": GRID,
        "axes.labelcolor": INK_2,
        "xtick.color": INK_2,
        "ytick.color": INK_2,
    })
    env = lower_envelope(ds.models, l_max)
    highlighted = []
    for r in env:
        if r.model not in highlighted:
            highlighted.append(r.model)
    highlighted = highlighted[: len(SLOTS)]
    color = {m.name: SLOTS[i] for i, m in enumerate(highlighted)}

    fig, ax = plt.subplots(figsize=(12, 6.75), dpi=200)
    fig.patch.set_facecolor(SURFACE)
    ax.set_facecolor(SURFACE)
    xs = [l_max * i / 400 for i in range(401)]

    # Uncertainty band for the last (resolved) crossover on the envelope
    if len(env) >= 2:
        e = crossover_estimate(env[-2].model, env[-1].model, ds.pass_rate_halfwidth)
        if e is not None and e.resolved:
            ax.axvspan(e.low, min(e.high, l_max), color=BAND, lw=0, zorder=0)
            ax.text((e.low + min(e.high, l_max)) / 2, 0.02, "approx. 95% range\nfor this crossover",
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
