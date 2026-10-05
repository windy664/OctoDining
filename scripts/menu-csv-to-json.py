#!/usr/bin/env python3
"""Convert a user-provided canteen CSV into OctoDining's pasteable JSON menu.

The app imports 3–200 items at once. Source name, update date and timezone are
entered in its onboarding screen; this tool never claims a CSV is live data.
"""
import argparse
import csv
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
import json
from pathlib import Path
import re
import sys

FIELDS = {
    "name": ("name", "商品名称"),
    "store": ("store", "店铺名称"),
    "category": ("category", "分类"),
    "business_hours": ("business_hours", "营业时间"),
    "price": ("price", "价格"),
}
HOURS = re.compile(r"^(?:[0-2][0-9]:[0-5][0-9]-[0-2][0-9]:[0-5][0-9])(?:,\s*[0-2][0-9]:[0-5][0-9]-[0-2][0-9]:[0-5][0-9])*$")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv_file", type=Path)
    parser.add_argument("--store", help="exact store name; useful when a CSV has more than 200 items")
    parser.add_argument("--output", type=Path, help="write JSON here instead of stdout")
    args = parser.parse_args()
    with args.csv_file.open(encoding="utf-8-sig", newline="") as source:
        reader = csv.DictReader(source)
        columns = {
            field: next((option for option in options if option in (reader.fieldnames or [])), None)
            for field, options in FIELDS.items()
        }
        if any(value is None for value in columns.values()):
            parser.error("CSV needs name/store/category/business_hours/price columns (English or menu.csv Chinese headers)")
        rows = []
        keys = set()
        for line, row in enumerate(reader, 2):
            values = {key: (row[column] or "").strip() for key, column in columns.items()}
            if args.store and values["store"] != args.store:
                continue
            if not values["name"] or not values["store"]:
                parser.error(f"line {line}: item name and store are required")
            try:
                cents = int((Decimal(values["price"]) * 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
            except (InvalidOperation, ValueError):
                parser.error(f"line {line}: invalid price")
            if not 100 <= cents <= 50000:
                parser.error(f"line {line}: price must be ¥1–500")
            hours = values["business_hours"].replace("，", ",")
            if not HOURS.fullmatch(hours):
                parser.error(f"line {line}: hours must use HH:MM-HH:MM, separated by commas")
            for period in hours.split(","):
                start, end = period.strip().split("-")
                if start >= "24:00" or end >= "24:00" or start == end:
                    parser.error(f"line {line}: invalid hours")
            key = (values["store"], values["name"], hours)
            if key in keys:
                parser.error(f"line {line}: duplicate item at the same store and hours")
            keys.add(key)
            rows.append({
                "name": values["name"], "store": values["store"],
                "category": values["category"], "business_hours": hours,
                "cents": cents,
            })
            if len(rows) > 200:
                parser.error("more than 200 items; select one store with --store or prepare a smaller menu")
    if len(rows) < 3:
        parser.error("at least three items are required")
    output = json.dumps(rows, ensure_ascii=False, separators=(",", ":")) + "\n"
    if args.output:
        args.output.write_text(output, encoding="utf-8")
        print(f"Converted {len(rows)} items to {args.output}", file=sys.stderr)
    else:
        sys.stdout.write(output)


if __name__ == "__main__":
    main()
