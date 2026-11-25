# 第十九版发布链路只读复查

## 结论

在六项 overlay 实测值正确填入、远端只先新增本轮 workflow 的前提下，未发现会使正常首次 runner 必然失败的版本错配，也未发现静默遗漏旧 manifest payload 的路径。此次没有改动三份冻结实现，没有重跑虚构夹具，没有执行 GitHub 写入或 runner。

## 可收紧的一处对象绑定

工作流先确定数值 release ID，随后各核验也按该 ID 读取；但 upload/download 及最终 `gh release edit` 仍用 tag 再次解析对象。官方 CLI 确认这些命令的入口参数是 tag。现有最终核验要求原 ID、tag、公开状态和实际 commit 同时匹配，因此没有发现“错误目标仍静默报成功”的路径。但最后的实际公开动作可以直接携带已经绑定的 ID。

建议最小替换（仅给建议，未修改实现）：

```bash
gh api --method PATCH   "repos/$EXPECTED_REPOSITORY/releases/$DRAFT_RELEASE_ID"   --field draft=false   --raw-field target_commitish="$PUBLISH_COMMIT_SHA"   >/dev/null
```

保留后面所有按 ID 和真实 tag 的复核。按 tag 上传的正常首次路径没有发现确定问题；如要进一步收紧，可在上传前要求同 tag 的所有状态 release 总数也是 1，防止出现额外同 tag 对象时继续。不要把这一未发生的边界情形误报为已确认失败。

## 历史文件完整性

实际 apply 的基线循环检查旧 3099 条记录全部仍在新清单，除三份批准更新的根文档外不得改变记录。新增 ZIP 成员限定新工程、快照、两份新工具及根文档。完整包输入为所有新清单 payload 加清单自身与六份 metadata，因此不会仅打包本地恢复的 777 条。

根 README、AGENTS、CONTINUE_HERE 允许更新，所以旧根文档需要快照。现已实际发现 `snapshots/20261125/` 下这三份文档及旧清单，并逐份确认 SHA-256 与基线相同。最终请将四份快照列入新 manifest/overlay。Git 对象历史本身并不包含在 payload-only ZIP 中。

六份 metadata 在 applier 和 packager 完全一致；新 applier 还拒绝清单自引用或 metadata 被误列为 payload。旧四份 metadata 来自完整 checkout，新 workflow 由前置提交提供，新 receipt 由 apply 生成。

## 必须保持的执行顺序

1. 按确定 asset ID 下载固定分片，核对次序、大小、完整 ZIP SHA，再执行其中 applier。
2. 全仓 checkout 中实际 apply：固定基线祖先、仅 workflow 差异、干净工作树、全部重构字节与旧条目保留检查。
3. `verify_repository.py --strict` 必须通过，再只提交清单路径、清单与 receipt；push 不带 force。
4. Runner 上 `--full` 打包并重读 ZIP 全成员；八个输出名称与 workflow 精确一致。
5. 现有资产只接受逐字节相同，不用 clobber；逐个核对原 release ID 下上传状态、大小与 SHA256/下载 cmp。
6. tag 不存在才创建；已存在必须指向最终提交；公开后再次核对原 release ID 和实际 tag。

`--verify-only` 不执行祖先、干净工作树与旧条目保留 gate；它不能替代上述真实 apply。工作流当前确实调用真实 apply，随后有 strict gate，无须放宽。

## 明确会停止的情况

远端出现其他改动、release 已公开而非草稿、实际 v19 tag 已指向 workflow 提交等旧 commit、已有同名资产内容不同或上传不完整，都会停下。它们是有意的冲突保护。不要提前创建实际 v19 tag；完整包上传中断时，先定位实际不完整资产再做具体修复，不能整体 clobber。

## 权限与外部依据

GitHub 官方说明，当 release 的目标相对默认分支修改 workflow 文件时，会额外要求 workflow 写权限。当前顺序先把最终提交 push 到 main，再以同一 commit 更新 release；在这个既定状态下没有此类差异。此次未探测 runner 的真实写权限。

官方参考：

- https://cli.github.com/manual/gh_release_upload
- https://cli.github.com/manual/gh_release_edit
- https://docs.github.com/en/rest/releases/releases?apiVersion=latest
- https://docs.github.com/en/rest/releases/assets

本结论绑定同名 JSON 所列四份实际源码 SHA-256。最终 overlay、真实新版 manifest、runner 结果和远端树仍须由主流程核验；不能由这次只读复查宣称发布完成。
