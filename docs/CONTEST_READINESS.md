# Agentic App 2026 初赛准备状态

## 当前技术路线

比赛主入口切换为 Rinx Mini Apps 的 OctoScript 应用：Rinx 宿主的 `octos.turn.start` 将已筛选的候选和用户偏好交给当前 Octos Agent。菜单筛选和边界检查在 bundle 本地执行；Agent 不获得 Matrix 聊天读取能力。用户点选后，应用只写入本地今晚计划。

本地权限为 `octos.turn.start` 与 `storage`。模型密钥由 Rinx/OctoSense 宿主管理。作品不请求 Matrix、外网、定位、下单或支付权限。网页原型和 Rust CLI 留作辅助验证，不作为主参赛入口。

## 初赛交付对照

| 要求 | 当前状态 |
| --- | --- |
| 清楚的用户需求 | 针对学生下课/打工人下班后的晚餐选择疲劳；输入预算、到店时间、口味偏好 |
| 可运行原型及启动说明 | Rinx 可审阅的 OctoScript bundle 已完成；OctoSense `card-host` admission/UI 加载通过。需要在比赛用 Rinx 账号中导入并试运行 |
| Agent 执行 | 已登记的 Rinx 内置 app 真实调用 `octos.turn.start`，交给宿主的 Octos 助手比较本地核验过的候选；尚未在有可用 provider 的 Rinx 会话里完成端到端请求 |
| 用户操作与可核验结果 | 预算/营业时段/避辣在本地筛选；候选展示菜单来源、标价和营业时段；用户点击确认后写入本地计划 |
| 失败或空状态 | 输入不合法、没有候选及 Agent/宿主错误均有明确状态；营业时间缺失时不纳入候选 |
| 数据来源与限制 | 1,497 项菜单快照；不代表实时库存、价格或营业状态；再分发许可和来源凭据待核验 |
| 可复现材料 | 生成脚本、OctoScript admission 检查、网页 smoke test、Rust 离线测试均可运行；比赛 Rinx 端到端演示、真实截图/视频、冻结版本待完成 |

## 演示路线

1. 在 Rinx 打开已审阅的 OctoScript app；展示它只请求 Agent 调用和本地存储权限。
2. 填写预算 ¥20、预计到店 18:30，再输入“刚下课，想吃饱一点，别太辣”。
3. 点击“问问 Octos Agent”；验证用户条件和快照候选确实进入宿主 Agent 请求，呈现首选与理由。
4. 对照候选的商品名、店铺、价格和营业时间，点击一项写入今晚计划；说明没有下单。
5. 提高预算或改到店时间触发空状态；说明菜单快照不是实时营业/库存信息。

必须在比赛环境验证真实 Agent 响应及宿主失败状态。不要把 `card-host` 的界面加载说成已验证 Rinx Agent 联调，也不要伪造截图或模型输出。

## 本地验证记录

- `tools/octo check bundle --allow-unsigned`：通过；manifest 请求 `octos.turn.start`、`storage`。
- `tools/octo run bundle --port 8141 --hidden --detach`：card-host bundle admission 及首帧通过。此 host 不提供 Octos Agent 服务，因此无法验证真实 Agent 调用。
- `./scripts/preview.sh`：无需 Matrix 登录的一键开发预览；Octos 不可用时明确标注本地规则回退，可测试筛选、空状态、候选显示和用户确认。
- Rinx `tools/package-system-apps/check.sh`：通过；内置目录保留 `org.octosense.meal-planner` ID，声明 `storage` 和 `octos.turn.start`。
- Rinx `cargo build --offline --locked --bin rinx --features agent_chat`：通过，已将内置应用打包进本地 Rinx 构建。当前运行环境没有可用 compositor/provider，尚未完成桌面端真实模型联调。
- `node scripts/smoke-web-demo.cjs`：网页备用原型 smoke test 通过。
- `cargo test --offline`：Rust 离线规划逻辑测试通过。
- 赛事与 Rinx 边界依据：<https://github.com/gosimfoundation/hackathon-agenticapp26/blob/main/docs/competition-schedule.md>、<https://github.com/gosimfoundation/hackathon-agenticapp26/blob/main/docs/rinx-miniapps.md>。

## 赛前待办

- 在 Rinx 比赛账号导入 bundle，审阅权限，配置 Octos provider，完成一次真实 Agent 请求及宿主不可用/无匹配候选测试。
- 重新运行 bundle 构建及检查，冻结同一个版本；采集并人工检查两张真实运行截图，录制 2–3 分钟同版本演示。
- 补全精确数据来源、采集日期和公开再分发授权；如无法确认，演示时说明数据快照并限制包内数据公开。
- 填入已报名成员名单；参赛资格以主办方报名记录为准。
