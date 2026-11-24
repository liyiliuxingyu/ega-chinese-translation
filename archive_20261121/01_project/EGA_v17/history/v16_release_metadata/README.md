# 代数几何基础·中文译校合订本（第十六版）

## 入口与内容
`main.pdf`为1060页合订本，分文件入口为`main.tex`；完整独立源码为`single.tex`。
`report.pdf`为253页累计核查报告，分文件入口为`report.tex`；完整独立源码为`report_single.tex`。
`PROGRESS.md`记载真实范围与下一接续点；`SOURCE_MAP.md`记录底本；`checks/`记录本轮核验。
`history/`为历史版本记录，里面的旧页数、进度和检查声明不代表本版。

本轮译完第0章§23“日本环”，至(23.2.10)末尾。第0章§§1—23现已连续收入；第IV章主体尚未开始连续译入，第V卷预备笔记仍有余文。
下一接续点是原书第IV章内容提要、章首说明及§1，不是重译第0章。
正文采用校订后的内容，原错误与依据写脚注，长反例及补证在报告。

## 编译
安装XeLaTeX及CTeX、AMS、TikZ-cd、hyperref等标准TeX Live宏包。
中文字体由ctexbook默认选择；不附任何字体文件，也不依赖外部图片。
在工程目录执行：
```bash
bash build.sh
```
对独立单文件构建并比对：
```bash
bash build.sh --verify-single
python3 checks/check_structure.py
python3 checks/verify_pdf_parity.py
```
结构检查仅需Python标准库；逐页PDF比对需PyMuPDF。反例多项式恒等式的辅助检查另需SymPy：
```bash
python3 checks/check_node_example.py
```
多项式脚本只验证列明恒等式，不是整段代数证明的形式化认证。
也可将`single.tex`或`report_single.tex`单独放入目录，连续运行XeLaTeX三遍。
发行包不重复收录`single_build/`的PDF和辅助文件；上述命令可重新生成。

## 版式和检查边界
实际使用`\documentclass[UTF8,a4paper]{ctexbook}`，不另设正文页边距、字号或字体；保留默认双面分页。
目录四位数页码栏沿用前版的宽度调整；本轮更新§23页眉内容，未改变默认页眉样式。
书内原著目录、索引仍采用原版页码，不能直接当作合订本页码。
所有页面做的是两个构建之间的机器比对；人工视觉检查限于新增与所列重点页，不声称逐页重审旧译文。
详细结果见`checks/CHECKS.md`和`checks/VISUAL_REVIEW.md`。发行包不附原著PDF或字体文件。
