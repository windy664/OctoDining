# OctoSense Shell 联调记录（本机 mock provider）

测试日期：2026-10-04。应用：OctoDining 1.2.1。宿主：OctoSense 提交 `4a541777`，Octos 内核 `056173e`。在隔离的 `/tmp/octodining-agent-smoke-20261004` 目录，使用临时签名的本地 Hub 目录将应用安装并更新到 1.2.1。此测试没有使用正式发布目录或生产签名密钥。

观察到的操作与结果：

1. OctoSense Shell 启动应用。标准卡片窗口内滚动选择区后，可以点击“查找 / 换一批”；日期设为 2026-10-04，晚餐到店时间 18:30，本餐上限 ¥14，应用展示三个候选。
2. 点击“让 OctoSense Agent 比较”。Shell 日志显示应用 peer 已准备，使用模型名 `mock-model`；本机 mock 服务日志记录 `/v1/chat/completions` 请求。应用展示“Agent 建议候选 1”及理由，候选 1 标注为建议。
3. 用户手动确认候选 1。应用报告“已保存并读回核验：晚餐 · 卤汁腐竹饭。仅为计划，未下单。”；预算摘要更新为当日已计划 ¥10.00、剩余 ¥22.00。宿主应用数据目录写入 `plans-a.json`，其中日期、餐次、商品、金额与预算一致。

本机原始记录为 `/tmp/octodining-agent-smoke-20261004/shell-v121.log`、`model.log`、`apps/org.octosense.octodining/plans-a.json`。日志和运行 profile 未提交；这份文件是测试观察摘要，不能代替可供评委独立运行的正式模型演示。该 profile 的应用授权状态已经是允许，未取得首次授权界面证据。Shell 内 DeepSeek provider、拒绝、服务失败和过期响应仍需验证。截图端点返回 404，本记录没有运行截图。
