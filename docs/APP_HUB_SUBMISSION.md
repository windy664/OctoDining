# App Hub 提交状态与操作

核对日期：2026-10-07。签名版已提交至[官方 Issue #117](https://github.com/OctoSense-org/OctoSense-App-Hub/issues/117)，等待维护者审查。官方版本：OctoSense `4081c30`、OctoSense-App-Hub `78dfda5`、OctoScript-App-Design-Flow `a5a87d3`。提交规则以官方 [Design Flow 发布流程](https://github.com/OctoSense-org/OctoScript-App-Design-Flow/blob/main/docs/PUBLISHING.md)和 [App Hub 发布契约](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/main/docs/PUBLISHING.md)为准；本页记录 OctoDining 在这些版本下的核对结果。

我们的作品是 `bundle/` 中的 **script app**，应用 ID `org.octosense.octodining`，当前包版本 `1.7.0`。OctoSense 仓库提供 Shell，不是 App Hub 的投稿地址；赛事作品仓库登记也不等于 App Hub 发布。App Hub 投稿 issue 已创建，固定版本为 `apphub-v1.7.0`（commit `8cf21bb41870da9f15752c21badd582027286062`）；是否收录由维护者审查决定。不要向 `catalog.json`、`index/` 或 `artifacts/` 提 PR。

## 已完成的预检

在上述 App Hub 源码构建的 `hub` 上，先对未签名包执行 `tools/octo check bundle` 和 `hub scan`，再由发布者授权使用仓库外的密钥以 `windy664` 签名。签名后的 `hub check bundle --publisher-key windy664=<public-key> --catalog <App Hub>/catalog.json` 结果为：

```text
org.octosense.octodining 1.7.0 — PASSED
  grants: capabilities {"net", "octos.turn.start", "storage"}, hosts {"img.pospal.cn"}, storage 16777216 bytes, agent none
```

公钥（可公开）为 `1b72b26cb53eef42eeb73d5017b57e0e734c25f26191f7f9c8bbf09520d90ba5`；私钥不在仓库。`hub scan bundle --packet build/review-170-final.json` 已在签名前生成七问审查包；签名不改变 `integrity.bundle_blake3`，仍为 `8ab383f6130d3c5e637fd35571ad283500780c88171067a46a0822e11bedd4ec`。`hub scan` 对签名包直接运行会因未提供公钥而拒绝，因此审查包使用签名前的同一内容摘要。`build/` 是本地工作目录，不随应用包提交。六张商店截图均为 824×1784 的原生 PNG；它们证明此前 1.7.0 card-host 运行，不证明同版真实模型建议。1.7.0 Shell 遇到模型服务 429；成功 Agent 建议的记录属于 1.2.2，详见[评审证据](AGENTIC_JUDGING.md)。

同日用重建后的 card-host 分别运行 `scripts/test-basic-app.py`、`scripts/test-language.py`、`scripts/test-week-draft.py`、`scripts/test-custom-menu.py`，四项均通过。基础测试覆盖服务不可用时的人工选择、保存读回与重启恢复；最新测试日志和隔离数据在本地 `.local-state/*-20261007-*`，未入包。六张已列出的商店截图已人工查看；截图仍是应用 1.7.0 先前运行时捕获，不声称在此次新宿主构建中重拍。

## 提交前仍需核定

1. **数据与图片使用权。** 发布者已声明自己是该校食堂管理员，管理菜单数据、持有本人拍摄照片的权利，并允许公开 GitHub / App Hub 分发；见[来源记录](DATA_PROVENANCE.md)。尚未附独立书面凭据，提交 issue 时应把声明原样提供给维护者；若维护者要求材料，再补授权文件或替换相关内容并重新预检。
2. **发布者资料。** 发布者已确认 `bundle/listing.json` 使用“跃珩科技”。GitHub issues 支持地址、[隐私说明](PRIVACY.md)和只声明 Linux 这一平台仍应由发布者在提交时复核。应用没有在更新后的 OctoSense Shell 上取得 1.7.0 成功模型建议，商品图片也不保证可用。
3. **最终版本。** `bundle/` 已签名，不可再用 `tools/octo run bundle` 或无公钥的 `tools/octo check bundle`；开发预览请用 `scripts/dev_bundle.py` 生成隔离副本。发布者需妥善保管仓库外私钥：后续同一发布者更新必须沿用它。若修改包内容，必须重新 stamp、签名、检查并固定新提交；不要把私钥、review packet 放进 `bundle/` 或 Git。

## 官方提交顺序

在本仓库根目录，以下命令用于核对这份已签名的发布包；若变更了应用内容，先在开发副本中运行功能测试并重新取得与最终版本一致的截图，再由发布者重新签名。

```sh
HUB_CLI=/path/to/OctoSense-App-Hub/target/release/hub
HUB_CATALOG=/path/to/OctoSense-App-Hub/catalog.json
PUBLISHER_PUBLIC_KEY=1b72b26cb53eef42eeb73d5017b57e0e734c25f26191f7f9c8bbf09520d90ba5
"$HUB_CLI" check bundle --publisher-key "windy664=$PUBLISHER_PUBLIC_KEY" --catalog "$HUB_CATALOG"
```

签名版使用 `apphub-v1.7.0` 标签；此前的 `v1.7.0` 指向无签名候选，**不要用于 App Hub 投稿**。[投稿 Issue #117](https://github.com/OctoSense-org/OctoSense-App-Hub/issues/117) 已包含仓库 URL、固定标签、完整 commit SHA、包路径 `bundle/`、发布者 ID `windy664` 与上方公钥、最终 `hub check` 原文，以及签名前 `hub scan` 七问答复。**开 issue 是提交申请，不代表已上架；维护者发布到签名目录后才算进入 App Hub。**
