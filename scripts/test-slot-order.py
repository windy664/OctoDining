#!/usr/bin/env python3
"""Day card lists meals in slot order (breakfast first) regardless of
confirmation order. Seeds dinner first, then adds breakfast, then reads the
week view's text order for today."""
from datetime import datetime
import importlib.util
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path("/home/windy/Project/OctoDining")
sys.path.insert(0, str(ROOT / "scripts"))
from dev_bundle import prepare_dev_bundle

spec = importlib.util.spec_from_file_location("octodining_basic", ROOT / "scripts/test-basic-app.py")
basic = importlib.util.module_from_spec(spec)
spec.loader.exec_module(basic)
App = basic.App

port = 8283
work = ROOT / ".local-state" / ("slotorder-" + datetime.now().strftime("%H%M%S"))
work.mkdir(parents=True)
preview_bundle = prepare_dev_bundle(work / "preview-bundle")
octo = ROOT.parent / "octosense-ws/OctoScript-App-Design-Flow/tools/octo"
app = App(port)

subprocess.run([str(octo), "run", str(preview_bundle), "--hidden", "--detach",
                "--port", str(port), "--app-data", str(work), "--timeout", "30"],
               check=True, cwd=ROOT, stdout=subprocess.DEVNULL)
try:
    app.fill("setup_monthly", "1500.00")
    app.fill("setup_fixed", "540.00")
    app.click("setup_preview")
    app.click("setup_start")
    # Onboarding now lands on the generated week draft; head home first.
    app.click("home_nav")

    app.click("manual")

    def confirm_current_slot():
        app.click("find")
        app.status("找到 ")
        app.click("确认候选 1")
        app.status("已保存并读回核验")

    # Dinner first.
    app.click("晚餐")
    confirm_current_slot()
    # Then breakfast for the same day.
    app.click("tab_choose")
    app.click("早餐")
    confirm_current_slot()

    app.click("tab_history")
    texts = [n.get("t", "") for n in app.snap() if n.get("t")]
    day_rows = [t for t in texts if t.startswith("早餐 · ") or t.startswith("午餐 · ") or t.startswith("晚餐 · ") or t.startswith("加餐 · ")]
    print("today rows:", day_rows, flush=True)
    assert len(day_rows) >= 2, day_rows
    assert day_rows[0].startswith("早餐 · "), day_rows
    assert day_rows[1].startswith("晚餐 · "), day_rows
    print("PASS day card lists breakfast before dinner regardless of confirmation order", flush=True)
finally:
    try:
        app.quit()
    except OSError:
        pass
