# 1.3.1 首页视觉修订

2026-10-04。参考 [OctoSense 官方学校场景](https://octosense.org/cn/experience/school/)的暖白底色、深绿文字、留白和明确的下一步；参考 [GSA 对 America.gov 的介绍](https://www.gsa.gov/about-gsa/newsroom/news-releases/gsa-joins-the-white-houses-national-design-studio-in-unveiling-americagov-09292026)及[公开新闻中的首页配图](https://www.gossipherald.com/news/66725-us-government-unveils-ai-chatbot-for-unified-federal-services)所呈现的单一主标题和自然语言入口。America.gov 本站对自动访问返回防护页，本轮没有声称直接检视其完整网页。

首页改为一条阅读路径：一句开场白 → 一道推荐 → 输入需求让 Agent 比较候选 → 调整预算与时间。旧版同权重的摘要、推荐、蓝色输入卡和多组按钮不再占据首屏。菜单推荐仍由本地快照、预算、餐次、到店时段和已存计划计算；短而明确的餐品名称优先，促销前缀降权。这是规则推荐，非模型生成。装饰图由 ImageGen 生成，展示餐桌氛围，不是所推荐菜品的实拍或数据来源。

- `python3 scripts/test-basic-app.py --port 8214`：14 组 card-host UI 回归通过。
- `python3 scripts/capture-card-host.py --port 8216 --output .local-state/editorial-final2-20261004`：采集 1.3.1 原生 [首页](editorial-home-131-20261004/01-home-recommendation.png)、[候选](editorial-home-131-20261004/02-candidates.png)、[一周餐表](editorial-home-131-20261004/03-week-plan-confirmed.png)，均为 824×1784，并同步到 `bundle/screenshots/`。
- 在隔离的 1.3.1 card-host 首页输入“别太辣”并提交，确认进入 Octos 请求路径；此宿主没有模型配置，应用明确提示服务暂不可用且保留人工候选。
- `tools/octo check bundle`：1.3.1 unsigned 预检通过，摘要以最终 `bundle/manifest.json` 为准。1.3.1 尚未在 OctoSense Shell 进行同版真实模型复验；此前 1.2.2 的真实 MiniMax 闭环见[独立记录](shell-ui122-minimax-20261004.json)。

画面中的菜单价格与营业时段来自本地快照，不是实时信息；计划确认不执行下单。
