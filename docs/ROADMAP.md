# 当前开发路线

更新：2026-10-04。按“基本功能 → 系统 Agent → UI”迭代。只把有对应运行证据的部分标为完成。

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
- 发起宿主请求前再次校验条件，拒绝已失效的预算/需求状态。
- 条件变化或候选失效时递增请求代次并释放界面忙碌状态；迟到回调直接丢弃，不能清掉较新请求的忙碌状态。
- 响应解析要求 JSON 对象、数值候选序号和字符串理由；无效格式显示回退信息，不成为可确认建议。
- Agent 只建议；用户必须手动确认，应用才保存并核验计划。
- card-host 中验证服务不可用反馈，OctoSense Shell 中继续验收授权拒绝、成功请求、服务失败、过期响应和确认后的持久化结果。

**当前进度：** OctoScript 页面和 manifest 已接入精确的 `octos.turn.start` 权限；card-host 验收了服务不可用回退。OctoSense 主仓库 `4a541777` 的 Linux `cargo check --locked -p octosense` 与 `cargo build --locked -p octosense` 已通过；并按该锁文件构建 Octos `2.0.3-rc.13 (056173e)`，产物 SHA-256 前缀为 `35d1d279c6b04061`。OctoSense Shell 已在独立 `/tmp` home/app-data 启动，并配置临时锚签名的本地测试目录；未使用真实发布密钥。先前将 Kimi Coding Plan key 错配到 Moonshot Open Platform 并得到的 HTTP 429 不可用于判断 Coding Plan。之后对正确的 Coding Plan endpoint（`https://api.kimi.com/coding/v1`）分别以 `k3` 和 `kimi-for-coding` 发起最小请求，均返回 HTTP 401 `invalid_authentication_error`，没有模型回复；认证失败本身不能区分 key 无效、过期或撤销，也不能排除所选模型不在当前计划权限内。Kimi 官方文档列出的下一步是确认 key 来自 Kimi Code Console、仍有效且有对应模型权限。临时 key 与 provider profile 已删除。

**本轮运行观察：** 首次启动时，Shell 的系统助手显示“尚未设置模型提供方”。按官方 OpenAI-compatible 配置使用 provider `moonshot-coding`、中国区 endpoint `https://api.kimi.com/coding/v1`；`k3` 与 `kimi-for-coding` 各做一次最小请求，均返回 HTTP 401 `invalid_authentication_error`。没有模型回复，也没有消耗到可验证的模型输出。该响应不能单独证明 key 无效，因为官方模型文档也将缺少对应模型计划权限列为 401 可能原因。旧 key 仅暂存在权限为 0600 的隔离 secret 文件，随后已删除；因其曾在聊天中明文发送，建议在 Kimi Code Console 撤销并重新生成。拿到新 key 后先核对 Coding Plan 归属和模型权限，再在 OctoSense 中完成授权、成功回复及拒绝/失败回退测试。当前测试 Shell 已正常退出。参考：[Kimi Code 模型与权限说明](https://www.kimi.com/code/docs/kimi-code/models.html)、[Kimi Code FAQ](https://www.kimi.ai/help/kimi-code/faq)。

2026-10-04：用户提供 DeepSeek API key 后，按 OctoSense 使用的 `/v1/chat/completions` 地址和模型 `deepseek-v4-flash` 最小请求返回 HTTP 200（服务端将模型名规范化为 `deepseek-flash`）；禁用思考模式的一次代码审查成功返回，记录用量为 2,158 tokens。随后用隔离 `OCTOS_HOME`、进程环境中的 `DEEPSEEK_API_KEY`，通过本机 `octos-kernel chat --provider deepseek --model deepseek-v4-flash --base-url https://api.deepseek.com/v1 --api-type openai` 得到结构化回复；Octos 记录 12,258 输入、70 输出 tokens。该命令证明 Octos 内核 provider 可用，但没有经过 OctoSense Shell 的应用 peer 或用户授权。key 未写入仓库或磁盘配置，但已在聊天中发送，建议在 DeepSeek 控制台轮换。OctoSense 本机目录登记了同一模型和默认 `DEEPSEEK_API_KEY`。参考：[DeepSeek 首次 API 调用](https://api-docs.deepseek.com/guides/codex)、[模型与价格](https://api-docs.deepseek.com/quick_start/pricing/)、[思考模式](https://api-docs.deepseek.com/guides/thinking_mode/)。

随后修正了一处异步竞态，发起请求前重验条件，并严格校验 Agent JSON 对象、数值序号和文本理由；用户再次请求时清除上次建议，旧响应按请求代次丢弃。bundle 通过 `octo check bundle`，完整 card-host 回归通过 14 组检查（`.local-state/acceptance-20261004-105105/results.json`）。card-host 没有 octos 服务；检查覆盖基本功能和无服务回退，不代表模拟或真实 Agent 成功。视觉截图仍未生成。

**通过条件：** Shell 中真实 Agent 请求与系统授权有记录；建议对应实际候选；用户确认后计划写入、读回和预算均正确；拒绝、错误或过期时没有假成功。本地预览、hub check、临时目录签名或单独构建内核均不算通过。

## 第三步：功能稳定后再完善 UI 和提交

- 根据真实截图检查不同窗口尺寸、滚动、长菜名和错误状态，再调整视觉层级。
- 采集与冻结 bundle 相符的实际运行截图和短演示；现有截图桥 404 的原因需先解决。
- 据实更新 `bundle/listing.json`，补齐发布者、作者、平台支持、数据来源与支持方式。
- 重新构建、检查并记录源码提交、bundle 摘要、宿主版本和可复现启动说明。

**通过条件：** 参赛者可依说明复现完整任务；展示材料来自同一提交，并准确标明数据快照与未实现能力。

## 赛事优先级

官方初赛截止为北京时间 2026-10-04 23:59。先完成并提交可运行的功能闭环与真实 Agent 证据。UI 润色、聊天分享、天气、日历、ROM 扩展和工具链悬赏不应挤占未完成的主任务。交付状态以官方赛程和实际运行记录为准。
