# 第六版实际构建与检查记录

1. 原始输入SHA256：source_hashes.json。
2. 旧正文35文件字节未变；2090个旧编号宏条目、848个旧公式标签全部保留；新增46条目、1公式、7个tikz-cd图。见structure.json。
3. main/report分文件工程与book_single/audit_single独立源码均三遍编译完成。最终日志见final_*.log。
4. 合订本900页、报告123页；独立源码与分文件工程逐页文字相等，MuPDF 72dpi逐页像素相等。页级哈希保存在main_page_hashes.json、report_page_hashes.json。
5. 新增正文PDF258—278页与本轮报告PDF11—20页渲染为108dpi PNG；查看缩览，并放大检查交换图、撤销提示、反例和脚注。19.2的页尾孤立标题已修复。
6. 最终日志无LaTeX错误、未定义控制序列、未定义引用、缺字和Overfull。Underfull与数学字体字号替代仍存在，如实记录于validation.json。
7. 例子脚本只检查报告给出的有限有理数/多项式等式，不是一般定理的形式化证明。
8. 未声称本轮逐句或逐证明审定全部旧稿；报告的历史部分保留原有结论与当时措辞。
