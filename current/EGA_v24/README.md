# 第二十四版中文译校工程

本版接续已发布第二十三版的实际源码，回校第五卷预备手稿第二篇§16“函数的奇异零点与超奇异零点”。这是已有中文译文的法英对读与订正；全套书籍尚未完结。完成与否以 `HANDOVER_STATE.json`、`ARTIFACTS.json` 及实际检查记录为准；工作中的目录不代表已经发布。

## 内容与入口

- `main.tex`、`main.pdf`：合订译稿的模块入口与成品。
- `single.tex`：由活动输入链精确展开的独立单文件；编译不需要外部正文模块。
- `report.tex`、`report.pdf`、`report_single.tex`：累计核查报告的入口、成品与独立源码。
- `continuations/v24_section16_early.tex`、`v24_section16_late.tex`：第16节两个连续回校模块。连续底本范围为法文物理95—111页、英文62页节标题至73页第17节标题之前。
- `reports/v24_*_audit.tex`：两个专题核查与整合记录。
- `recollation/legacy_v23/`：第二十三版状态、成品及检查的历史副本，不作为本版成功证据。
- `checks/current_*.json`、`checks/visual_verification_summary.json`、`ARTIFACTS.json`：明确绑定具体源文件、成品与实际检查结果。

207个继承正文、续篇、书末和报告TeX保持原字节。旧第16节全部61,675字节仍在 `text/v1_2.tex`；活动输入使用两个新模块，不重复排印旧入口。原 `v_dot_late.tex`、第一篇第15节旧全文及历史分拆继续保留。前版项目1,285项文件及其保存路径见 `recollation/legacy_v23/RETAINED_PROJECT_FILES.json`；40份Dot69—108模块各输入一次。

## 编译与复现

建议把交付项目复制到新的工作目录后再运行，保留交付快照的原字节。使用真实ctexbook默认字体、字号和版心，需要XeLaTeX、CTeX、Fandol及所用宏包。工程附带的vendor资源与许可不能替代完整TeX发行版。

```bash
bash build.sh --verify-single
python3 -B checks/verify_current_source.py
python3 -B checks/check_build_logs.py
python3 -B checks/compare_current_pdfs.py
```

有冻结的第二十三版目录时，可增加实际文件对比：

```bash
python3 -B checks/verify_current_source.py --reference-project /absolute/path/to/EGA_v23
```

没有旧目录时，结构检查仍逐个验证随项目记录的旧源散列，并明确记为“只对记录散列核验”，不能声称重新读取了旧目录。单文件先由 `flatten_sources.py` 精确展开，再分别编译正文与报告的模块版和独立版。完整页面比较包括文字、页面尺寸和72dpi像素；PDF散列变化本身不等于排印内容有变化。

视觉检查需要实际显示并查看渲染页。`checks/assemble_visual_verification.py`只汇总明确列出的真实看图记录，重新渲染并验证它们与最终PDF一致，不会替人看图，也不能从旧版pass生成新版审核结论。改稿后须重新检查受影响页面。

## 接续与限制

下一回校点为第二篇§17，法文物理112页、英文73页中部节标题；该节不计入本轮新增范围。第16节的旧中文 `text/v1_2.tex` 已停用保存，两份新模块在相同内容位置替换活动输入。正文所处顺序与源扫描物理页序不同，不能据目录位置推断缺失或重复。具体源页、旧译边界和未决事项见 `SOURCE_MAP.md`、`PENDING_ISSUES.md`。

第14节既有充分条件和第15节新增的适用条件不得删除。法稿错误、英文转写错、译者补证与尚未解决的字词分别标记。原8.7(c)、8.8、9.5缺文、13.4(d)一般基底推广等旧限制继续有效。本版不表示全部旧证明已经再次审定；正式第IV章主体另从其第一分册物理221页提要及后续章首接续。

## 备份与发布

当前项目包可独立编译当前译稿；全库续作包另含全部可恢复底本、历版工程、Dot原包与真实交接说明。旧历史中7个早期原ZIP容器未能恢复的边界保留，成员文件不能冒充原容器。

公开仓库继续使用 `liyiliuxingyu/ega-chinese-translation`。发布目标 `v24-20261126` 只是目标名；只有实际根目录导入回执、工作流结果、远端标签和附件验证才能证明发布成功。
