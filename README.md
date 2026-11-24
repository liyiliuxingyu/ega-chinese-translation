# EGA 中文译校工程（含 Dot）

本仓库保存本对话及 **Dot 中的 EGA 译校工程**：当前合订译稿、可重建的模块与单文件 TeX、累计核查报告、原始底本、逐批工程、校验记录和历史恢复资料。

**当前工作版本为第十八版，日期为 2026-11-25（北京时间）。** 先前另存的 Dot 原批号 69—108 共 40 个工程包已经按原著位置整合；回校段替换对应旧段，后续译文继续保留。本轮另据法文物理 126、136、140 页补译了三块可辨删划草稿。确切范围与实际技术检查结果见当前工程的状态文件。此版本仍是已译内容的工作合订稿，**不是全部上传书籍的完结全译本**。

## 当前成品与源码

| 内容 | 文件或入口 |
|---|---|
| 合订译稿 PDF | [current/EGA_v18/main.pdf](current/EGA_v18/main.pdf) |
| 合订译稿单文件 TeX | [current/EGA_v18/single.tex](current/EGA_v18/single.tex) |
| 累计译校核查报告 PDF | [current/EGA_v18/report.pdf](current/EGA_v18/report.pdf) |
| 报告单文件 TeX | [current/EGA_v18/report_single.tex](current/EGA_v18/report_single.tex) |
| 可构建模块工程 | [current/EGA_v18/README.md](current/EGA_v18/README.md) |
| 实际进度及成品散列 | [PROGRESS.md](current/EGA_v18/PROGRESS.md) · [HANDOVER_STATE.json](current/EGA_v18/HANDOVER_STATE.json) · [ARTIFACTS.json](current/EGA_v18/ARTIFACTS.json) |
| 新对话接续 | [CONTINUE_HERE.md](CONTINUE_HERE.md) |
| 原文映射与未决事项 | [SOURCE_MAP.md](current/EGA_v18/SOURCE_MAP.md) · [PENDING_ISSUES.md](current/EGA_v18/PENDING_ISSUES.md) |

下载工程时，当前项目包用于重建本版；**完整工程包**还包含全部已恢复原底本、Dot 原包、历史版本及本版工程。原文校勘应使用完整仓库或完整包。各次正式发布的文件与 SHA-256 校验表见仓库 Releases；保留前一公开快照，不用新版覆盖旧档案。

## 这次接入的内容

| 原批号或来源 | 第十八版中的处理 |
|---|---|
| Dot 69—72 | 接入附录 17.16：光滑二次型，16.1—16.14及作者按语 |
| Dot 73—85 | 接入第三篇：射影丛、多重射影丛、相对除子、伪态射及线性系，至命题4.4和篇末说明 |
| Dot 86 | 收入1965年9月29日致迪厄多内的信，单独标明信中删段 |
| Dot 87 | 收入法文物理150页手写提纲和153页异扫说明；同文不在正文重复排印，完整对照保留在报告 |
| Dot 88—108 | 替换第一篇§§1—7及8.1—8.13的对应旧段；8.14以后已有正文继续保留 |
| 本轮新增补译 | 法文物理126、136、140页三块大叉删稿的可辨主体，单列为非定稿补遗，难辨部分明确标出 |

40批是恢复的原工程数量，不能当作本轮从头新译的章节数。原批次长篇补证与独有旧译注保留在累计报告，逐批去向在 [integration/](current/EGA_v18/integration/) 记录。本轮对关键异文和错误作定点原页复核及明确计算，没有声称重新独立证明全部原有命题。

## 真实接续位置

**第五卷第一篇最新法英回校到命题8.13。** 下一从 `EGA5_francais.pdf` 物理46页下部“Combinant 8.13”及推论8.14接续，再接47页，对读 `EGAVaiello.pdf` 物理32页。8.14及其后文已有译稿，不应因回校点较早而截断总稿。

英文编辑稿实际有112页，末页书信已接入；法文扫描实际有171页，末页为二次型附录。英文没有第113页的续译点；到达英文末页也不能证明法文171页已经全部逐行校勘。

**正式第IV章主体仍未连续译入。** 另一分支从 `EGAIV.1.pdf` 物理221页内容提要、222—223页章首说明及223页(1.1.1)开始。第0章§§14—23和第五卷预备笔记的拟定章号均不能替代这一主体。用户若明确指定卷次或任务，以其指示为准。

8.7(c)的缺续、8.8工作假设的来源、8.13与8.14的依赖、7.4一般版本及其他原稿难辨与未证问题仍需逐项处理；详见当前未决事项。编译成功和散列相同都不是数学审定。

## 完整保存的档案

| 路径 | 内容与身份 |
|---|---|
| [current/EGA_v18/](current/EGA_v18/) | 当前整合源码、PDF、报告及本轮实际检查证据 |
| [archive_20261121/](archive_20261121/) | 2026-11-21完整续作工程原件；含第十七版1158页译稿、287页报告，保持原样 |
| [dot_updates_20261124/](dot_updates_20261124/) | 后来恢复的40个Dot原ZIP及展开内容，批号69—108；原文档的“未并入”等是当时状态 |
| [snapshots/20261124/](snapshots/20261124/) | 上次公开快照的根说明、接续规则和清单原件 |
| [archive_20261121/03_sources/](archive_20261121/03_sources/) | 13份原底本：I、II、III.1、III.2、IV.1—4、第五卷法英稿及三份PS |
| [archive_20261121/05_Dot/](archive_20261121/05_Dot/) | 先前75个来源批次及历史Dot原始归档，原编号序列各自保留 |
| [archive_20261121/04_history/RESTORE_INDEX.json](archive_20261121/04_history/RESTORE_INDEX.json) | 历史普通文件的恢复映射及逐文件散列 |

旧75批与后加40批是来源档案计数，不能换算为独有译文量或已审定命题数。历史Dot总归档还含其他数学项目附件，为恢复历史而原样保留，未收入现行EGA正文。仓库入口不包含聊天全文。

第I章既有正文至(10.15.7)，第II章至(8.14.14)，第III章两分册合接至(7.9.14)，第0章至(23.2.10)(ii)及原“待续”；相关已有书末资料保留。以上是继承源码范围，本轮没有重新逐卷审定。

## 核验与重建

先核验交付快照（Python 3.11或更新版本）：

```bash
python3 tools/verify_repository.py --strict
```

随后复制当前项目到一个新目录再重建，保留交付快照和原始档案：

```bash
python3 -c 'from shutil import copytree; copytree("current/EGA_v18", "../ega-v18-work")'
cd ../ega-v18-work
bash build.sh --verify-single
python3 checks/check_current_project.py
python3 checks/check_current_build_logs.py
python3 checks/compare_current_pdfs.py
```

项目采用真实 `ctexbook` 默认字体与版心。需要 Bash、Python、XeLaTeX及相关宏包；逐页比较需要PyMuPDF，精确二次型示例复算需要SymPy。随包保留CTeX/Fandol及许可，不宣称附带完整跨平台TeX发行版。单文件TeX不再依赖其他正文文件，但仍依赖TeX宏包和默认字体。

项目副本离开完整仓库后，结构检查会明确记录未在本地重新读取旧归档；这不妨碍构建，也不能冒称完成了原件核对。构建会生成临时文件，故严格快照核验应在构建前执行。修改源码后，必须重新展开、构建、查看实际页面并更新真进度，不能只刷新散列。

检查结果存于当前 [checks/](current/EGA_v18/checks/)，源文件改动与迁移在 [integration/](current/EGA_v18/integration/)。自动逐页比较只比较模块版与单文件版输出，不表示每页均经人工审校。

## 历史恢复

```bash
python3 archive_20261121/restore_versions.py --list
python3 archive_20261121/restore_versions.py --version v17 --destination ../ega-v17-restored
```

目标须为新目录或空目录。该工具恢复清单所列普通文件并核对字节，不承诺重新生成原ZIP容器的相同字节。正常续作使用 `current/EGA_v18/`，无需先恢复旧版。
