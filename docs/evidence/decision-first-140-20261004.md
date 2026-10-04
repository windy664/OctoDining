# 1.4.0：首页先回答今天吃什么

日期：2026-10-04。宿主：Linux 原生 Makepad `card-host`，通过 OctoScript-App-Design-Flow `tools/octo run bundle` 启动；独立应用数据目录在 `.local-state/`，未加入仓库。本轮没有调用模型或声称在 OctoSense Shell 完成同版 Agent 验证。

产品定位：中文名为“好好吃饭”，界面保持 `octodining.` 标识。用户打开应用先看到今天已安排的餐品；没有安排时，首页直接给一道与预算、餐次、到店时段匹配的菜单推荐，附菜名、价格、店铺和一键加入餐表。下方输入供 Agent 调整，一周餐表从右上角进入。配图标为“氛围图 · 非菜品实拍”。推荐依据本地菜单快照，不代表实时库存、价格或已下单。

验收：

- `python3 scripts/test-basic-app.py --port 8228` 通过 14 组原生 UI bridge 检查，含预算、非法输入、Agent 服务不可用回退、保存读回、重启恢复、日期隔离、修改取消和损坏存储保护；报告在本机 `.local-state/acceptance-20261004-211957/results.json`。
- 在空数据目录点首页“就吃这道 · 加入餐表”，状态显示“已保存并读回核验”，七日页显示同一菜名。返回首页后显示“今天晚餐 · 已安排”和“查看今日餐表”；重启仍显示该已安排餐品。
- 对已安排餐品点“换一道”得到另一道推荐，确认后同日同餐次被替换；本次从“孜然土豆饭”切到“烧烤煎肉饭”，无重复餐次。
- `python3 scripts/capture-card-host.py --port 8226 --output .local-state/decision-first-140-20261004-release` 生成并检查三张 824×1784 原生画面：[首页](decision-first-140-20261004/01-home-recommendation.png)、[候选](decision-first-140-20261004/02-candidates.png)、[一周餐表](decision-first-140-20261004/03-week-plan-confirmed.png)。同三图放入 `bundle/screenshots/`。
- `tools/octo check bundle` 通过 unsigned Hub 预检；签名和正式发布未执行。1.4.0 的 Shell 模型闭环仍需同版复验；现有真实 MiniMax 证据属于 1.2.2。
