# §16 前半最终本地预览核验

日期：2026-11-26。范围为独立模块预览，不是完整合订本的最终核验。

## 实际构建

使用工程代理已经配置的 `v24_work/EGA_v24/scripts/tex_environment.sh`，然后运行：

```bash
xelatex -interaction=nonstopmode -halt-on-error -file-line-error preview.tex
xelatex -interaction=nonstopmode -halt-on-error -file-line-error preview.tex
xelatex -interaction=nonstopmode -halt-on-error -file-line-error audit_preview.tex
```

正文最终两次运行均成功，报告在修正表格边缘留白后成功。实际生成 `preview.pdf`（10页）和 `audit_preview.pdf`（9页），使用真实 `ctexbook` 和默认中文字体。没有另换字体、页面几何或缩小整页。

## 实际渲染和观看

两份 PDF 均以 PyMuPDF 的 1.5 倍矩阵逐页渲染。正文最终10页均在脚注锚点布局修正后逐页实际观看；报告最终9页均在表格修正后实际观看，随后只重编译正文而未改报告输入。逐页图片 SHA-256、最终 PDF SHA-256 和源文件 SHA-256 见 `validation_early.json`。

正文检查包括标题及定义跨页、数学行内及显示公式、法文删除段的译校脚注、三幅交换图、最长脚注和结尾 K 图。最终没有发现裁切、缺字、脚注标号独占空行或公式越界。报告两张长表、矩阵、正合列、反例和证明均完整。

日志未出现编译错误、Overfull、Missing character 或未定义引用。保留标准 rsfs 字号替代警告；报告有一处 Underfull（badness 1565），目视未造成截断或内容丢失。没有为消除此类默认数学字体警告修改书籍默认格式。

## 最终文件

| 文件 | 字节数 | SHA-256 |
|---|---:|---|
| `v24_section16_early.tex` | 30,917 | `5d7ec3073f921a23b05c87905c8d800cff580f49eb3490f7f7561a1f659fb553` |
| `v24_section16_early_audit.tex` | 17,895 | `77f27fe61dc37f6386fc3191a24c4fcda4dd0e8cbac78a617ffbd82f0beed2c4` |
| `preview.pdf` | 380,725 | `f7d1715f06346d0e6cf16a93e91a8775fcf067e797fb160826a38725a77c67ef` |
| `audit_preview.pdf` | 326,357 | `856aba30dbfd4cbc25fab747cc6c004273ccb49ea80942bda5776d731351e169` |

本记录没有声明完整合订本已编译、已发布或上传。正式整合仍需由 root/engineering 完成后对相应最终 PDF 另作实际图检。
