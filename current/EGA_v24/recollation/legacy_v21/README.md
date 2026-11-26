# EGA 中文译校合订工程：第二十一版

本版实际新增工作为第五卷预备笔记第一篇 **§13的完整法英回校、订正与明列范围的补证**。法稿物理74—82页，英编稿49—53页。已有各卷译文和Dot模块继续保留，所有书籍尚未完结。

## 续作入口

依次读 `PROGRESS.md`、`HANDOVER_STATE.json`、`ARTIFACTS.json`、`SOURCE_MAP.md`、`PENDING_ISSUES.md`，再核对实际源码。

下一回校位置是 **§14（锥投影）**：法稿物理83页；英文53页末标题、54页开始正文。旧译在 `continuations/v_dot_late.tex`。不要把已存在旧译等同于已经通过本轮原文回校。

`main.tex` 为合订本模块入口，`single.tex` 为可独立编译单文件；`report.tex`、`report_single.tex` 是累计核查报告的两个入口。

## 重建与验证

使用真正的 `\documentclass[UTF8,a4paper]{ctexbook}`，默认字体、字号和正文版心。需要XeLaTeX、Bash、Python；PDF比较需要PyMuPDF。`vendor/texmf/` 附CTeX/Fandol及许可，不等于一个完整跨平台TeX发行版。

```bash
bash build.sh --verify-single
python3 checks/verify_current_source.py
python3 checks/check_build_logs.py
python3 checks/compare_current_pdfs.py
python3 checks/assemble_visual_verification.py
```

最后一项只核对已经实际查看的图片记录与成品绑定；它不会代替人工看图，也不会自动制造通过记录。重建会覆盖生成物，要保留交付快照应先复制到工作副本。单文件不依赖外部正文输入，仍依赖正常的TeX宏包和默认字体。

## 保存范围

- 当前项目包保存当前源码、成品、累计报告、默认字体依赖、源页摘录、核查和交接资料。
- 包含Dot的完整续作工程包保存完整仓库载荷，包括原底本、Dot原批、可恢复历史、前版和现版。继续译校优先使用完整包或完整仓库。

187个继承正文/报告/书末TeX文件保持原样，旧§13的33,351字节原文及副本都在；当前输入链仅以三份新模块替换旧§13入口。Dot69—108共40模块各输入一次。旧§13和第20版状态在 `recollation/legacy_v20/`，本轮源页与独立核查在 `recollation/v21/`。历史文档的旧进度不覆盖当前状态。

确证错误的正确表述写正文，原错及依据进入脚注。原作者删改、英文转写误差、译者补证和未决一般化分别标明。页数、编译、散列、输出一致和版面检查均不等于全书数学审定。

用户已授权持续译校和上传已有公开GitHub仓库（包括Dot），不重复索要同一授权，不发邮件、不创建重复自动任务。若原文或当前源码确实不可恢复，要记录具体阻碍而非反复空进度。
