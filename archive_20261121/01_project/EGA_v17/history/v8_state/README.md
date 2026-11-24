# 《代数几何基础》中文译校合订本，第八版

- `main.pdf`：932页当前已译内容合订本。
- `report.pdf`：153页累计译校核查报告。
- `single.tex` / `report_single.tex`：分别可独立编译的完整源码。
- `main.tex` / `report.tex`：分文件入口。
- `PROGRESS.md`：真实覆盖、未译范围、待核事项和下一接续点。
- `checks/`：条目/公式覆盖、旧正文哈希、逐页文字及像素比较、日志和视觉检查范围。
- `history/`：既有版本来源、差异与历史检查记录；历史页数/接续点不是当前进度。

## 编译

需要包含CTeX的TeX Live或MiKTeX、XeLaTeX、amsmath、amssymb、amsthm、tikz-cd、enumitem、longtable、booktabs、array、needspace、footmisc、adjustbox、hyperref、bookmark等宏包。正文采用文档类的默认字体；工程不提供或分发字体文件。

在项目目录执行：

```bash
bash build.sh
bash build.sh --verify-single
```

脚本先展开源码，XeLaTeX运行三遍（前两遍`-no-pdf`，第三遍输出PDF）。第二条命令还把两份单文件复制到独立`single_build/`中重编译。也可单独对`single.tex`或`report_single.tex`连续运行XeLaTeX三遍。

检验代码的Python依赖为PyMuPDF；重新运行`python checks/validate_v8.py`须先完成`--verify-single`。覆盖比较脚本默认使用工程所存第七版单文件快照。

交付ZIP保留最终PDF、源码和最终检查记录，不包含体积较大的中间XDV/辅助文件和单文件构建的重复PDF；需要时可重建。

## 校订范围

本版新增第0章19.7—19.10，共32个编号条目。确定错误已按“正文校正、脚注记录原文差异”处理。19.7.1.5的较弱拓扑版本仍待核，正文采用明确标记、已证明并足够支持后文的完备局部形式，原文及证明完整保存在报告。未译材料和旧文未复审部分绝不计作完成或审定。
