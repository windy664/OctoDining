# 参赛准备状态

更新：2026-10-04。基本功能通过 `card-host` 交互验收；OctoSense Shell 已安装运行 OctoDining 1.2.1，并使用真实 MiniMax-M3 完成 Agent 建议、用户确认与计划读回闭环。[空计划运行记录](evidence/shell-minimax-clean-20261004.json)证明从零新建计划；[同版本 Shell 截图记录](evidence/shell-minimax-20261004.json)、[Agent 建议截图](evidence/shell-minimax-agent-20261004.png)及[计划读回截图](evidence/shell-minimax-plan-20261004.png)来自另一次已有计划的运行。

## 当前交付判断

| 项目 | 状态与证据 |
| --- | --- |
| 产品任务 | 面向预算有限人群的餐饮规划，见 [BRIEF](BRIEF.md) |
| 菜单快照 | 1,497 条记录，含名称、店铺、类别、标价和营业时段；来源授权待补 |
| 基本功能 | A1–A6、三餐候选、预算与时段过滤、保存/重启恢复/修改/取消、写入核验通过 card-host UI 验收 |
| 数据健全 | 金额按分计算；确认计划保留商品 ID、名称、店铺、原快照价格、营业时段与用户需求 |
| 持久化 | 双文件轮换；测试覆盖文件损坏恢复、保存故障保护、双副本无效时锁写 |
| Agent 能力 | `octos.turn.start` 候选比较、请求前条件复核、序号校验、失效回调丢弃和响应 JSON 类型校验已进入源码；card-host 验证无服务回退，Shell 已验证授权拒绝与未配置模型时仍可人工确认 |
| App Hub 检查 | bundle 1.2.1 在 listing 和截图更新前通过 unsigned hub check；声明 `storage`、`octos.turn.start`。隔离 Shell 通过临时本地签名目录安装和更新；更新后的 bundle 摘要与预检须重新执行，正式发布签名未完成 |
| 运行宿主 | OctoSense `4a541777` 与锁定依赖下，Linux `cargo check --locked -p octosense`、`cargo build --locked -p octosense` 已通过；Octos `2.0.3-rc.13 (056173e)` 内核已构建。隔离 Shell 中通过 App Hub 安装并运行 OctoDining 1.2.1，`octos.turn.start` → Octos kernel → MiniMax-M3 返回候选建议；用户确认后 `plans-a.json` 写入并读回。首次授权在干净 profile 中通过；拒绝授权和无模型回退也已实测。Agent 会话 ledger 因上游会话路径过长而退到内存，本次不声称 Agent 对话持久化 |
| 页面外观 | `bundle/screenshots/01-main.png` 和 `02-plan-confirmed.png` 是 card-host 实机画面；新增 Shell 真实 MiniMax Agent 建议与计划读回截图，见上方证据链接 |
| 商店资料 | `bundle/listing.json` 已改为 OctoDining 文案，列出已在 Linux 实测的平台、队伍名「跃珩科技」及仓库 Issues 支持地址；隐私说明见 [PRIVACY](PRIVACY.md)。上架前仍须核对发布者身份与有效截图；菜单来源和授权未补齐 |
| 许可与隐私 | 代码 Apache-2.0；菜单的采集来源、日期和再分发许可待确认。请求仅发送本次需求、候选和当日计划摘要 |
| 赛事登记 | 队伍主题已在[官方 Issue #5](https://github.com/gosimfoundation/hackathon-agenticapp26/issues/5#issuecomment-5854778542)登记：跃珩科技、成员 id Torine、餐谱规划、已加群；初赛仓库已在[官方 Issue #13](https://github.com/gosimfoundation/hackathon-agenticapp26/issues/13#issuecomment-5924251291)登记。个人报名表是否完成尚无证据 |
| 冻结版本 | 原始初赛版保留在 `qualifier-2026-10-04`；包含真实 MiniMax 验收材料的版本固定为 `qualifier-2026-10-04-minimax`。执行 `git rev-parse qualifier-2026-10-04-minimax` 获取完整 SHA。官方 Issue #13 已指向本公开仓库 |

## 当前完整任务路径

输入日期、每日预算、餐次、本餐上限和到店时间 → 本地快照筛选候选 → 可选地请系统 Agent 比较 → 用户确认一个候选 → 保存并读回核验 → 重启后继续修改或取消。

Agent 不会搜索整份菜单、创建新候选或自动保存。菜单不提供实时库存/价格、营养或过敏原信息；没有下单、付款或配送能力。七日计划和历史去重仍未迁入应用。

## 验收记录

`python3 scripts/test-basic-app.py --port 8174` 通过 14 组预算、非法输入、Agent 服务不可用回退、候选筛选、计划保存/恢复、日期隔离、修改/取消、写盘故障和损坏文件恢复检查。[公开报告](evidence/basic-app-20261004.json)保留测试脚本当时的 1.2.1 manifest、14 项检查、无截图及工作树未冻结的状态；复跑仍应以最终提交为准。[空计划 MiniMax 联调记录](evidence/shell-minimax-clean-20261004.json)记录一次实际 LLM 响应、新建计划和读回；[已有计划的 Shell 截图记录](evidence/shell-minimax-20261004.json)记录另两次真实 LLM 响应及界面图像，两组证据不可当作同一次运行。先前[本机 mock 联调记录](evidence/shell-mock-20261004.md)仅作基线。[Shell 失败路径记录](evidence/shell-failures-20261004.json)验证拒绝授权和未配置模型仍可人工确认。

## 评审复现顺序

1. 检出本仓库 `qualifier-2026-10-04-minimax` 标记（`git rev-parse qualifier-2026-10-04-minimax` 可获取完整 SHA），并记录 `bundle/manifest.json` 的版本和摘要。当前目标包是 OctoDining 1.2.1。
2. 在 Linux 使用已记录的 OctoSense Shell 版本 `4a541777` 和 Octos 内核 `056173e` 构建宿主；具体依赖、环境和构建入口见 [ARCHITECTURE](ARCHITECTURE.md) 与上游仓库文档。应用 bundle 位于 `bundle/`。评审需要自行配置宿主模型 provider；仓库不含 API key。
3. 运行 `python3 scripts/build-octos-bundle.py`，以 OctoScript-App-Design-Flow 的 `tools/octo check bundle` 做本地预检。若已经签名或冻结，勿在同一个检出目录重建；对开发副本运行该命令，并按包发布规范重新 stamp。
4. 在 OctoSense Shell 中安装此 bundle，打开 OctoDining，输入日期、餐次、到店时间和预算，点击“查找 / 换一批”，再点击“让 OctoSense Agent 比较”。检查建议只引用画面中至多三个候选。用户点“确认候选”后，检查状态显示“已保存并读回核验”和预算摘要；重启应用检查计划恢复。
5. 测无 Agent 服务/拒绝时的反馈：应用仍可由用户直接确认候选。运行截图或视频必须来自同一冻结版本，并标注模型是正式 provider 还是 mock。

第 4 步已使用 MiniMax-M3 正式 provider 在 Shell 实测，独立的 `octos-kernel chat` 测试不计作应用联调。评审复现需自备有效 MiniMax API key，并在宿主隔离 profile 中设置 `minimax-cn`、`MiniMax-M3` 与 `https://api.minimax.cn/v1`；本仓库没有密钥。

## 交付前还需要

- 格式错误与过期 Agent 响应仍待 Shell 运行验收；首次授权通过已在干净 profile 实测，拒绝和无模型回退另有记录。
- 本次两张 Shell 截图来自真实 MiniMax provider；补录包含授权、建议、确认和失败回退的连续视频可帮助评委复现。至少一张有效 PNG/SVG 截图是 Hub listing 的要求。
- 补全菜单来源、采集日期、再分发许可和作者/发布者身份核对；在正式上架前核对隐私说明与实际 provider 配置。
- 完成个人报名状态核对；在截止前冻结可运行提交、记录完整 SHA、更新官方登记材料中可见的版本证据。无需先等待 App Hub 商店上架。[官方交付说明](https://github.com/gosimfoundation/hackathon-agenticapp26/blob/main/docs/app-hub-submission.md)
