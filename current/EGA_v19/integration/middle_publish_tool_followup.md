# 发布工具修订复核

## 结论

原审阅的 PUB-M-01（打包路径/链接校验）与 PUB-M-02（回执幂等分支提前成功）均已在本次所读代码中解决。针对这两项的只读复核未发现新的阻断问题。原审阅文件保持不变。

## 当前代码散列

- `tools/apply_edition18_update.py`：`b8f5d3a65bb32b097e5cc9a19f4411b5b700e690e5421334e4611aec7a19ea3f`（8739字节）。
- `tools/package_edition18.py`：`2aa0ca2101e57680b7f08504c2456a4c855230a8f91a2c0cdd8571d701b5681e`（6577字节）。

## 修订证据

- **PUB-M-01**：package safe_name rejects noncanonical/absolute/parent/.git/backslash paths; safe_file rejects file or ancestor symlinks and requires resolved containment. pack rejects duplicate inputs and unsafe output member names; fixed exports must appear in the verified manifest; publication metadata is an exact four-name allowlist.
- **PUB-M-02**：apply records already_applied without returning. Archive SHA, member count/size and manifest payload checks run first. Same-SHA branch additionally compares current manifest bytes with archive manifest bytes, hashes all current payload files after rejecting symlinks, runs verify_repository.py --strict, then returns without writing.

## 实际检查与界限

两份源码均通过Python语法解析。只运行了不写文件的路径谓词案例，确认绝对路径、`..`、非规范分隔、反斜线与`.git`均被拒绝；另外对打包器的safe_file调用确认三种不安全路径被拒绝及工具文件自身可读。没有执行导入、成包或GitHub操作。

- This is not an execution of the full publication workflow or a final overlay/ZIP validation.
- verify-only still intentionally omits Git ancestry and previous-manifest preservation guards; its result is limited to archive/reconstructed byte checks.
- Final package self-containment and immutable raw-byte retention must still be confirmed against the final generated manifest and real output ZIPs.

此结论仅适用于上列代码散列；最终overlay及真实ZIP仍由全量执行检查确认。
