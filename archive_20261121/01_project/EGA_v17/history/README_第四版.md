# 代数几何基础：按内容顺序编排的中文译校合订本（第四版）

这是当前实际已译材料的工作译稿，不是全部上传EGA材料的完结全译本。完整范围和接续点见PROGRESS.md。

## 文件

- main.pdf：合订本，A4，860页。
- report.pdf：累计核查报告，95页。本轮D4条目在前；既有C3等报告作为历史记录收入。
- single.tex：合订本可独立编译的UTF-8单文件源码。
- report_single.tex：核查报告可独立编译的UTF-8单文件源码。
- main.tex、report.tex及各源码目录：分章节工程。
- checks/：原始输入哈希、编号清点、最终编译日志、逐页比较及审阅范围记录。
- history/：第三版进度及说明档案，仅供追踪，不代表本版状态。

## 排版

实际使用\documentclass[UTF8,a4paper]{ctexbook}，沿用CTeX默认字体、字号、版心和双面分页，不使用geometry或自定义字体。原著章号、条目号、公式号保留，公式和原有交换图是TeX内容。源码不依赖原文扫描图片或第一卷外部文件。

## 编译

需要安装XeLaTeX、CTeX、amsmath、mathtools、mathrsfs、tikz-cd、enumitem、longtable、footmisc、adjustbox、hyperref及bookmark等标准TeX宏包。使用常见完整TeX Live环境即可；本包不分发任何字体文件。

分章节工程：在本文件所在目录中运行

    xelatex -interaction=nonstopmode -halt-on-error main.tex
    xelatex -interaction=nonstopmode -halt-on-error main.tex
    xelatex -interaction=nonstopmode -halt-on-error main.tex

报告将main换成report。Linux/macOS可运行bash build.sh；需要同时独立编译单文件并检查时运行bash build.sh --verify-single（逐页像素比较结果已另存于checks，并非该脚本自动执行的功能）。

单文件：将single.tex单独放入一个文件夹，用XeLaTeX连续编译三遍。报告对report_single.tex作同样操作。编辑分文件后运行python3 flatten_sources.py重新生成两个单文件，再编译；不要只修改一个版本而遗忘另一版本。

## 编校说明

原注、英译编者注和D4译校注分开；采用作者勘误的地方注明来源，未静默改写原著。D4-E02是零模边界，不是一般结论被反驳；D4-P01仍为待补证明事项。原有工作译稿与历史核查报告未经本轮全部重新逐句审定。

编号存在、TeX可编译、页面比较一致，都不等于全部数学内容通过独立审校。最终日志保留了underfull和数学花体字号替代等非致命提示，不以“零警告”表述验证结果。
