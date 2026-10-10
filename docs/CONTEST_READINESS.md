# 参赛准备状态

更新：2026-10-10。**初赛入围（80/100）**，评审意见与决赛前改进清单见[初赛结果](PRELIMINARY-RESULT.md)。当前工作版 **1.8.0**：1.7.0 功能之上并入 Agent 跨日换餐提案，card-host 验收与签名检查已通过，Shell 内真实模型回复待验收；最后有人工核验实机画面的版本是 1.7.0。以 OctoSense Shell / OctoScript 为主线。Rinx 分享是可选扩展，App Hub 是包检查与提交规范；它们不要求一起实现。应用先完成真实餐食任务，再展示 Agent 决策及结果核验。[按最佳 Agentic 评分项核验](AGENTIC_JUDGING.md)：1.2.2 的真实模型闭环与 1.7.0 的失败回退分版呈现。最新[App Hub 投稿状态与步骤](APP_HUB_SUBMISSION.md)单独记录。

## 版本与证据边界

| 范围 | 已验证 | 尚需完成 |
| --- | --- | --- |
| 1.8.13 OctoSense Shell | 七日草案 Agent 换餐全链路：真实 MiniMax-M3 提案 → 校验通过 → 应用到草案（不落盘）→ 人工确认整周 → 保存并读回，Agent 所选菜品出现在计划文件；[本版记录](evidence/shell-week-agent-1813-20261010.md) | 拒绝授权、无效 JSON、过期回复等异常路径在本版未验；帧截图未人工核验 |
| 1.8.x card-host | 草案生成、Agent 提案选项填充、无 Agent 服务时如实回退、无提案时拒绝应用、全套基础回归（16 项）、中英文与自定义菜单 | card-host 不能证明 Shell 模型调用 |
| 1.7.0 card-host | 首次预算、内置/自定义菜单、下一餐推荐、候选、七日草案确认、记录实付、取消与恢复；中英文原生画面；本地持久化及故障保护 | 已并入 1.8.x 继续维护 |
| 1.7.0 App Hub | 最新 Hub `78dfda5` 的签名检查通过；`windy664` 公钥已验证，`hub scan` 审查包在签名前生成；[投稿 #117](https://github.com/OctoSense-org/OctoSense-App-Hub/issues/117) 已提交 | App Hub 维护者审查与发布；预检不代替实际运行 |
| 1.7.0 OctoSense Shell | 本地测试目录加载、首次 Agent 授权、请求进入 Octos；供应商 HTTP 429 后手动选餐、保存读回与重启恢复通过，[本版记录](evidence/shell-170-20261005.md) | 限流导致本次无模型建议；仍需同版成功模型闭环及响应异常验收 |
| 1.2.2 OctoSense Shell | 本地测试目录安装，`octos.turn.start` 经 Octos kernel 得到真实 MiniMax-M3 建议，用户确认后保存并读回；拒绝授权和无模型回退分别实测 | 不能代替 1.7.0 的真实模型成功证据 |

冻结标签 `qualifier-2026-10-04-final` 仍指向 **1.2.2**；不得将 1.8.0 新功能、1.7.0 截图和旧版真实模型记录说成同一次运行。[1.2.2 联调记录](evidence/shell-ui122-minimax-20261004.json)、[1.7.0 Shell 部分联调](evidence/shell-170-20261005.md)与[1.7.0 card-host 截图](evidence/next-meal-170-20261005.md)分开保留。模型密钥只由宿主本地配置，仓库不含密钥。

## 当前任务路径

首次选择菜单并设置生活费 → 首页出现下一餐 → 查看菜单来源、价格和营业时段 → 需要时更换或请 Agent 比较最多三个实际候选 → 用户确认 → 写入并读回计划 → 可记录实付、撤销和查看七日餐表。七日草案仍由应用本地规则生成，**不是模型自动规划**；生成后用户可写下调整需求（如“少辣”“别重复”），Agent 在最多五个日期的已验证换餐选项中提出具体替换，应用校验后先改**待确认草案**，用户核对后确认整周才保存——该链路已于 1.8.13 在 Shell 中用真实 MiniMax-M3 实测通过（见上表）。已确认计划不是订单。

菜单快照有 1,497 条，构建时与 `menu.csv` 关联，其中 1,209 条有非默认商品图 URL。自定义菜单需粘贴 3–200 条 JSON 数据，带来源、更新日期和时区；CSV 可用本地脚本转换。当前没有文件选择器、自动爬取、实时售价/库存、营养或过敏原数据，也没有订餐或付款。正餐判断基于菜名启发式，不能证明吃得饱或均衡。

## 已有的 1.7.0 本地验收

依次运行 `python3 scripts/test-basic-app.py`、`python3 scripts/test-language.py`、`python3 scripts/test-week-draft.py`、`python3 scripts/test-custom-menu.py`。测试覆盖菜单无效数据拒绝、导入与重启恢复、七日草案无提前写入、逐日预算及确认读回、实际金额与撤销、Agent 服务不可用时人工操作、存储损坏和写入故障保护。中文与英文截图由 `scripts/capture-card-host.py` 的 Makepad framebuffer 获得并人工查看，详见[截图记录](evidence/next-meal-170-20261005.md)。签名前已用官方 `tools/octo check bundle` 预检；签名后以公钥执行 `hub check`，结果通过。之后的 card-host 测试使用无签名开发副本，不修改发布包。

## 交付与待办

- 源码采用 Apache 2.0；发布者已声明有权公开分发内置菜单数据与其拍摄的照片，但尚未附独立书面凭据；见[数据来源](DATA_PROVENANCE.md)。代码许可不自动涵盖菜单与图片。
- 赛事队伍主题已在[官方 Issue #5](https://github.com/gosimfoundation/hackathon-agenticapp26/issues/5#issuecomment-5854778542)登记，初赛仓库已在[官方 Issue #13](https://github.com/gosimfoundation/hackathon-agenticapp26/issues/13#issuecomment-5924251291)登记。**个人报名表是否完成无可核验记录**。
- 若把 1.7.0 作为评审版本，需在 OctoSense Shell 用同一 bundle 补齐**成功的真实模型建议**；授权、手动确认、读回、重启和限流回退已有同版证据。记录完整复现步骤后再冻结提交号；当前不能移动旧标签代表这一结果。
- App Hub 签名版已通过[官方 Issue #117](https://github.com/OctoSense-org/OctoSense-App-Hub/issues/117) 提交，固定标签为 `apphub-v1.7.0`；等待维护者审查，尚未上架。赛事评审仍以公开源码、冻结版本与可运行证据为准。

运行当前源码包的方法见[README](../README.md)；1.8.0 新功能的待验收项见[记录](evidence/agent-week-180-20261006.md)，宿主与版本关系见[架构](ARCHITECTURE.md)。
