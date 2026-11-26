# 第二十一版来源与正文映射

日期：2026-11-26（Asia/Shanghai）。实际基线：99cd048abd72adad984613aaa4f5fef86cd5a6c8，current/EGA_v20。此轮为既有第13节的法英回校、恢复和订正，不重复计为从头新译。

## 连续源页及正文模块

| 模块 | 法稿物理页 | 英编稿物理页 | 精确边界 |
|---|---|---|---|
| continuations/v21_section13_initial.tex | 74—77 | 49—51首段 | 第13节标题，13.1、13.2、13.3陈述与初等邻域构造；止于所求邻域。 |
| continuations/v21_section13_bertini.tex | 78—79和80顶部NB | 51中段—52附记末 | 引理13.3证明、固定点截面、归纳及正维中心附记；止于13.4之前。 |
| continuations/v21_section13_remarks.tex | 80中段—82末 | 52末—53的13.4(e)末 | 13.4(a)—(e)完整；法稿纸面a,b,d,c,e，按既有编号次序排印并记录移排。 |

下一处为§14：法稿物理83页；英文53页末标题、54页正文。法83和英54只用于边界确认，不计入本轮已回校正文。后续旧译在continuations/v_dot_late.tex。

## 原底本与可携带摘页

- 原文件：`archive_20261121/03_sources/EGA5_francais.pdf`，实际171页；SHA-256 `24cf8204184b58b18a46e5f63ecc36d6e791b3c8c96a09daac93de96ebd8e830`。
  当前工程摘页：`recollation/v21/source_pages/fr_physical_74_83.pdf`，依次对应原PDF物理74—83页；摘页SHA-256 `06687eb3379ed3451144d3308b85e184eb89caeae62db604f62c567ec47b6a2a`。

- 原文件：`archive_20261121/03_sources/EGAVaiello.pdf`，实际112页；SHA-256 `23a20ef32fd16a1bd623c0c08ac080d04fc94f248de12133b713a19d6b0330d9`。
  当前工程摘页：`recollation/v21/source_pages/en_physical_49_54.pdf`，依次对应原PDF物理49—54页；摘页SHA-256 `e5bb640fa52730e958caef446fc035c611bc17c9dce3806d948d41c42f239938`。

摘页不是完整原底本。原始法稿171页、英文112页保存在全库包内。全文末页与本轮回校接点分开；不存在英文113页的续译起点。

## 可核查证据

- recollation/v21/initial/：逐段P01a—P10b检查、四个英文编辑脚注、15条旧注原文及初段补证的事实记录。
- recollation/v21/bertini/：14个连续源段映射、20条旧注原文、固定点补证与跨模块独立复核记录。
- recollation/v21/remarks_historical_notes.json：旧D17-M081—093十三条脚注的完整TeX原文及其来源散列。
- recollation/v21/topology_review.md：实际读过源页、原记号与英文误排、保边界平行移动及普遍覆盖的完整独立核查。
- 本版累计报告前四个模块分别为整合、初段、截面证明和13.4诸注的核查；全部补证明确标记译者身份。

## 保留与前版映射

187个继承正文、报告和书末TeX文件与实际第20版逐字节比较；Dot69—108共40个模块各输入一次。原第13节33,351字节保留在continuations/v20_section13_inherited.tex和recollation/legacy_v20/同名副本中，只退出当前输入链，不删除内容。

第20版的完整来源表在recollation/legacy_v20/SOURCE_MAP.md，其中§12及Dot117—119的原页对应继续有效；其“下一§13”仅是旧时点进度。第19版及更早的来源表也保留在既有legacy层。所有原Dot工程、已回校内容和历史核查不回写。

## 外部证明支点

连通性使用Martinelli–Naranjo–Pirola的Connectedness Bertini Theorem via numerical equivalence（2017），Theorem1.1，实际原作者PDF已读；所有代数闭特征都适用，所需射影不可约条件明列。解析部分使用Ehresmann定理、Riemann曲面均匀化与纤维丛同伦正合列，具体署名一手讲义及命题位置见本版报告。

外部证明支点与译者独立补证不替代原法稿的辨读；8.7(c)、8.8及一般基底推广等未决范围仍见PENDING_ISSUES.md。未将所有旧报告重新审定，也未将技术构建当作数学完备性证明。
