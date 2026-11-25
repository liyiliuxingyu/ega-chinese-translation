# EGA 中文译校合订工程：第二十版

本版为第五卷预备笔记第一篇 **§12的完整法英回校整合**，对应法稿物理64—73页、英编稿43页中段至48页末；法67/68重复扫描只译一次。采用经原页复核的Dot117—119候选内容，再接续至§12末。其他已有译文完整保留，尚非全部书籍完结。

## 先读这些文件

`PROGRESS.md` → `HANDOVER_STATE.json` → `ARTIFACTS.json` → `SOURCE_MAP.md` → `PENDING_ISSUES.md`。

下一实际接点为法稿74页／英稿49页的§13标题与定义13.1，已有译文在 `continuations/v20_section13_inherited.tex`。`main.tex`是模块入口，`single.tex`是独立单文件；`report.tex`和`report_single.tex`分别是累计核查报告的模块/单文件入口。

## 重建

使用真实 `\documentclass[UTF8,a4paper]{ctexbook}`，默认字体、字号和正文版心，没有自设字体或页边距。需要XeLaTeX、Bash、Python；PDF逐页比对需要PyMuPDF。`vendor/texmf/`附有CTeX/Fandol及许可，以支持本工程的默认字体环境；不等于完整跨平台TeX发行版。

```bash
bash build.sh --verify-single
python3 checks/verify_current_source.py
python3 checks/check_build_logs.py
python3 checks/compare_current_pdfs.py
```

构建会覆盖本目录的生成文件；需要保留交付快照时请先复制到工作副本再运行。`single.tex`与`report_single.tex`没有外部正文输入，但仍需要相应TeX宏包和默认字体。`checks/rebuild_report.sh`只用于报告改动后的局部重编，完整重建入口仍是`build.sh`。

## 包的范围

- **当前项目包**：本目录中的源码、四份PDF构建证据、累计报告、默认字体依赖、进度、来源摘页与本轮检查。可以重建当前成品。较早的完整底本和独立Dot原包在全库包中。
- **包含Dot的完整续作工程包**：完整仓库载荷，包括原底本、Dot各批、可恢复历史、前版、现版和所有接续文档。需要继续按原文回校时，优先使用完整包或仓库。

旧§12全源和相关旧文档在 `recollation/legacy_v19/`；§13的33,351字节原样继承，§§14—15及其他旧正文继续输入。历史文件中的旧进度不替代本版进度。`checks/`的实际执行记录注明哪些页面只是自动比较、哪些曾人工读图；不声称全部页面人工审定。

用户已授权持续推进与上传既有公开GitHub仓库（包括Dot）；每轮据真实源码续作，不重复索要同一授权，不发邮件、不创建重复自动任务。若原稿或工具确实不可恢复，应记录具体阻碍，不能用空进度代替文件交付。
