# 第24版第16节后半交接

## 已完成的实际工作

正文 `v24_section16_late.tex` 与报告 `audit.tex` 已核定并冻结，正文自成作用域，报告有独立章节标题。法文104–111全部逐段保留，兼收英译68的划去编者说明；段落标识30个，编号译校脚注28条，报告B01–B12。§17只作边界和术语依据，没有把其原有译文算成本轮新增。

完整来源映射见 `SOURCE_MAP.md` 与 `paragraph_map.json`；旧附56–62每个小标题的数学内容去向见 `OLD_NOTES_MAP.md`，报告B12亦有概览。正文对应工程接口 `continuations/v24_section16_late.tex`，报告对应 `reports/v24_section16_late_audit.tex`。两文件共同接入后仍须由根代理和工程代理检查整合页码、接缝及最终PDF。

## 编译与视觉证据

`preview.tex`、`preview_preamble.tex`、正文及报告构成这份17页的独立检查工程。配置完整的XeLaTeX/ctex发行版后，在该目录运行两遍 `xelatex -interaction=nonstopmode -halt-on-error preview.tex` 即可。此工作区实际使用上层EGA_v24的 `scripts/tex_environment.sh` 提供工程字体/格式搜索环境，未改ctexbook字体、字号或版心。

最终两个成功编译日志是 `compile7.stdout.txt` 和 `compile8.stdout.txt`；`preview.log`：0 Overfull，0 缺字，0 LaTeX/Package warning，2 Underfull。正文预览1–8页，报告9–17页。所有17页均渲染并实际查看，报告最后补回旧反例后重看受影响的12–17页。`FINAL_EVIDENCE.json` 绑定源稿、PDF、日志、逐页PNG与底本的真实SHA-256。它只证明本分工预览，不代替整合后最终PDF的检查。

## 应保留的数学边界

- 命题8的Hilbert函数、下界不能推出线丛、引理8.1正秩例外，均已落实正文与原错脚注。
- 命题9/推论10在1≤m≤n下陈述；相对二阶判别在1≤m≤d下陈述。零维空泛极化与前半EAR034对应，不擅自宣称处理所有m>d边界。
- 命题9无需另加完备/分离；极化同构自动使W有限投射，双向有限阶消元补证在B05。
- 分歧建议仍保留作者“未详细验证”的语气；B10仅明确证明以Fitt₀相对微分定义的源端分歧子预概形等式。
- 最大子式退化轨迹原≥方向改为每分支余维≤；不能从上界推出前段预期维数等号。
- 旧注“英文重复V⁰”无据，已据实际英文V⁰/V′撤回归责。

未修改当前v23、archive或其他代理目录；未作远程写入。根代理可据 `SHA256SUMS` 接入本快照。
