# 参赛准备状态

更新：2026-10-10。**初赛入围（80/100）**，评审意见与决赛前改进清单见[初赛结果](PRELIMINARY-RESULT.md)。当前工作版 **1.8.0**：1.7.0 功能之上并入 Agent 跨日换餐提案，待运行验收；最后有实机画面的版本是 1.7.0。以 OctoSense Shell / OctoScript 为主线。Rinx 分享是可选扩展，App Hub 是包检查与提交规范；它们不要求一起实现。应用先完成真实餐食任务，再展示 Agent 决策及结果核验。[按最佳 Agentic 评分项核验](AGENTIC_JUDGING.md)：1.2.2 的真实模型闭环与 1.7.0 的失败回退分版呈现。最新[App Hub 投稿状态与步骤](APP_HUB_SUBMISSION.md)单独记录。

## 版本与证据边界

| 范围 | 已验证 | 尚需完成 |
| --- | --- | --- |
| 1.8.0 源码 / App Hub | 七日草案新增 Agent 换餐提案入口；Makepad 脚本语法解析通过、unsigned 包预检通过，见[记录](evidence/agent-week-180-20261006.md) | card-host UI、Shell 授权和真实模型、应用草案与确认读回均未在同版运行验收 |
| 1.7.0 card-host | 首次预算、内置/自定义菜单、下一餐推荐、候选、七日草案确认、记录实付、取消与恢复；中英文原生画面；本地持久化及故障保护 | card-host 不能证明 Shell 模型调用 |
| 1.7.0 App Hub | 最新 Hub `78dfda5` 的签名检查通过；`windy664` 公钥已验证，`hub scan` 审查包在签名前生成；[投稿 #117](https://github.com/OctoSense-org/OctoSense-App-Hub/issues/117) 已提交 | App Hub 维护者审查与发布；预检不代替实际运行 |
| 1.7.0 OctoSense Shell | 本地测试目录加载、首次 Agent 授权、请求进入 Octos；供应商 HTTP 429 后手动选餐、保存读回与重启恢复通过，[本版记录](evidence/shell-170-20261005.md) | 限流导致本次无模型建议；仍需同版成功模型闭环及响应异常验收 |
| 1.2.2 OctoSense Shell | 本地测试目录安装，`octos.turn.start` 经 Octos kernel 得到真实 MiniMax-M3 建议，用户确认后保存并读回；拒绝授权和无模型回退分别实测 | 不能代替 1.7.0 的真实模型成功证据 |

冻结标签 `qualifier-2026-10-04-final` 仍指向 **1.2.2**；不得将 1.8.0 新功能、1.7.0 截图和旧版真实模型记录说成同一次运行。[1.2.2 联调记录](evidence/shell-ui122-minimax-20261004.json)、[1.7.0 Shell 部分联调](evidence/shell-170-20261005.md)与[1.7.0 card-host 截图](evidence/next-meal-170-20261005.md)分开保留。模型密钥只由宿主本地配置，仓库不含密钥。

## 当前任务路径

首次选择菜单并设置生活费 → 首页出现下一餐 → 查看菜单来源、价格和营业时段 → 需要时更换或请 Agent 比较最多三个实际候选 → 用户确认 → 写入并读回计划 → 可记录实付、撤销和查看七日餐表。七日草案仍由应用本地规则生成，**不是模型自动规划**。1.8.0 源码允许 Agent 在最多七个日期中选择具体替代餐，每日最多两个已筛选选项；应用校验后先改待确认草案，用户再确认保存。该新增链路还没有运行证据，已确认计划不会被自动覆盖。已确认计划不是订单。

菜单快照有 1,497 条，构建时与 `menu.csv` 关联，其中 1,209 条有非默认商品图 URL。自定义菜单需粘贴 3–200 条 JSON 数据，带来源、更新日期和时区；CSV 可用本地脚本转换。当前没有文件选择器、自动爬取、实时售价/库存、营养或过敏原数据，也没有订餐或付款。正餐判断基于菜名启发式，不能证明吃得饱或均衡。

## 已有的 1.7.0 本地验收

依次运行 `python3 scripts/test-basic-app.py`、`python3 scripts/test-language.py`、`python3 scripts/test-week-draft.py`、`python3 scripts/test-custom-menu.py`。测试覆盖菜单无效数据拒绝、导入与重启恢复、七日草案无提前写入、逐日预算及确认读回、实际金额与撤销、Agent 服务不可用时人工操作、存储损坏和写入故障保护。中文与英文截图由 `scripts/capture-card-host.py` 的 Makepad framebuffer 获得并人工查看，详见[截图记录](evidence/next-meal-170-20261005.md)。签名前已用官方 `tools/octo check bundle` 预检；签名后以公钥执行 `hub check`，结果通过。之后的 card-host 测试使用无签名开发副本，不修改发布包。

## 交付与待办

- 源码采用 Apache 2.0；发布者已声明有权公开分发内置菜单数据与其拍摄的照片，但尚未附独立书面凭据；见[数据来源](DATA_PROVENANCE.md)。代码许可不自动涵盖菜单与图片。
- 赛事队伍主题已在[官方 Issue #5](https://github.com/gosimfoundation/hackathon-agenticapp26/issues/5#issuecomment-5854778542)登记，初赛仓库已在[官方 Issue #13](https://github.com/gosimfoundation/hackathon-agenticapp26/issues/13#issuecomment-5924251291)登记。**个人报名表是否完成无可核验记录**。
- 若把 1.7.0 作为评审版本，需在 OctoSense Shell 用同一 bundle 补齐**成功的真实模型建议**；授权、手动确认、读回、重启和限流回退已有同版证据。记录完整复现步骤后再冻结提交号；当前不能移动旧标签代表这一结果。
- App Hub 签名版已通过[官方 Issue #117](https://github.com/OctoSense-org/OctoSense-App-Hub/issues/117) 提交，固定标签为 `apphub-v1.7.0`；等待维护者审查，尚未上架。赛事评审仍以公开源码、冻结版本与可运行证据为准。

运行当前源码包的方法见[README](../README.md)；1.8.0 新功能的待验收项见[记录](evidence/agent-week-180-20261006.md)，宿主与版本关系见[架构](ARCHITECTURE.md)。
