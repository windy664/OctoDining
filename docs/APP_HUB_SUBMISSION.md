# App Hub 提交状态与操作

核对日期：2026-10-07。官方版本：OctoSense `4081c30`、OctoSense-App-Hub `78dfda5`、OctoScript-App-Design-Flow `a5a87d3`。提交规则以官方 [Design Flow 发布流程](https://github.com/OctoSense-org/OctoScript-App-Design-Flow/blob/main/docs/PUBLISHING.md)和 [App Hub 发布契约](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/main/docs/PUBLISHING.md)为准；本页记录 OctoDining 在这些版本下的核对结果。

我们的作品是 `bundle/` 中的 **script app**，应用 ID `org.octosense.octodining`，当前包版本 `1.7.0`。OctoSense 仓库提供 Shell，不是 App Hub 的投稿地址；赛事作品仓库登记也不等于 App Hub 发布。App Hub 当前接受的入口是在其仓库开标题为 `Submit org.octosense.octodining 1.7.0` 的 issue，由维护者检查并发布；不要向 `catalog.json`、`index/` 或 `artifacts/` 提 PR。

## 已完成的预检

在上述 App Hub 源码构建的 `hub` 上，执行 `tools/octo check bundle` 和 `hub check bundle --allow-unsigned --catalog <App Hub>/catalog.json`，结果均为：

```text
org.octosense.octodining 1.7.0 — PASSED
  [warning] publisher-signature: unsigned: accountability rests on the hub alone
  grants: capabilities {"net", "octos.turn.start", "storage"}, hosts {"img.pospal.cn"}, storage 16777216 bytes, agent none
```

`hub scan bundle --packet build/review-170-20261007.json` 已生成七问审查包。`build/` 是本地工作目录，不随应用包提交。六张商店截图均为 824×1784 的原生 PNG；它们证明此前 1.7.0 card-host 运行，不证明同版真实模型建议。1.7.0 Shell 遇到模型服务 429；成功 Agent 建议的记录属于 1.2.2，详见[评审证据](AGENTIC_JUDGING.md)。

同日用重建后的 card-host 分别运行 `scripts/test-basic-app.py`、`scripts/test-language.py`、`scripts/test-week-draft.py`、`scripts/test-custom-menu.py`，四项均通过。基础测试覆盖服务不可用时的人工选择、保存读回与重启恢复；最新测试日志和隔离数据在本地 `.local-state/*-20261007-*`，未入包。六张已列出的商店截图已人工查看；截图仍是应用 1.7.0 先前运行时捕获，不声称在此次新宿主构建中重拍。

## 提交前仍需核定

1. **数据与图片使用权。** 发布者已声明自己是该校食堂管理员，管理菜单数据、持有本人拍摄照片的权利，并允许公开 GitHub / App Hub 分发；见[来源记录](DATA_PROVENANCE.md)。尚未附独立书面凭据，提交 issue 时应把声明原样提供给维护者；若维护者要求材料，再补授权文件或替换相关内容并重新预检。
2. **发布者资料。** 发布者已确认 `bundle/listing.json` 使用“跃珩科技”。GitHub issues 支持地址、[隐私说明](PRIVACY.md)和只声明 Linux 这一平台仍应由发布者在提交时复核。应用没有在更新后的 OctoSense Shell 上取得 1.7.0 成功模型建议，商品图片也不保证可用。
3. **最终版本。** 确认上述资料后，以最终 `bundle/` 再运行 `tools/octo check bundle`、`hub scan`；任何改动都必须重新 stamp。首次投稿可以按官方规则选择无签名，但后续发布者连续性会受影响；若签名，私钥应由发布者自行创建和保存于仓库外，签名后再用公钥执行最终 `hub check`。不要把私钥、review packet 放进 `bundle/` 或 Git。

## 官方提交顺序

在本仓库根目录，以下命令用于最终复核；若变更了应用内容，先运行 `python3 scripts/build-octos-bundle.py`、原生功能测试，并重新取得与最终版本一致的截图。

```sh
OCTO_CLI=/home/windy/Project/octosense-ws/OctoScript-App-Design-Flow/tools/octo
HUB_CLI=/home/windy/Project/octosense-ws/OctoSense-App-Hub/target/release/hub
"$OCTO_CLI" check bundle
"$HUB_CLI" check bundle --allow-unsigned --catalog /home/windy/Project/octosense-ws/OctoSense-App-Hub/catalog.json
mkdir -p build
"$HUB_CLI" scan bundle --packet build/review.json
```

发布者核定资料、签名方案和最终 `bundle/` 后：将包提交到自己的公开仓库并打 `v1.7.0` 标签；在 App Hub 的[Issues](https://github.com/OctoSense-org/OctoSense-App-Hub/issues) 开 `Submit org.octosense.octodining 1.7.0`，附仓库 URL、标签、完整 commit SHA、包路径 `bundle/`、发布者 ID 与公钥（或标明首次无签名）、最终 `hub check` 原文，以及 `hub scan` 七问答复。**开 issue 是提交申请，不代表已上架；维护者发布到签名目录后才算进入 App Hub。**
