const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');

const html = fs.readFileSync(new URL('../meal_planner.html', `file://${__filename}`), 'utf8');
const script = html.match(/<script>([\s\S]*?)<\/script>/)?.[1];
assert.ok(script, 'inline app script exists');
new vm.Script(script, { filename: 'meal_planner.html' });

class Element {
  constructor() {
    this.children = [];
    this.dataset = {};
    this.style = {};
    this.value = '';
    this.classList = { add() {}, toggle() {} };
  }
  append(...nodes) { this.children.push(...nodes); }
  appendChild(node) { this.children.push(node); }
  replaceChildren(...nodes) { this.children = nodes; }
  scrollIntoView() {}
  set innerHTML(value) { this.html = value; if (value === '') this.children = []; }
}

function boot(source = script) {
  const elements = new Map();
  const created = [];
  const document = {
    getElementById(id) {
      if (!elements.has(id)) elements.set(id, new Element());
      return elements.get(id);
    },
    querySelectorAll() {
      if (arguments[0] === '.choose-meal') return created.filter((element) => element.className === 'choose-meal');
      return Array.from({ length: 6 }, (_, i) => Object.assign(new Element(), { dataset: { tier: `A${i + 1}` } }));
    },
    createElement() { const element = new Element(); created.push(element); return element; },
  };
  const math = Object.create(Math);
  let roll = 0;
  math.random = () => ((roll++ * 37) % 97) / 100;
  const context = vm.createContext({ document, Math: math });
  vm.runInContext(source, context, { timeout: 5000 });
  return { context, document, elements };
}

const app = boot();
const tierBudgets = [15, 22, 32, 45, 65, 100];
for (let i = 1; i <= 6; i++) {
  app.context.selectTier(`A${i}`);
  app.document.getElementById('requestInput').value = '';
  app.context.generateMealPlan();
  const title = app.elements.get('taskTitle').textContent;
  assert.match(title, /自动任务已完成/, `A${i} task verification passed`);
  const proof = app.elements.get('taskSteps').children[3].children[1].textContent;
  assert.match(proof, /超预算 0 天/);
  const dayCards = app.elements.get('daysGrid').children;
  assert.equal(dayCards.length, 7, `A${i} produces seven day cards`);
  for (const card of dayCards) {
    const amounts = [...card.html.matchAll(/class="day-total">¥([\d.]+)/g)].map((m) => Number(m[1]));
    assert.equal(amounts.length, 1);
    assert.ok(amounts[0] <= tierBudgets[i - 1] + 0.001, `A${i} daily cap`);
  }
}

app.document.getElementById('requestInput').value = '帮我按每天 30 元规划一周三餐';
app.context.generateMealPlan();
assert.match(app.elements.get('taskSummary').textContent, /识别为 A3/);

app.document.getElementById('requestInput').value = '预算 20 元，晚上 19 点到食堂';
app.context.pickTonight();
assert.match(app.elements.get('taskTitle').textContent, /今晚候选已核验/);
assert.ok(app.elements.get('tonightList').children.length > 0 && app.elements.get('tonightList').children.length <= 3);
app.document.getElementById('requestInput').value = '预算 20 元，晚上 19 点到食堂，不吃辣';
app.context.pickTonight();
assert.ok(app.elements.get('tonightList').children.every((card) => !/(辣|麻|椒)/.test(card.children[0].textContent)));
const chosen = app.elements.get('tonightList').children[0].children.at(-1);
chosen.onclick();
assert.equal(chosen.disabled, true, 'user confirmation changes the selected meal state');
assert.match(app.elements.get('tonightIntro').textContent, /不会代你下单或付款/);

app.document.getElementById('requestInput').value = '不要奶茶';
app.context.generateMealPlan();
assert.match(app.elements.get('taskTitle').textContent, /暂时无法识别预算/);
app.document.getElementById('requestInput').value = '预算 30 元，但我要素食';
app.context.pickTonight();
assert.match(app.elements.get('tonightIntro').textContent, /不会忽略/);
const defaultApp = boot();
defaultApp.context.pickTonight();
assert.match(defaultApp.elements.get('taskSummary').textContent, /预算 ¥20/);
assert.equal(app.context.isOpen({ business_hours: '未设置' }, 8), false, 'unknown hours fail closed');
assert.equal(app.context.isOpen({ business_hours: '22:00-02:00' }, 1), true, 'overnight hours are supported');

const emptyScript = script.replace(/const allProducts = \[[\s\S]*?\];/, 'const allProducts = [];');
assert.notEqual(emptyScript, script, 'can construct an empty-menu failure fixture');
const empty = boot(emptyScript);
empty.context.generateMealPlan();
assert.match(empty.elements.get('taskTitle').textContent, /菜单数据不可用/);
empty.document.getElementById('requestInput').value = '预算 20 元，晚上 19 点';
empty.context.pickTonight();
assert.match(empty.elements.get('tonightIntro').textContent, /没有找到快照中确认营业/);

console.log('网页 smoke test 通过：今晚预算/时间/避辣、候选确认、未支持要求拒绝、空结果、A1–A6 周计划预算/来源核验和营业时间边界。');
