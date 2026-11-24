# 第十三版最终检查记录

## 来源和完成范围
来源工程V12展开后与实际交付V12单文件相同（source_provenance.json）。
实际译入0_IV §22章首、22.1—22.3，20条，终点22.3.4；下一条22.4.1。
3项作者勘误据IV.4页面核对；22.3.3的OCR误识已排除。

## 编译
main、report、book_single、audit_single均3遍返回0；详见build_results.json。
独立单文件在清空辅助文件的目录编译。最终书1028页、报告219页。
中间一次被中止的试编译留下截断aux，已清空并重新完整编译；最终记录仅对应重新完成的构建。

## 全页对比
1247页文字一致；同一渲染器72 dpi像素逐页一致；不一致页均为0。
详见output_comparison.json及book_page_hashes.json、report_page_hashes.json。
非PDF字节相同检查：时间等PDF元数据可以不同。

## 源码保留
63份既有数学正文文件及所有既有报告正文逐字节未改。
更改的既有范围文件为text/remaining.tex；backmatter/errata_IV_selected.tex仅追加本轮勘误。
条目宏2359→2379，公式标签1010→1016；旧项无丢失，见structure_check.json。
另有3个原编号文字条件22.1.3.1—22.1.3.3，未计作公式标签。
新文包括9个tikz-cd块、21条M13脚注。

## 最终日志
主书：0编译错误、0未定义控制序列、0缺字、0未定义引用、0overfull；47条underfull提示、4条字体警告（含汇总）。
报告：相应错误和overfull均0；34条underfull、4条字体警告、14条hyperref书签文本规范化提示。
独立单文件的各类提示数量与分文件一致。详见final_log_summary.json及保存的最终log。
不将上述非致命提示隐瞒为“零警告”。

## 视觉与数学边界
见VISUAL_REVIEW.md。已查看新增及修改范围，不声称放大审查全部1247页。
M13-E01有非完备环反例；N03/N05是保留原条件(i)的作用域解释；G项是补证，A项是作者已有勘误。它们不等价于相同数量的错误定理。
特征2算例另用SymPy核对基础商环计算（char2_example.json），该检验不代替报告中的证明。
既有H8-P01等事项仍待核；未完成全书独立审定。
