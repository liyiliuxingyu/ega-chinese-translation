# 第二十版入口与冻结器只读复核

日期：2026-11-25。审查对象为仓库根 `README.md`、`AGENTS.md`、`CONTINUE_HERE.md`，以及 `current/EGA_v20/recollation/engineering/freeze_edition20_delivery.py`。未修改这些文件，未执行冻结器，也未扩大样例测试。

## 结论

**入口文档与冻结器逻辑审查通过，未发现实质不一致。** 本次结论只覆盖实际读取的文档、脚本及所列配置比较，不表示已经执行正式冻结或发布。

三个入口均把本轮完成位置限定为第五卷预备笔记第一篇§12的法英回校，而非全书译稿终点；同时明确§13旧译、§§14—15及其他已译材料继续保存和输入。默认下一回校点一致为法稿物理74页／英编稿49页的§13标题及定义13.1。正式第IV章另作为未连续译入的分支，接于 EGAIV.1 物理221页提要、222—223页章首及223页(1.1.1)；根AGENTS采用221—223页的简写，没有改变这条分支。三文档也保留全部书籍及未证推广未完成的边界。

## 冻结器与已审更新器的对应

- `BASE` 与更新器的 `BASE_COMMIT` 同为 `997597a5476cb07338a9b2feef61077ae795774e`。
- 新目录 `current/EGA_v20/`、`snapshots/20261125-v20/` 与更新器允许前缀一致；两个新工具名称一致。
- 十项 `METADATA` 与更新器的 `PUBLICATION_METADATA` 集合完全相同，保留基线八项并增加本版工作流与回执。
- 三个可替换根文档对应更新器的根更新项；根 `REPOSITORY_MANIFEST.json` 由冻结器另行生成并在映射完成后加入 ZIP，不进入其自身 `files`，与更新器的自引用排除规则一致。
- 旧清单的全部记录先保留；已在本地展开的旧文件逐项核对大小与哈希，旧根文档改为核对 snapshot 中的原件。未展开的旧文件明确递延到 runner，不冒称已在本地验证。
- 新选取路径若已在旧映射中且不是指定根文档，则报 `Unapproved overwrite`。既有 payload 不因新版本而改写；完整历史的最终字节核验仍由更新器在真实 checkout 上强制执行。
- 冻结器要求结构检查、构建日志检查、PDF逐页一致性和视觉汇总四份记录的 `pass` 严格为 `true`，并额外要求 `status=build_and_review_verified` 与 `all_books_finished=false`，没有由“构建成功”推断全部书籍完成。

实际只读取得的 `snapshots/20261125-v20/REPOSITORY_MANIFEST.json` 与 `git show 997597a5476cb07338a9b2feef61077ae795774e:REPOSITORY_MANIFEST.json` 字节相同，其 SHA-256 为 `0d710ced118a6562625cdbfd4e6ad35fb01860e052611507e37ae4da1b522a32`。

## 读取时点的门禁状态

首次检查时，`current_structure_verification.json`、`current_build_log_summary.json`、`current_pdf_parity.json` 均存在，且读取到 `pass=true`；`visual_verification_summary.json` 和 `HANDOVER_STATE.json` 尚未落盘。此情况已即时告知主流程：当时直接运行冻结器会先在第四门禁处退出，是预期的阻止行为。主流程须完成这两份最终记录后再冻结。

这段只记录审查当时的状态，不把它当成后续最终交付状态；最终是否落齐、门禁是否实际通过及冻结是否执行，应以最终文件和冻结输出记录为准。本次仅读取既有门禁结果，没有重跑或代签这些检查。

## 实际读取版本的 SHA-256

| 文件 | SHA-256 |
|---|---|
| 根 `README.md` | `97f260fba4208b290cf7f05346359cb4cbe860734a7c93545ab5a05e65f76bf5` |
| 根 `AGENTS.md` | `afad527051eb996f49b92f7ca8ba9ef65e568d11ce24a615c13fac76e9de3621` |
| 根 `CONTINUE_HERE.md` | `e1a623d07bb7fca042897f7d7d8748d8d6c67480abad3ac8f4c5d6588f00933b` |
| `freeze_edition20_delivery.py` | `dd516f329fa144063935491f8ffd9f85d64905af9bda01222700908e709b0218` |

以上指纹限定本次审查对象。没有修改被审文件、旧 payload 或发布模板，没有运行更新、上传、Git提交或发布。
