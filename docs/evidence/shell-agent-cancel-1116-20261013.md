# 1.11.6 Agent 取消与恢复 · Shell 真实模型验证 · 2026-10-13

当前签名版 **1.11.6** 在 OctoSense Shell（可见窗口，Wayland，硬件输入事件经 MAKEPAD_REMOTE 桥下发）用真实 **MiniMax-M3** 验证 Agent 请求的可中止性。本记录是文本断言转录，不是截图或录屏。

## 环境与边界

- 应用包：`bundle/` 1.11.6，windy664 签名，`hub check` PASSED；能力声明新增 `octos.turn.interrupt`（宿主日志：`running under 5 capability(ies)`）。
- 隔离环境 `.local-state/shell-env-cancel/`：保留 profile（日预算 ¥32）与 MiniMax-M3 内核 profile，不含计划文件，启动后从首页生成七天草案。
- 超时兜底（90 秒无响应自动停止）本次未用真实慢请求触发，路径与取消共用同一复位逻辑（requestId 过期 + busy 复位 + interrupt），经代码审查与 card-host 回归覆盖；取消与恢复为真实模型实证。
- 内核侧没有单独的 turn 日志行；宿主日志含 `Model: MiniMax-M3`、`agents: org.octosense.octodining's agent is prepared`。

## 流程与断言（全部通过）

1. `week_nav` → `make_draft`：草案就绪（待确认 21 餐，缺口 0）。
2. 填写调整需求「这周想省点钱，少辣」→ 点「请 Agent 提案」：状态变为「正在请 OctoSense Agent 比较本周换餐…」，**「取消」按钮出现**。
3. 等待 2 秒让真实请求发出后点「取消」：状态变为「已取消这次 Agent 请求，草案未改变。」取消按钮隐藏，草案原样保留。
4. 再次点「请 Agent 提案」：MiniMax-M3 正常返回——提议 5 处午餐替换（鸡腿饭→水饺、霸王炒鸡饭→叉烧河粉等），应用核算**预计节省 ¥7.70**；证明取消没有卡死后续请求，宿主轮次确实可被中断并重新开始。

## 对应回归

- `test-week-agent.py`：新增断言——未请求时取消按钮不可见；宿主无 Agent 服务失败后取消按钮不残留。
- 其余七套 card-host 套件在同版源码上全部通过（test-rebalance 的草案等待改为 30 秒轮询，帧缓冲节流下 5 秒不够，与本次功能无关）。
