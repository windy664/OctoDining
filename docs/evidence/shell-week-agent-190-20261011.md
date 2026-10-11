# 1.9.0 七日餐表 Agent 闭环录屏（Shell 真实模型）

2026-10-11 晚。当前签名版 1.9.0（含预算指标条、快捷 chips、约束证据、状态 pill 与语言切换修复）在 OctoSense Shell（`octosense-home`，OctoSense `4081c30`）中用真实 MiniMax-M3 完成整周换餐闭环。本记录用于回应初赛评审"补签名版 AI 成功录屏"的建议。

## 环境与边界

- 应用包：`bundle/` 经 windy664 签名并发布到本机隔离测试目录（`hub publish`，catalog sequence 3，`hub verify` 通过）；非 App Hub 正式上架。
- 隔离环境：`.local-state/shell-env/`（不进仓库）；模型密钥只在内核 profile 中。
- 首次授权画面此前已在 1.8.13 记录过，本机 consent 仍有效，本次未重复授权步骤；授权拒绝路径仍属旧版证据。
- 视频由 `MAKEPAD_WRITE_FRAMEBUFFER_PNG` 的真实帧缓冲采集（约 4–6 帧/秒）按序合成，**不是操作系统的连续录屏**；帧间隔不均匀处是宿主编码节流，过程中没有补帧或摆拍。驱动经 `MAKEPAD_REMOTE` 桥点击真实按钮。
- 演示前只清空了计划文件（`plans-*.json`）以展示完整周草案；`profile.json`（日预算 ¥32）与宿主授权保留。

## 录屏与帧证据

[录屏 octodining-190-shell-week-agent.mp4](shell-week-agent-190-20261011/octodining-190-shell-week-agent.mp4)（约 38 秒，190 帧）对应的关键帧，均经人工查看：

1. [首页](shell-week-agent-190-20261011/frame-home.png)：次日早餐推荐与「本餐 / 今日可用」预算指标条。
2. [七天草案就绪](shell-week-agent-190-20261011/frame-draft.png)：待确认 21 餐；预算账目逐日列出"已计划 / 日预算"，作为 Agent 的输入。
3. [请求进行中](shell-week-agent-190-20261011/frame-agent-waiting.png)：「正在请 OctoSense Agent 比较本周换餐…」。
4. [Agent 提议](shell-week-agent-190-20261011/frame-agent-proposal.png)：MiniMax-M3 返回围栏 JSON，应用剥围栏、映射日期文本、校验编号后展示 5 处午餐替换，**预计节省 ¥7.70 由应用按真实菜价核算**，不是模型口算。
5. [确认后](shell-week-agent-190-20261011/frame-confirmed.png)：已确认并读回核验 21 餐；周餐表显示 Agent 所选（如 2026-10-13 午餐「叉烧河粉」），餐次带「待吃」状态 pill；顶部同时出现系统的下一餐提醒通知。

- 模型原始回复：[agent-week-last-reply.txt](shell-week-agent-190-20261011/agent-week-last-reply.txt)（围栏 JSON 原文，含模型的重复度理由）。
- 计划读回：[plans-readback.json](shell-week-agent-190-20261011/plans-readback.json)：revision 1、7 天、21 餐；2026-10-12 午餐为 Agent 所选「水饺 ¥10.00」，与录屏中的提议一致。

## 与旧证据的关系

1.2.2（单餐 MiniMax 闭环）与 1.8.13（Shell 整周换餐）记录仍然各自有效；本次补的是**当前签名版**在同一 Shell 环境的整周 Agent 闭环与帧核验。`test-week-agent.py` 等 card-host 回归在同版源码上通过。
