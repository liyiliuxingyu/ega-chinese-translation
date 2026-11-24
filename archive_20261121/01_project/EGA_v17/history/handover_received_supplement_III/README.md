# 第十七版·第五卷增补第三辑

已连续合入批次 50–68，第三辑新收 63–68，至英译物理77页、法文物理159→158（印117→118）15.7末。下一英78、法物理161附录IV.17.16《光滑二次型》。正式第IV章未改，接续 EGAIV.1 物理221–223。
运行 build_supplement_III.sh；报告已连同历史报告重编。下文旧版页码、状态仅供追溯。

---

# 第十七版·第五卷增补第二辑

- 当前合订本 1146 页；第二辑新合入七批 56–62（UTC 2026-11-20 07:00 至 19:00）。第 956–969 页为本辑正文及校注所在区域。
- 与第一辑接合，自合并英译物理第68页划去说明之后，至英译物理第73页、法文扫描物理第111页的命题7推广及降秩旁注末。旧增补与本辑区分作者划去稿、英译编者按、恢复的正文与译校说明。
- **下一处：英译物理第73页、法文物理第112页 IV.17.15「光滑二次型与初等奇点」。**
- 第IV章正式正文未被改动。继续位置仍为 EGAIV.1.pdf 物理第221页提要、第222–223页章首说明、第223页§1（1.1.1）。
- 独立累计核查报告 283 页未重编，仍比对历史；本次核查随正文刊载。已校订降秩旁注的错误余维不等号，保留原式及反例；分歧子概形证明作为译校重构，不当作底稿已证。
- 按 `HANDOVER_STATE.json`、`PENDING_ISSUES.md` 续作；旧进度记录只供追溯，旧次序、页码及待校标记不作当前断点。

## 构建入口

阅读 main.pdf，按 build_book.sh 重编分章入口 main.tex；也可独立编译 single.tex。工程的 vendor/texmf 带部分兼容依赖和许可，不含 XeLaTeX 引擎。不要用旧历史 build.sh 重编原报告。

---

# 代数几何基础中文译校合订本·第十七版

当前成品为1130页合订PDF和283页累计核查报告。Dot已恢复的56批EGA V译稿已经纳入：54批接合正文，2批同文校订。未完成的卷次仍明确标示。

## 入口

- main.tex → main.pdf；single.tex为同内容的独立单文件。
- report.tex → report.pdf；report_single.tex为独立报告单文件。
- PROGRESS.md是当前实际进度；SOURCE_MAP.md记来源；PENDING_ISSUES.md列待核问题；HANDOVER_STATE.json为结构化状态。
- history是历史记录，不是当前进度；checks是本版可核验记录。

## 编译

使用XeLaTeX及标准TeX Live的CTeX、AMS、TikZ-cd、hyperref、bookmark、footmisc等依赖，Python 3.9或更新版本。

    bash build.sh

独立单文件及完整本版技术核验：

    bash build.sh --verify-single
    python3 checks/check_structure.py
    python3 checks/check_build_logs.py
    python3 checks/verify_pdf_parity.py

PDF比对脚本需要PyMuPDF；结构检查只需Python标准库。single.tex及report_single.tex均无外部TeX或图片输入，可单独置于任意目录，用标准完备TeX环境各运行XeLaTeX三遍。

本工程附vendor/texmf中的CTeX、相关中文支持和Fandol等开放字体及原许可证。scripts/tex_environment.sh仅在检测到所需CTeX或XeLaTeX格式缺失时启用本项目目录下的补充树，必要时在runtime中生成格式；不修改系统TeX设置。没有附完整TeX Live或XeLaTeX可执行引擎。跨操作系统的ctex默认字体选择可能不同，不承诺任意环境逐像素相同。

发行工程不收录可重建的aux、xdv及二进制格式缓存；最终日志保存在checks/build_logs。首次恢复前可先在交接包根目录运行verify_package.py。修改或重新编译后PDF时间元数据等会变化，旧散列不再代表新版本，应在核验新版本后重新制表。

## 排版与保留

真实文档类为ctexbook；不另设字体、字号或版心。数学公式和交换图用TeX。为四位数页码保留目录宽度。无编号分隔页由类的part命令在secnumdepth=-2下生成并自行写目录，避免在跨页结束后手写目录导致页码偏移；随后恢复secnumdepth=2。

本次整合的18处公式/列表后脚注引标调整了附着位置，注全文和顺序、显示公式全文和顺序经程序比对保持不变。旧正文除有据登记的PS短篇校订外保持原样，不因此声称旧内容全部重审。

## 第十七版·第五卷增补本：运行入口与核查边界

- 本册在第十七版正文的惟一接合点补入了2026-11-19 19:00 UTC至2026-11-20 05:00 UTC六批译文，第IV章主线不变。
- 重新生成合订本请运行 `bash build_book.sh`；输出写入 `build/`。不要用原历史 `build.sh` 重新生成未更新的累计报告，本次报告另存为历史基线且未重编。
- 新增译校附记随新增正文排印。原283页累计报告、`report_single.tex` 原样保留，未纳入新版累计统计。checks/中原第十七版核验为旧版历史记录，不能拿来证明本次新增部分。
- 解压后从包顶层 START_HERE.md 开始。当前项目的旧源映射、旧构建报告和旧进度引用只供追溯；原 v17 完整归档仍单独保管。另外保留此次六份原ZIP。
- 新增图、两条正合列、正规性维数及扭曲幂次必须按正文后的译校附记区分文本与推断；划去说明是英译编者注，不是原作者正文。

## 下一步

V卷：EGAVaiello.pdf物理第68页“Upon arriving at this point”，已译至其前的英译编者方括号说明；对读法文扫描物理第104页。
IV章：EGAIV.1.pdf第221页章首提要；(1.1.1)在第223页。
两处是底本的物理页。详细原句及约束见PROGRESS.md。
