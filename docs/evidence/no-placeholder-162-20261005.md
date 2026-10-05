# 1.6.2 商品图片与无图状态原生验收

日期：2026-10-05。上一版只在首页加载菜单图片，且 288 条没有专属图片的商品仍显示通用餐桌占位图。1.6.2 移除该占位资源：首页、候选和一周餐表有商品图片 URL 才显示图片；无图时展示完整的文字卡片。`menu.csv` 与 1,497 条清洗记录按原始顺序对应，其中 1,209 条有关联的非默认图片 URL。

以下画面均从实际运行的 **1.6.2 原生 card-host** 通过 Makepad framebuffer 截取。商品图来自原始菜单，可能是宣传配图，并不保证与菜名完全一致或为实拍。

| 状态 | 截图 |
| --- | --- |
| 中文首页有商品图 | [今日推荐](no-placeholder-162-20261005/zh/01-home-recommendation.png) |
| 中文候选有商品图 | [候选卡](no-placeholder-162-20261005/zh/02-candidates.png) |
| 英文一周餐表有商品图 | [已确认晚餐](no-placeholder-162-20261005/en/03-week-plan-confirmed.png) |
| 英文首页无专属图 | [芽菜肉沫面纯文字卡片](no-placeholder-162-20261005/en/04-text-only-no-image.png) |

另有[中文首次引导](no-placeholder-162-20261005/zh/00-first-run-setup.png)、[中文餐表](no-placeholder-162-20261005/zh/03-week-plan-confirmed.png)、[英文首次引导](no-placeholder-162-20261005/en/00-first-run-setup.png)、[英文首页](no-placeholder-162-20261005/en/01-home-recommendation.png)与[英文候选](no-placeholder-162-20261005/en/02-candidates.png)。`scripts/capture-card-host.py` 验证中英文预算、候选、确认保存与读回；`scripts/test-basic-app.py --port 8256` 通过首次引导及 14 组中文交互检查；`scripts/test-language.py` 验证英文流程、无图卡片、重启语言保持及切回中文。unsigned `tools/octo check bundle` 通过。

这些证据确认 card-host 中对应的网络图片能够加载，以及缺图时界面没有通用占位图。**本版尚未在 OctoSense Shell 中重验图片加载或真实模型**；远程图片失效、断网时的显示仍需故障注入检查。
