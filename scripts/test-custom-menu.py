#!/usr/bin/env python3
"""Exercise first-run JSON menu import, validation and restart recovery."""
from datetime import datetime
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


def main():
    port = 8265
    work = ROOT / ".local-state" / ("import-" + datetime.now().strftime("%Y%m%d-%H%M%S"))
    jail = work / "org.octosense.octodining"
    work.mkdir(parents=True)
    preview_bundle = prepare_dev_bundle(work / 'preview-bundle')
    app = App(port)
    octo = ROOT.parent / "octosense-ws/OctoScript-App-Design-Flow/tools/octo"
    env = dict(os.environ)
    env.pop("WAYLAND_DISPLAY", None)
    meals = [
        {"name": "鲜肉蒸饺", "store": "第一食堂", "category": "主食", "business_hours": "07:00-21:00", "cents": 800},
        {"name": "鸡腿饭", "store": "第一食堂", "category": "正餐", "business_hours": "07:00-21:00", "cents": 1200},
        {"name": "番茄鸡蛋面", "store": "第二食堂", "category": "正餐", "business_hours": "07:00-21:00", "cents": 1100},
    ]

    def start():
        subprocess.run([
            str(octo), "run", str(preview_bundle), "--hidden", "--detach",
            "--port", str(port), "--app-data", str(work), "--timeout", "30",
        ], check=True, env=env, stdout=subprocess.DEVNULL)
        time.sleep(.2)

    running = False
    try:
        start(); running = True
        app.click("setup_import_toggle")
        app.fill("setup_import_source", "自带食堂表")
        app.fill("setup_import_date", datetime.now().strftime("%Y-%m-%d"))
        bad = [dict(item) for item in meals]
        bad[2]["cents"] = 0
        app.fill("setup_import_json", json.dumps(bad, ensure_ascii=False))
        app.click("setup_import")
        assert "导入失败" in app.text("setup_import_result")
        assert not (jail / "custom-menu.json").exists()
        print("PASS invalid menu cannot replace the bundled menu", flush=True)

        # Restart clears the long rejected paste before the valid import.
        app.quit(); running = False
        start(); running = True
        app.click("setup_import_toggle")
        app.fill("setup_import_source", "自带食堂表")
        app.fill("setup_import_date", datetime.now().strftime("%Y-%m-%d"))
        app.fill("setup_import_json", json.dumps(meals, ensure_ascii=False))
        app.click("setup_import")
        assert "菜单已验证并读回" in app.text("setup_import_result")
        imported = json.loads((jail / "custom-menu.json").read_text())
        assert imported["source"] == "自带食堂表" and len(imported["products"]) == 3
        app.fill("setup_monthly", "1500.00")
        app.fill("setup_fixed", "540.00")
        app.click("setup_start")
        assert json.loads((jail / "profile.json").read_text())["menu"] == "custom-v1"
        assert app.text("home_name") in {item["name"] for item in meals}
        app.click("home_cta")
        app.status("已保存并读回核验")
        plans = [json.loads(path.read_text()) for path in jail.glob("plans-*.json")]
        assert max(plans, key=lambda plan: plan["revision"])["menu"] == "custom-v1"
        print("PASS imported canteen can recommend and save a real menu ID", flush=True)

        app.quit(); running = False
        start(); running = True
        assert app.text("home_name") in {item["name"] for item in meals}
        app.click("week_nav")
        assert any(item["name"] in str(app.snap()) for item in meals)
        print("PASS custom source and confirmed meal survive restart", flush=True)
        print("Evidence:", work, flush=True)
    finally:
        if running:
            try:
                app.quit()
            except OSError:
                pass


if __name__ == "__main__":
    main()
