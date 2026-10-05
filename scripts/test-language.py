#!/usr/bin/env python3
"""Exercise both languages, persistence and Agent fallback in native card-host."""
from datetime import datetime
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import time

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('octodining_basic_test', ROOT / 'scripts/test-basic-app.py')
basic = importlib.util.module_from_spec(spec)
spec.loader.exec_module(basic)
App = basic.App


def main():
    port = 8245
    work = ROOT / '.local-state' / ('language-' + datetime.now().strftime('%Y%m%d-%H%M%S'))
    work.mkdir(parents=True)
    app = App(port)
    octo = ROOT.parent / 'octosense-ws/OctoScript-App-Design-Flow/tools/octo'
    env = dict(os.environ)
    env.pop('WAYLAND_DISPLAY', None)

    def start():
        subprocess.run([str(octo), 'run', str(ROOT / 'bundle'), '--hidden', '--detach',
                        '--port', str(port), '--app-data', str(work), '--timeout', '30'],
                       check=True, stdout=subprocess.DEVNULL, env=env)
        time.sleep(.2)

    running = False
    try:
        start(); running = True
        assert app.text('lang_toggle') == 'EN'
        app.click('lang_toggle')
        assert app.text('setup_title') == 'Set aside meal money.'
        assert json.loads((work / 'org.octosense.octodining' / 'language.json').read_text())['lang'] == 'en'
        app.fill('setup_monthly', '1500.00')
        app.fill('setup_fixed', '540.00')
        app.get('m', k='scroll', x=200, y=610, dy=250, wait=1)
        app.click('setup_preview')
        assert 'about ¥32.00/day' in app.text('setup_result')
        app.click('setup_start')
        assert app.text('intro_title') == 'Eat well today.'
        app.click('manual')
        app.click('find')
        app.status('Found 3 options')
        app.click('ask_agent')
        assert 'unavailable' in app.text('agent_result').lower()
        app.click('Confirm option 1')
        app.status('Saved and read back')
        app.click('tab_history')
        assert 'My week' in app.text('week_title')
        assert app.node('Cancel Dinner')
        print('PASS English onboarding, meal choice, Agent fallback and week plan', flush=True)

        app.quit(); running = False
        start(); running = True
        assert app.text('lang_toggle') == '中文'
        app.click('week_nav')
        assert app.node('Cancel Dinner')
        app.click('lang_toggle')
        assert app.text('lang_toggle') == 'EN'
        assert app.node('取消晚餐')
        print('PASS language persists across restart and switches back without losing plans', flush=True)
        print('Evidence:', work, flush=True)
    finally:
        if running:
            try: app.quit()
            except OSError: pass


if __name__ == '__main__':
    main()
