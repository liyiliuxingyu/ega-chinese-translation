# 第十八版发布工具只读审阅

本记录针对以下源文件哈希，随后若修改应重新检查。

- `tools/apply_edition18_update.py`：`eaa0601c3f1b812761e517e90e26600a9415598e41568b320ee945f4b35eec36`
- `tools/package_edition18.py`：`cba8dd2cd4a93278462acdacf4c7d17e322d058a719ad8d5213491d740aa7a7d`

## 结论

正常首次应用路径未发现会改写原archive/Dot或遗漏旧清单payload的问题。发布前应补包生成器的路径/链接检查，以及receipt幂等分支的字节复核。

## 具体事项

### PUB-M-01

`tools/package_edition18.py`：pack/manifest/allowed_publication_metadata缺少规范相对路径与父目录符号链接检查；前缀匹配不排除current/EGA_v18/../../x，从而可读取工程外文件并创建含..的ZIP条目。重复项目清单项也未先拒绝。

建议：统一验证非空规范PurePosixPath、非绝对/无..、拒绝.git、反斜线、每级符号链接及重复项；四个固定成品必须列于已验证清单。

### PUB-M-02

`tools/apply_edition18_update.py`：同SHA receipt分支在本次归档SHA或当前payload核验之前返回0，不能证明当前工程仍与已应用快照一致。

建议：同overlay SHA仅改变不再写入的策略；仍验证归档SHA及当前新清单的全量字节，失败则报告损坏。

## 已有守卫

- 首次apply仅允许根文档、新current/snapshots及两工具路径，不允许直接写archive_20261121或dot_updates_20261124。
- 首次apply在所有写入前校验所有新清单文件的字节，并要求旧清单所有payload行保留且除允许根文档外完全相同。
- 首次apply要求基线为HEAD祖先，基线到HEAD差异仅为发布workflow且工作树干净。
- package对已写ZIP全部成员重新读取校验大小、SHA和CRC，不仅依赖ZIP成功关闭。

## 待最终工作流与包验证的条件

- 新工作流应在RUNNER_TEMP执行提取的导入器，避免预先把新工具写进checkout导致dirty守卫阻止导入。
- 最终清单需要允许旧两项publication metadata和新workflow、EDITION_18_IMPORT.json；当前清单还是v17的2346项，尚未生成v18清单。
- verify-only跳过Git与旧清单保留守卫，结果仅表明归档和拼合后仓库字节预检；不能称实际应用或全部安全检查。

当前项目README正确区分可独立构建源码工程与含原著/Dot/历史的完整仓库包；实际完整v18清单、全局输入闭包与两个最终ZIP仍待父代理生成和运行验证。未修改脚本、原包、源码或访问GitHub。
