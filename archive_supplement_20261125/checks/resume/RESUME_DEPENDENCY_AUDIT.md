# 第十九版接续依赖与上传完整性核查

核查对象：`liyiliuxingyu/ega-chinese-translation` 的固定提交 `4daf708a87069e2a6e28c22a29d3e3af26880f0b`。

本次在从 GitHub 重新取得的完整检出上实际执行只读检查，未修改发布工程，未重编译，也未重新进行数学审定。

## 结论

**未发现会阻断当前译稿重建或新对话接续的漏传文件。**

| 核查项目 | 本次实际结果 |
|---|---|
| 根入口与导入回执 | README、AGENTS、CONTINUE_HERE、EDITION_19_IMPORT 四项均存在 |
| 当前进度与接续说明 | README、AGENTS、PROGRESS、HANDOVER_STATE、ARTIFACTS、SOURCE_MAP、PENDING_ISSUES 七项均存在 |
| 构建与检查工具 | build.sh、展开脚本、TeX 环境脚本及四项主要检查工具均存在 |
| 实时源码依赖图 | 主稿含驱动共143项，报告含驱动共35项；共177个不同源码文件全部存在且匹配所记录的字节数及SHA-256 |
| 单文件源码 | 实际重新展开的两份内容均与发布的single.tex、report_single.tex完全一致；无残留外部input/include/includegraphics依赖 |
| 成品及证据 | ARTIFACTS列出的10项文件、绑定的4份检查JSON、4组原始与归档构建日志、62张最终样页，散列均匹配 |
| 继承文件 | 对照仓库中的第十八版，167项既有TeX文件字节不变 |
| 历史恢复 | restore_versions.py、package_common.py、恢复索引和全库检查脚本均在；v17、supplement_III、supplement_III_delta的1827、753、40条保存路径均存在 |
| 随包排版资源 | ctexbook类及Fandol默认中文字体、许可均在；外部TeX发行版等环境要求已在README说明 |

下一法英回校位置仍是法文物理64页§12／英文物理43页中段，现有译文在 `continuations/v_dot_middle.tex`；这些位置与真实入口一致。该点是回校接续点，不是所有译稿的最后一页。全部EGA书籍并未完成。

## 后发布临时记录

上轮发布后在工作区产生的以下独立核验副本没有写入这一冻结提交：

- PUBLICATION_VERIFICATION.json
- REMOTE_TREE_VERIFICATION.json
- REMOTE_ENTRYPOINT_REVIEW.json、REMOTE_ENTRYPOINT_REVIEW.md
- REMOTE_RELEASE_METADATA.json
- PUBLISH_WORKFLOW_VERIFICATION.json
- OVERLAY_VERIFICATION.json

这些文件记录远端发布检查，属于可由固定Git树、发布标签、Release附件及Actions记录重新生成的副本。其缺席没有移除任何正文、TeX依赖、底本或接续说明。若补充归档，应把本次实跑的结果作为新的核查记录保存，不能冒称找回了已不存在的上轮原始文件。Release专属的PACKAGE_VERIFICATION.json、SHA256SUMS.txt由父任务另行核对。

## 范围与复现

机器结果见同目录 `RESUME_DEPENDENCY_AUDIT.json`，检查程序为 `audit_resume.py`。程序只读取所指定仓库，并把结果写到仓库外；未重新运行会改写交付检查记录的官方检查脚本。本结果不代替父任务的全库清单核验、Release ZIP逐成员核验、历史附件覆盖核查或Dot原包核查。

复现：

```bash
python3 audit_resume.py /path/to/repository /path/to/output/RESUME_DEPENDENCY_AUDIT.json
```

Bash、Python、XeLaTeX和相应TeX宏包属于已说明的运行环境依赖。PyMuPDF用于逐页输出比较，SymPy用于另外列明的符号计算；当前工程没有宣称包含完整跨平台TeX发行版。因此这些系统环境依赖不计为漏传工程文件。
