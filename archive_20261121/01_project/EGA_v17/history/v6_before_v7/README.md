# 代数几何基础：按内容顺序合订本（第六版）

## 文件

- `main.pdf`：900页中文工作译稿合订本。
- `single.tex`：同一合订本的可独立编译单文件TeX源码。
- `report.pdf`：123页累计译校核查报告。
- `report_single.tex`：报告的独立单文件TeX源码。
- `main.tex`、`report.tex`及各源目录：便于维护的分文件工程。
- `PROGRESS.md`：实际覆盖、未译范围和精确接续点。
- `checks/`：本轮原始检查记录与脚本。
- `history/`：旧版进度、检查记录；其页数不代表本版。

## 编译

需要Python 3、XeLaTeX及常用TeX Live宏包（CTeX、AMS、tikz-cd、hyperref等）。不提供、也不依赖工程内的字体文件；中文字体由ctexbook默认配置选择。

在工程根目录执行：

```sh
bash build.sh
```

此命令重新合并源文件，并分别三遍编译合订本和报告。验证独立源码编译可执行：

```sh
bash build.sh --verify-single
```

单文件源码可单独复制到其他目录，然后使用XeLaTeX连续编译三遍。编译引擎不是pdfLaTeX。

结构及具体反例的有理数等式检查：

```sh
python3 checks/check_structure.py
python3 checks/check_examples.py
```

页级比较脚本 `checks/verify_pdfs.py` 需要PyMuPDF；`--independent`参数指向同时含 `book_single.pdf` 和 `audit_single.pdf` 的目录。程序比较不代替数学审校。

## 本版更新

连续译入第0章19.0—19.4（19.0.1—19.4.7），46个编号条目，包括原作者正式撤销的19.3.12。该条完整保留为历史译文，已明确标记撤销，不能当作有效定理引用。
新增内容保持原有章节次序，未改写35份已译正文文件。作者勘误、译校注与原文区分。

下一连续接续处：19.5章首及19.5.1。19.5—19.10、第0章§§20—23、第IV章主体及第V卷笔记余文尚未全部译完。

最终构建日志无编译错误、未定义引用、缺字、Overfull box；仍有Underfull及少量数学字体字号替代提示。具体结果见 `checks/validation.json`。

本稿供对照研读使用，尚未经独立的出版级逐句校勘与数学审定。禁止把“可编译”“条目未丢失”解释为全部定理已经证明无误。
