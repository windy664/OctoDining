#!/usr/bin/env python3
"""Verify the week-page Agent proposal flow and its no-service fallback."""
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
    port = 8274
    work = ROOT / ".local-state" / ("week-agent-" + datetime.now().strftime("%Y%m%d-%H%M%S"))
    jail = work / "org.octosense.octodining"
    jail.mkdir(parents=True)
    preview_bundle = basic.prepare_dev_bundle(work / 'preview-bundle') if hasattr(basic, 'prepare_dev_bundle') else __import__('dev_bundle', fromlist=['prepare_dev_bundle']).prepare_dev_bundle(work / 'preview-bundle')
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
    running = False
    try:
        subprocess.run([
            str(octo), "run", str(preview_bundle), "--hidden", "--detach",
            "--port", str(port), "--app-data", str(work), "--timeout", "30",
        ], check=True, env=env, stdout=subprocess.DEVNULL)
        running = True
        app.click("week_nav")
        app.click("make_draft")
        summary = ""
        deadline = time.monotonic() + 15
        while time.monotonic() < deadline:
            summary = app.text("draft_summary")
            if "待确认" in summary:
                break
            time.sleep(.4)
        assert "待确认" in summary, summary
        options = app.text("week_agent_options")
        assert "¥" in options and ". " in options, f"swap options not populated: {options[:80]!r}"
        assert not list(jail.glob("plans-*.json")), "draft wrote a plan before confirmation"

        app.fill("week_agent_request", "本周少辣，避免重复")
        app.click("week_agent_ask")
        deadline = time.monotonic() + 15
        result = ""
        while time.monotonic() < deadline:
            result = app.text("week_agent_result")
            if "暂不可用" in result or "Agent" in result and "不可用" in result:
                break
            time.sleep(.2)
        assert "暂不可用" in result, result
        print("PASS agent request fails honestly without a host agent service", flush=True)

        assert not list(jail.glob("plans-*.json")), "agent failure wrote a plan"
        app.click("week_agent_apply")
        deadline = time.monotonic() + 6
        status = ""
        while time.monotonic() < deadline:
            status = app.text("status")
            if "提案" in status:
                break
            time.sleep(.1)
        assert "失效" in status or "重新请求" in status, status
        assert not list(jail.glob("plans-*.json")), "apply without proposal wrote a plan"
        if frame.exists():
            shutil.copyfile(frame, work / "fallback.png")
        print("PASS apply rejected without a proposal; draft stayed unconfirmed", flush=True)
        print("Evidence:", work, flush=True)
    finally:
        if running:
            try:
                app.quit()
            except OSError:
                pass


if __name__ == "__main__":
    main()
