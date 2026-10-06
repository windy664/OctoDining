#!/usr/bin/env python3
"""Capture native OctoDining frames in an isolated card-host run.

The local Makepad /g bridge currently times out on this Linux/X11 setup.
MAKEPAD_WRITE_FRAMEBUFFER_PNG writes the actual rendered GPU framebuffer.
These images prove the app's card-host UI, not a Shell or live LLM run.
"""

import argparse
from datetime import datetime
import json
import os
from pathlib import Path
import struct
import subprocess
import time
import urllib.parse
import urllib.request
from dev_bundle import prepare_dev_bundle


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OCTO = ROOT.parent / "octosense-ws/OctoScript-App-Design-Flow/tools/octo"
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--octo", type=Path, default=DEFAULT_OCTO)
    parser.add_argument("--port", type=int, default=8189)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--language", choices=("zh", "en"), default="zh")
    args = parser.parse_args()
    output = args.output or ROOT / ".local-state" / ("screenshots-" + datetime.now().strftime("%Y%m%d-%H%M%S"))
    output = output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    preview_bundle = prepare_dev_bundle(output / "preview-bundle")
    framebuffer = output / "framebuffer.png"
    env = dict(os.environ)
    env.pop("WAYLAND_DISPLAY", None)  # X11 backend supplies this framebuffer hook.
    env["MAKEPAD_WRITE_FRAMEBUFFER_PNG"] = str(framebuffer)
    base = f"http://127.0.0.1:{args.port}/"

    def get(route):
        with urllib.request.urlopen(base + route, timeout=10) as response:
            return response.read()

    def snap():
        return json.loads(get("snap"))["s"]

    def click(widget_id=None, label=None):
        def matching():
            return [node for node in snap() if ((widget_id is not None and node.get("i") == widget_id) or (label is not None and node.get("t") == label)) and node.get("r", [0, 0, 0, 0])[2] > 0 and node["r"][3] > 0]
        nodes = matching()
        if not nodes:
            get("m?k=scroll&x=200&y=610&dy=-2000&wait=1")
            for _ in range(8):
                nodes = matching()
                if nodes:
                    break
                get("m?k=scroll&x=200&y=610&dy=250&wait=1")
        if not nodes:
            raise RuntimeError(f"Missing widget {widget_id or label!r}")
        x, y, w, h = nodes[-1]["r"]
        print("click", widget_id or label, (x, y, w, h), flush=True)
        get(f"click?x={x + w / 2}&y={y + h / 2}&wait=1")

    def fill(widget_id, value):
        for _ in range(3):
            click(widget_id=widget_id)
            get("k?k=down&c=End")
            current = next(node.get("t", "") for node in snap() if node.get("i") == widget_id)
            for _ in range(len(current) + 2):
                get("k?k=down&c=Backspace")
                get("k?k=up&c=Backspace")
            get("t?" + urllib.parse.urlencode({"t": value, "wait": 1}))
            actual = next(node.get("t", "") for node in snap() if node.get("i") == widget_id)
            if actual == value:
                return
        raise RuntimeError(f"Could not fill {widget_id}: {actual!r}")

    def capture(name, previous_mtime=0):
        # Product images arrive asynchronously after the UI frame. Give the
        # native renderer time to replace its black loading rectangle.
        if name != "00-first-run-setup.png":
            time.sleep(1.5)
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline:
            if framebuffer.exists() and framebuffer.stat().st_mtime_ns > previous_mtime:
                data = framebuffer.read_bytes()
                if data.startswith(PNG_MAGIC) and len(data) > 100_000:
                    time.sleep(.2)  # let the last UI redraw finish
                    data = framebuffer.read_bytes()
                    width, height = struct.unpack(">II", data[16:24])
                    path = output / name
                    path.write_bytes(data)
                    print(f"{path}: {width}x{height}, {len(data)} bytes")
                    return
            time.sleep(.05)
        raise RuntimeError("Rendered PNG did not appear; inspect card-host.log")

    started = False
    try:
        subprocess.run(
            [str(args.octo), "run", str(preview_bundle), "--hidden", "--detach", "--port", str(args.port), "--app-data", str(output), "--timeout", "30"],
            cwd=ROOT, env=env, check=True,
        )
        started = True
        current_toggle = next((node.get("t") for node in snap() if node.get("i") == "lang_toggle"), "")
        if current_toggle != ("中文" if args.language == "en" else "EN"):
            click(widget_id="lang_toggle")
        capture("00-first-run-setup.png")
        fill("setup_monthly", "1500.00")
        fill("setup_fixed", "540.00")
        get("m?k=scroll&x=200&y=610&dy=250&wait=1")
        click(widget_id="setup_preview")
        expected_budget = "每天约 ¥32.00" if args.language == "zh" else "about ¥32.00/day"
        if not any(expected_budget in node.get("t", "") for node in snap()):
            raise RuntimeError("First-run budget calculation failed: " + repr([(node.get("i"), node.get("t")) for node in snap() if node.get("t")]))
        click(widget_id="setup_start")
        if not any(node.get("i") == "home_name" for node in snap()):
            raise RuntimeError("First-run setup did not open the meal-first home")
        capture("01-home-recommendation.png")
        before = framebuffer.stat().st_mtime_ns
        click(widget_id="manual")
        click(widget_id="find")
        found = "找到 " if args.language == "zh" else "Found "
        if not any(found in node.get("t", "") for node in snap() if node.get("i") == "status"):
            raise RuntimeError("Candidate lookup did not complete: " + repr([node.get("t") for node in snap() if node.get("i") == "status"]))
        capture("02-candidates.png", before)
        before = framebuffer.stat().st_mtime_ns
        click(label="确认候选 1" if args.language == "zh" else "Confirm option 1")
        verified = "已保存并读回核验" if args.language == "zh" else "Saved and read back"
        if not any(verified in node.get("t", "") for node in snap() if node.get("i") == "status"):
            raise RuntimeError("Plan was not saved and read back")
        click(widget_id="tab_history")
        capture("03-week-plan-confirmed.png", before)
        print("card-host native capture complete; model and OctoSense Shell are outside this script")
    finally:
        if started:
            try:
                get("quit")
            except OSError:
                pass


if __name__ == "__main__":
    main()
