# 包校验与历史文件恢复

这些脚本只使用 Python 标准库，需要 Python 3.9 或更新版本。把以下四个文件放在最终包根目录并保持同级：

- `verify_package.py`
- `refresh_manifest.py`
- `restore_versions.py`
- `package_common.py`

现行工程已经完整展开在 `01_project/EGA_v17`。接续翻译可直接进入现行工程，按当前进度和构建说明操作。历史恢复用于取得旧版本的原路径、原字节文件。

## 校验当前包

在包根目录执行：

```sh
python3 verify_package.py --strict
```

也可从任意位置指定包根，取得 JSON 结果：

```sh
python3 /path/to/package/verify_package.py --root /path/to/package --strict --json
```

校验器只读，逐项检查路径、普通文件类型、字节数和 SHA-256；同时校验 `MANIFEST.json` 自身在 `SHA256SUMS.txt` 中的散列，以及两个清单的条目集合是否一致。重复条目、重复 JSON 键、路径穿越、绝对路径、反斜线、盘符及流路径均拒绝。文件名还拒绝控制字符、行分隔符、末尾空格/点、Windows保留设备名及该系统不支持的特殊字符，避免跨平台重解释路径。包内符号链接、可识别的 Windows 重解析点和特殊文件即使未列入清单也会被拒绝。

`--strict` 还拒绝清单外的普通文件。不加此选项时，清单外普通文件会列在结果中，不因此返回失败。空目录不计入普通文件清单。成功返回退出码 0，校验失败返回 1，命令行参数错误返回 2。

清单约定：

- `MANIFEST.json` 的 `files` 记录包内全部普通文件，但不含包根的 `MANIFEST.json` 和 `SHA256SUMS.txt`。
- `SHA256SUMS.txt` 记录上述所有载荷文件，加上 `MANIFEST.json`；它不列自身。
- 清单内路径使用 UTF-8、规范相对 POSIX 路径，散列使用小写十六进制。

散列检查能够判断当前文件是否与清单相符。它本身不证明数学正确、翻译完整、编译成功或来源真实性。

## 刷新清单

在已完成必要的内容核查、编译和发布步骤后执行：

```sh
python3 refresh_manifest.py
python3 verify_package.py --strict
```

刷新器会重新读取当前普通文件，写出新的 `MANIFEST.json` 和 `SHA256SUMS.txt`。**刷新散列只记录当前字节，不是数学校验或译文核查，也不会替用户选择正确的现行成品。** 它不改正文、PDF、进度或恢复索引。执行期间应保持包内容不变；两张清单分别替换，其他进程不应在替换过程中读取并发布此包。

## 查看与恢复历史版本

版本键从 `04_history/RESTORE_INDEX.json` 动态读取，支持其中登记的安全键；不限于下列示例：

```sh
python3 restore_versions.py --list
python3 restore_versions.py --version v17 --destination /path/to/empty-v17 --strict
python3 restore_versions.py --version supplement_III --destination /path/to/empty-supplement --strict
python3 restore_versions.py --version supplement_III_delta --destination /path/to/empty-delta --strict
```

目标目录须为空，或尚不存在但其父目录已经存在。目标须位于包外。脚本会在该目标下创建索引给定的 `root_name`，然后按每项 `original_path` 写入文件。来源按 `stored_path` 从新包读取，因此可以复用现行文件或 `04_history/content/<SHA前两位>/<SHA>` 中的去重载荷。

复制前，脚本先校验包，核对该版本所有记录与包清单一致，再创建目标。写文件采用排他创建，不覆盖已存在文件；路径穿越、链接、文件与目录路径冲突及非空目标均拒绝。复制完成后，再次从磁盘读取全部恢复文件，复算字节数和 SHA-256。

若复制阶段因磁盘或其他错误中止，脚本返回失败，并报告本次创建的部分恢复目录；它不自动删除或覆盖该目录。处理后应另选空目标重新恢复。执行恢复时，也应保持来源包和目标目录不受其他程序修改。

**恢复保证的对象是原 ZIP 中登记的全部普通文件的原路径与原字节。脚本不重建原 ZIP 容器字节，不生成与旧 ZIP 相同散列的压缩包，也不重建 ZIP 顺序、压缩参数、空目录、文件时间或权限等容器属性。** 索引中的原 ZIP 文件名、大小和散列是原容器的出处元数据，不能当作重新生成 ZIP 的校验值。目标文件系统须能保存原文件名。

## 小型合成测试

若保留 `test_package_tools.py`，可执行：

```sh
python3 test_package_tools.py
```

测试使用自行创建的临时目录，覆盖普通恢复、第三种动态版本键、完整清单检查、字节篡改、清单篡改、缺失/额外文件、重复条目、路径穿越、链接、特殊文件、非空目标、目标位于包内及恢复索引不一致等情形。它不替代最终实际包的完整校验和各版本全量恢复试验。
