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
    env['MAKEPAD_WRITE_FRAMEBUFFER_PNG'] = str(work / 'framebuffer.png')

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
        for _ in range(3):
            app.get('m', k='scroll', x=200, y=610, dy=250, wait=1)
            app.click('setup_preview')
            if 'about ¥32.00/day' in app.text('setup_result'):
                break
        assert 'about ¥32.00/day' in app.text('setup_result'), app.text('setup_result')
        app.click('setup_start')
        assert app.text('intro_title') == 'Eat well today.'
        assert app.text('home_name') == '螺丝椒炒鸡蛋盖饭'
        assert any(n.get('i') == 'home_image_wrap' and n.get('r', [0, 0, 0, 0])[2] > 0 for n in app.snap())
        app.click('manual')
        app.fill('daily', '9.00')
        app.click('save_daily')
        app.click('home_nav')
        assert app.text('home_name') == '芽菜肉沫面', app.text('home_name')
        assert not any(n.get('i') == 'home_image_wrap' and n.get('r', [0, 0, 0, 0])[2] > 0 for n in app.snap())
        time.sleep(.2)
        (work / 'no-image-home.png').write_bytes((work / 'framebuffer.png').read_bytes())
        app.click('manual')
        app.fill('daily', '32.00')
        app.click('save_daily')
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
