# EGA中文译校：当前可续作工程

版本：第十七版·第五卷增补第三辑；工程整理日期：2026-11-21（Asia/Shanghai）。当前成品为1158页合订本和287页累计核查报告。本次整理没有增加新的翻译量。

## 先读什么

按 PROGRESS.md、HANDOVER_STATE.json、SOURCE_MAP.md、PENDING_ISSUES.md 的顺序读取，再检查实际输入源码末段。项目约束见 AGENTS.md。包根目录 00_START_HERE/新对话接续提示.txt 可用于新对话。

最近接续为 EGAVaiello.pdf 物理78页附录17.16《光滑二次型》之16.1，对读法文物理161页。正式第IV章另有未启动的连续翻译分支。旧66、68、73页断点只保留在历史资料中。

## 编译

需要 Python 3、XeLaTeX/TeX Live。工程附有既有 vendor/texmf 宏包、Fandol默认字体及许可文件；不是完整的跨平台TeX发行版。系统有完整CTeX时直接使用其环境；必要时 scripts/tex_environment.sh 启用随包依赖并在项目内生成运行时格式。

现行完整构建入口：

```bash
bash build.sh --verify-single
python3 checks/check_current_project.py
python3 checks/check_current_build_logs.py
python3 checks/compare_current_pdfs.py
```

第一条命令展开两个独立TeX，对主稿、报告、两份独立TeX各实际运行三遍XeLaTeX；前两遍建立目录和引用，第三遍输出PDF。产物为 main.pdf、report.pdf、single_build/book_single.pdf、single_build/audit_single.pdf。

最后一条逐页比较文本、尺寸及同一PyMuPDF渲染器72 dpi像素，需要安装PyMuPDF。依赖或编译失败时报告实错，不能把旧PDF冒作新构建结果。

single.tex 和 report_single.tex 不依赖其他TeX或图片输入，在安装相应TeX宏包及字体的环境中可单独编译。ctexbook使用默认字体及既有版式，公式和图保持TeX代码。

## 检查记录与历史

- checks/current_*：本轮当前源码、编译日志和模块/单文件对比记录。
- checks/VISUAL_REVIEW_20261121.md：实际查看的源页与译本抽样页、结果及检查边界。
- checks/v17-baseline/及history/：历史证据，不作为当前检查入口。
- history/handover_received_supplement_III/：收到的旧状态和构建脚本逐字备份。

数学正文和数学核查报告保持第三辑源码字节。原稿错误、有据订正、疑点和译校补证继续分别标记。编译成功、无缺字、文件齐全和页面一致均不等于全部证明已经独立审定。

## 完整性与历史恢复

在改写或重编之前，到工程包根目录运行：

```bash
python3 verify_package.py --strict
```

全包清单保存路径、字节数及SHA-256。重编后PDF元数据和日志可能改变；核验新结果后再更新状态和清单，不隐瞒变化。

旧完整包和第三辑原工程的每个普通文件，都由根目录 04_history/RESTORE_INDEX.json 映射到本包实际内容。相同内容可共用一份存储；恢复脚本可在新的空目录还原原来完整路径。当前工程已直接展开，无需先恢复历史即可续作。
