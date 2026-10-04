# OctoDining 1.2.1 最终包预检

2026-10-04，在提交 `1b9e473` 的 `bundle/` 上执行只读检查；最终标签的应用包字节与该提交一致：

```text
$ hub check bundle --allow-unsigned
org.octosense.octodining 1.2.1 — PASSED
  [warning] publisher-signature: unsigned: accountability rests on the hub alone
  grants: capabilities {"octos.turn.start", "storage"}, hosts {}, storage 16777216 bytes, agent none
```

另将同一 `bundle/` 复制到临时目录，运行 `tools/octo check`（内部执行 `hub stamp` 和 `hub check --allow-unsigned`）。复算摘要为 `cea68804cdf4b056fdb33de91ff9965a10740b595bbd8c9646be0f83f6b3e386`，与仓库内 `bundle/manifest.json` 一致；没有修改冻结包。

`hub scan bundle --packet /tmp/octodining-hub-review-20261004.json` 已成功生成七问审核材料；该 review packet 含完整应用源码，仅保留在本机临时目录，未提交。预检证明包结构和声明的能力通过本地规则，签名发布仍需真实发布者密钥；真实运行与模型调用见 `shell-minimax-clean-20261004.json`。
