"""Load benchmark results and their source metadata from data/."""

from __future__ import annotations

import csv
import sys

if sys.version_info >= (3, 11):
    import tomllib
else:  # pragma: no cover
    import tomli as tomllib
from dataclasses import dataclass
from pathlib import Path

from .model import ModelResult

DATA_DIR = Path(__file__).resolve().parents[2] / "data"


@dataclass(frozen=True)
class Dataset:
    key: str
    meta: dict
    models: list[ModelResult]

    @property
    def pass_rate_halfwidth(self) -> float:
        return float(self.meta["pass_rate_ci95_halfwidth"])


def load_sources(data_dir: Path = DATA_DIR) -> dict:
    with open(data_dir / "sources.toml", "rb") as fh:
        return tomllib.load(fh)


def load_dataset(key: str, data_dir: Path = DATA_DIR) -> Dataset:
    meta = load_sources(data_dir)["datasets"][key]
    models = []
    with open(data_dir / meta["file"], newline="") as fh:
        for row in csv.DictReader(fh):
            published = row.get("cost_per_success_usd") or None
            models.append(
                ModelResult(
                    name=row["model"],
                    provider=row["provider"],
                    pass_rate=float(row["pass_rate"]),
                    cost_per_attempt=float(row["cost_per_attempt_usd"]),
                    published_cpst=float(published) if published else None,
                )
            )
    return Dataset(key=key, meta=meta, models=models)


# ------------------------------------------------------------ per-run results

EXTERNAL_DIR = DATA_DIR / "external"


def runs_dir(ds: Dataset, data_dir: Path = DATA_DIR) -> Path:
    return data_dir / "external" / f"arize-{ds.meta['runs']['commit']}"


def runs_file(ds: Dataset, data_dir: Path = DATA_DIR) -> Path | None:
    """Path to the per-run JSONL if it has been fetched, else None."""
    if "runs" not in ds.meta:
        return None
    p = runs_dir(ds, data_dir) / "benchmark_40x6.jsonl"
    return p if p.exists() else None


def model_keys(ds: Dataset) -> dict[str, str]:
    """Published model name -> per-run model_key."""
    return dict(ds.meta["runs"]["model_keys"])
