#!/usr/bin/env python3
"""Embed the canonical menu snapshot into the OctoScript mini-app source."""
import json
import argparse
import csv
import re
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
breakfast_hint = re.compile("包子|馒头|粥|肠粉|油条|饺|馄饨|云吞|三明治|鸡蛋|煎蛋")

# Slot pools mirror matches_meal_for / matches_snack in scripts/main.splash.in.
# Keep these regexes byte-identical to the template's.
_non_meal = re.compile("勿点|专用|补差|打包费|餐具|加料|加粉|加饭|加面|配菜|小料|升级")
_breakfast_excl = re.compile("饮|奶茶|果切|水果|咖啡|甜品|蛋糕|豆浆|牛奶|加料")
_breakfast_exact = re.compile("^鸡蛋$|^煎蛋$|^煎鸡蛋$|^鸡蛋泥$|^肉沫干蒸鸡蛋$")
_main_staple = re.compile("饭|粉|面|米线|馄饨|云吞|饺子|套餐|堡")
_main_protein = re.compile("肉|鸡|鸭|猪|牛|鱼|虾|蛋|肘|排骨|叉烧|云吞|饺|腊|煲仔|麻婆")
_main_excl = re.compile("饮|奶茶|果切|水果|咖啡|甜品|蛋糕|面包|早餐|粥类|豆浆|油条|斋|清汤|青菜|白饭|米饭|单点|小份|半份|小碗")
_snack_hint = re.compile("面包|蛋糕|奶茶|果切|鲜果|饮料|柠檬|咖啡|小吃|甜品|糕点")
_snack_excl = re.compile("勿点|专用|补差|打包费|餐具|加料")

def _pool_for(slot):
    out = []
    # Drafts always use the slot's default arrival time, so the build filters
    # business hours too; the runtime loop then skips per-item hour checks.
    default_time = {0: "08:00", 1: "12:00", 2: "18:30", 3: "15:30"}[slot]
    for index, product in enumerate(products):
        text = product["name"] + " " + product["category"]
        open_ok = any(
            len(parts) == 2 and parts[0].strip() <= default_time < parts[1].strip()
            for parts in (period.strip().split("-") for period in product["business_hours"].split(","))
        )
        if not open_ok:
            continue
        if slot == 0:
            ok = (not _non_meal.search(text)
                  and breakfast_hint.search(text)
                  and not _breakfast_excl.search(text)
                  and not _breakfast_exact.search(product["name"]))
        elif slot == 3:
            ok = (not _snack_excl.search(text)
                  and _snack_hint.search(text)
                  and product["cents"] <= 2000)
        else:
            ok = (not _non_meal.search(text)
                  and _main_staple.search(text)
                  and _main_protein.search(product["name"])
                  and not _main_excl.search(text)
                  and product["cents"] >= 800)
        if ok:
            out.append(index)
    return out

lunch_pool = _pool_for(1)
dinner_pool = _pool_for(2)
snack_pool = _pool_for(3)
breakfast_pool = _pool_for(0)
print(f"Pools: breakfast {len(breakfast_pool)}, lunch {len(lunch_pool)}, dinner {len(dinner_pool)}, snack {len(snack_pool)}")
source = template.replace("__MENU_JSON__", json.dumps(compact, ensure_ascii=False))
source = source.replace("__BREAKFAST_POOL__", json.dumps(json.dumps(breakfast_pool)))
source = source.replace("__LUNCH_POOL__", json.dumps(json.dumps(lunch_pool)))
source = source.replace("__DINNER_POOL__", json.dumps(json.dumps(dinner_pool)))
source = source.replace("__SNACK_POOL__", json.dumps(json.dumps(snack_pool)))
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
