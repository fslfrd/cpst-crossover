"""Command line: python -m cpst {report,figure,fetch,policies,policy-figure}"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .data import load_dataset, runs_file

DEFAULT_DATASET = "arize_terminalbench_2026_07"


def _runs_or_exit(ds):
    path = runs_file(ds)
    if path is None:
        sys.exit("Per-run results not found. Run `python -m cpst fetch` first.")
    from .policies import load_runs
    return load_runs(path), path


def main() -> None:
    p = argparse.ArgumentParser(prog="cpst")
    p.add_argument("--dataset", default=DEFAULT_DATASET)
    sub = p.add_subparsers(dest="cmd", required=True)

    r = sub.add_parser("report", help="single-model results (RESULTS.md)")
    r.add_argument("--lmax", type=float, default=20.0, help="max repair cost per failure, USD")
    r.add_argument("--hourly", type=float, default=80.0, help="loaded labor cost per hour, USD")

    f = sub.add_parser("figure", help="render the single-model crossover chart")
    f.add_argument("--out", type=Path, default=Path("figures/crossover.png"))
    f.add_argument("--lmax", type=float, default=4.0)
    f.add_argument("--hourly", type=float, default=80.0)

    sub.add_parser("fetch", help="download per-run results at the pinned commit")

    pr = sub.add_parser("policies", help="retry and escalation policies (POLICIES.md)")
    pr.add_argument("--lmax", type=float, default=20.0)
    pr.add_argument("--hourly", type=float, default=80.0)
    pr.add_argument("--replicates", type=int, default=2000)

    pf = sub.add_parser("policy-figure", help="render the policy chart")
    pf.add_argument("--out", type=Path, default=Path("figures/policies.png"))
    pf.add_argument("--lmax", type=float, default=5.0)
    pf.add_argument("--hourly", type=float, default=80.0)

    args = p.parse_args()
    ds = load_dataset(args.dataset)

    if args.cmd == "report":
        from .report import build_report
        runs = _runs_or_exit(ds)[0] if runs_file(ds) else None
        print(build_report(ds, l_max=args.lmax, hourly=args.hourly, runs=runs))
    elif args.cmd == "figure":
        from .figures import crossover_chart
        runs = _runs_or_exit(ds)[0] if runs_file(ds) else None
        args.out.parent.mkdir(parents=True, exist_ok=True)
        crossover_chart(ds, args.out, l_max=args.lmax, hourly=args.hourly, runs=runs)
        print(f"wrote {args.out}", file=sys.stderr)
    elif args.cmd == "fetch":
        from .fetch import fetch_runs
        print(f"saved to {fetch_runs(ds)}", file=sys.stderr)
    elif args.cmd == "policies":
        from .policy_report import build_policy_report
        runs, path = _runs_or_exit(ds)
        print(build_policy_report(ds, runs, path, hourly=args.hourly, l_max=args.lmax,
                                  replicates=args.replicates))
    elif args.cmd == "policy-figure":
        from .figures import policy_chart
        runs, _ = _runs_or_exit(ds)
        args.out.parent.mkdir(parents=True, exist_ok=True)
        policy_chart(ds, runs, args.out, l_max=args.lmax, hourly=args.hourly)
        print(f"wrote {args.out}", file=sys.stderr)


if __name__ == "__main__":
    main()
