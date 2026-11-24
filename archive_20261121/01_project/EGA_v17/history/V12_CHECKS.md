# 第十二版实际校验记录

日期：2026-11-16。PDF渲染与对比使用同一PyMuPDF/MuPDF版本；像素对比为72 dpi RGB。

## 源码恢复与覆盖
- 第十一版工程展开结果与实际交付单文件一致。
- 81个既有TeX文件的基线哈希已保存；79个未变。
- 两个修改的既有文件：text/remaining.tex（范围元数据）；backmatter/errata_IV_selected.tex（追加2项作者正式勘误并更新范围）。
- 56份既有数学正文文件保持逐字节不变。历史报告正文未改。
- 新译34个编号条目，25个公式/图标签，32条译校脚注，5个TikZ-cd块。
- 累计条目宏2325→2359，标签985→1010；多重集保留检查无丢失。
- 公式标签与条目数检查只证明结构保留，不证明内容正确。

## 构建
- 分文件main.pdf：1008页；report.pdf：209页。
- clean目录book_single.tex与audit_single.tex各自三遍XeLaTeX成功。
- 分文件日志与单文件最终日志保存在本目录。
- 早期有一次调用因执行时限中断，清理相关中间文件后重新编译；中断结果不计作有效构建。
- 所有最终输出均有正常结束的XeLaTeX日志。

## 对比
- 合订本1008页：文字不一致0页；72 dpi像素不一致0页。
- 报告209页：文字不一致0页；72 dpi像素不一致0页。
- 详见output_comparison.json、book_page_hashes.json、report_page_hashes.json。

## 最终日志
```json
{
  "book": {
    "source": "main.metadata2.txt",
    "latex_error": 0,
    "undefined_control_sequence": 0,
    "missing_glyph": 0,
    "overfull": 0,
    "undefined_references": 0,
    "underfull_hbox": 41,
    "underfull_vbox": 6,
    "font_warning": 4,
    "hyperref_pdf_string_warning": 0
  },
  "report": {
    "source": "report.finalpass3.txt",
    "latex_error": 0,
    "undefined_control_sequence": 0,
    "missing_glyph": 0,
    "overfull": 0,
    "undefined_references": 0,
    "underfull_hbox": 31,
    "underfull_vbox": 1,
    "font_warning": 4,
    "hyperref_pdf_string_warning": 14
  },
  "book_single": {
    "source": "single_build/book_single.metadata2.txt",
    "latex_error": 0,
    "undefined_control_sequence": 0,
    "missing_glyph": 0,
    "overfull": 0,
    "undefined_references": 0,
    "underfull_hbox": 41,
    "underfull_vbox": 6,
    "font_warning": 4,
    "hyperref_pdf_string_warning": 0
  },
  "report_single": {
    "source": "single_build/audit_single.pass3.txt",
    "latex_error": 0,
    "undefined_control_sequence": 0,
    "missing_glyph": 0,
    "overfull": 0,
    "undefined_references": 0,
    "underfull_hbox": 31,
    "underfull_vbox": 1,
    "font_warning": 4,
    "hyperref_pdf_string_warning": 14
  }
}
```
字体替代为数学花体小字号的非致命提示；未更换CTeX默认中文字体。
书签提示来自数学命令在PDF书签字符串中的规范化，不是正文缺字。

## 视觉检查
- 已查看新增正文PDF365—386页及与第I章衔接的387页缩览。
- 已查看本轮新核查报告PDF15—24页缩览。
- 已放大检查合订本366页（校订c条件及脚注）、370页（三行交换图及脚注）、385页（无限p秩例子与符号校订）；报告18页（平方零修补的具体计算与证明）。
- 相关缩览与抽查图保存在renders/；其他关键页和新增作者勘误也予以渲染检查。
- 全1217页已按同一渲染器计算像素哈希；没有声称全部页面均以高分辨率逐字人工审阅。
- 技术检查与数学审校分开：本轮不替代出版级逐句核对，不重新确认所有历史核查判断。
