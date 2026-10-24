"""Command line: python -m cpst {report,figure}"""

from __future__ import annotations

import argparse
from pathlib import Path

from .data import load_dataset

DEFAULT_DATASET = "arize_terminalbench_2026_07"


def main() -> None:
    p = argparse.ArgumentParser(prog="cpst")
    p.add_argument("--dataset", default=DEFAULT_DATASET)
    sub = p.add_subparsers(dest="cmd", required=True)

    r = sub.add_parser("report", help="print results tables")
    r.add_argument("--lmax", type=float, default=20.0, help="max repair cost per failure, USD")
    r.add_argument("--hourly", type=float, default=80.0, help="loaded labor cost per hour, USD")

    f = sub.add_parser("figure", help="render the crossover chart")
    f.add_argument("--out", type=Path, default=Path("figures/crossover.png"))
    f.add_argument("--lmax", type=float, default=4.0)
    f.add_argument("--hourly", type=float, default=80.0)

    args = p.parse_args()
    ds = load_dataset(args.dataset)

    if args.cmd == "report":
        from .report import build_report
        print(build_report(ds, l_max=args.lmax, hourly=args.hourly))
    elif args.cmd == "figure":
        from .figures import crossover_chart
        args.out.parent.mkdir(parents=True, exist_ok=True)
        crossover_chart(ds, args.out, l_max=args.lmax, hourly=args.hourly)
        print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
