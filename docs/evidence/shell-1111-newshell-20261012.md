# 1.11.1 在新版 OctoSense（37eb1e2）的复验 · 2026-10-12 傍晚

范围：OctoSense 上游从 4081c30 快进到 37eb1e2（542 个提交，含声明式能力准入改动），
本地重建 octosense-home 与 octos 内核（v2.0.3-rc.13）后，签名版 1.11.1 未改一字节直接复验。

## 通过的项

- **启动与准入**：`launch-hub:org.octosense.octodining` 拉起应用（client 1, in-process card）。
  新版两处环境语义变化：`OCTOSENSE_HUB` 现在指**目录**（读 `<dir>/catalog.json`，不再是文件路径），
  且新增 `OCTOSENSE_HUB_CATALOG` 通道选择（默认 `github-v2` 读 `catalog-v2.json`；本地镜像须显式 `legacy`）。
- **桌面窗口渲染**：应用在新桌面 WM 中以窗口片运行（见同目录截图，含顶栏「Ask OctoDining」入口）。
- **Glance**：应用的一览卡出现在新「At a glance」面板（晚餐 · 蛋肉炒饭 ¥12.00 · 到店 18:30）。
- **真实 Agent 调用**：首页输入「少辣」→ 候选 3 个 → `octos.turn.start` 经新内核取得真实
  MiniMax-M3 建议：「Agent 建议候选 1: 蛋肉炒饭不辣符合少辣要求，¥12.00 在本餐上限 ¥12.80 与日预算内，
  18:30 在 10:00-22:00 营业时段内；候选 2 火鸡拌面、候选 3 辣番茄火锅米线均偏辣，与少辣需求冲突。
  仅为建议；请核对信息并自行确认。」未出现新的能力拒绝；授权沿用环境内既有同意状态，未再弹窗。
- **交互**：远程桥硬件指针路径（`hw=1`）可驱动瓦片内 UI（软点击路径不进嵌套瓦片）。

## 未通过 / 限制

- 新版 hidden 模式下 `/g`、`/gseq` 抓帧超时（后端不按需呈现）；`capture:<path>` 只拿到启动首帧。
  本文截图即该首帧。桌面瓦片内的后续画面未截取，交互验证以 snap 结构断言为准。
- 未逐条重跑 1.11.0 的异常路径（授权拒绝、429）；shell-env 为本地测试目录，非正式上架环境。

截图：`shell-1111-newshell-20261012.png`（新桌面 + OctoDining 首页 + At a glance 面板中的本应用卡片）。
