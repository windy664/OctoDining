# OctoDining 视频证据

## 1.2.2 · 真实 Agent 闭环

[观看 15 秒 Agent 证据剪辑](octodining-122-agent-evidence-reel.mp4)（1920×1080，H.264/AAC）。三幕分别取自**同一次** [1.2.2 OctoSense Shell + MiniMax-M3 联调记录](../evidence/shell-ui122-minimax-20261004.json)中的[模型建议](../evidence/shell-ui122-minimax-agent-20261004.png)、[下滑后可见的人工确认按钮](../evidence/shell-ui122-minimax-scrolled-20261004.png)和[保存读回结果](../evidence/shell-ui122-minimax-confirmed-20261004.png)。这是实机截图剪辑，不是连续录屏；第二幕证明确认入口可见，实际点击和结果由原始运行记录及第三幕呈现。已有晚餐计划场景中的建议是候选 3，不能把它说成 Agent 从零规划整周。

使用 `python3 scripts/render-evidence-reel.py --agent` 可从仓库原始截图重新生成，不需要再调用模型，也不会消耗比赛 Token。失败回退、版本限制和评分项索引见[Agentic 验收说明](../AGENTIC_JUDGING.md)。

## 1.7.0 · 产品功能展示

[观看 35 秒演示剪辑](octodining-170-evidence-reel.mp4)（1920×1080，H.264/AAC）。这是将已有的**真实应用截图**配文字和原创合成音乐制作的展示片，**不是连续屏幕录制**。

前六幕取自 [1.7.0 card-host 原生运行与验收截图](../evidence/next-meal-170-20261005.md)，依次展示下一餐、首次预算设置、候选、七日草案、确认结果和实付记录。最后一幕取自 [1.7.0 OctoSense Shell 局部联调](../evidence/shell-170-20261005.md)，展示重启后仍可见的原计划。截图证明画面及所述本地交互；这一版的模型请求遇到 HTTP 429，尚无成功建议证据。完整运行步骤和版本边界见 [README](../../README.md)。

视频可用以下命令从仓库里的截图重新生成：

```sh
python3 -m pip install numpy
python3 scripts/render-evidence-reel.py
```

还需系统安装 `ffmpeg` 和 Noto Sans CJK 字体，当前脚本按 Linux 上 `/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc` 定位字体。原始截图保留在 `docs/evidence/`；音乐由脚本合成，不使用 `pdoom-video` 的歌曲或歌词。创意参考：[pdoom-video](https://github.com/mexicat/pdoom-video)。

提交评审时，请同时提供源码、固定版本、运行说明及原始证据；剪辑视频不能替代可运行作品或 Agent 结果核验。当前执行环境禁止本地 socket，无法在此重新启动宿主录制连续操作，故没有把剪辑标作实机录屏。
