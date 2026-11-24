# 第十八版检查记录入口

最终结论先读 `current_structure_verification.json`、`current_build_log_summary.json`、`current_stdout_verification.json`、`current_pdf_parity.json` 和 `visual_verification_summary.json`，并以根项目 `ARTIFACTS.json` 绑定实际成品。

`initial_four_build_run.json` 保存首次四份PDF构建；`layout_rebuild_run.json` 保存前言及脚注分隔的主稿重建；`standalone_rebuild_after_flatten_fix.json` 保存展开器修复后的独立版构建；`current_build_run.json` 保存最后两处段落边界修复的主稿/独立版重建。最终报告沿用首次模块构建和修复展开器后的独立构建。

`parity_first_failure.json`、`parity_after_line_fix.json` 和 `middle_single_file_diagnosis*` 是确实发生的中间失败及诊断，不是最终交付失败状态。原始失败PDF、相关页面图和文字保留，以便追溯。`main_before_layout_fix.pdf` 与 `main_before_paragraph_fix.pdf` 是已明确标识的中间版本，不能作为默认成品。

各组 `*_final_visual_review` 记录绑定实际查看时的PDF散列；若其中写着等待父代理版本绑定，应读 `visual_verification_summary.json` 及最终页面比较，不能删去或改写历史观察来伪造一次新的查看。

散列、输入图、构建日志、像素一致和抽样页面各有不同用途；均不表示全书逐句或全部一般数学命题已经审定。
