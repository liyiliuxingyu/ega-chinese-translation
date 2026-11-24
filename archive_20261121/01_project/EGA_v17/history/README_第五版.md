# 代数几何基础：按内容顺序编排的中文译校合订本（第五版）

这是当前已译内容的工作译稿，不是所有上传EGA材料的完结全译本。准确范围见PROGRESS.md。
本版连续补齐第0章§18，止于（18.5.4）及证明；下一接续点§19章首及（19.0.1）。

## 文件

- main.pdf：880页合订本；report.pdf：109页累计核查报告。
- single.tex：合订本可独立编译的UTF-8单文件源码。
- report_single.tex：核查报告可独立编译的UTF-8单文件源码。
- main.tex、report.tex、preamble.tex及text/、continuations/、backmatter/、reports/：分章节工程。
- checks/：编号覆盖、原文件哈希、具体例子验证、最终日志与逐页比较结果。
- history/：旧版进度、旧报告检查记录，以及第四版源码/哈希参考。均为历史材料，不代表第五版范围。

## 排版与编译

使用实际的 \documentclass[UTF8,a4paper]{ctexbook}，默认字体、字号、版心、页眉及双面分页。
公式和交换图为TeX内容，不依赖原文扫描图。本包不含字体文件。

需要XeLaTeX、CTeX及常见数学宏包（amsmath、amssymb、mathtools、mathrsfs、tikz-cd、enumitem、longtable、footmisc、adjustbox、hyperref、bookmark）。完整TeX Live环境可提供这些依赖。

分章节工程：在本目录运行 bash build.sh。
单文件独立编译和分文件工程同时建立：bash build.sh --verify-single。
也可将single.tex或report_single.tex单独放入一个目录，用XeLaTeX连续编译三遍。

编辑分文件后，运行 python3 flatten_sources.py 更新两个单文件；不要只改其中一个版本。
构建后逐页比较：python3 checks/verify_build.py（需要PyMuPDF；此前应运行build.sh --verify-single）。
具体例子的计算检查：python3 checks/verify_section18.py（需要SymPy）。这些计算不代替报告中的一般证明。

## 编校说明

新译校注以E5开头；原注、作者正式勘误、英译编者注与本次分析分开。
中心作用/代数扩张的双模约定须按报告限定理解；不能把所有脚注当作错误定理。
历史报告没有在本轮重新逐项审定。可编译、编号完整和版面一致不等于数学内容已通过独立出版级审校。
