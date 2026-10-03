# 当前开发路线

更新：2026-10-03。按“基本功能 → 系统 Agent → UI”迭代。只把有对应运行证据的部分标为完成。

## 第一步：基本功能 — 已完成 card-host 验收

- A1–A6 六档每日预算及三餐单餐上限。
- 按日期安排早餐、午餐和晚餐；筛选依据包括预算、菜单餐次关键词、营业时段和关键词避辣。
- 最多显示三个不同店铺的候选；同日同餐确认新选项会替换原计划。
- 保存、读回校验、重启恢复、修改、取消、每日预算编辑和剩余计划金额核算。
- 输入日期、金额或需求变化后让旧候选失效；不支持的饮食安全要求明确拒绝猜测。
- 两份轮换记录损坏时恢复仍有效的副本；写盘失败保留上一份有效记录；两份都无效时暂停写入并保留原文件。

**验收证据：** `python3 scripts/test-basic-app.py` 通过 15 项真实 card-host UI bridge 用例，记录在 `.local-state/acceptance-20261003-204851/results.json`。运行端点未能生成截图（隐藏窗口的 `/g?raw=1` 返回 404）；截图外观尚未验收。该结果不证明 OctoSense Shell 兼容性。

**基本功能范围外：** 七日周计划、历史不重样、实时菜单与价格、订单支付。保留 HTML/Rust 参考实现。

## 第二步：结合 OctoSense 系统 Agent — 进行中

- 仅申请 `octos.turn.start` 精确服务能力，模型 provider 和密钥由宿主管理。
- 将用户需求、预算、餐次、至多三个已筛候选及当天已有计划传给宿主。
- 限定响应为候选序号与理由；校验序号属于本次候选，且响应回来时请求条件未变化。
- Agent 只建议；用户必须手动确认，应用才保存并核验计划。
- card-host 中验证服务不可用反馈，OctoSense Shell 中继续验收授权拒绝、成功请求、服务失败、过期响应和确认后的持久化结果。

**当前进度：** OctoScript 页面和 manifest 已接入精确的 `octos.turn.start` 权限；card-host 验收了服务不可用回退。OctoSense 主仓库 `4a541777` 的 Linux `cargo check --locked -p octosense` 与 `cargo build --locked -p octosense` 已通过；并按该锁文件构建 Octos `2.0.3-rc.13 (056173e)`，产物 SHA-256 前缀为 `35d1d279c6b04061`。OctoSense Shell 已在独立 `/tmp` home/app-data 启动，并配置临时锚签名的本地测试目录；未使用真实发布密钥。曾将 Kimi Coding Plan key 错配到 Moonshot Open Platform endpoint，并请求 `kimi-k2.5`，收到 HTTP 429；该响应不能判断 Coding Plan 的 key 或额度。测试结束后已删除隔离目录中的临时 key 与 provider profile。真实 Coding Plan provider 尚未验证，不能把内核构建、目录签名或错误 endpoint 的连通性尝试写成 Agent 已验证。

**本轮运行观察：** 首次启动时，Shell 的系统助手显示“尚未设置模型提供方”。随后误将 Coding Plan key 配到 Moonshot Open Platform 的 `api.moonshot.cn` endpoint，并请求 `kimi-k2.5`；其 429 响应不适用于判断 Coding Plan。provider key 仅保存在权限为 0600 的隔离临时 secret 文件，测试后已删除，未写进仓库。OctoSense 已内置 `moonshot-coding` provider（Kimi Coding Plan），中国区 endpoint 应为 `https://api.kimi.com/coding/v1`，本地模型 catalog 有 `k3`。用轮换后的新 key 按此配置后，仍须完成应用首次授权并验证成功回复、拒绝/错误/过期回退及确认后的持久化结果。当前测试 Shell 已正常退出。

**通过条件：** Shell 中真实 Agent 请求与系统授权有记录；建议对应实际候选；用户确认后计划写入、读回和预算均正确；拒绝、错误或过期时没有假成功。本地预览、hub check、临时目录签名或单独构建内核均不算通过。

## 第三步：功能稳定后再完善 UI 和提交

- 根据真实截图检查不同窗口尺寸、滚动、长菜名和错误状态，再调整视觉层级。
- 采集与冻结 bundle 相符的实际运行截图和短演示；现有截图桥 404 的原因需先解决。
- 据实更新 `bundle/listing.json`，补齐发布者、作者、平台支持、数据来源与支持方式。
- 重新构建、检查并记录源码提交、bundle 摘要、宿主版本和可复现启动说明。

**通过条件：** 参赛者可依说明复现完整任务；展示材料来自同一提交，并准确标明数据快照与未实现能力。

## 赛事优先级

官方初赛截止为北京时间 2026-10-04 23:59。先完成并提交可运行的功能闭环与真实 Agent 证据。UI 润色、聊天分享、天气、日历、ROM 扩展和工具链悬赏不应挤占未完成的主任务。交付状态以官方赛程和实际运行记录为准。
