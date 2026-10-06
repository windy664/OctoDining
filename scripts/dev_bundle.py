#!/usr/bin/env python3
"""Make an unsigned local preview copy without touching the signed release."""

import argparse
import json
from pathlib import Path
import shutil


ROOT = Path(__file__).resolve().parents[1]


def prepare_dev_bundle(destination: Path) -> Path:
    destination = destination.resolve()
    source = ROOT / "bundle"
    local_state = (ROOT / ".local-state").resolve()
    if local_state not in destination.parents:
        raise ValueError("Development copy must be inside .local-state/")
    if destination.exists():
        shutil.rmtree(destination)
    shutil.copytree(source, destination)
    manifest = destination / "manifest.json"
    data = json.loads(manifest.read_text(encoding="utf-8"))
    data.get("integrity", {}).pop("signature", None)
    manifest.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return destination


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / ".local-state/preview-bundle")
    args = parser.parse_args()
    print(prepare_dev_bundle(args.output))
