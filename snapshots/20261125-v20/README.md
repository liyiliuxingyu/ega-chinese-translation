# EGA 中文译校工程（包括 Dot）

本仓库保存本对话及 **Dot 中可恢复的 EGA 译校工程**：合订译稿、模块与单文件 TeX、累计核查报告、原始底本、逐批工程、校验记录和历史恢复资料。2026-11-25上传复查补入15个旧合订工程原ZIP和Dot109—119批11个原ZIP；另7个早期独立卷册原ZIP无法恢复，具体范围见下方核查报告。

**当前工作版本为第十九版，日期为 2026-11-25（北京时间）。** 本版以第十八版为基线，逐段对读第五卷预备笔记第一篇 **8.14 至第 11 节末**。原已收入的 Dot69—108 共40批以及较早全部已译内容继续保存。本工程仍是已译内容的工作合订稿，**不是全部书籍已完成的声明**。

## 2026-11-25 归档补充

本次归档补充标签为 `v19-archive1-20261125`，不增加翻译版号。现行1214页主稿和389页报告及其源码保持原字节。

- [漏传核查报告](archive_supplement_20261125/AUDIT_REPORT.md)：查出的遗漏、实际补入内容及7个不可恢复原包。
- [26个补充原包的完整索引](archive_supplement_20261125/ARCHIVE_INDEX.json)：15个第1—15版旧工程和11个Dot新批次。
- [归档补充发布](https://github.com/liyiliuxingyu/ega-chinese-translation/releases/tag/v19-archive1-20261125)：更新的完整库包、仅补充包与核验记录。

Dot109—119以独立工程身份保存，未据此改写合订稿已完成范围。下一轮整合§12时先读取117—119批；独立119批下一位置是法71页末／英47页，合订稿整合入口仍是法64页§12／英43页。

## 当前成品与源码

| 内容 | 文件或入口 |
|---|---|
| 合订译稿 PDF | [current/EGA_v19/main.pdf](current/EGA_v19/main.pdf) |
| 合订译稿单文件 TeX | [current/EGA_v19/single.tex](current/EGA_v19/single.tex) |
| 累计核查报告 PDF | [current/EGA_v19/report.pdf](current/EGA_v19/report.pdf) |
| 报告单文件 TeX | [current/EGA_v19/report_single.tex](current/EGA_v19/report_single.tex) |
| 可构建模块工程 | [current/EGA_v19/README.md](current/EGA_v19/README.md) |
| 真实进度、状态、散列 | [PROGRESS.md](current/EGA_v19/PROGRESS.md) · [HANDOVER_STATE.json](current/EGA_v19/HANDOVER_STATE.json) · [ARTIFACTS.json](current/EGA_v19/ARTIFACTS.json) |
| 新对话接续 | [CONTINUE_HERE.md](CONTINUE_HERE.md) |
| 原文映射、未决项 | [SOURCE_MAP.md](current/EGA_v19/SOURCE_MAP.md) · [PENDING_ISSUES.md](current/EGA_v19/PENDING_ISSUES.md) |

正式发布的PDF、TeX、当前工程、包含全部原底本/Dot/历史的完整续作包及SHA-256校验表见 [Releases](https://github.com/liyiliuxingyu/ega-chinese-translation/releases)。当前项目包可重建译稿；继续校勘原文时应取得完整仓库或完整包。旧版本及原包不被新版覆盖；可恢复的历史范围和原容器缺失边界见归档核查报告。

## 本版做了什么

- 对读法稿物理46页下部至63页、英文32至43页第12节以前；按段替换对应旧译。
- 恢复8.17手写补充、第9节析取词、第10节不等号与零点概形、第11节被英译漏掉的完整条件。
- 给出8.16弱非分歧条件、8.18仅不可约特殊截面、一般线性系固定分支及9.3缺条件的明确反例；正文采用有依据且说明范围的表述，原说法及证明另有完整保存。
- 区分作者原错、英译误读、作者删稿和译者补证；撤销若干旧报告对法稿缺条件的不准确归责。
- 保留所有其他已译正文、全部Dot档案及历史核查报告。来源对读与技术检查记录见当前项目的`recollation/`、`checks/`。

这次是已有译稿的继续严谨回校，不把已整合的40批重复计为新译。编译与散列校验也不能代替数学审定。

## 真实接续位置

**第五卷第一篇下一处：法稿 `EGA5_francais.pdf` 物理第64页 §12，对读 `EGAVaiello.pdf` 物理第43页中段。** 既有译文位于`continuations/v_dot_middle.tex`，必须先读其实际末项和未决注记，再按原文回校。§§12—15已经有旧译，不应截断或假称不存在。

英文底本实际112页，末页书信已收入；法文扫描171页，末为二次型附录。到达英文末页不表示法稿全页已逐行审结。9.5仍无完整结论，8.8完整起首等缺文仍在；详见未决事项。

**正式第IV章主体仍未连续译入。** 另一分支从`EGAIV.1.pdf`物理221页内容提要、222—223页章首说明及223页(1.1.1)接续。第0章§§14—23及预备手稿拟定章号不能替代它。用户另有明确分支要求时遵其指示。

## 已保存的档案

| 路径 | 内容与身份 |
|---|---|
| `archive_supplement_20261125/` | 本次恢复的15个旧合订工程原ZIP、Dot109—119批11个原ZIP及漏传核查证据 |
| `current/EGA_v19/` | 本版工作源码、PDF、累计报告及实际检查证据 |
| `current/EGA_v18/` | 前一公开版本，完整保留不回写 |
| `archive_20261121/` | 2026-11-21完整续作工程原件及第十七版等历史 |
| `dot_updates_20261124/` | Dot原批号69—108的40个原ZIP及展开内容；这些内容已收入正文相应位置 |
| `archive_20261121/05_Dot/` | 先前75个来源批次及历史Dot原始归档，各编号序列原样保留 |
| `archive_20261121/03_sources/` | 13份原底本：I、II、III.1、III.2、IV.1—4、第五卷法英稿及三份PS |
| `snapshots/20261124/`、`snapshots/20261125/` | 各次更新前的根说明与清单原件 |
| `archive_20261121/04_history/RESTORE_INDEX.json` | 历史普通文件恢复映射及逐文件散列 |

旧75批与后来40批是来源档案计数，不能换算为独有译文量或已审命题数。历史Dot总归档还含其他数学项目附件，为恢复历史原样保留，未收入EGA正文。仓库入口不含聊天全文。

第I章既有源码至(10.15.7)，第II章至(8.14.14)，第III章两分册合接至(7.9.14)，第0章至(23.2.10)(ii)及原“待续”；已有书末资料继续保留。本轮没有重新逐卷审定这些内容。

## 核验与重建

先核验原始交付快照：

```bash
python3 tools/verify_repository.py --strict
```

随后复制当前项目到新目录重建，保持交付快照不变：

```bash
python3 -c 'from shutil import copytree; copytree("current/EGA_v19", "../ega-v19-work")'
cd ../ega-v19-work
bash build.sh --verify-single
python3 checks/check_current_project.py
python3 checks/check_current_build_logs.py
python3 checks/compare_current_pdfs.py
```

使用真实`ctexbook`默认字体和正文版心。需要Bash、Python、XeLaTeX及相关宏包；逐页比较需PyMuPDF，列明的精确计算需SymPy。项目附有CTeX/Fandol及许可，不声称附带完整跨平台TeX发行版。单文件TeX不依赖外部正文输入，仍依赖TeX宏包和默认字体。

离开完整仓库后，结构检查会明确记录未在本地重新读取前一版；不能冒称完成原件对照。修改源码后必须实际构建、查看变动页并更新进度，不能只刷新散列。自动逐页比较检验模块版和单文件版输出，不表示全部页面均人工校勘。

历史恢复：

```bash
python3 archive_20261121/restore_versions.py --list
python3 archive_20261121/restore_versions.py --version v17 --destination ../ega-v17-restored
```

目标须为新目录或空目录。恢复工具核对所列普通文件字节，不承诺重造原ZIP容器的相同字节。常规续作用`current/EGA_v19/`。
