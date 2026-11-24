# 代数几何基础：按内容顺序合订本，第十版

保留既有译稿，新增第0章20.6—20.7，止于(20.7.20)。
这不是全部上传材料的完结全译本。正确陈述和已核实的补证在正文；
原文错误及修订依据在脚注，较长论证在核查报告。
确切接续点和待核事项见 `PROGRESS.md`。

## 文件
- `main.pdf` / `main.tex`：974页合订本与分文件入口。
- `single.tex`：独立单文件源码，不依赖其他源码或外部图片。
- `report.pdf` / `report.tex`：181页累计核查报告与入口。
- `report_single.tex`：报告独立源码。
- `continuations/iv0_20_6a.tex`、`iv0_20_6b.tex`、`iv0_20_7a.tex`、`iv0_20_7b.tex`：46条新增译文。
- `reports/tenth_audit.tex`：本轮新核查，其余报告保留为历史记录。
- `checks/`：实际覆盖/哈希/构建比较、有限例子脚本、最终日志、版面缩览。
- `history/`：旧批次档案，不是本轮新检查的证据。

## 编译
需要完整的XeLaTeX/CTeX发行版及AMS、tikz-cd、hyperref等宏包；
默认中文字体由CTeX选择。工程不附字体，不依赖原扫描PDF。

```sh
bash build.sh
# 同时在隔离目录重新编译单文件：
bash build.sh --verify-single
```

单文件也可分别连续编译三遍：
```sh
xelatex -interaction=nonstopmode -halt-on-error single.tex
xelatex -interaction=nonstopmode -halt-on-error single.tex
xelatex -interaction=nonstopmode -halt-on-error single.tex
```
报告将文件名换成 `report_single.tex`。保留ctexbook默认双面分页产生的空白偶数页。

## 复算检查
```sh
python3 checks/verify_j10_examples.py
python3 checks/check_sources.py
# 先执行 build.sh --verify-single，并安装PyMuPDF：
python3 checks/compare_builds.py
```

有限算例检查只针对J10所列矩阵/小环计算，不是一般证明。
构建一致性也不是出版级数学审定。最终仍有underfull及少量数学字体字号替代提示。
下一连续点：EGAIV.1.pdf第152页§21章首，编号条目21.1.1从第153页开始。
