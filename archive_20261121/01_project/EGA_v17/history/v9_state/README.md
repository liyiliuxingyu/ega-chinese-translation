# 代数几何基础：按内容顺序合订本，第九版

本工程保留旧译文，并新增0章§20章首及20.1—20.5，止于20.5.15。不是全部上传材料的完结全译本。
正文使用已核实的正确陈述和证明，原文差异、作者勘误或译者修补在脚注说明；长论证在核查报告。

## 文件
- main.pdf / main.tex：952页合订本及分文件入口。
- single.tex：合订本独立单文件源码，不依赖工程内其他源码或外部图片。
- report.pdf / report.tex：167页累计核查报告及分文件入口。
- report_single.tex：报告独立单文件源码。
- continuations/iv0_20_*.tex：本轮49条新增译文。
- reports/ninth_audit.tex：本轮新核查；其余报告作为历史档案保留。
- PROGRESS.md：实际进度、准确接续点、范围和待核事项。
- checks/：覆盖检查、有限反例验证、构建一致性、最终日志及检查记录。
- history/：旧批次检查和变更记录；不是本轮新检验的证据。

## 编译
需要完整的XeLaTeX、CTeX、Fandol默认字体、AMS、tikz-cd、hyperref等常用宏包。本工程不附带字体文件，不需要原扫描PDF作为编译输入。

```sh
bash build.sh
# 同时在隔离目录核验单文件编译：
bash build.sh --verify-single
```

单文件可分别以XeLaTeX连续编译三遍，例如：
```sh
xelatex single.tex
xelatex single.tex
xelatex single.tex
```
报告同理，将文件名换为report_single.tex。默认双面分页中的空白偶数页保留。

## 复算检查
```sh
python3 checks/verify_counterexample.py
python3 checks/check_sources.py
# 须先完成 --verify-single，且安装PyMuPDF：
python3 checks/compare_builds.py
```
有限枚举只核验特征2双数环例子，不证明全部数学内容。源码及渲染一致性检查也不是出版级审校。
当前接续点：EGAIV.1.pdf第135页（印刷第136页）的20.6章首及20.6.1。
