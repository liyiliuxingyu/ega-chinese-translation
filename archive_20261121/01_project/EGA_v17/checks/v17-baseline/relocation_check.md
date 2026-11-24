# 工程新目录接续编译检验

**结果：通过本次目录迁移检验。** 在清除运行缓存、改变目录且路径含中文及空格的条件下，工程实际重新生成本地 XeLaTeX 格式，并用未修改的当前 `preamble.tex` 编译出一页中文、数学及交换图探针。

## 实测复制与缓存清理

- 原工程：`/workspace/scratch/a886fd56dd2f/work/EGA_v17`。
- 新目录：`/workspace/scratch/a886fd56dd2f/integration/EGA 迁移验证 zorgz4gr/第十七版 续作工程`。
- 复制 657 个文件，共 83,993,361 字节，复制前后逐文件 SHA-256 一致。
- 排除 `runtime/texmf-var`、`runtime/texmf-config`、`single_build`、`__pycache__`、根目录构建辅助文件及既有 `layout_probe.*`。source 之前新目录没有 `.fmt`。
- shell 启动于新工程父目录；使用带中文与空格的绝对路径 source 脚本，正确解析出新工程根目录。

## 实际执行

完整调用、基线查询和 stdout/stderr 见 JSON 及 `relocation_logs/execution_initial.json`。使用 `bash --noprofile --norc`；清理可能存在的 TeX 环境覆盖变量，本次起始环境实际没有此类覆盖变量。核心脚本为：

```bash
set -euo pipefail
ega_reloc_project=$1
source "$ega_reloc_project/scripts/tex_environment.sh"
cd "$ega_reloc_project"
for pass in 1 2; do
  xelatex -interaction=nonstopmode -halt-on-error -recorder relocation_probe.tex > "relocation_probe.pass${pass}.stdout.txt" 2>&1
done
```

## 实际结果

- 起始系统查询找不到 `ctexbook.cls` 和 `xelatex.fmt`。首次执行退出码 0，耗时 15.561 秒。
- CTeX 与 FandolSong 字体由新目录的 `vendor/texmf` 提供；新格式在本地 `runtime/texmf-var/web2c/xetex/xelatex.fmt` 重新生成。
- 格式文件 4,095,526 字节；SHA-256：`14e8d54902949ce9e60fc0a7d028e31258ce32bbaa9884f5d1f077ebbf6df68f`。
- 最终探针两遍编译成功，PDF 一页；SHA-256：`03ecc28b311a5642b547a289b18339304aa297da7a18fd553d74309aaf6b3642`。
- 首轮探针长公式同行有 4.63205 pt 超宽；仅在临时探针中换行，重编后无超宽或缺字。保留首轮日志，未修改正文或导言。
- 已渲染并实际查看最终探针：中文、上下标、公式、交换图四条箭头与标签、脚注均完整可读，无重叠或裁切。
- 记录器读取 192 个唯一文件，其中 20 个来自新工程、172 个来自系统 TeX；没有读取原工程路径。
- 最终日志仅有 `mathrsfs` 字号替代警告，无 `Missing character`、`Overfull` 或 TeX 错误。

## 依赖界限

实测引擎：`XeTeX 3.141592653-2.6-0.999996 (TeX Live 2025/dev/Debian)`，使用 `/usr/bin/xelatex`、`/usr/bin/xetex`、`/usr/bin/kpsewhich`。系统输入位于 `/usr/share/texlive/texmf-dist` 及 `/etc/texmf/web2c/texmf.cnf`，涉及基础 LaTeX、AMS、PGF/TikZ、系统字体和配置；逐文件列表保存在 JSON 与 `.fls`。

`vendor/texmf` 是补充宏包/字体集合，**不是完整 TeX Live**。新环境仍须提供系统 XeTeX/XeLaTeX、Kpathsea 和相应基础宏包。全书 `build.sh` 另需 Python 3；本次没有在新目录重编全书，也未验证另一操作系统或 TeX 发行版。

## 证据与并发变更说明

必要日志、验证脚本、探针源、截图与复制清单保存在 `checks/relocation_logs/`。二进制 `.fmt` 与探针 PDF 只留在临时目录，没有作为图书正文或 PDF 交付。这里的探针源/截图均为检查证据。

根代理在迁移试验进行时独立修订 frontmatter.tex：删除 IV.1 物理第 221 页所对应的未经明印页码“印刷第 222 页”，并重编主稿为 df949bd9daa04547214b6e3c68e066812be0fb2918601c0d6403cccfce568046。迁移探针不读取前言或主稿；preamble、环境脚本、build.sh 和数学正文未因本试验改变。这不是迁移检验造成的修改。

被测构建输入的哈希没有变化；以下对照同时保留复制时与报告写入时的状态，避免将根代理的独立修订混入迁移试验。

| 文件 | 报告时 SHA-256 | 与复制时一致 |
|---|---|---|
| `preamble.tex` | `8b6a2fd4a276a66c543be909c637c2a4ff6a380a8261518932fe4e910e540dd3` | 是 |
| `build.sh` | `a94d376b90abf3165c2f38216ebabe63ff3ff8bd2d402fc1106d7ada36aea258` | 是 |
| `scripts/tex_environment.sh` | `5789d403e386f4240d62cceb6ba7e52a9837916a5310486579abcfbf8e10e61c` | 是 |
| `main.tex` | `9c180dd2b32c8bf55546793176703b052a7f2a4b2655193b46214428b12314c7` | 是 |
| `report.tex` | `34d7e7aeb59d4765747b611de2f2269ff353294562783c4ba2ea6c83bf43012b` | 是 |
| `main.pdf` | `df949bd9daa04547214b6e3c68e066812be0fb2918601c0d6403cccfce568046` | 否；根代理独立前言修订 |
| `report.pdf` | `b61fe870fd83b90a505893ecfc8403fafb9037053bc452f0ae7b723e9e401949` | 是 |
| `frontmatter.tex` | `f8ef311b6c88b44ee444efb12529e7e255f35cca56f8afc9232684deb499483b` | 否；根代理独立前言修订 |
