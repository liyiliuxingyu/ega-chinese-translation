# EGA 中文译校工程（包括 Dot）

本仓库保存本对话及 **Dot 中可恢复的 EGA 译校工程**：合订译稿、模块与单文件TeX、累计核查报告、原始底本、逐批工程、校验记录和历史恢复资料。

当前工作版本为**第二十一版**，日期2026-11-26（北京时间），入口为 `current/EGA_v21/`。本轮逐段回校第五卷预备笔记第一篇§13，法稿物理74—82页、英编稿49—53页；这是已有译稿的回校、恢复与订正。**全书及原稿所有未证推广尚未完成。**

## 当前成品和源码

| 内容 | 入口 |
|---|---|
| 合订译稿PDF | [main.pdf](current/EGA_v21/main.pdf) |
| 可独立编译的合订单文件TeX | [single.tex](current/EGA_v21/single.tex) |
| 累计核查报告PDF | [report.pdf](current/EGA_v21/report.pdf) |
| 报告单文件TeX | [report_single.tex](current/EGA_v21/report_single.tex) |
| 工程与重建说明 | [当前项目说明](current/EGA_v21/README.md) |
| 真实进度及实测核验 | [PROGRESS](current/EGA_v21/PROGRESS.md) · [状态](current/EGA_v21/HANDOVER_STATE.json) · [成品散列](current/EGA_v21/ARTIFACTS.json) |
| 新对话接续 | [CONTINUE_HERE](CONTINUE_HERE.md) |
| 来源和未决项 | [SOURCE_MAP](current/EGA_v21/SOURCE_MAP.md) · [PENDING_ISSUES](current/EGA_v21/PENDING_ISSUES.md) |

PDF、TeX、当前项目包、含原底本/Dot/可恢复历史的完整续作包及校验表，发布目标为 [v21-20261126](https://github.com/liyiliuxingyu/ega-chinese-translation/releases/tag/v21-20261126)。是否已实际发布，以该Release、根EDITION_21_IMPORT.json及Actions执行记录为准；本地冻结文档不提前宣称远程成功。

## 本轮实际工作

- 逐段恢复§13全部陈述、证明、作者编写提醒、可辨删改及英文编辑脚注，区分法稿原错和英文转写误差。
- 核验初等态射的基底、非空有限平展边界、横截中心、关联族的相对Jacobian条件及几何连通性；一般纤维的基域明确为κ(η)。
- 另给d≥2 Veronese固定点截面的充分补证，并通过有限平展点集下降共同中心条件，补足非有理闭点及有限个点的共同邻域归纳。
- 给出不完美域上的曲线反例、三次Veronese切线所致全坏平面束反例，以及仅删连通条件的零维反例。各例所否定的断言分别限定；不把作者猜测误称为已证明定理。
- 对13.4(e)以保持边界的平行移动证明普遍覆盖实微分同胚于R^(2n)，正文仍保留同胚于C^n的表述，不改成双全纯。

187个继承正文/报告/书末TeX文件保持原字节；旧§13及33,351字节对照副本保留，当前仅替换输入入口。Dot69—108共40个既有模块各输入一次，Dot后续原包和旧报告完整保存。这些技术保存核验不等于本轮重新审定全部继承数学内容。

## 下一处与未完成范围

默认继续第五卷第一篇 **§14（锥投影）**：

- 法稿 `archive_20261121/03_sources/EGA5_francais.pdf`，PDF物理83页。
- 英编稿 `archive_20261121/03_sources/EGAVaiello.pdf`，物理53页末标题、54页开始正文。
- 旧译 `current/EGA_v21/continuations/v_dot_late.tex`，须逐段回校，不能按旧译存在即认定已完成新审。

原8.7(c)、8.8和9.5的缺文、有限域无扩域版本、13.4(d)一般基底推广及其他明列问题仍未解决。法稿171页全部逐行覆盖审计也未完成；英编稿112页是末页，不能虚构113页接点。

正式第IV章主体仍是另一未完成分支：从 `EGAIV.1.pdf` 物理221页提要、222—223页章首及223页(1.1.1)接续。第0章补篇及预备手稿拟定章号不能替代正式第IV章。

## 原件与历史

| 路径 | 内容 |
|---|---|
| current/EGA_v21/ | 当前源码、成品、报告及实际核查记录 |
| current/EGA_v20/、EGA_v19/、EGA_v18/ | 前版工程原样保留 |
| archive_supplement_20261125/ | 15个旧合订原ZIP、Dot109—119的11个原ZIP、漏传核查报告 |
| dot_updates_20261124/ | Dot69—108的40个原ZIP及展开内容 |
| archive_20261121/ | 先前完整续作包、原底本、历史恢复和Dot资料 |
| archive_20261121/03_sources/ | I、II、III.1—2、IV.1—4、第五卷法英稿及三份PS底本 |
| snapshots/20261126-v21/ | 基线99cd048中的根说明和清单原字节 |

补充归档已保存26个恢复的原ZIP；另7个早期独立卷册原ZIP仍不可恢复，详见 [归档核查报告](archive_supplement_20261125/AUDIT_REPORT.md)。普通成员文件可恢复与原ZIP容器齐全是两件事。历史Dot档案的其他数学项目附件为恢复历史而保留，没有混入EGA正文。

既有源码范围：第I章止于(10.15.7)，第II章止于(8.14.14)，第III章两部分合接至(7.9.14)，第0章止于(23.2.10)(ii)及原“待续”；书末资料继续保存。本轮没有重新逐卷核定这些旧译。

## 核验与重建

先在交付快照上运行：

```bash
python3 tools/verify_repository.py --strict
```

然后复制当前项目到仓库外重建，保留已交付快照的字节：

```bash
python3 -c 'from shutil import copytree; copytree("current/EGA_v21", "../ega-v21-work")'
cd ../ega-v21-work
bash build.sh --verify-single
python3 checks/verify_current_source.py
python3 checks/check_build_logs.py
python3 checks/compare_current_pdfs.py
```

真实ctexbook默认字体、字号和版心；需Bash、Python、XeLaTeX及相关宏包，PDF比较需PyMuPDF。附带CTeX/Fandol和许可，不是完整TeX发行版。两份单文件没有外部正文输入，仍需TeX宏包与字体。视觉汇总记录真正看过的页和图像散列，不等于全书人工逐页审定。
