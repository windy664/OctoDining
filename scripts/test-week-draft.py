#!/usr/bin/env python3
"""Verify a seven-day draft and one confirmed write in the native app."""
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
    port = 8264
    work = ROOT / ".local-state" / ("week-" + datetime.now().strftime("%Y%m%d-%H%M%S"))
    jail = work / "org.octosense.octodining"
    jail.mkdir(parents=True)
    (jail / "profile.json").write_text(json.dumps({
        "schema": 1, "menu": "gzis-snapshot", "monthly_cents": 150000,
        "fixed_cents": 54000, "reserve_cents": 0, "daily_cents": 3200,
    }))
    frame = work / "framebuffer.png"
    env = dict(os.environ)
    env.pop("WAYLAND_DISPLAY", None)
    env["MAKEPAD_WRITE_FRAMEBUFFER_PNG"] = str(frame)
    octo = ROOT.parent / "octosense-ws/OctoScript-App-Design-Flow/tools/octo"
    app = App(port)

    def press(key):
        x, y, width, height = app.node(key)["r"]
        app.get("click", x=x + width / 2, y=y + height / 2, wait=0)

    def await_status(fragment):
        deadline = time.monotonic() + 12
        while time.monotonic() < deadline:
            value = app.text("status")
            if fragment in value:
                return value
            time.sleep(.1)
        raise AssertionError((fragment, value))

    running = False
    try:
        subprocess.run([
            str(octo), "run", str(ROOT / "bundle"), "--hidden", "--detach",
            "--port", str(port), "--app-data", str(work), "--timeout", "30",
        ], check=True, env=env, stdout=subprocess.DEVNULL)
        running = True
        app.click("week_nav")
        press("make_draft")
        await_status("已生成七天草案")
        assert "缺口 0 餐" in app.text("draft_summary"), app.text("draft_summary")
        assert not list(jail.glob("plans-*.json")), "draft wrote a plan before confirmation"
        if frame.exists():
            shutil.copyfile(frame, work / "draft.png")
        print("PASS draft leaves no confirmed plan and reports no gaps", flush=True)

        press("confirm_draft")
        await_status("已确认并读回核验")
        documents = [json.loads(path.read_text()) for path in jail.glob("plans-*.json")]
        plan = max(documents, key=lambda document: document["revision"])
        assert len(plan["days"]) == 7
        assert sum(len(day["meals"]) for day in plan["days"]) >= 19
        for day in plan["days"]:
            assert sum(meal["cents"] for meal in day["meals"]) <= day["daily_cents"]
            assert len({meal["slot"] for meal in day["meals"]}) == len(day["meals"])
            assert all(meal["name"] not in {"鸡蛋", "煎蛋", "煎鸡蛋", "鸡蛋泥"} for meal in day["meals"])
        if frame.exists():
            time.sleep(2)
            shutil.copyfile(frame, work / "confirmed.png")
        print("PASS seven-day plan saved, read back, and kept within each daily budget", flush=True)
        print("Evidence:", work, flush=True)
    finally:
        if running:
            try:
                app.quit()
            except OSError:
                pass


if __name__ == "__main__":
    main()
