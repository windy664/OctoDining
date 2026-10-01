# Octos Agent 晚餐任务边界

比赛主入口是 Rinx 中运行的 OctoScript bundle。应用把用户预算、到店时间、口味描述和本地筛出的候选交给当前 Octos Agent，再由用户确认计划。

## 一次请求

| 阶段 | 责任方 | 可核对内容 |
| --- | --- | --- |
| 读取结构化预算、时间和避辣选择 | OctoScript app | 输入校验；无效输入直接提示 |
| 在本地菜单快照中检索 | OctoScript app | 价格不超预算、营业时段覆盖到店时间、避辣关键词规则、商品/店铺来源 |
| 用自然语言偏好比较候选 | Rinx 宿主 Octos Agent | `octos.turn.start` 真实请求与宿主返回文本；Agent 只能选择已给候选 |
| 最终选择 | 用户 | 点选卡片后才保存为本地今晚计划 |

应用只申请 `octos.turn.start` 与 `storage`。没有 Matrix 读取能力，不访问外网、库存或订单服务。App 会把用户输入文本和最多 3 个候选发送给宿主 Agent；菜单筛选本身在本地完成。

## 失败处理与限制

- 非法预算/时间、没有营业时段匹配项、Agent 服务不可用或 Agent 请求失败时，显示明确提示，不虚构候选或回复。
- 避辣只按商品名和类别关键词筛选，不构成过敏原识别；未实现素食保证。
- 订单、当前库存、即时营业状态、路程、评论与营养数据均不可用。用户确认仅是本地计划，不触发交易。
- 当前 card-host 只验证脚本解析、bundle admission 和首帧，不支持 Rinx 的 Octos 服务；实际 Rinx Agent 联调尚未完成。

## 检查

```sh
python3 scripts/build-octos-bundle.py
/home/windy/Project/octosense-ws/OctoScript-App-Design-Flow/tools/octo check bundle
node scripts/smoke-web-demo.cjs
cargo test --offline
```

比赛状态和待办见 `CONTEST_READINESS.md`。
