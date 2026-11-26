# 第十九版模块工程

本目录以已发布的第十八版为基线，继续法英逐段回校第五卷预备笔记第一篇8.14至第11节末。Dot69—108四十批以及较早全部已译材料均保留；未宣称所有书籍完结。实际状态以`HANDOVER_STATE.json`和`ARTIFACTS.json`为准。主稿1214页、报告389页；模块与独立单文件全部页面的文字、尺寸和72dpi渲染像素一致。本轮62个样页已实际检查并绑定最终文件。

## 阅读入口

- `main.pdf`：合订译稿。
- `single.tex`：合订译稿单文件源码，无需其他正文输入。
- `report.pdf`、`report_single.tex`：累计核查报告及其单文件源码。
- `PROGRESS.md`：实际完成范围、下一原文位置与本轮执行情况。
- `SOURCE_MAP.md`、`integration/source_mapping.json`：40个原批次的实际来源和输出位置。
- `PENDING_ISSUES.md`：仍未解决的原文、数学与范围问题。
- `recollation/`：本版法英对读、原页证据、补证及边界记录。`integration/`保留第十八版的四十批整合历史。
- `checks/`：本版全局源码、构建、输出比对和人工版面抽查结果。

## 从源码重建

采用真实`ctexbook`，保留类默认字体和版心。需要Bash、Python 3.11或更新版本和XeLaTeX及相关宏包。项目包含已有CTeX宏包和默认Fandol字体及其许可，`scripts/tex_environment.sh`在系统未装CTeX或XeLaTeX格式时启用本地依赖；这不等于随包附带完整跨平台TeX发行版。

在本目录执行：

```bash
bash build.sh --verify-single
python3 checks/check_current_project.py
python3 checks/check_current_build_logs.py
python3 checks/compare_current_pdfs.py
```

构建会展开`main.tex`和`report.tex`，分别执行三轮XeLaTeX；`--verify-single`还将两份单文件放在独立构建子目录编译。逐页PDF比对需要PyMuPDF。判别式示例复算另需SymPy，可执行`python3 checks/check_quadratic_examples.py`；它只核对列明的精确计算，不验证整个二次型分类定理。

若只需单文件编译，在具有相应宏包与默认字体的TeX环境中，对`single.tex`或`report_single.tex`运行XeLaTeX三次。不要改用普通LaTeX或pdfLaTeX处理这些Unicode中文源文件。

## 保存与校验

仓库原件位于`archive_20261121/`和`dot_updates_20261124/`；本目录的源文件是它们的工作副本或本次明确记录的新模块。源工程ZIP提供当前可构建源码和检查记录；包含全部底本、Dot原包和历史的归档另为完整仓库工程包。只取得当前项目ZIP时，仍可重建译稿，但下一轮原文校勘需要同时取得仓库原始底本。

仓库根的`python3 tools/verify_repository.py --strict`核验交付快照。构建会产生新的临时文件，因此要重现交付快照核验，建议先在原目录核验，再复制到新工作目录构建。`checks/check_current_project.py`在完整仓库中还会核对继承源码；若仅有独立项目ZIP，清楚记录未在本地再次读取旧归档，不伪称完成了原件对照。

有意修改源码后，要先记录具体修改及来源，重新展开、构建、渲染，再用`--record-sources`记录新源码清单。不得以单纯刷新散列代替核查。旧目录中的制作脚本含其制作时点的转换步骤；一般续作直接编辑当前模块，重跑转换脚本前先核对`integration/`中的后续补丁记录，避免覆盖已完成的人工校正。

## 续作规则

沿用预概形／概形、拟凝聚／凝聚、双同态、丰沛层等术语。确证错误的正确表述写正文，原错和依据写脚注；不确定和缺文单独标记，不凭常识填成作者原文。分清作者删划、英文编者、原批译者补证和本轮新增译校。

当前第五卷最新回校点为第11节末，下一法文物理64页§12，对读英文物理43页中段；对应旧译为`continuations/v_dot_middle.tex`。正式第IV章仍为另一未完成分支，从EGAIV.1物理221页提要、223页(1.1.1)接续。各项详细状态以实际源码、进度及源页为准。

本轮制作脚本位于`recollation/engineering/`，其中一次性接合脚本不应在已更新工程上直接重跑。常规续作只修改现有模块并执行构建、检查；原件和历史版目录不回写。
