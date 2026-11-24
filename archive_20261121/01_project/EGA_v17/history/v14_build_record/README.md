# 代数几何基础·中文译校合订本（第十四版）

## 文件与范围
- main.pdf：1042页合订本；main.tex是分章节工程入口。
- single.tex：可独立编译的完整合订本源码。
- report.pdf：231页累计译校核查报告；report.tex为工程入口。
- report_single.tex：报告的独立单文件源码。
- PROGRESS.md：实际完成范围、下一接续点及未译范围。
- checks/：真实来源哈希、结构检查、日志、逐页对照与新增页视觉记录。

本轮连续译入第0章22.4—22.5，从（22.4.1）至（22.5.10，ii）末尾。
下一接续点为22.6章首及（22.6.1）。这不是全部上传材料的完结全译本。
正文使用本轮校订形式；原文错误、修改理由及依据在脚注；长反例和补证在报告。
历史报告保留原文，不表示本轮重新审定全部旧判断。

## 编译
需要XeLaTeX与标准TeX Live的CTeX、AMS、TikZ-cd等宏包。字体采用CTeX默认配置，不附字体文件。
在工程根目录执行：
```bash
bash build.sh
```
验证独立单文件构建：
```bash
bash build.sh --verify-single
python3 checks/check_structure.py
python3 checks/verify_outputs.py
python3 checks/finite_cotangent_check.py
```
前两项脚本分别进行结构保存和完整逐页文字／72 dpi像素比较；PDF比较需要PyMuPDF。
有限环余切空间检验仅使用Python标准库，不把有限阿廷商环误称为正则环。
也可将single.tex或report_single.tex单独放入干净目录，XeLaTeX连续编译三遍。

## 版式
实际文档类为ctexbook，默认字体、字号、版心、页眉和双面分页保留。
沿用四位数目录页码栏宽度修正；22.5标题前增加局部分页，避免标题孤留在前一页脚注上方。
原著页码与合订本页码不同，原目录和索引仍保留原著页码。

## 检查边界
全页构建一致性不等于逐页人工数学审校。人工视觉复核集中于新增正文、报告和本次调整页。
详情见checks/CHECKS.md和checks/VISUAL_REVIEW.md。压缩包不附原文PDF或字体文件。
