# EGA 中文译校工程（包括 Dot）

本仓库保存本对话及 **Dot 中可恢复的 EGA 译校工程**：合订译稿、模块和单文件TeX、累计核查报告、原底本、逐批工程、校验记录及历史恢复资料。

当前版本为 **第二十二版**，日期2026-11-26（北京时间），入口 `current/EGA_v22/`。本轮完整回校第五卷预备手稿第一篇§14“锥投影”，法稿物理83—90页、英文53页末标题及54—59页，均止于§15前。它是已有译文的回校、恢复与订正。**全套书籍及原稿全部未证推广尚未完成。**

## 成品与续作入口

| 内容 | 入口 |
|---|---|
| 合订译稿PDF | [main.pdf](current/EGA_v22/main.pdf) |
| 独立合订TeX | [single.tex](current/EGA_v22/single.tex) |
| 累计核查报告PDF | [report.pdf](current/EGA_v22/report.pdf) |
| 独立报告TeX | [report_single.tex](current/EGA_v22/report_single.tex) |
| 重建说明 | [当前README](current/EGA_v22/README.md) |
| 实际进度及核验 | [PROGRESS](current/EGA_v22/PROGRESS.md) · [状态](current/EGA_v22/HANDOVER_STATE.json) · [成品散列](current/EGA_v22/ARTIFACTS.json) |
| 新对话接续 | [CONTINUE_HERE](CONTINUE_HERE.md) |
| 来源与未决项 | [SOURCE_MAP](current/EGA_v22/SOURCE_MAP.md) · [PENDING](current/EGA_v22/PENDING_ISSUES.md) |

PDF、TeX、当前工程包、含全部可恢复底本/历版/Dot资料的完整续作包及校验表，发布目标为 [v22-20261126](https://github.com/liyiliuxingyu/ega-chinese-translation/releases/tag/v22-20261126)。是否已经实际发布，以该Release、根EDITION_22_IMPORT.json、远程标签及Actions执行结果为准；本地冻结说明不提前宣称远程成功。

## 本轮数学工作

- 逐段对照§14全部陈述、简略证明、作者编写提醒、可辨删改、公式及交换图，区分法稿原错和英文转写误差。
- 对14.1(a)以爆破三维射影空间的特殊纤维给出反例；正文明确补强全部非空几何f纤维纯共同d维，并以像闭包及边界完成非固有情形的维数证明。
- 对14.3以平面与孤立点的并否定无分支限制的平坦结论，补入每个分支像维至少m，展开CM、正则参数、局部平坦判据及CM凝聚模证明。
- 对14.4(a)补m≥1及Y与T不交。恢复14.4(b)法稿手添强断言后，以直线加厚反例否定全逆像非分歧；正文仅保留指定T上的正确范围。
- 对14.5以k[t³,t⁴,t⁵]的奇异点否定任意原闭点平展；在有限型几何约化对象的原光滑闭点范围，补全射影闭包边界、剩余域、Nakayama和局部同构步骤。
- 一般拟凝聚模按本版核验的Koszul正则性使用，普通正则列及CM模结论明列有限性。未定位交叉引用、难辨字及原稿研究设想保持标记。

本轮41条新校注、19项专题核查和3项整合记录。194个继承正文/报告/书末TeX保持原字节；旧§14全文和47条原注保留，§15的14,614字节完整后缀精确接入。Dot69—108共40个活动模块各输入一次，Dot后续原包和旧报告全部保存。保存核验不等于重新审定全部继承数学内容。

## 下一处与未完成范围

默认继续第五卷第一篇 **§15“前述若干结果的公理化”**：法稿 `archive_20261121/03_sources/EGA5_francais.pdf` 物理90页末；英编稿 `archive_20261121/03_sources/EGAVaiello.pdf` 物理59页。现有译文为 `current/EGA_v22/continuations/v22_section15_inherited.tex`；须从真实源码逐段回校。

原8.7(c)、8.8、9.5缺文、有限域无扩域版本、13.4(d)一般基底推广，以及本轮仍未定位的“第21页上方、第5节之前”引用和一个层记号字形继续明列。英文112页是末页；法稿171页全部逐行覆盖审计尚未完成。

正式第IV章主体是另一未完成分支：`EGAIV.1.pdf` 物理221页提要、222—223页章首、223页(1.1.1)。第0章补篇及预备手稿拟定章号不能替代正式第IV章。

## 原件与历史

| 路径 | 内容 |
|---|---|
| current/EGA_v22/ | 当前源码、成品、报告与核查记录 |
| current/EGA_v21/及前版 | 既有工程原样保留 |
| archive_supplement_20261125/ | 15个旧合订原ZIP、Dot109—119的11个原ZIP及漏传核查报告 |
| dot_updates_20261124/ | Dot69—108的40个原ZIP及展开文件 |
| archive_20261121/ | 先前完整续作包、原底本、历史恢复和Dot资料 |
| archive_20261121/03_sources/ | I、II、III.1—2、IV.1—4、第五卷法英稿及三份PS底本 |
| snapshots/20261126-v22/ | 基线79c1100b中的根说明与清单原字节 |

另7个早期独立卷册原ZIP仍不可恢复，详见 [归档核查报告](archive_supplement_20261125/AUDIT_REPORT.md)。普通成员文件留存与原ZIP容器齐全不同。历史Dot中的其他数学项目附件作为历史资料保存，没有混入EGA正文。

继承源码范围：第I章至(10.15.7)，第II章至(8.14.14)，第III章两部分合接至(7.9.14)，第0章至(23.2.10)(ii)及原“待续”；书末资料保存。本轮没有重新逐卷核定这些旧译。

## 核验与重建

先在交付快照运行：

```bash
python3 tools/verify_repository.py --strict
```

再复制当前项目到仓库外重建，保留已交付字节：

```bash
python3 -c 'from shutil import copytree; copytree("current/EGA_v22", "../ega-v22-work")'
cd ../ega-v22-work
bash build.sh --verify-single
python3 checks/verify_current_source.py
python3 checks/check_build_logs.py
python3 checks/compare_current_pdfs.py
```

需要Bash、Python、XeLaTeX及相关宏包；PDF比较用PyMuPDF。附CTeX/Fandol和许可，不是完整TeX发行版。独立TeX不依赖其他正文输入，仍需宏包和默认字体。实际看图记录列出具体页码及图像散列，不等于全书人工逐页数学审核。
