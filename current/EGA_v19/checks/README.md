# 当前核验与历史记录

第十九版的实际全局核验文件为：

- current_source_inputs.json 与 current_structure_verification.json：实际输入链、展开结果及继承源码；
- current_build_log_summary.json 与 current_build_logs/：最后四份真实构建日志；
- current_pdf_parity.json：模块稿与独立单文件稿每一页的文字、尺寸及72dpi像素比对；
- visual_verification_summary.json 与 v19_visual_final/：实际查看范围以及最终PDF/图像绑定；
- current_build_run.json：实际最终输出和执行记录。

历史记录保留：history_v18/内文件，以及本目录其他未以current_或v19_开头的既有记录/旧图片，均是第十八版制作时的证据，不能作为第十九版本轮通过的证明。其原内容继续保留供追踪。比如early_final_visual_review.json和middle_final_visual_review.json是旧版，不要用这些名称中的final推断当前版已验。

recollation/engineering/ 中首轮视觉记录可能绑定排版修正前的校样；其中发现的问题须以本目录visual_verification_summary.json的最后闭环为准。

文件散列、构建成功、逐页像素一致和人工抽查各有独立含义，均不代替全书数学证明的审定。
