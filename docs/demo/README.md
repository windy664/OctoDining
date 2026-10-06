# OctoDining 1.7.0 视频素材

[观看 35 秒演示剪辑](octodining-170-evidence-reel.mp4)（1920×1080，H.264/AAC）。这是将已有的**真实应用截图**配文字和原创合成音乐制作的展示片，**不是连续屏幕录制**。

前六幕取自 [1.7.0 card-host 原生运行与验收截图](../evidence/next-meal-170-20261005.md)，依次展示下一餐、首次预算设置、候选、七日草案、确认结果和实付记录。最后一幕取自 [1.7.0 OctoSense Shell 局部联调](../evidence/shell-170-20261005.md)，展示重启后仍可见的原计划。截图证明画面及所述本地交互；这一版的模型请求遇到 HTTP 429，尚无成功建议证据。完整运行步骤和版本边界见 [README](../../README.md)。

视频可用以下命令从仓库里的截图重新生成：

```sh
python3 -m pip install numpy
python3 scripts/render-evidence-reel.py
```

还需系统安装 `ffmpeg` 和 Noto Sans CJK 字体，当前脚本按 Linux 上 `/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc` 定位字体。原始截图保留在 `docs/evidence/`；音乐由脚本合成，不使用 `pdoom-video` 的歌曲或歌词。创意参考：[pdoom-video](https://github.com/mexicat/pdoom-video)。

提交评审时，请同时提供源码、固定版本、运行说明及原始证据；剪辑视频不能替代可运行作品或 Agent 结果核验。当前执行环境禁止本地 socket，无法在此重新启动宿主录制连续操作，故没有把剪辑标作实机录屏。
