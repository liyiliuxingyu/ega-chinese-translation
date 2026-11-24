# 代数几何基础·中文译校合订本（第十三版）

## 交付文件
- main.pdf：1028页合订本；main.tex读取分章节输入文件。
- single.tex：可独立编译的完整合订本源码，不依赖外部图片或第一卷工程。
- report.pdf：219页累计核查报告；report.tex读取各轮报告。
- report_single.tex：核查报告可独立编译单文件。
- PROGRESS.md：真实完成范围、下一条及未译范围。
- checks/：来源哈希、编号保存、编译日志、逐页对照、视觉检查记录及脚本。
- history/：继承的历史档案和V12进度，历史结论未在本轮全部重审。

## 本轮范围
从§22章首及22.1.1开始，连续译入22.1—22.3，止于22.3.4及其证明。
下一接续点为22.4章首及22.4.1。尚不是全部材料的完结全译本。
正文采用本轮核定的陈述与证明，原文差异和依据放脚注，长反例及补证放报告。

## 编译
需要XeLaTeX、CTeX、AMS、TikZ-cd等标准TeX Live宏包。沿用CTeX默认字体，不附字体文件。
在根目录执行：
```bash
bash build.sh
```
同时检查独立单文件：
```bash
bash build.sh --verify-single
python3 checks/verify_outputs.py
python3 checks/check_structure.py
```
后两项需PyMuPDF；渲染缩览还需Pillow。反例代数检验需SymPy：`python3 checks/verify_char2.py`。
也可只复制single.tex到干净目录，用XeLaTeX连续编译三遍；report_single.tex同理。
`checks/build_final.py`提供四组编译并行运行方式，会清空项目内single_build中的生成文件。

## 版式与检查边界
使用实际ctexbook，未改变默认正文字体、字号、版心或页眉；仅为四位数目录页码扩大目录页码栏。
默认双面排版保留正常空白偶数页。索引和原目录的原版页码不是合订本页码。
编译、逐页一致性及新增页视觉检查不代替出版级校勘或全书证明审定。准确检查结论见checks/CHECKS.md。
