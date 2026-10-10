#!/usr/bin/env python3
"""Verify taste memory: verdict after check-in, badge rendering, scoring influence."""
from datetime import datetime
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import time

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("octodining_basic", ROOT / "scripts/test-basic-app.py")
basic = importlib.util.module_from_spec(spec)
spec.loader.exec_module(basic)
App = basic.App


def main():
    port = 8386
    work = ROOT / ".local-state" / ("taste-" + datetime.now().strftime("%Y%m%d-%H%M%S"))
    jail = work / "org.octosense.octodining"
    jail.mkdir(parents=True)
    from dev_bundle import prepare_dev_bundle
    preview_bundle = prepare_dev_bundle(work / "preview-bundle")
    (jail / "profile.json").write_text(json.dumps({
        "schema": 1, "menu": "gzis-snapshot", "monthly_cents": 150000,
        "fixed_cents": 54000, "reserve_cents": 0, "daily_cents": 3200,
    }))
    env = dict(os.environ)
    env.pop("WAYLAND_DISPLAY", None)
    octo = ROOT.parent / "octosense-ws/OctoScript-App-Design-Flow/tools/octo"
    app = App(port)
    running = False

    def get(node_id):
        return next((n.get("t", "") for n in app.snap() if n.get("i") == node_id), None)

    def scroll(dy, x=300, y=380):
        app.get("m", k="scroll", x=x, y=y, dy=dy, wait=1)
        time.sleep(.3)

    def wait_button(text):
        for _ in range(10):
            if text in [n.get("t", "") for n in app.snap() if n.get("t")]:
                return
            scroll(240)
        raise AssertionError(f"button {text!r} never appeared")

    try:
        subprocess.run([
            str(octo), "run", str(preview_bundle), "--hidden", "--detach",
            "--port", str(port), "--app-data", str(work), "--timeout", "30",
        ], check=True, env=env, stdout=subprocess.DEVNULL)
        running = True

        dish = None
        for _ in range(20):
            dish = get("home_name")
            if dish and "挑选" not in dish and "暂无" not in dish:
                break
            time.sleep(.3)
        assert dish, "no home recommendation"

        # Skip path (works at any hour): 换一道 records a skip and changes the pick.
        app.click("next_pick")
        time.sleep(1)
        data = json.loads((jail / "taste.json").read_text())
        assert data["items"][0]["skips"] == 1 and data["items"][0]["name"] == dish, data
        print(f"PASS skip recorded in taste.json for {dish}", flush=True)

        # Eaten-verdict path needs a check-in-able meal planned for today.
        for _ in range(20):
            caption = get("home_caption") or ""
            if caption:
                break
            time.sleep(.3)
        if "明天" in caption:
            print("NOTE late evening: next meal is tomorrow; eaten flow is same-day only — skipping it", flush=True)
            print("Evidence:", work, flush=True)
            return

        slot = next((s for s in ("早餐", "午餐", "晚餐") if s in caption), None)
        assert slot, caption
        app.click("home_cta")
        time.sleep(1)
        assert "已保存并读回核验" in (get("status") or ""), get("status")
        confirmed = get("home_name")
        assert confirmed and "暂无" not in confirmed, confirmed
        scroll(-2400)
        wait_button("记录已吃" + slot)
        app.click("记录已吃" + slot)
        time.sleep(.6)
        app.click("checkin_confirm")
        time.sleep(1)
        assert get("taste_title") == "这顿怎么样？", get("taste_title")
        app.click("taste_dislike")
        time.sleep(.6)
        data = json.loads((jail / "taste.json").read_text())
        entry = next((i for i in data["items"] if i["name"] == confirmed), None)
        assert entry and entry["dislikes"] == 1, data
        scroll(-2400)
        wait_button("撤销已吃" + slot)
        texts = [n.get("t", "") for n in app.snap() if n.get("t")]
        assert any("差评" in t and confirmed in t for t in texts), [t for t in texts if confirmed in t]
        print("PASS verdict recorded to taste.json and dislike badge shows on the week row", flush=True)

        app.click("撤销已吃" + slot)
        time.sleep(.6)
        scroll(-2400)
        wait_button("取消" + slot)
        app.click("取消" + slot)
        time.sleep(.8)
        app.click("home_nav")
        time.sleep(1)
        changed = get("home_name")
        assert changed and changed != confirmed, (confirmed, changed)
        print(f"PASS disliked dish {confirmed} no longer recommended (now {changed})", flush=True)
        print("Evidence:", work, flush=True)
    finally:
        if running:
            try:
                app.quit()
            except OSError:
                pass


if __name__ == "__main__":
    main()
