# 历史开发接续记录 · 2026-09-29 至 09-30

> **历史归档。** 下文保留当时的实现、测试和判断，不代表当前状态。
> 2026-10-03 已改为优先验证 OctoSense Shell + OctoScript + 系统 octos，
> Rinx 是可选宿主。当前计划见 [ROADMAP](ROADMAP.md)，实际缺口见
> [CONTEST_READINESS](CONTEST_READINESS.md)。当前 bundle 权限与源码不一致，
> 旧文中的通过记录不能作为新版本验收证据。

接续 OpenCode 会话：参与 agenticapp26 比赛和 OctoSense 项目研究。

> 在 2026-09-30 的工作中，比赛入口曾设为 Rinx Mini Apps OctoScript bundle。
> 这段话描述当时路线；2026-10-03 之后以文首指向的当前文档为准。

## 用户要求

保留广州软件学院原始食堂数据、A1–A6 档次和原网页设计及功能；关注美观、易用、跨平台和低配手机。用户同意 Rust + egui 重写，但参赛目标仍在。

## 当前 Rust 桌面版

- `src/main.rs`：egui 界面入口。
- `src/planner.rs`：本地餐表规划逻辑。
- `products_clean.json` 在构建时嵌入；中文字体和原网页背景图也嵌入应用。
- `data.rs`、`algorithm.rs`、原网页和 `bundle/` 均保留；桌面入口没有调用旧 CLI 算法。

## 原网页迁移对照

参照 `meal_planner.html` 迁移六档预算卡与月生活费说明、生成按钮、六项统计、七日自动布局餐卡、餐名/店铺/价格/营业时间。保留背景图、暗色遮罩、紫色按钮及玻璃卡片风格。布局按宽度变成 1、2、3 或 6 列档次卡和统计卡；餐卡最多三列，小屏单列。餐表规则包括六档价格范围、分类关键字、副餐预算与概率、A4+ 午餐饮品及周四肯德基优先。

网页没有采购清单、营养分析或勾选功能。曾有的 egui 原型加入过这些额外控件；当前完整迁移版未保留它们。

## 诚实的限制

- 规划用的是本地菜单快照与规则，尚未接入真实 Agent，也不会推断数据中没有的营养信息。
- 商品营业状态和库存是快照，不能据此保证未来七天仍营业或有货；界面提醒以商家当天为准。
- 桌面窗口已截图检查背景、中文和六档及统计布局。按钮逐项操作、滚动查看完整七天、小屏及其他操作系统尚未验收。
- 赛事官网当前说明 Rinx 是主要小程序宿主；独立 egui 版是否满足提交要求尚未确认。比赛来源：<https://github.com/gosimfoundation/hackathon-agenticapp26>。
- `docs/BRIEF.md`、`docs/AGENT-TASKS.md` 和旧 README 的完成勾选属于历史记录，不等于当前功能已验证。
- `bundle/` 有上一会话未提交的修改，本次没有改动 bundle 文件。

## 验证

- `cargo build --offline`：通过。
- `cargo run --offline -- --verify-data`：六档均从 1,497 条商品数据生成七天餐表。
- `/tmp/campus-meal-full.png`：实际桌面窗口截图。

## 2026-09-30 比赛准备续记

用户要求把作品推进到符合 Agentic App 2026 初赛交付方式。当前演示入口改以根目录 `meal_planner.html` 网页小程序为主，适配 Rinx 的 HTTP(S) URL 卡片路径；桌面 egui 版保留为备用可运行原型。没有部署 HTTPS 地址，也没有修改 Rinx 宿主或发布 App Hub。

网页现在识别 A1–A6 或每日金额短句，按餐次、菜单类别、快照营业时间与剩余预算生成七天餐表；结果核验日预算、金额合计和菜单来源，并展示任务步骤。未知意图、空菜单和某餐次无匹配项可见失败/空状态。未知营业时间按不可确认处理。修复了水果金额未计入汇总以及餐表可超过日预算的问题。

`README.md`、`docs/BRIEF.md` 和 `docs/AGENT-TASKS.md` 已更正旧版虚构的 AI、热量/蛋白质和购物清单说法。`docs/CONTEST_READINESS.md` 记录赛项对照与未完成事项。网页规则引擎不是模型 Agent，Rinx HTTPS 部署、Agent 接入、运行截图/演示视频、队外用户试用及菜单数据公开许可仍需解决；不得宣传成完整 Agentic 奖作品。

本次验证：`node scripts/smoke-web-demo.cjs`、`cargo fmt -- --check`、`cargo test --offline`（4 项通过）、`cargo run --offline -- --verify-data`（A1–A6 各 1,497 条快照均生成七日结果）。

## 2026-09-30 技术栈调整

用户要求先切换到符合比赛方向的技术栈。根目录 `AGENTS.md` 与本地 OctoSense App Design Flow 要求表明本项目 bundle 应使用 OctoScript；同时 Rinx Mini Apps 的正式 Agent 服务为 `octos.turn.start`。因此比赛主入口现为 `bundle/main.splash`，通过生成脚本将 1,497 条菜单数据嵌入，先做本地候选筛选，再把候选和自然语言偏好发送给宿主 Agent，用户确认后写入本地计划。manifest 仅申请 `octos.turn.start` 与 `storage`。

新源码模板和构建脚本位于 `scripts/main.splash.in`、`scripts/build-octos-bundle.py`。运行 `/home/windy/Project/octosense-ws/OctoScript-App-Design-Flow/tools/octo check bundle` 通过；card-host admission 和首帧也通过。card-host 不实现 Rinx Octos 服务，因此 Rinx 中真实 Agent 联调仍未验证。HTML/Rust 为备用原型。查看当前范围请以 `README.md` 与 `docs/CONTEST_READINESS.md` 为准。

Rinx checkout 原有的 `apps/meal-planner` 内置应用也已同步成同一套源码，保留 ID `org.octosense.meal-planner`，版本升至 1.1.0，并移除原先的 OpenAI 网络权限与模拟营养/采购输出。系统应用打包检查、Rinx system-apps 7 项测试、Rinx `agent_chat` 离线构建及 Octos 回调 2 项定向测试均通过。当前环境没有可用 Wayland compositor，不能启动桌面 Rinx 做 provider 端到端验证；card-host 明确返回设备没有 Octos 服务。
