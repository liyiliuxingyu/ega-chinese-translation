# EGA 中文译校工程（包括 Dot）

本仓库保存本对话及 **Dot 中可恢复的 EGA 译校工程**：合订译稿、模块及单文件 TeX、累计核查报告、原始底本、逐批工程、校验记录和历史恢复资料。

**当前工作版本为第二十版，日期为 2026-11-25（北京时间），入口为 `current/EGA_v20/`。** 本轮完整回校第五卷预备笔记第一篇§12；下一实际位置为法稿物理74页／英编稿49页的§13标题及定义13.1。这是已有译稿的逐段回校、缺漏恢复和订正。全部书籍及所有未证推广尚未完成。

## 当前成品与源码

| 内容 | 入口 |
|---|---|
| 合订译稿 PDF | [current/EGA_v20/main.pdf](current/EGA_v20/main.pdf) |
| 合订译稿单文件 TeX | [current/EGA_v20/single.tex](current/EGA_v20/single.tex) |
| 累计核查报告 PDF | [current/EGA_v20/report.pdf](current/EGA_v20/report.pdf) |
| 报告单文件 TeX | [current/EGA_v20/report_single.tex](current/EGA_v20/report_single.tex) |
| 可构建工程及依赖说明 | [current/EGA_v20/README.md](current/EGA_v20/README.md) |
| 真实范围与核验结果 | [PROGRESS.md](current/EGA_v20/PROGRESS.md) · [HANDOVER_STATE.json](current/EGA_v20/HANDOVER_STATE.json) · [ARTIFACTS.json](current/EGA_v20/ARTIFACTS.json) |
| 新对话接续 | [CONTINUE_HERE.md](CONTINUE_HERE.md) |
| 来源及未决项 | [SOURCE_MAP.md](current/EGA_v20/SOURCE_MAP.md) · [PENDING_ISSUES.md](current/EGA_v20/PENDING_ISSUES.md) |

PDF、TeX、当前项目包、包含底本／Dot／可恢复历史的完整续作包和校验表见 [第二十版发布](https://github.com/liyiliuxingyu/ega-chinese-translation/releases/tag/v20-20261125)。此处列出发布目标；是否已经完成，以对应 Release、根 `EDITION_20_IMPORT.json` 和 Actions 实际记录为准。当前项目包可重建译稿；继续对照原文应取得完整仓库或完整续作包。

## 第二十版的实际内容

- 对读法稿物理64—73页和英编稿43页中段—48页末，完整处理第一篇§12。法67、68页是同一稿页的重复扫描，正文只排一次。
- 修正关联 Grassmann 纤维维数为 `m(r−1−m)`，区分法稿原错与英文转写错误，并证明泛点／任意基变换下的零点概形描述。
- 恢复“自8.6起”，撤销英译“除8.6外”及旧中文据此形成的错误归责；恢复“经过x”“光滑子簇的闭包”以及法稿的 `V¹`、基 `X` 等。
- 分清截面的奇异零点、纤维内在非光滑点、下一退化层的支集与概形结构；补明余维估计所用的有限型条件。
- 用二次 Veronese 圆锥曲线的一般直线束反驳“整个判别集合一般几何不可约”的原文断言。正文订正、原错入脚注，报告保存完整反例；另外独立证明原段的一般中心余维界，不将它用于推出不可约性。
- Dot117—119原工程已实际读取、与源页对读；其候选结论按证据取舍。本轮继续处理其后法71页末—73页，使§12完整接到§13。

所有177个继承 TeX 文件保留原字节，Dot69—108共40个现行模块仍各输入一次。§13旧译另存继承模块，33,351字节逐字保留；§§14—15及其他已有译文继续输入。旧§12及旧报告仍完整存档。技术核验不表示所有继承内容本轮都已重新数学审定。

## 下一实际位置和未完成范围

默认继续第五卷第一篇§13的法英回校：

- 法稿 `archive_20261121/03_sources/EGA5_francais.pdf`，PDF物理74页，§13标题及定义13.1。
- 英编稿 `archive_20261121/03_sources/EGAVaiello.pdf`，PDF物理49页。
- 既有译文 `current/EGA_v20/continuations/v20_section13_inherited.tex`，其后为 `v_dot_late.tex` 的§§14—15。

英文底本实际112页，末页书信已经收入；法文扫描171页，末为二次型附录。不得由此推定全部法文页逐行审结。8.7(c)、8.8、9.5残文、非诺特正则性及§12未证推广等仍见未决表。

**正式第IV章主体仍未连续译入。** 这是另一分支，从 `EGAIV.1.pdf` 物理221页提要、222—223页章首及223页(1.1.1)继续。第0章§§14—23及第五卷预备手稿章号不能替代正式第IV章。

## 原件与历史

| 路径 | 内容 |
|---|---|
| `current/EGA_v20/` | 本版源码、成品、报告及本轮实际检查证据 |
| `current/EGA_v19/`、`current/EGA_v18/` | 前版工程原样保留 |
| `archive_supplement_20261125/` | 15个旧合订工程原ZIP、Dot109—119的11个原ZIP及漏传核查报告 |
| `dot_updates_20261124/` | Dot69—108的40个原ZIP和展开内容，已收入正文相应位置 |
| `archive_20261121/` | 先前完整续作工程、原底本、历史恢复资料及Dot档案 |
| `archive_20261121/03_sources/` | I、II、III.1—2、IV.1—4、第五卷法英稿及三份PS底本 |
| `snapshots/20261125-v20/` | 本轮开始前公开提交 `997597…` 的根说明与清单原件 |

2026-11-25补充归档已保存26个恢复的原ZIP。另7个早期独立卷册原ZIP不可恢复，不能声称最初全部附件原容器均已保存；详细边界见 [漏传核查报告](archive_supplement_20261125/AUDIT_REPORT.md) 和 [归档索引](archive_supplement_20261125/ARCHIVE_INDEX.json)。普通文件恢复与原ZIP容器恢复是不同事项。

历史Dot档案含其他数学项目附件，为历史恢复而原样保存，未收入EGA正文。档案批次数不能换算成独有译文量。第I章既有源码至(10.15.7)，第II章至(8.14.14)，第III章两分册合接至(7.9.14)，第0章至(23.2.10)(ii)及原“待续”；其书末材料继续保留，本轮未重新逐卷审定。

## 核验与重建

先在原始交付快照上运行：

```bash
python3 tools/verify_repository.py --strict
```

然后复制当前工程，在新目录重建，避免改写已交付快照：

```bash
python3 -c 'from shutil import copytree; copytree("current/EGA_v20", "../ega-v20-work")'
cd ../ega-v20-work
bash build.sh --verify-single
python3 checks/verify_current_source.py
python3 checks/check_build_logs.py
python3 checks/compare_current_pdfs.py
```

采用真实 `ctexbook` 默认字体、字号与正文版心。需要 Bash、Python、XeLaTeX及相关宏包；逐页比较需 PyMuPDF，精确代数计算需 SymPy。工程附 CTeX/Fandol 及许可，不是完整跨平台TeX发行版。单文件TeX无外部正文输入，仍依赖TeX宏包和默认字体。

离开完整仓库后，继承检查会按记录散列进行，并明确没有重新读取前版原件。自动逐页比较验证模块版与独立单文件版的输出；抽样看图的准确页码和散列见 `checks/visual_verification_summary.json`，不表示全书人工逐页校勘。数学、来源、构建和保存核查各有具体范围。
