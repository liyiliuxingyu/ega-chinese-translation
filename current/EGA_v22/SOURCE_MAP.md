# 第二十二版来源映射

基线：公开提交 `79c1100b13427e447fad5525f27d9b64e4d4ead7`，`current/EGA_v21`。本轮是已有第一篇 §14 的完整法英回校、恢复与订正，不是该节第一次翻译。

所有页码为完整底本 PDF 的物理页，从1起数。法稿 §14 标题在83页顶部；英文标题在53页底，正文始于54页。新审内容严格止于法90页、英59页的 §15 标题之前。

| 新正文模块 | 法文连续范围 | 英文连续范围 | 接缝 |
|---|---|---|---|
| `v22_section14_geometry.tex` | 83—84全文及85至Grosso modo之前 | 53末标题、54全文、55前部 | 止于“F不是本节开头那个F” |
| `v22_section14_fibers.tex` | 85末 Grosso modo 至88首段末 | 55末至57的 More delicate 前 | 正则中心、爆破、14.1—14.3、模版本、CM必要性 |
| `v22_section14_differential.tex` | 88第二段至90的§15前 | 57的 More delicate 至59的§15前 | 14.4—14.6、微分限制、一般基底图式及最后说明 |

对应三份专题报告为同名 `_audit.tex`；另有 `reports/v22_integration_audit.tex`。各模块详细 `SOURCE_MAP.md`、源页摘录、实际看图和散列证据在 `recollation/v22/geometry/`、`fibers/`、`differential/`。来源对照所用相邻页及法21页只用于边界/交叉引用核查，不算新译范围。外部 Stacks 资料作为译者补证支点，不冒充法稿原文。

## 旧内容的精确保留

`continuations/v_dot_late.tex` 的49,224字节全文件不改。§15唯一标题起点位于字节34,610；其14,614字节后缀写入 `continuations/v22_section15_inherited.tex`。原§14前缀保存在 `recollation/legacy_v21/v21_section14_original.tex`。边界散列及拼接验证见 `checks/inherited_source_baseline.json` 和 `checks/current_structure_verification.json`。

原§14三段分别为字节 `[0,9292)`、`[9292,22560)`、`[22560,34610)`，各段原字节副本随专题证据保存。47条旧注 V-H-L001—047 保留于旧全文及分段副本；本轮活动正文改用41条 V22-GEO、V22-FIB、V22-DIF 注，不重复排印旧入口。

第二十一版194个正文、续篇、书末及报告TeX保留。原项目762个文件的保存位置见 `recollation/legacy_v21/RETAINED_PROJECT_FILES.json`；旧记录明确标为历史，不能充当第二十二版编译或目视证据。

## 接续

下一回校点为第一篇§15，法90末、英59，现有译文在 `continuations/v22_section15_inherited.tex`。先核其实际末条与相应底本，再逐段对照。正式第IV章主体是另一未完分支，位置及全部历史限制见本项目 `PENDING_ISSUES.md`、`PROGRESS.md` 和继承档案。
