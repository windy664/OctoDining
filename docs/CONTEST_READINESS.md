# 参赛准备状态

更新：2026-10-04。基本功能来自 `card-host` 真实交互验收；OctoSense Shell 已启动，但系统 Agent 尚未完成联调，不能把本地开发预览标成完整参赛作品。

## 当前交付判断

| 项目 | 状态与证据 |
| --- | --- |
| 产品任务 | 面向预算有限人群的餐饮规划，见 [BRIEF](BRIEF.md) |
| 菜单快照 | 1,497 条记录，含名称、店铺、类别、标价和营业时段；来源授权待补 |
| 基本功能 | A1–A6、三餐候选、预算与时段过滤、保存/重启恢复/修改/取消、写入核验通过 card-host UI 验收 |
| 数据健全 | 金额按分计算；确认计划保留商品 ID、名称、店铺、原快照价格、营业时段与用户需求 |
| 持久化 | 双文件轮换；测试覆盖文件损坏恢复、保存故障保护、双副本无效时锁写 |
| Agent 能力 | `octos.turn.start` 候选比较、请求前条件复核、序号校验、失效回调丢弃和响应 JSON 类型校验已进入源码；card-host 已验证无服务时的回退 |
| App Hub 检查 | bundle 1.2.0 已通过 unsigned hub check；声明 `storage`、`octos.turn.start`。签名警告和 listing 模板占位仍待处理 |
| 运行宿主 | OctoSense `4a541777` 与锁定依赖下，Linux `cargo check --locked -p octosense`、`cargo build --locked -p octosense` 已通过；Octos `2.0.3-rc.13 (056173e)` 内核已构建。隔离 profile 的 `octos-kernel chat` 收到 DeepSeek `deepseek-v4-flash` 回复；OctoSense Shell 的 4 个真实内核基线测试通过（News peer、Shell relay、会话共享，mock LLM）。测试没有操作真实首次授权界面，也没有运行 OctoDining 包；本项目的 Shell 授权和 `octos.turn.start` 仍未联调。Kimi 与 DeepSeek key 均曾发到聊天中，应轮换 |
| 页面外观 | 功能验证页面可交互；隐藏窗口截图端点返回 404，未完成视觉验收 |
| 商店资料 | `bundle/listing.json` 仍有示例发布者/平台信息，不可发布 |
| 许可与隐私 | 代码 Apache-2.0；菜单的采集来源、日期和再分发许可待确认。请求仅发送本次需求、候选和当日计划摘要 |
| 冻结版本 | Agent 联调与正式运行截图通过后再冻结提交 |

## 当前完整任务路径

输入日期、每日预算、餐次、本餐上限和到店时间 → 本地快照筛选候选 → 可选地请系统 Agent 比较 → 用户确认一个候选 → 保存并读回核验 → 重启后继续修改或取消。

Agent 不会搜索整份菜单、创建新候选或自动保存。菜单不提供实时库存/价格、营养或过敏原信息；没有下单、付款或配送能力。七日计划和历史去重仍未迁入应用。

## 验收记录

`python3 scripts/test-basic-app.py` 在 card-host UI bridge 上完整通过 14 组预算、非法输入、Agent 服务不可用回退、候选筛选、计划保存/恢复、日期隔离、修改/取消、写盘故障和损坏文件恢复检查。报告为 `.local-state/acceptance-20261004-105105/results.json`。测试使用相对日期验证空白计划日，截图端点仍返回 404；报告不是 OctoSense Shell 或真实 Agent 的成功请求证据。OctoSense 自身的 4 个真实内核基线测试通过，但测试目标是 News 而非本应用，详见 [开发路线](ROADMAP.md)。

## 交付前还需要

- Shell 中打开已验证目录安装的 OctoDining 包，并完成首次授权；当前 UI 启动检查尚未形成应用任务运行记录。
- 将 DeepSeek key 配置到隔离的 OctoSense profile（provider `deepseek/deepseek-v4-flash`、`https://api.deepseek.com/v1`、`DEEPSEEK_API_KEY`），完成首次应用授权和真实 `octos.turn.start` 请求；再测试拒绝、服务不可用、格式错误与过期响应。Kimi 与 DeepSeek key 均应在各自控制台撤销轮换。
- 修复截图采集，检查最终真实界面并录制任务演示。
- 补全菜单来源与再分发许可，填写真实 listing 元数据。
- 以冻结的可运行提交参加赛事；无需先等待 App Hub 商店上架。[官方交付说明](https://github.com/gosimfoundation/hackathon-agenticapp26/blob/main/docs/app-hub-submission.md)
