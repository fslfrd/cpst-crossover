"""Download the per-run results at a pinned commit and verify their checksums.

The files stay in data/external/, which is gitignored: the source repository
has no license file, so this project links to the data rather than
redistributing it.
"""

from __future__ import annotations

import hashlib
import urllib.request
from pathlib import Path

from .data import Dataset, runs_dir

RAW = "https://raw.githubusercontent.com/{owner_repo}/{commit}/{path}"


def fetch_runs(ds: Dataset, force: bool = False) -> Path:
    runs = ds.meta["runs"]
    owner_repo = runs["repo"].removeprefix("https://github.com/").rstrip("/")
    out = runs_dir(ds)
    out.mkdir(parents=True, exist_ok=True)
    for path, expected in runs["files"].items():
        dest = out / Path(path).name
        if dest.exists() and not force and _sha256(dest) == expected:
            print(f"ok      {dest.name}")
            continue
        url = RAW.format(owner_repo=owner_repo, commit=runs["commit"], path=path)
        with urllib.request.urlopen(url, timeout=60) as resp:
            data = resp.read()
        got = hashlib.sha256(data).hexdigest()
        if got != expected:
            raise RuntimeError(f"checksum mismatch for {path}: expected {expected}, got {got}")
        dest.write_bytes(data)
        print(f"fetched {dest.name}")
    return out


def _sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()
