# 代数几何基础：按内容顺序中文译校合订本·第十一版

新增第0章§21章首及21.1—21.4，止于(21.4.8)。保留此前已译正文。
此为当前已译内容合订本，不是全部上传材料的完结全译本。

## 文件
- main.pdf / main.tex：988页合订本及分文件编译入口。
- single.tex：合订本独立单文件TeX，不依赖其他源码、原扫描PDF或外部图片。
- report.pdf / report.tex：193页累计译校核查报告及入口。
- report_single.tex：报告独立单文件TeX。
- continuations/iv0_21_*.tex：本轮34条新译文；reports/eleventh_audit.tex：本轮核查。
- PROGRESS.md：准确范围、接续点、待核事项。
- checks/：哈希、覆盖、实际构建和逐页比较、最终日志、有限例子核验与已查看的缩览。
- history/：历史记录，不作为本轮新增检查证据。

## 编译
需要XeLaTeX、CTeX、AMS、tikz-cd、hyperref等宏包。字体和版心采用ctexbook默认设置；不附字体文件。

```sh
bash build.sh
# 独立编译单文件并保留其输出：
bash build.sh --verify-single
```

也可将single.tex复制到空目录，连续执行三遍：
```sh
xelatex -interaction=nonstopmode -halt-on-error single.tex
```
报告同理，将文件名换为report_single.tex。默认双面分页产生的空白偶数页保留。
不同TeX/字体发行版可能产生不同分页，本包记录的是本轮实际环境的结果。

## 复核脚本
```sh
python3 checks/verify_structure.py
python3 checks/verify_k11_examples.py
# 先运行build.sh --verify-single；此脚本需要PyMuPDF：
python3 checks/verify_outputs.py
```

原文差异在脚注，长反例和修补在报告。有限脚本测试不证明一般命题；编译和像素一致也不等于数学审定。
下一连续点：EGAIV.1.pdf第163页，分册印刷第164页，21.5章首及(21.5.1)。
