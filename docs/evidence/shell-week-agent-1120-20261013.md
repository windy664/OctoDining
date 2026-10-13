# 1.12.0 七日餐表 Agent 闭环录屏（Shell 真实模型）

2026-10-13 晚。当前签名版 **1.12.0** 在 OctoSense Shell 中用真实 **MiniMax-M3** 完成整周换餐闭环，全程帧缓冲录制。本记录把"当前签名版"的整周 Agent 视频证据从 1.11.0 刷新到 1.12.0，并首次展示 **Agent 提议的逐条 diff 卡**。

## 环境与边界

- 应用包：`bundle/` 1.12.0，windy664 签名，`hub check` PASSED；发布到隔离环境本地目录（store/apps 目录均 sequence 13）。
- 隔离环境 `.local-state/shell-env-cancel/`：保留 profile（日预算 ¥32）与 MiniMax-M3 内核 profile，无计划文件；宿主授权此前版本已记录，本次仍有效。
- 录屏：可见 Wayland 窗口 + `MAKEPAD_WRITE_FRAMEBUFFER_PNG` 真实帧缓冲采集（98 帧，约 1.5 帧/秒，宿主编码节流），按实时速度合成，**不是操作系统的连续录屏**；画面裁剪到应用窗口区域（990×603 瓦片 ×1.25 像素比），无桌面元素。驱动经 `MAKEPAD_REMOTE` 桥下发硬件输入事件。
- 录制于晚间约 20:00，当天早餐/午餐已过，草案从当天晚餐起排（正确行为）。

## 录屏与关键帧（均经人工查看）

[录屏 octodining-1120-shell-week-agent.mp4](shell-week-agent-1120-20261013/octodining-1120-shell-week-agent.mp4)（约 63 秒，98 帧）：

1. [首页](shell-week-agent-1120-20261013/frame-home.png)：下一餐推荐与预算指标。
2. [七天草案就绪](shell-week-agent-1120-20261013/frame-draft.png)：待确认 20 餐，缺口 0。
3. [请求进行中](shell-week-agent-1120-20261013/frame-agent-waiting.png)：「正在请 OctoSense Agent 比较本周换餐…」，「取消」按钮在场；需求为「这周想吃点清淡的，顺便省点钱」。
4. [Agent 提议摘要](shell-week-agent-1120-20261013/frame-agent-proposal.png)：MiniMax-M3 提议 5 处换餐，「预计共省 ¥9.30」由应用按真实菜价核算；理由提及少油清淡品类并逐日列出节省。
5. [逐条 diff 卡](shell-week-agent-1120-20261013/frame-diff-cards.png)：「霸王炒鸡饭 ¥12.00 → 牛筋丸米粉 ¥10.00 · 省 ¥2.00」等，绿色节省标签。
6. [确认读回](shell-week-agent-1120-20261013/frame-confirmed.png)：「已确认并读回核验 20 餐；仅为计划，未下单」；周餐表 10-16 日卡显示 Agent 所选「鱼蛋粉 ¥9.90」。

## 读回核验

[plans-readback.json](shell-week-agent-1120-20261013/plans-readback.json)：revision 1、7 天、20 餐。Agent 所选全部落盘：10-14 午餐牛筋丸米粉 ¥10.00、10-15 午餐火鸡拌面 ¥9.00、10-16 午餐鱼蛋粉 ¥9.90、10-17 午餐筒骨汤香菇肉丝红薯粉 ¥8.00，与录屏 diff 卡逐条一致。

## 与旧证据的关系

1.11.0（[录屏](shell-week-agent-1110-20261012.md)）等旧记录各自有效；本次在当前签名版 1.12.0 上重跑完整闭环，展示 diff 卡与取消按钮同屏。八套 card-host 回归在同版源码上全部通过。
