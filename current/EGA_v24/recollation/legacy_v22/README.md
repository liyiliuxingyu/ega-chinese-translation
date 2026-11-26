# 第二十二版中文译校工程

本版接续第二十一版的真实源码，完整回校第五卷预备手稿第一篇§14“锥投影”。这是已有译文的法英对照、恢复与订正；全套书籍尚未完结。先读 `PROGRESS.md`、`HANDOVER_STATE.json`、`SOURCE_MAP.md`、`PENDING_ISSUES.md` 和对应实际TeX，再开展续作。

## 文件与范围

- `main.pdf`、`main.tex`：合订译稿及模块入口。
- `single.tex`：由当前输入链展开的独立合订TeX，不需要外部正文文件。
- `report.pdf`、`report.tex`、`report_single.tex`：累计核查报告、模块入口及独立TeX。
- `continuations/v22_section14_*.tex`：三个连续的新回校模块；法83—90、英53末标题及54—59，均止于§15前。
- `continuations/v22_section15_inherited.tex`：原§15完整14,614字节后缀，仅保留，尚未新回校。
- `recollation/v22/`：源页、逐段对照、旧段副本、独立核查及路径迁移映射。独立模块小样与最终合订本的图检分开记录。
- `recollation/legacy_v21/`：原状态、成品及历史证据；其中的成功状态不能代替本版记录。
- `ARTIFACTS.json`、`checks/current_*.json`、`checks/visual_verification_summary.json`：实测成品及具体检查；缺失或未通过时不能声称完成。

194个继承正文、续篇、报告和书末TeX保持原字节。旧 `v_dot_late.tex` 全文49,224字节保留，旧§14的47条校注仍可核验；活动输入用三个新§14模块及原§15后缀替换旧入口，不重复排印。Dot69—108的40个模块各输入一次。

## 编译与核验

建议复制到新的工作目录后运行，保持本交付快照的字节。使用真实 `ctexbook` 默认字体、字号、版心和分页；需要 XeLaTeX、CTeX、Fandol 及所用宏包。随包 vendor 是已有字体/宏包及许可，不能代替完整TeX发行版。构建入口自动配置本工程附带资源。

```bash
bash build.sh --verify-single
python3 -B checks/verify_current_source.py
python3 -B checks/check_build_logs.py
python3 -B checks/compare_current_pdfs.py
```

`build.sh`先展开单文件并检查输入链，再分别以XeLaTeX编译模块书稿、模块报告和两份独立稿。逐页比较包括文字、页面尺寸及72dpi像素。PDF字节散列可因重新生成的元数据而改变，不能把不同散列直接当作正文差异。

版面需真实渲染、实际查看，记录最终PDF、图像散列和明确页码。`checks/assemble_visual_verification.py`只汇总并校验实际看图记录，不替人看图；重编之后旧散列绑定不得冒用。历史页面没有全数重新人工审定，不能从抽样图检写成全书每页审核。

## 下一位置与正确性边界

下一回校点为第一篇§15：法稿物理90页末、英文59页。先读原后缀及底本，不以“已经收入”推定审定。14.1、14.3、14.4、14.5本版补入的充分条件不得删去；具体反例和证明见本版报告。难辨字、未定位引用、非有限模边界及旧缺文详见 `PENDING_ISSUES.md`。

正式第IV章主体另从 `EGAIV.1.pdf` 物理221页提要及后续章首接续。旧卷范围、Dot材料及历史容器缺失记录保持；不回退到EGAII早期分册接点。

## 完整备份与发布

当前项目包可独立编译当前译稿；全库续作包另含全部可恢复原底本、历版工程和Dot原包。根 `CONTINUE_HERE.md` 给出新对话入口。公开仓库继续使用 `liyiliuxingyu/ega-chinese-translation`，本版发布目标标签为 `v22-20261126`。冻结文件中的发布目标不是成功回执；实际发布须核根 `EDITION_22_IMPORT.json`、Actions结果、远程标签及Release资产。
