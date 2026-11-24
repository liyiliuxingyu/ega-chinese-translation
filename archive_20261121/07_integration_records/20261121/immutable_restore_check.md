# 不可变历史内容调整后的独立恢复复核

检查时间：2026-11-21T09:19:28.261493+00:00。

**本轮全部通过。** 三个版本均重新实际恢复到新的空目录，并逐文件与前轮已直接匹配原 ZIP 成员的恢复物比较；没有重复读取同一原 ZIP 的 CRC 流。未编辑包内文件，未编译 TeX。

## 被核验的候选快照

- 包目录：`release_20261121/EGA_20261121_Dot_handover`。
- 根清单 SHA-256：`f82d0f046d9c6681bc2f102c03969fd3234b98446ed1084c7567e60c9f6d95e7`。
- 当前恢复索引 SHA-256：`a8391e069aa02a2c60bb8453ab256d22c7a1f4a7397e72d953ef32491b581aa0`。
- 调整后，初始及恢复结束时两次实际执行 `verify_package.py --strict --json`，均通过：**1,792 个清单载荷、572,104,812 字节、无额外文件**。
- 新恢复目录为 `integration_20261121/restore_tests_immutable/<version>/<原根目录名>`；父目录此前不存在，三个版本使用各自此前不存在的空目标。

## 历史索引的调整范围

原索引的 **2,620 条**记录（1,827＋753＋40）与新索引逐条比较，`original_path`、`bytes`、`sha256` 全部不变，版本根目录及原件仍按相应恢复程序核对。

本次有 **365 条历史引用**改指向 **130 个不可变内容对象**，合计 **6,818,839 字节**。实际观察的新旧索引差异与调整记录完全相符；130 个对象均实际读取核验大小及 SHA。

为独立确认旧索引，本检查把新索引中的 365 条 `stored_path` 按变更记录反向恢复，并去掉新增的两项政策元数据。所得序列化字节的 SHA-256 为：

`0ba618f7d9b590fd93ac9b9a54e0f2158eeeee61a272301d5b837b2aaf4c5ab4`

它与前轮实际记录的旧恢复索引 SHA 精确相同。由此对照的是同一份旧索引内容，而非仅相信“旧路径未变”的文字声明。核实后的旧索引保存在 `restore_index_before_immutable_verified.json`。

当前恢复索引中，指向 `01_project/EGA_v17` 而又不属于 `vendor`、`history`、`checks` 的活动文件引用数为 **0**，涵盖活动 TeX、脚本、状态文件及成品。日后续译改写这些活动文件时，历史版本依赖的是已冻结的相同字节对象。

原底本、Dot 原始资料以及标明为历史或依赖的共享目录仍需保持原件不变；若需要改动它们，应在副本上工作。

## 再次实际恢复与逐字节比较

三个 `restore_versions.py --strict --json` 调用均成功，程序内部对每个恢复文件再次读取核验。随后独立脚本同时检查两轮恢复的路径集合，逐块比较两轮文件字节，分别重算 SHA，并对照前轮从原 ZIP 成员记录的 SHA 与大小。

| 版本 | 本轮实际恢复文件 | 两轮逐字节一致 | 对应原 ZIP 记录一致 | 本轮恢复字节数 |
|---|---:|---:|---:|---:|
| `v17` | 1,827 | 1,827 | 1,827 | 547,998,859 |
| `supplement_III` | 753 | 753 | 753 | 344,168,141 |
| `supplement_III_delta` | 40 | 40 | 40 | 33,175,272 |

三组路径集合全部一致，零缺失、零额外文件、零字节差异。前轮的原 ZIP 直接比较仍由 `final_preservation_check.json` 和逐成员记录提供证据；本轮通过重新读取的旧恢复物来确认没有证据链断裂。

## 证据文件

- `immutable_restore_check.json`：本轮摘要、索引对比、实际恢复结果和限制。
- `immutable_strict_verify_initial.json`、`immutable_strict_verify_after_restores.json`：前后两次严格校验输出。
- `immutable_restore_v17_cli.json`、`immutable_restore_supplement_III_cli.json`、`immutable_restore_supplement_III_delta_cli.json`：实际恢复调用输出。
- `immutable_restored_members_v17.json`、`immutable_restored_members_supplement_III.json`、`immutable_restored_members_supplement_III_delta.json`：2,620 个文件的独立比较结果。
- `immutable_object_checks.json`：130 个冻结对象的实际尺寸和 SHA 核对。
- `immutable_restore_index_snapshot.json`：本轮新索引快照。
- `restore_index_before_immutable_verified.json`：经已记录 SHA 认证的旧索引重建结果。
- `run_immutable_restore_check.py`：读取两轮恢复物及新旧索引的复核脚本。

## 过程记录与边界

根代理告知，期间曾短暂增加并移除了三份封包证据文件。本检查的各次严格调用均通过，没有观察到额外文件报错，也没有为隐藏失败而重跑；结束时的严格检查确认没有额外文件残留。两端快照相同不用于声称整个检查期间从未发生过任何短暂目录变化。

本轮证明文件路径和字节的恢复保留性，不证明全书翻译完成或所有数学论证正确。恢复程序还原普通成员文件，不重建原 ZIP 容器的压缩元数据、时间戳或权限。最终加入本报告和摘要后应刷新并再次核验根清单；上述清单散列始终仅指本轮已经实测的候选快照。
