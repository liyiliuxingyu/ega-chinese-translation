# 最终候选工程：独立全量恢复与保留性检查

检查时间：2026-11-21T09:15:30.713590+00:00。

**本轮全部通过。** 这次执行了实际恢复，并直接读取最初三个 ZIP 的每个普通成员作路径、字节、SHA-256 对照，没有沿用此前候选映射的检查结果。未编辑包内文件，未编译 TeX，未重审数学证明。

## 被核验的候选快照

- 包目录：`release_20261121/EGA_20261121_Dot_handover`。
- 清单 SHA-256：`613a21d35cc9b178e226f36c8f218399e0363a66d8dacd0212b88adead4269ee`。
- 恢复索引 SHA-256：`0ba618f7d9b590fd93ac9b9a54e0f2158eeeee61a272301d5b837b2aaf4c5ab4`。
- 初次及恢复后均实际执行 `python3 verify_package.py --strict --json`，结果均为通过：**1,661 个清单载荷、565,115,004 字节，无额外普通文件**。
- 两次严格检查的根清单散列一致，恢复索引散列也一致，说明本轮试验期间所用包快照未变。

该散列标识的是本轮测试的暂行清单。整合者计划随后把历史指针从现行可编辑源码移入不可变内容区，并加入检查报告后刷新清单；这些变更之后不得把本轮的清单散列称为最终新清单散列。

## 三个版本实际恢复

先确认 `integration_20261121/restore_tests` 不存在，然后新建父目录。每个版本使用此前不存在的独立目标目录运行：

```sh
python3 restore_versions.py --version VERSION --destination EMPTY_DIRECTORY --strict --json
```

脚本实际复制并再次读取全部恢复文件。随后，本独立检查重新打开最初 ZIP，用逐块字节比较并分别计算原 ZIP 解压流与恢复文件的 SHA-256；同时检查恢复文件路径集合没有遗漏或额外文件。每个 ZIP 成员均完整读到结束，原成员 CRC 随读取校验。

| 版本 | 原 ZIP 普通成员 | 原始字节一致 | SHA 一致 | 恢复字节数 | 路径集合完全相同 |
|---|---:|---:|---:|---:|---|
| `v17` | 1,827 | 1,827 | 1,827 | 547,998,859 | 是 |
| `supplement_III` | 753 | 753 | 753 | 344,168,141 | 是 |
| `supplement_III_delta` | 40 | 40 | 40 | 33,175,272 | 是 |

实际恢复根目录分别是：

- `integration_20261121/restore_tests/v17/EGA_v17_handover`
- `integration_20261121/restore_tests/supplement_III/EGA_v17_V_supplement_III`
- `integration_20261121/restore_tests/supplement_III_delta/EGA_v17_V_supplement_III_delta`

原 ZIP 外层文件也独立重算了大小和 SHA，均与恢复索引记录相符：

- `v17`：`f11fa64ad6c3632b09b7379abb99b01b9b72f84cbf65e730d1e74319585295e8`；493,141,776 字节。
- `supplement_III`：`050be3e6625f0749205531c085aa8cc757432bc5a46bdcd003430c0e4a7b3b8d`；313,603,196 字节。
- `supplement_III_delta`：`28de61871669e470d0d3d4e78269ee3742852418cfc563261486ee14b8979cae`；30,152,476 字节。

这里恢复的是普通成员路径与完整字节；没有重新生成原 ZIP 容器，不保证重建原 ZIP 的压缩元数据、文件时间戳或权限。

## Dot 原件和索引

`05_Dot/DOT_BATCHES_COMBINED.json` 实有 **75 条、75 个唯一 ID**，分为 56 条旧批次和 19 条新增批次。

- **75/75** 的 `packaged_source_path` 指向实际存在的源稿，实测 SHA 与索引的 `source_tex_sha256` 一致。
- **75/75** 同时与原始来源相符：旧 56 条对照恢复基线源稿，新增 19 条直接读取实取原 ZIP 内登记的主 TeX 成员核对。
- **75/75** 的 `current_project_input` 指向实际存在的当前工程文件。此项仅证明路径存在，不能由此推断数学证明已经审定。
- 原基线 `05_Dot` 的 **364 个普通文件**全部在候选包的同相对路径保留，并逐字节及 SHA 比较通过。新增内容没有覆盖旧目录载荷。
- 新增 **19 个 ZIP**逐字节比较候选包中原件与 `recovered_20261121/dot_new` 的实取文件，**19/19 通过**，索引所列 ZIP SHA 也全部相符。

没有将批次标签 50–68 当成全工程累计批次数，也没有把源文件数当成定理数或完成的数学核验量。

## 证据文件

- `final_preservation_check.json`：本轮完整摘要、范围和限制。
- `final_strict_verify_initial.json`、`final_strict_verify_after_restores.json`：两次根严格校验原始结果。
- `restore_v17_cli.json`、`restore_supplement_III_cli.json`、`restore_supplement_III_delta_cli.json`：实际恢复程序的输出。
- `final_restore_members_v17.json`、`final_restore_members_supplement_III.json`、`final_restore_members_supplement_III_delta.json`：每个 ZIP 成员的独立字节与 SHA 对照。
- `final_dot_75_source_checks.json`：75 条索引逐条核验。
- `final_old_Dot_364_checks.json`：旧 Dot 364 文件逐条核验。
- `run_final_preservation_check.py`：独立对比脚本。它读取已经完成的恢复目录和原 ZIP，不会编辑候选包。

## 后续清单变更的界限

本轮没有发现载荷丢失、字节差异或索引源稿失配。整合者提出的不可变内容调整仍应完成，以免日后编辑当前 `.tex`、`.py`、`.sh` 等文件后影响旧版本恢复。调整会改变恢复索引及根清单，故应另行记录调整后的严格核验和实际恢复结果。本轮结果应保留为已完成试验的证据，不能不加说明地套用到另一份清单。
