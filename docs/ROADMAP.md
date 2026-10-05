# 当前开发路线

更新：2026-10-05。按“基本功能 → 系统 Agent → UI”迭代；当前工作版 1.7.0 的下一餐、菜单导入与七日草案已通过 card-host，下一道关口是**同版 Shell / 真实模型复验**。历史 1.2.2 联调记录不能替代。当前状态以[参赛准备状态](CONTEST_READINESS.md)为准。

## 产品闭环补齐（1.5.0 起）

首次使用已支持内置菜单或验证后粘贴 JSON 菜单、月生活费核算；下一餐优先显示确认计划，七日草案经用户确认后写入，实际花费可记录。还没有文件选择器、自动采集和 1.7.0 同版 Shell Agent 证据。份量与营养信息缺失时不宣称“最佳”或“保证吃饱”。

## 第一步：基本功能 — 已完成 card-host 验收

- A1–A6 六档每日预算及三餐单餐上限。
- 按日期安排早餐、午餐和晚餐；筛选依据包括预算、菜单餐次关键词、营业时段和关键词避辣。
- 最多显示三个不同店铺的候选；同日同餐确认新选项会替换原计划。
- 保存、读回校验、重启恢复、修改、取消、每日预算编辑和剩余计划金额核算。
- 输入日期、金额或需求变化后让旧候选失效；不支持的饮食安全要求明确拒绝猜测。
- 两份轮换记录损坏时恢复仍有效的副本；写盘失败保留上一份有效记录；两份都无效时暂停写入并保留原文件。

**验收证据：** `python3 scripts/test-basic-app.py` 通过 14 组真实 card-host UI bridge 检查，公开摘要见 [测试报告](evidence/basic-app-20261004.json)。1.2.2 将候选列表与建议合入同一滚动区，card-host 再次通过 14 项回归和原生截图检查；标准 Shell 窗口又验证了真实 MiniMax 建议、滚动到后两个候选、确认保存和预算读回，见 [同版联调记录](evidence/shell-ui122-minimax-20261004.json)与 [UI 修正记录](evidence/ui-scroll-122-20261004.md)。

**1.7.0 补充：** 七日草案、一定程度的历史避重复与实付记录已通过 card-host；实时菜单与价格、订单支付仍未实现。保留 HTML/Rust 参考实现。

## 第二步：结合 OctoSense 系统 Agent — 进行中

- 仅申请 `octos.turn.start` 精确服务能力，模型 provider 和密钥由宿主管理。
- 将用户需求、预算、餐次、至多三个已筛候选及当天已有计划传给宿主。
- 限定响应为候选序号与理由；校验序号属于本次候选，且响应回来时请求条件未变化。
- 发起宿主请求前再次校验条件，拒绝已失效的预算/需求状态。
- 条件变化或候选失效时递增请求代次并释放界面忙碌状态；迟到回调直接丢弃，不能清掉较新请求的忙碌状态。
- 响应解析要求 JSON 对象、数值候选序号和字符串理由；无效格式显示回退信息，不成为可确认建议。
- Agent 只建议；用户必须手动确认，应用才保存并核验计划。
- card-host 中验证服务不可用反馈；OctoSense Shell 中已完成 MiniMax-M3 真实 provider 的成功请求与计划持久化读回，并验证拒绝授权、未配置模型时仍可人工确认。格式错误和过期响应仍待 Shell 验收。

**当前进度：** OctoScript 页面和 manifest 已接入精确的 `octos.turn.start` 权限；card-host 验收了服务不可用回退。OctoSense 主仓库 `4a541777` 的 Linux `cargo check --locked -p octosense` 与 `cargo build --locked -p octosense` 已通过；并按该锁文件构建 Octos `2.0.3-rc.13 (056173e)`，产物 SHA-256 前缀为 `35d1d279c6b04061`。OctoSense Shell 已在独立 `/tmp` home/app-data 启动，并配置临时锚签名的本地测试目录；未使用真实发布密钥。先前将 Kimi Coding Plan key 错配到 Moonshot Open Platform 并得到的 HTTP 429 不可用于判断 Coding Plan。之后对正确的 Coding Plan endpoint（`https://api.kimi.com/coding/v1`）分别以 `k3` 和 `kimi-for-coding` 发起最小请求，均返回 HTTP 401 `invalid_authentication_error`，没有模型回复；认证失败本身不能区分 key 无效、过期或撤销，也不能排除所选模型不在当前计划权限内。Kimi 官方文档列出的下一步是确认 key 来自 Kimi Code Console、仍有效且有对应模型权限。临时 key 与 provider profile 已删除。

**OctoSense Shell 基线测试（2026-10-04）：** 在 OctoSense `4a541777` 工作树运行 `OCTOS_SHELL_TEST_KERNEL=.../target/debug/octos-kernel cargo test --locked --features mobile-apps -p octosense-shell real_kernel -- --nocapture`，4 个匹配测试通过。真实 Octos 内核配合仓库 mock LLM 验证了 Shell 的脚本应用 peer 准备、`peer_list`、会话共享，以及 Agent 工具经 Shell relay 到宿主服务再返回。测试直接预置了同意状态，没有点击首次授权界面；测试应用是 News，不是 OctoDining。随后另用隔离 home/app-data 和临时签名本地目录，在 OctoSense Shell 的 App Hub 中安装并更新 OctoDining 1.2.1，确认滚动后的候选操作可用。点击“让 OctoSense Agent 比较”后，应用 `host.request("octos.turn.start")` 经 Shell → Octos 内核 → 本机 OpenAI-compatible mock 模型返回有效建议；用户确认候选 1 后，应用写入 `plans-a.json` 并读回验证，预算摘要同步更新。此为应用到宿主再到内核的真实 Shell 调用链，但模型响应来自本机 mock，不能称为 DeepSeek 成功联调；隔离 profile 中该应用权限已处于允许状态，本轮没有首次授权界面的人工确认截图。临时目录和签名密钥仅用于本地测试，不是发布签名。

**本应用失败路径（2026-10-04）：** 另用隔离 Shell profile 将应用 Agent 授权状态设为拒绝，点击比较后显示“系统 Agent 暂不可用”，仍能手动确认候选并读回计划。允许授权但不配置模型时，应用显示 `profile_unresolved`，确认按钮仍可用。[实际 UI 状态摘要](evidence/shell-failures-20261004.json)记录了两次 Shell `/snap` 的选定节点。宿主对已拒绝状态返回的英文文案仍说“Waiting for the person”，表述不准确；这一组失败路径记录没有首次授权界面截图或正式模型回复，另见下方 MiniMax 成功记录。

**本轮运行观察：** 首次启动时，Shell 的系统助手显示“尚未设置模型提供方”。按官方 OpenAI-compatible 配置使用 provider `moonshot-coding`、中国区 endpoint `https://api.kimi.com/coding/v1`；`k3` 与 `kimi-for-coding` 各做一次最小请求，均返回 HTTP 401 `invalid_authentication_error`。没有模型回复，也没有消耗到可验证的模型输出。该响应不能单独证明 key 无效，因为官方模型文档也将缺少对应模型计划权限列为 401 可能原因。旧 key 仅暂存在权限为 0600 的隔离 secret 文件，随后已删除；因其曾在聊天中明文发送，建议在 Kimi Code Console 撤销并重新生成。拿到新 key 后先核对 Coding Plan 归属和模型权限，再在 OctoSense 中完成授权、成功回复及拒绝/失败回退测试。当前测试 Shell 已正常退出。参考：[Kimi Code 模型与权限说明](https://www.kimi.com/code/docs/kimi-code/models.html)、[Kimi Code FAQ](https://www.kimi.ai/help/kimi-code/faq)。

2026-10-04：用户提供 DeepSeek API key 后，按 OctoSense 使用的 `/v1/chat/completions` 地址和模型 `deepseek-v4-flash` 最小请求返回 HTTP 200（服务端将模型名规范化为 `deepseek-flash`）；禁用思考模式的一次代码审查成功返回，记录用量为 2,158 tokens。随后用隔离 `OCTOS_HOME`、进程环境中的 `DEEPSEEK_API_KEY`，通过本机 `octos-kernel chat --provider deepseek --model deepseek-v4-flash --base-url https://api.deepseek.com/v1 --api-type openai` 得到结构化回复；Octos 记录 12,258 输入、70 输出 tokens。该命令证明 Octos 内核 provider 可用，但没有经过 OctoSense Shell 的应用 peer 或用户授权。key 未写入仓库或磁盘配置，但已在聊天中发送，建议在 DeepSeek 控制台轮换。OctoSense 本机目录登记了同一模型和默认 `DEEPSEEK_API_KEY`。参考：[DeepSeek 首次 API 调用](https://api-docs.deepseek.com/guides/codex)、[模型与价格](https://api-docs.deepseek.com/quick_start/pricing/)、[思考模式](https://api-docs.deepseek.com/guides/thinking_mode/)。

随后修正了一处异步竞态，发起请求前重验条件，并严格校验 Agent JSON 对象、数值序号和文本理由；用户再次请求时清除上次建议，旧响应按请求代次丢弃。bundle 通过 `octo check bundle`，完整 card-host 回归通过 14 组检查。card-host 没有 octos 服务；检查覆盖基本功能和无服务回退，不代表模拟或真实 Agent 成功。后续已采集原生截图，并在 Shell 中取得真实 MiniMax 建议。

**通过条件：** Shell 中真实 Agent 请求与系统授权有记录；建议对应实际候选；用户确认后计划写入、读回和预算均正确；拒绝、错误或过期时没有假成功。本地预览、hub check、临时目录签名或单独构建内核均不算通过。

## 第三步：功能稳定后再完善 UI 和提交

- 根据真实截图检查不同窗口尺寸、滚动、长菜名和错误状态，再调整视觉层级。
- 两张 card-host 功能截图及 1.2.2 同版 Shell/MiniMax 建议、滚动和确认画面已采集；连续短演示仍可补录。
- `bundle/listing.json` 已改为餐饮规划文案并只声明已实测 Linux；上架前复核发布者身份、隐私说明、截图和菜单再分发许可。
- 重新构建、检查并记录源码提交、bundle 摘要、宿主版本和可复现启动说明。
- 以同一冻结提交提供公开仓库、Apache-2.0 许可、有效运行截图/短演示、输入与授权/Agent/人工确认/结果核验的复现步骤。队伍主题和初赛仓库地址分别已登记在官方 Issue #5 与 #13；个人报名表状态待核。

**通过条件：** 参赛者可依说明复现完整任务；展示材料来自同一提交，并准确标明数据快照与未实现能力。

## 赛事优先级

2026-10-04 补充：在全新隔离 Shell 中配置 `minimax-cn` / `MiniMax-M3`，完成首次应用授权、真实 `octos.turn.start` 建议、人工确认及 `plans-a.json` 写入读回。[空计划运行](evidence/shell-minimax-clean-20261004.json)证明新建计划；[另一次已有计划的运行](evidence/shell-minimax-20261004.json)提供两次模型响应和原生截图。密钥只在本机 0600 profile 中，仓库没有密钥。上游 Octos ledger 对此应用的长会话 ID 报路径过长并退到内存；因此 Agent 对话跨重启持久化尚未通过，不影响应用计划文件读回。

官方初赛截止为北京时间 2026-10-04 23:59。先冻结并交付可运行的功能闭环与真实 Agent 证据。Hub 预检可作为包结构证据，不能代替在注明版本的宿主中启动和完成任务；现阶段公开仓库与可运行作品即可参评，无需等待 App Hub 上架。UI 润色、聊天分享、天气、日历、ROM 扩展和工具链悬赏不应挤占未完成的主任务。[赛事提交说明](https://github.com/gosimfoundation/hackathon-agenticapp26/blob/main/docs/app-hub-submission.md)
