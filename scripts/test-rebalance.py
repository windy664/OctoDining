#!/usr/bin/env python3
"""Week rebalance flow: an inflated actual payment pushes the week over budget,
the Heads up card offers a rebalance, the user reviews swaps and applies them.

Also covers: missed check-in alert (a past planned meal never confirmed) and
the week budget bar counting eaten meals at the amount actually paid.

Assumes a canteen-local time roughly 06:00–20:00 so today gets plannable meals.
"""
from datetime import datetime, timedelta
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import time
from dev_bundle import prepare_dev_bundle

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("octodining_basic", ROOT / "scripts/test-basic-app.py")
basic = importlib.util.module_from_spec(spec)
spec.loader.exec_module(basic)
App = basic.App

SLOT_NAMES = ["早餐", "午餐", "晚餐", "加餐"]


def canteen_today():
    return (datetime.utcnow() + timedelta(hours=8)).date()


def load_menu_products():
    line = (ROOT / "bundle/main.splash").read_text().splitlines()[0]
    assert line.startswith("let menuJson = "), line[:40]
    return json.loads(json.loads(line[len("let menuJson = "):]))


def hours_cover(business_hours, hhmm):
    h, m = int(hhmm[:2]), int(hhmm[3:])
    moment = h * 60 + m
    for part in business_hours.split(","):
        part = part.strip()
        if "-" not in part:
            continue
        start, end = part.split("-")
        sh, sm = int(start[:2]), int(start[3:])
        eh, em = int(end[:2]), int(end[3:])
        if sh * 60 + sm <= moment <= eh * 60 + em:
            return True
    return False


def week_window_dates(today):
    return [today + timedelta(days=i) for i in range(7)]


def committed_total(plan, today, daily_default):
    window = {d.isoformat() for d in week_window_dates(today)}
    budget = 0
    committed = 0
    by_date = {day["date"]: day for day in plan["days"]}
    for d in week_window_dates(today):
        day = by_date.get(d.isoformat())
        if day is None:
            budget += daily_default
            continue
        budget += day["daily_cents"]
        for meal in day["meals"]:
            if meal.get("eaten_at") is not None:
                committed += meal["actual_cents"]
            else:
                committed += meal["cents"]
    return budget, committed


def newest_plan(jail):
    documents = [json.loads(path.read_text()) for path in jail.glob("plans-*.json")]
    return max(documents, key=lambda document: document["revision"])


def main():
    port = 8281
    work = ROOT / ".local-state" / ("rebalance-" + datetime.now().strftime("%Y%m%d-%H%M%S"))
    jail = work / "org.octosense.octodining"
    jail.mkdir(parents=True)
    preview_bundle = prepare_dev_bundle(work / "preview-bundle")

    today = canteen_today()
    yesterday = (today - timedelta(days=1)).isoformat()
    products = load_menu_products()
    past_product = next(p for p in products if hours_cover(p["business_hours"], "12:00"))
    past_id = products.index(past_product)
    (jail / "profile.json").write_text(json.dumps({
        "schema": 1, "menu": "gzis-snapshot", "monthly_cents": 100000,
        "fixed_cents": 40000, "reserve_cents": 0, "daily_cents": 2000,
    }))
    (jail / "plans-a.json").write_text(json.dumps({
        "schema": 1, "revision": 1, "last_date": yesterday,
        "days": [{
            "date": yesterday, "daily_cents": 2000,
            "meals": [{
                "slot": 1, "product_id": past_id, "cents": past_product["cents"],
                "name": past_product["name"], "store": past_product["store"],
                "hours": past_product["business_hours"], "arrival": "12:00",
                "note": "", "saved_at": int(time.time()) - 86400,
            }],
        }],
    }))

    frame = work / "framebuffer.png"
    env = dict(os.environ)
    env.pop("WAYLAND_DISPLAY", None)
    env["MAKEPAD_WRITE_FRAMEBUFFER_PNG"] = str(frame)
    env["MAKEPAD_WRITE_FRAMEBUFFER_PNG"] = str(frame)
    octo = ROOT.parent / "octosense-ws/OctoScript-App-Design-Flow/tools/octo"
    app = App(port)

    running = False
    try:
        subprocess.run([
            str(octo), "run", str(preview_bundle), "--hidden", "--detach",
            "--port", str(port), "--app-data", str(work), "--timeout", "30",
        ], check=True, env=env, stdout=subprocess.DEVNULL)
        running = True

        deadline = time.monotonic() + 12
        while "未确认" not in app.text("alerts_text") and time.monotonic() < deadline:
            time.sleep(.2)
        assert "未确认" in app.text("alerts_text"), app.text("alerts_text")
        print("PASS missed check-in alert for a past planned meal", flush=True)

        app.click("week_nav")
        app.click("make_draft")
        app.status("已生成七天草案")
        app.click("confirm_draft")
        app.status("已确认并读回核验")
        plan = newest_plan(jail)
        today_iso = today.isoformat()
        today_day = next((d for d in plan["days"] if d["date"] == today_iso), None)
        assert today_day and today_day["meals"], "today has no plannable meal; rerun 06:00–20:00 canteen time"
        meal = today_day["meals"][0]

        app.click("记录已吃" + SLOT_NAMES[meal["slot"]])
        app.fill("actual_price", "99.00")
        app.click("checkin_confirm")
        app.status("已记录吃过")
        app.click("taste_mid")
        time.sleep(.3)

        plan = newest_plan(jail)
        budget, committed = committed_total(plan, today, 2000)
        assert committed > budget, f"test setup did not overspend: {committed} vs {budget}"

        app.click("home_nav")
        deadline = time.monotonic() + 12
        while "超出周预算" not in app.text("alerts_text") and time.monotonic() < deadline:
            time.sleep(.2)
        alerts = app.text("alerts_text")
        assert "超出周预算" in alerts, alerts
        assert app.node("alerts_rebalance")["r"][2] > 0, "rebalance button not visible"
        print("PASS week overspend alert with rebalance entry", flush=True)

        label = app.text("week_budget_label") if False else None
        app.click("alerts_rebalance")
        app.status("已生成省钱调整方案")
        summary = app.text("rebalance_summary")
        assert "本周超支 ¥" in summary, summary
        lines = [n.get("t", "") for n in app.snap() if "（省 ¥" in n.get("t", "")]
        assert lines, "no rebalance lines rendered"
        print("PASS rebalance proposal:", summary, flush=True)
        for line in lines[:3]:
            print("  change:", line, flush=True)

        app.click("lang_toggle")
        summary_en = app.text("rebalance_summary")
        assert "Over budget by ¥" in summary_en, summary_en
        assert [n for n in app.snap() if "(save ¥" in n.get("t", "")], "no English rebalance lines"
        app.click("lang_toggle")
        assert "本周超支 ¥" in app.text("rebalance_summary"), app.text("rebalance_summary")
        print("PASS rebalance card follows language switch", flush=True)

        app.node("rebalance_apply")
        time.sleep(1.2)
        if frame.exists():
            import shutil
            shutil.copyfile(frame, work / "rebalance-proposal.png")

        app.click("rebalance_apply")
        app.status("已调整")
        app.status("读回核验")
        plan_after = newest_plan(jail)
        budget_after, committed_after = committed_total(plan_after, today, 2000)
        assert committed_after < committed, (committed, committed_after)
        eaten = [m for d in plan_after["days"] for m in d["meals"] if m.get("eaten_at") is not None]
        assert len(eaten) == 1 and eaten[0]["actual_cents"] == 9900, eaten
        label = app.text("week_budget_label")
        assert f"已计入 ¥{committed_after/100:.2f}" in label, label
        print(f"PASS swaps saved ¥{(committed-committed_after)/100:.2f}; bar counts actual payment", flush=True)
        print("Evidence:", work, flush=True)
    finally:
        if running:
            try:
                app.quit()
            except OSError:
                pass


if __name__ == "__main__":
    main()
