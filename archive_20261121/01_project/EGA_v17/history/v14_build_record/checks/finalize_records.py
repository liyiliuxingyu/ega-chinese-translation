from pathlib import Path
import json,shutil,hashlib,fitz
R=Path(__file__).resolve().parents[1]
v=json.loads((R/'checks/output_verification.json').read_text());s=json.loads((R/'checks/structure.json').read_text())
assert all(x['all_text_equal'] and x['all_pixels_equal'] for x in v['pairs'].values())
assert all(x['latex_errors']==x['missing_chars']==x['undefined_references']==x['overfull_boxes']==0 for x in v['logs'].values())
for name in ['README.md','PROGRESS.md']:
 p=R/name;h=R/'history/v13_check_records'/('v13_'+name)
 if not h.exists():shutil.copy2(p,h)
book=v['pairs']['book']['pages_main'];report=v['pairs']['report']['pages_main']
(R/'README.md').write_text(f'''# 代数几何基础·中文译校合订本（第十四版）

## 文件与范围
- main.pdf：{book}页合订本；main.tex是分章节工程入口。
- single.tex：可独立编译的完整合订本源码。
- report.pdf：{report}页累计译校核查报告；report.tex为工程入口。
- report_single.tex：报告的独立单文件源码。
- PROGRESS.md：实际完成范围、下一接续点及未译范围。
- checks/：真实来源哈希、结构检查、日志、逐页对照与新增页视觉记录。

本轮连续译入第0章22.4—22.5，从（22.4.1）至（22.5.10，ii）末尾。
下一接续点为22.6章首及（22.6.1）。这不是全部上传材料的完结全译本。
正文使用本轮校订形式；原文错误、修改理由及依据在脚注；长反例和补证在报告。
历史报告保留原文，不表示本轮重新审定全部旧判断。

## 编译
需要XeLaTeX与标准TeX Live的CTeX、AMS、TikZ-cd等宏包。字体采用CTeX默认配置，不附字体文件。
在工程根目录执行：
```bash
bash build.sh
```
验证独立单文件构建：
```bash
bash build.sh --verify-single
python3 checks/check_structure.py
python3 checks/verify_outputs.py
python3 checks/finite_cotangent_check.py
```
前两项脚本分别进行结构保存和完整逐页文字／72 dpi像素比较；PDF比较需要PyMuPDF。
有限环余切空间检验仅使用Python标准库，不把有限阿廷商环误称为正则环。
也可将single.tex或report_single.tex单独放入干净目录，XeLaTeX连续编译三遍。

## 版式
实际文档类为ctexbook，默认字体、字号、版心、页眉和双面分页保留。
沿用四位数目录页码栏宽度修正；22.5标题前增加局部分页，避免标题孤留在前一页脚注上方。
原著页码与合订本页码不同，原目录和索引仍保留原著页码。

## 检查边界
全页构建一致性不等于逐页人工数学审校。人工视觉复核集中于新增正文、报告和本次调整页。
详情见checks/CHECKS.md和checks/VISUAL_REVIEW.md。压缩包不附原文PDF或字体文件。
''')
(R/'PROGRESS.md').write_text(f'''# EGA中文译校合订本：第十四版实际进度

记录日期：2026-11-17。
合订本：{book}页；累计核查报告：{report}页。
文档类：`\\documentclass[UTF8,a4paper]{{ctexbook}}`。

## 来源恢复
以用户已上传第十三版完整工程及独立单文件源码恢复；展开工程与上传的第十三版TeX逐字一致。
确证见checks/source_provenance.json。没有把聊天中的进度声明替代源码证据。
底本：用户上传EGAIV.1.pdf，PDF第192—204页中属于22.4—22.5的部分；原分册印刷第193—205页。
关键公式、反例与混合特征断言均对照扫描页核读。

## 本轮实际完成
22.4全部：（22.4.1）至（22.4.8），含子编号22.4.4.2、22.4.4.7、22.4.7.4。
22.5全部：（22.5.1）至（22.5.10，ii）末尾。
共21个原著编号条目、26个原编号公式／图标签、3幅TikZ-cd交换图、14条N14译校脚注。
新源文件：continuations/iv0_22_4a.tex、iv0_22_4b.tex、iv0_22_5a.tex、iv0_22_5b.tex。
新核查：reports/fourteenth_audit.tex。
本轮新增正文位于合订本PDF第403—417页；报告新核查位于PDF第15—21页。

## 下一连续接续点
**第0章22.6“Zariski的Jacobian判据”及（22.6.1）。**
EGAIV.1.pdf第204页（原分册印刷第205页），在22.5.10(ii)后。
为辨认边界而读取的22.6内容没有计为译完。

## 累计与未译范围
第0章§§1—21及22.1—22.5已经连续收入。
第I、II章及第III章两个已出版分册的译文沿用已有工作稿。
第V卷预备笔记仍只含此前已译部分；“超平面截面与锥投影”的下一条为7.1。
未译：第0章22.6—22.7、§23，第IV章主体及未完成书末材料，第V卷预备笔记余文。
尚非全部材料的完结全译本。

## 本轮主要修订
N14-E01（22.5.4）：混合特征下原正则性等价关系有反例，A=Z_(p)、B=A[T]/(T^p-p)。
正文不只缩小为等特征情形，而给出完整修订：b）、c）等价于“B正则，且p的余切类在A与B中同为零或同非零”；c）的目标改为m/(m²+pA)。
反例、双向证明及等特征特例写入报告。后续22.5.7、22.5.8的域上证明不使用错误的一般化。
N14-E02（22.5.6）：证明中的提升必须是结构同态指定的像，不能为同一剩余类的任意代表；引理结论不变。
N14-E03（22.5.10）：原例漏写生成元Z。正文改为K=k(Z,X^(1/p)+ZY^(1/p))，证明其不可分性及K^p∩k=k^p。
N14-G01（22.5.2）：无限维情形不直接套用诺特结构定理，另给有限滤过及基数证明。
T/N/G类脚注另有引用、商理想平方、张量后取核、p商空间及有限支撑的澄清；不按脚注条数统计错误定理。
上述独立修订标为译者校订，没有冒称作者正式勘误。旧版H8-P01等待核问题不作已解决处理。

## 实际校验
67份既有数学正文文件和15份历史报告正文逐字节未变。
原编号条目宏2379增至2400；原公式标签1016增至1042；多重集对照无丢失。
四组构建均经XeLaTeX三遍编译；当前分文件与独立单文件的全部{book+report}页文字和72 dpi渲染像素一致。
最终日志无编译错误、缺字、未定义引用或overfull溢出；有underfull、字体字号替代及历史报告书签规范化提示，实际数量见checks/output_verification.json。
报告两个中文数学下标缺字已修正；22.5标题孤留页末已通过局部分页处理，重编译后复查。
技术检查和本轮定点证明分析不等于全书独立出版级审校。
''')
(R/'checks/CHECKS.md').write_text(f'''# 第十四版检查记录

## 构建与结构
合订本{book}页，报告{report}页。主工程与独立TeX各三遍XeLaTeX编译成功。
全部{book+report}页逐页文字一致，PyMuPDF {v['renderer']}、72 dpi渲染像素一致。这里只比较同渲染器构建一致性，不声称跨渲染器一致。
原67份数学正文、15份历史报告源文件哈希未变；条目宏2379→2400，公式标签1016→1042，无旧项丢失。
详见structure.json、output_verification.json和source_provenance.json。

## 最终日志
{json.dumps(v['logs'],ensure_ascii=False,indent=2)}

最终无错误、缺字、未定义引用和overfull。underfull不作为编译错误；字号替代与历史报告书签警告如实保留。
此前报告两处\\mathrm{{原}}导致缺字，已改为\\text{{原}}后重编译；本记录只对最终日志作判断。
22.5标题曾孤留页末，已在新小节前局部分页，重编译与渲染复核完成。

## 计算与数学边界
finite_cotangent_check.py对p=2,3的有限商环做穷举余切空间检验。它验证有限模型的理想大小与p余切类，不代替原无限局部环的正则性证明。
N14-E01的修订证明和N14-E02/E03的反例、修补在报告中明确标为译者分析。
未对全部旧数学证明重新独立审定；未将未译范围计作完成。
''')
(R/'checks/VISUAL_REVIEW.md').write_text('''# 新增页与调整页视觉检查

使用PyMuPDF渲染，缩览约108 dpi，关键页126 dpi。
查看了合订本新增与衔接页PDF第402—418页的缩览；放大查看406（大型交换图）、412（小节标题和长脚注）、413—414（混合特征修订与证明）、415（指定提升）、417（反例及接续说明）。
查看报告新增主体PDF第15—21页的缩览，以及18（中文数学下标修复）等关键页放大图。
查看了封面、说明和目录相关页缩览，四位数目录页码沿用前版加宽栏，不改变正文版心。
小节22.5标题孤留页末问题已修正。报告“原”字下标已恢复，没有以缺字警告为可忽略项。
本轮检查未见新增页文字或公式裁切、重叠、缺字黑块；不声称对全部1273页人工逐页放大检查。
默认双面排版产生的空白偶数页保留，未为增加页数插入空白页。
''')
# Preserve final build logs in a location included in the package.
logs=R/'checks/logs';logs.mkdir(exist_ok=True)
for n in ['main.log','report.log','single_build/book_single.log','single_build/audit_single.log']:
 shutil.copy2(R/n,logs/Path(n).name)
print('Records finalized',book,report)
