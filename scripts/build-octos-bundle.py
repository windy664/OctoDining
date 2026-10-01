#!/usr/bin/env python3
"""Embed the canonical menu snapshot into the OctoScript mini-app source."""
import json
import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument(
    "--rinx-app",
    type=Path,
    help="also sync the generated main.splash into a registered Rinx app directory",
)
args = parser.parse_args()
products = json.loads((ROOT / "products_clean.json").read_text(encoding="utf-8"))
template = (ROOT / "scripts/main.splash.in").read_text(encoding="utf-8")
compact = json.dumps(products, ensure_ascii=False, separators=(",", ":"))
source = template.replace("__MENU_JSON__", json.dumps(compact, ensure_ascii=False))
(ROOT / "bundle/main.splash").write_text(source, encoding="utf-8")
print(f"Embedded {len(products)} menu records ({len(source.encode('utf-8'))} bytes) in bundle/main.splash")
if args.rinx_app:
    manifest_path = args.rinx_app / "bundle/manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    capabilities = set(manifest.get("capabilities", []))
    if "octos.turn.start" not in capabilities or "net" in capabilities:
        raise SystemExit("Rinx target must request octos.turn.start and must not request net")
    target = args.rinx_app / "bundle/main.splash"
    target.write_text(source, encoding="utf-8")
    print(f"Synced the same script to {target}")
