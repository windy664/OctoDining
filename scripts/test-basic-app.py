#!/usr/bin/env python3
"""Runs the full flow; some checks assume today has a plannable dinner (run roughly 06:00–20:00 canteen time).Exercise the real OctoScript app through Makepad's local UI bridge.

Uses an isolated storage directory. No model calls or desktop input injection.
"""
import argparse
from datetime import date, datetime, timedelta
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import time
import urllib.parse
import urllib.request
from urllib.error import HTTPError, URLError
from dev_bundle import prepare_dev_bundle

ROOT = Path(__file__).resolve().parents[1]
APP_ID = 'org.octosense.octodining'

class App:
    def __init__(self, port):
        self.base = f'http://127.0.0.1:{port}'
        self.http = urllib.request.build_opener(urllib.request.ProxyHandler({}))

    def get(self, route, **params):
        url = self.base + '/' + route
        if params:
            url += '?' + urllib.parse.urlencode(params)
        with self.http.open(url, timeout=10) as r:
            return r.read()

    def snap(self):
        return [x for x in json.loads(self.get('snap'))['s'] if x.get('ty') != 'Splash']

    def node(self, key):
        def visible():
            nodes = self.snap()
            matches = [x for x in nodes if x.get('i') == key or x.get('t') == key]
            min_height = 30 if key in ('setup_import_json', 'setup_import') else 0
            return nodes, [x for x in matches if x.get('r', [0,0,0,0])[2] > 0 and x['r'][3] > min_height]
        nodes, matches = visible()
        if not matches:
            # The conditions and weekly plan are real native scroll views.
            # Start at the top, then look through the currently open view.
            scroll_x = 20 if key.startswith('setup_import') else 200
            if key.startswith('setup_import'):
                self.get('m', k='scroll', x=20, y=600, dy=650, wait=1)
                nodes, matches = visible()
                if matches:
                    return matches[-1]
            self.get('m', k='scroll', x=scroll_x, y=610, dy=-2000, wait=1)
            for _ in range(8):
                nodes, matches = visible()
                if matches:
                    break
                self.get('m', k='scroll', x=scroll_x, y=610, dy=250, wait=1)
        if not matches:
            raise AssertionError(f'Missing widget {key!r}; visible texts: {[n.get("t") for n in nodes if n.get("t")]}')
        return matches[-1]

    def click(self, key):
        x,y,w,h = self.node(key)['r']
        self.get('click', x=x+w/2, y=y+h/2, wait=1)
        time.sleep(.06)

    def text(self, key):
        return self.node(key).get('t', '')

    def fill(self, key, text):
        for attempt in range(3):
            self.click(key)
            self.get('k', k='down', c='End')
            # Remote text entry can lose a focused frame after scrolling.
            current = self.text(key)
            if key == 'setup_import_json' and current == '粘贴 JSON 菜单 / Paste JSON menu':
                current = ''
            for _ in range(len(current) + 2):
                self.get('k', k='down', c='Backspace')
                self.get('k', k='up', c='Backspace')
            self.get('t', t=text, wait=1)
            deadline = time.monotonic() + 2
            actual = self.text(key)
            while actual != text and time.monotonic() < deadline:
                time.sleep(.05)
                actual = self.text(key)
            if actual == text:
                return
        raise AssertionError(f'Could not enter {text!r} in {key!r}; got {actual!r}')

    def status(self, fragment):
        deadline = time.monotonic() + 5
        actual = self.text('status')
        while fragment not in actual and time.monotonic() < deadline:
            time.sleep(.1)
            actual = self.text('status')
        assert fragment in actual, (fragment, actual)

    def quit(self):
        self.get('quit')
        time.sleep(.2)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', type=int, default=8172)
    parser.add_argument('--octo', type=Path, default=ROOT.parent/'octosense-ws/OctoScript-App-Design-Flow/tools/octo')
    parser.add_argument('--inspect', action='store_true', help='inspect an already running app only')
    args = parser.parse_args()
    app = App(args.port)
    if args.inspect:
        for node in app.snap():
            if node.get('t'):
                print(node.get('i'), node.get('ty'), node.get('r'), node['t'])
        return
    stamp = time.strftime('%Y%m%d-%H%M%S')
    work = ROOT / '.local-state' / ('acceptance-' + stamp)
    work.mkdir(parents=True)
    preview_bundle = prepare_dev_bundle(work / 'preview-bundle')
    jail = work / APP_ID
    evidence = []
    def record(label):
        evidence.append(label)
        print('PASS',label,flush=True)
    def start():
        # Makepad's screenshot bridge needs a rendered X11 frame in this
        # headless acceptance run. Keep DISPLAY and select X11 explicitly by
        # removing Wayland's protocol selector from the child environment.
        env = dict(os.environ)
        env.pop('WAYLAND_DISPLAY', None)
        env['MAKEPAD_WRITE_FRAMEBUFFER_PNG'] = str(work / 'framebuffer.png')
        subprocess.run([str(args.octo),'run',str(preview_bundle),'--hidden','--detach','--port',str(args.port),'--app-data',str(work),'--timeout','30'],check=True,stdout=subprocess.DEVNULL,env=env)
        time.sleep(.2)
    def state():
        docs = []
        for path in jail.glob('plans-*.json'):
            try: docs.append(json.loads(path.read_text()))
            except (ValueError,IsADirectoryError): pass
        return max(docs,key=lambda v:v['revision'])
    current_date = ''
    def day():
        return next(d for d in state()['days'] if d['date']==current_date)
    started = False
    try:
        start(); started = True
        app.node('setup')
        app.fill('setup_monthly','1500.00')
        app.fill('setup_fixed','800.00')
        app.click('看看如何分配')
        assert '预算偏紧' in app.text('setup_result')
        app.fill('setup_fixed','540.00')
        app.click('看看如何分配')
        assert '每天约 ¥32.00' in app.text('setup_result')
        app.click('使用这份菜单，开始选餐')
        assert json.loads((jail/'profile.json').read_text())['daily_cents']==3200
        canteen_minute = datetime.now().hour * 60 + datetime.now().minute
        expected_slot = '早餐' if canteen_minute < 600 else '午餐' if canteen_minute < 840 else '晚餐' if canteen_minute < 1200 else '早餐'
        assert expected_slot in app.text('home_caption'), app.text('home_caption')
        record('First-run living allowance and non-food costs yield a persisted dining budget')
        app.click('week_nav')
        app.node('history')
        app.click('home_nav')
        app.click('manual')
        assert app.text('date') == date.today().isoformat()
        app.status('已打开 ')
        app.click('dinner')
        for i,amount in enumerate([15,22,32,45,65,100],1):
            app.click(f'a{i}')
            assert app.text('daily') == f'{amount}.00'
        record('A1–A6 daily budgets')
        app.click('a3')
        current_date=app.text('date')
        app.click('open_day')
        app.fill('arrival','99:00');assert app.text('arrival')=='99:00';app.click('find');app.status('时间需为有效')
        app.fill('arrival','18:30')
        app.fill('budget','1.001');assert app.text('budget')=='1.001';app.click('find');app.status('最多两位小数')
        app.fill('budget','14.00')
        app.fill('request','花生过敏');assert app.text('request')=='花生过敏';app.click('find');app.status('无法可靠核验')
        app.fill('request','别太辣')
        app.fill('date','2026-02-30');app.click('open_day');app.status('有效日期')
        app.fill('date',current_date);app.click('open_day')
        record('Invalid money, time, date and unsupported dietary conditions rejected')
        app.fill('budget','1.00')
        assert app.text('budget') == '1.00', ('budget field did not update',app.text('budget'))
        app.click('find');app.status('没有符合')
        app.fill('budget','14.00');app.click('find');app.status('找到')
        app.click('ask_agent')
        assert '暂不可用' in app.text('agent_result')
        record('Agent service unavailable is reported without blocking manual choice')
        app.click('确认候选 1');app.status('已保存并读回核验')
        assert len(day()['meals'])==1 and day()['meals'][0]['slot']==2
        assert day()['meals'][0]['cents']<=1400
        assert not any(c in day()['meals'][0]['name'] for c in '辣麻椒')
        record('Real menu filtering and confirmed dinner saved/read back')
        app.click('tab_choose');app.click('breakfast');app.click('find');app.status('找到')
        app.click('确认候选 1')
        assert len(day()['meals'])==2 and any(m['slot']==0 for m in day()['meals'])
        assert not any(c in day()['meals'][-1]['name'] for c in '加料打包费餐具')
        record('Breakfast candidates and breakfast plan saved')
        app.click('修改晚餐');app.click('find');app.click('确认候选 1')
        assert len(day()['meals'])==2
        record('Replacing same meal never double counts')
        app.click('tab_choose');app.click('lunch');app.click('find');app.click('确认候选 1')
        assert len(day()['meals'])==3
        total=sum(m['cents'] for m in day()['meals'])
        assert total<=day()['daily_cents']
        record('Multiple meals respect daily budget')
        app.click('记录已吃晚餐')
        app.fill('actual_price','20.00')
        app.click('checkin_confirm');app.status('已记录吃过')
        eaten=next(m for m in day()['meals'] if m['slot']==2)
        assert eaten['actual_cents']==2000 and eaten['eaten_at']>=eaten['saved_at']
        assert '已吃 ¥20.00' in app.text('summary')
        time.sleep(1)
        if (work/'framebuffer.png').exists():
            shutil.copyfile(work/'framebuffer.png',work/'meal-eaten.png')
        app.click('撤销已吃晚餐');app.status('已撤销用餐记录')
        assert next(m for m in day()['meals'] if m['slot']==2)['eaten_at'] is None
        record('Meal check-in records paid amount, updates budget, and can be undone')
        empty_date=(date.fromisoformat(current_date)+timedelta(days=1)).isoformat()
        app.fill('date',empty_date);app.click('open_day');app.click('tab_history')
        assert '还没有已确认计划' in app.text('这一天还没有已确认计划。')
        app.fill('date',current_date);app.click('open_day')
        record('Plans stay isolated by calendar date')
        app.click('tab_choose');app.fill('daily','1.00');app.click('save_daily');app.status('低于已计划')
        app.fill('daily','35.25');app.click('save_daily');app.status('日预算已保存')
        assert day()['daily_cents']==3525
        app.click('find');app.click('tab_choose');app.fill('budget','2.00')
        assert not any(n.get('t','').startswith('确认候选') for n in app.snap())
        record('Decimal budget persistence and stale candidates invalidated')
        app.quit();started=False
        start();started=True
        app.click('manual')
        assert app.text('daily')=='35.25'
        assert f'已计划 ¥{total/100:.2f}' in app.text('summary')
        app.click('tab_history');app.node('取消午餐');app.node('取消晚餐')
        record('Restart restores saved budget and meals')
        app.click('取消晚餐');app.status('已取消晚餐')
        assert len(day()['meals'])==2 and {m['slot'] for m in day()['meals']}=={0,1}
        record('Cancellation updates and verifies saved totals')
        # A directory at the next journal destination forces a real write failure.
        doc=state();rev=doc['revision']
        active=next(p for p in jail.glob('plans-*.json') if p.is_file() and json.loads(p.read_text())['revision']==rev)
        target=jail/('plans-b.json' if active.name=='plans-a.json' else 'plans-a.json')
        target.rename(target.with_suffix('.previous'))
        target.mkdir()
        app.click('取消午餐');app.status('保存失败')
        assert len(day()['meals'])==2 and state()['revision']==rev
        app.node('取消午餐')
        record('Actual storage failure preserves prior confirmed plan')
        target.rmdir();target.write_text('{broken')
        app.quit();started=False
        start();started=True
        app.click('manual')
        app.status('恢复另一份有效记录')
        app.click('tab_history');app.node('取消午餐')
        record('Corrupt journal copy recovers last valid record')
        shot=work/'plans.png'
        try:
            shot.write_bytes(app.get('g',raw=1))
            screenshot=str(shot)
        except (HTTPError,URLError,TimeoutError) as error:
            screenshot=None
            print('NOTE screenshot capture unavailable:',error,flush=True)
        app.quit();started=False
        # Both invalid files must never silently reset or overwrite user data.
        for p in jail.glob('plans-*.json'):p.write_text('{broken')
        start();started=True
        app.click('manual')
        app.status('已暂停保存')
        app.click('save_daily');app.status('已暂停保存')
        assert all(p.read_text()=='{broken' for p in jail.glob('plans-*.json'))
        record('Unreadable storage locks writes without resetting data')
        manifest=json.loads((ROOT/'bundle/manifest.json').read_text())
        report={'checks':evidence,'app_data':str(work),'screenshot':screenshot,'head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'worktree_dirty':bool(subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True).strip()),'bundle_sha256':hashlib.sha256((ROOT/'bundle/main.splash').read_bytes()).hexdigest(),'manifest':manifest}
        (work/'results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
        print('Evidence:',work,flush=True)
    finally:
        if started:
            try: app.quit()
            except Exception: pass

if __name__=='__main__':
    main()
