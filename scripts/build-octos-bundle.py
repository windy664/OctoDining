#!/usr/bin/env python3
"""Embed the canonical menu snapshot into the OctoScript mini-app source."""
import json
import argparse
import csv
from collections import defaultdict, deque
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument(
    "--rinx-app",
    type=Path,
    help="also sync the generated main.splash into a registered Rinx app directory",
)
args = parser.parse_args()
products = json.loads((ROOT / "products_clean.json").read_text(encoding="utf-8"))
source_rows = defaultdict(deque)
with (ROOT / "menu.csv").open(encoding="utf-8-sig", newline="") as menu_file:
    for row in csv.DictReader(menu_file):
        key = (row["商品名称"], row["店铺名称"],
               int((Decimal(row["价格"]) * 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP)),
               row["分类"], row["营业时间"])
        source_rows[key].append(row)
photo_count = 0
for product in products:
    product["cents"] = int((Decimal(str(product["price"])) * 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
    if product["cents"] <= 0:
        raise SystemExit("Menu prices must be positive")
    key = (product["name"], product["store"], product["cents"],
           product["category"], product["business_hours"])
    if not source_rows[key]:
        raise SystemExit(f"No source CSV row for {product['name']!r} at {product['store']!r}")
    image_url = source_rows[key].popleft()["商品图片"].strip()
    parsed = urlparse(image_url)
    if image_url and "/default/" not in parsed.path:
        if parsed.scheme != "https" or parsed.hostname != "img.pospal.cn":
            raise SystemExit(f"Unexpected menu image host for {product['name']!r}")
        product["image_url"] = image_url
        photo_count += 1
    else:
        product["image_url"] = ""
template = (ROOT / "scripts/main.splash.in").read_text(encoding="utf-8")
compact = json.dumps(products, ensure_ascii=False, separators=(",", ":"))
source = template.replace("__MENU_JSON__", json.dumps(compact, ensure_ascii=False))
(ROOT / "bundle/main.splash").write_text(source, encoding="utf-8")
print(f"Embedded {len(products)} menu records, {photo_count} menu images ({len(source.encode('utf-8'))} bytes) in bundle/main.splash")
if args.rinx_app:
    manifest_path = args.rinx_app / "bundle/manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    capabilities = set(manifest.get("capabilities", []))
    if "octos.turn.start" not in capabilities or "net" in capabilities:
        raise SystemExit("Rinx target must request octos.turn.start and must not request net")
    target = args.rinx_app / "bundle/main.splash"
    target.write_text(source, encoding="utf-8")
    print(f"Synced the same script to {target}")
