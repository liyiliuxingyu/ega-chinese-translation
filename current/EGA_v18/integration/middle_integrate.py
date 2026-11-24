#!/usr/bin/env python3
"""Integrate immutable Dot batches 100--108 without modifying the source archives."""
from pathlib import Path
import hashlib, json, re

REPO = Path(__file__).resolve().parents[3]
PROJECT = REPO / 'current/EGA_v18'
SRC = REPO / 'dot_updates_20261124/batches'
OUT = PROJECT / 'continuations'
INTEG = PROJECT / 'integration'
names = {
100:'EGA第五卷_法文覆盖审计_例外超平面余维.tex',
101:'EGA第五卷_法文覆盖审计_Serre条件与截面.tex',
102:'EGA第五卷_法文覆盖审计_截面余维下降.tex',
103:'EGA第五卷_法文覆盖审计_Serre原阶保持判据.tex',
104:'EGA第五卷_余法射影丛与奇异零概形.tex',
105:'EGA第五卷_奇异参数维数与超奇异判据.tex',
106:'EGA第五卷_对偶超曲面的泛双有理性.tex',
107:'EGA第五卷_双切超平面与特征零判据.tex',
108:'EGA第五卷_几何正则性的例外超平面.tex',
}
lines={n:(SRC/f'batch{n}'/name).read_text().splitlines() for n,name in names.items()}
old_path=PROJECT/'continuations/v_dot_early.tex'
old_lines=old_path.read_text().splitlines()
old_segment='\n'.join(old_lines[53:431])+'\n'
(INTEG/'middle_legacy_segment.tex').write_text(old_segment)

# A local namespace prevents these standalone batches from redefining shared symbols.
local=r'''\begingroup
\def\PP{\mathbb P}\def\OO{\mathcal O}\def\Ocal{\mathcal O}
\def\F{\mathcal F}\def\G{\mathcal G}\def\N{\mathcal N}
\def\PD{\check P}\def\Pdual{\check P}
\def\Ys{Y^{\mathrm{sing}}}\def\Ysing{Y^{\mathrm{sing}}}
\def\Ds{Y^{\mathrm{sup\,sing}}}\def\Ysup{Y^{\mathrm{sup\,sing}}}
\def\cod{\operatorname{codim}}\def\Sing{\operatorname{Sing}}
\def\depth{\operatorname{depth}}\def\coprof{\operatorname{coprof}}
\def\Ass{\operatorname{Ass}}\def\Supp{\operatorname{Supp}}
\def\Gr{\operatorname{Gr}}\def\Spec{\operatorname{Spec}}\def\Proj{\operatorname{Proj}}
'''
body_ranges={
100:[(20,40)],101:[(18,28)],102:[(22,63)],103:[(22,66)],
104:[(21,54),(59,97),(102,106)],
105:[(21,24),(32,41),(51,52)],
106:[(22,44),(52,73),(78,82)],
107:[(18,23),(37,44),(54,58),(63,64),(70,71)],
108:[(18,41),(64,69)],
}
report_ranges={
100:[(41,62)],101:[(31,76)],102:[(66,90)],
103:[(68,68),(71,96)],
104:[(55,57),(99,100)],
105:[(26,29),(43,49),(55,66)],
106:[(46,50),(75,76)],
107:[(25,35),(46,51),(60,61),(66,67)],
108:[(43,62),(72,87)],
}
pages={
100:('30--32','21--22'),101:('32--33','22'),
102:('33--34','22--24'),103:('32、34--35','24--25'),
104:('36--39','25--27'),105:('39--40；另对读41--42','27--29'),
106:('41--43','28--30'),107:('43--45','30--31'),108:('45--46','31；另对读32'),
}
def take(n,ranges):
    return '\n\n'.join('\n'.join(lines[n][a-1:b]) for a,b in ranges)
def clean(s):
    return re.sub(r'(?m)^\\newpage\s*$', '',s).replace(r'\footnote{',r'\transnote{')
def replace(s,a,b):
    if a not in s: raise ValueError('missing replacement: '+a[:90])
    return s.replace(a,b,1)
def report_pointer(n,phrase='相关译校补证'):
    return rf'\transnote{{{phrase}完整保存于核查报告“D18-{n}”项，属译校文字，不是原文。}}'
# Preserve the complete note wording as a dated historical record, not current claims.
def extract_notes(s):
    pat=re.compile(r'\\(transnote|ednote|orig|cmt|footnote)\{')
    ans=[]
    def arg(start):
        if s[start]!='{': raise ValueError('expected {')
        d=1;i=start+1
        while i<len(s) and d:
            if s[i]=='\\' and i+1<len(s) and s[i+1] in '{}%':
                i+=2;continue
            if s[i]=='{':d+=1
            elif s[i]=='}':d-=1
            i+=1
        if d:raise ValueError('unbalanced note')
        return s[start+1:i-1],i
    for m in pat.finditer(s):
        a,e=arg(m.end()-1)
        ident=None
        if m.group(1)=='cmt':
            ident=a
            while s[e].isspace():e+=1
            a,e=arg(e)
        line=54+s[:m.start()].count('\n')
        ans.append({'macro':m.group(1),'line':line,'id':ident,'text':a})
    return ans

body={}
for n in names:
    body[n]=clean(take(n,body_ranges[n]))
    # Non-numbered batch headings become local subheadings; entry anchors follow below.
    body[n]=body[n].replace(r'\section*{',r'\subsection*{')

# 100: restore formulas and the two English editorial footnotes.
s=body[100]
s=replace(s,r'\subsection*{第8节\quad 例外超平面集合的维数}',r'\egasection{§8\quad 例外超平面集合的维数}')
s=replace(s,r'\textbf{8.1.}',r'\egap{8.1}')
s=replace(s,r'\subsection*{8.2\quad 维数跳跃和模的正则性}',r'\egap{8.2}')
s=replace(s,'法稿此处引用的节号没有定稿；英稿的“29”是其脚注号，不是所指节号。}',
'法稿此处引用的节号没有定稿；英稿的“29”是其脚注号，不是所指节号。}'+r'\ednote{节号遗漏，请询问 A.G.。〔英编稿脚注29。〕}')
s=replace(s,r'\emph{Redactor decidetur}（作者的拉丁语附记，意在请编者决定）。',
r'\emph{Redactor decidetur}〔作者的拉丁语附记〕。\ednote{由编辑决定。〔英编稿脚注30。〕}')
s=replace(s,'在 $y$ 的余深度相同。因此，',r'''在 $y$ 的余深度相同，即
\[
 \coprof_y\mathcal F_{k(\xi)}=\coprof_y\mathcal G_\xi .
\]
因此，''')
s=s.rstrip()+report_pointer(100,'直线参数、正维像及正则商的独立核算')
body[100]=s

# 101: the lower margin has now been read together with batch103; keep its limits.
s=body[101]
s=replace(s,r'\subsection*{8.3\quad 原有的 $(S_k)$ 不一定保留}',r'\egap{8.3}')
s=replace(s,'不是否定8.2的降阶结论。}','不是否定8.2的降阶结论。}'+r'\ednote{字迹不清，请询问 A.G.。〔英编稿脚注31。〕}')
s=replace(s,'在下述两个具体例子中，例外集恰为这个对偶超平面。',
'核查报告所收的两个具体译校例子中，例外集恰为这个对偶超平面。')
s=replace(s,'其中下标和连接语的读法未定，留待与8.5合核，不补写为已经证明的结论。',
'其中可辨的保持原阶问题已与下文8.5的改写层合读；仍不能辨明的连接语不补写为已经证明的结论。')
s=s.rstrip()+report_pointer(101,'深度计算及两个具体反例')
body[101]=s

# 102: entry numbers and full original authorial closing remark.
s=body[102]
s=replace(s,'记 $K$ 为底域',r'\noindent\textbf{译校记号约定。}记 $K$ 为底域')
s=replace(s,r'\subsection*{命题8.4\quad 何时例外参数的余维至少为二}',r'\egas{8.4}{命题}')
s=replace(s,r'\subsection*{引理8.4.1\quad 单个方程所致的余维变化}',r'\egas{8.4.1}{引理}')
s=replace(s,'详证见后。','独立补证完整列于核查报告“D18-102”，不作为作者原证明。')
s=replace(s,'后文给出反例。','核查报告“D18-102”给出反例。')
s=replace(s,'不是英23留下的问号。}',r'不是英23留下的问号。}\ednote{大概是 $H_\xi$。〔英编稿脚注32；保留原编者的疑读层。〕}')
old_closing=old_lines[135]
s=replace(s,'作者补记：这里一直在代数闭域上的点上作几何推理，却未事先说明。8.4的条件是几何的，可以在代数闭域上取有理点来作上述论证。',
old_closing)
body[102]=s

# 103: recover authorial short sufficiency, mark detailed proof as translator's.
s=body[103]
s=replace(s,r'\subsection*{推论8.5\quad 保持原阶 $(S_k)$}',r'\egas{8.5}{推论}')
s=replace(s,r'\subsection*{拟有限情形与8.6}',r'\subsection*{拟有限情形}')
s=replace(s,r'\paragraph{8.6.}',r'\egap{8.6}')
s=replace(s,'几何一语沿用8.4证明末对底域的说明。}','几何一语沿用8.4证明末对底域的说明。}'+r'\ednote{字迹不清，请询问 A.G.。〔英编稿脚注33。〕}')
s=replace(s,r'不能改作 $\coprof\ge n$。}',r'不能改作 $\coprof\ge n$。}\ednote{请询问 A.G.。〔英编稿脚注34。〕}')
s=replace(s,'必要性如下。',r'取 $z=x$，立即看出这个条件是充分的。'+report_pointer(103,'这一简短原句的展开，以及余深度集的闭性、换底和参数判据补证')+'\n\n必要性如下。')
s+=r'''\par\noindent〔法文物理第35页末关于一般判据的承接句带有删改、边缘裁切和覆写；未能可靠辨读的部分仍留缺，不补成原文结论。〕
'''
body[103]=s

# 104: preserve authorial argument; the expanded coordinate checks are in the report.
s=body[104]
s=replace(s,r'\subsection*{余法模及其射影化}',r'''\subsection*{余法模及其射影化}
\noindent〔原稿段首编号有覆写，本段沿原先的无编号主题位置收入，不据猜测另造编号。〕
''')
s=replace(s,r'\noindent 这里目标',r'\noindent\textbf{译校说明。}这里目标')
s=replace(s,'（原稿指向第16段，英注35指这批笔记的另一部分）。',
r'（原稿指向第16段）。\ednote{参见这些笔记的第二部分。〔英编稿脚注35。〕}')
insert=r'''
一旦把这个陈述的含义说清楚，也就是说，说明 $P$ 在 $a=f(x)$ 处的切空间的一个向量子空间怎样确定 $P$ 的一个线性子空间，使“$H$ 不包含这个子空间”有意义，结论便立即由光滑性的雅可比判据或奇异零点的定义得出。这一对应来自正合列(b)：它给出 $a$ 处切空间的向量子空间与 $P$ 中包含 $a$ 的线性子空间之间的一一对应。无论如何，这一对应就是将经过 $a$ 的线性子簇送到它在 $a$ 处的切空间，并将后者视为 $P$ 在 $a$ 处切空间的子空间。\transnote{英编稿称“factor subspaces”；在域上每个向量子空间均有补空间。本译按紧接的说明译为向量子空间。展开的局部坐标与线性代数核算完整收入核查报告“D18-104”，不是原稿新增证明。}

这类“连锁事实”，连同有关线性子簇和 Grassmann 簇的各项类似事实，应当集中在一两个预备编号或预备段落中，当然要对任意基底陈述。
'''
s=replace(s,r'\subsection*{奇异零的闭子概形}',insert+'\n'+r'\subsection*{奇异零的闭子概形}')
s=replace(s,'且它在 $S$ 上光滑，因而处于第16段所讨论的情形。','且它在 $S$ 上光滑，因而处于第16段所讨论的情形。'+r'\ednote{请询问 A.G. 这个引文的位置：应在这些笔记稍后的部分。〔英编稿脚注36。〕}')
s=replace(s,r'的零概形，其中 $\Omega^1_{B/\Pdual}$',
r'的零概形，其中\ednote{此处有难辨内容，请询问 A.G.。〔英编稿脚注37。〕} $\Omega^1_{B/\Pdual}$')
s=replace(s,r'''\begin{tikzcd}[row sep=3.3ex,column sep=2.4em]
0\arrow[d] &0\arrow[d] \\
\N^\vee_{X/P}\otimes\Ocal_Z(1,0)\arrow[d] &
 \Ocal_Z(0,-1)\arrow[d]\arrow[dl,dashed,swap,"\beta"]\arrow[dr,"\alpha"] \\
\Omega^1_{P/S}\otimes\Ocal_Z(1,0)\arrow[r]\arrow[d] &
 E_Z\arrow[r] &\Ocal_Z(1,0)\\
\Omega^1_{X/S}\otimes\Ocal_Z(1,0)\arrow[d] &
 T_{\Pdual/S}\otimes\Ocal_Z(0,-1)\arrow[d]\\
0&0
\end{tikzcd}''',r'''\begin{tikzcd}[row sep=3.3ex,column sep=1.6em]
 &0\arrow[d] &0\arrow[d] \\
 &\N^\vee_{X/P}\otimes\Ocal_Z(1,0)\arrow[d] &
 \Ocal_Z(0,-1)\arrow[d]\arrow[dl,dashed,swap,"\beta"]\arrow[dr,"\alpha"] \\
0\arrow[r]&\Omega^1_{P/S}\otimes\Ocal_Z(1,0)\arrow[r]\arrow[d] &
 E_Z\arrow[r]\arrow[d] &\Ocal_Z(1,0)\arrow[r]&0\\
 &\Omega^1_{X/S}\otimes\Ocal_Z(1,0)\arrow[d] &
 T_{\Pdual/S}\otimes\Ocal_Z(0,-1)\arrow[d]\\
 &0&0
\end{tikzcd}''')
s=replace(s,r'\noindent 横行左、右端的 $0$ 从略；',r'\noindent 横行及两条竖列均正合；')
s=replace(s,'图把原稿自下而上的列改为向下，并保持箭头方向与对应映射。}',
'图把原稿自下而上的列改为向下，并保持箭头方向与对应映射。第104批排版漏画中列从 $E_Z$ 到 $T_{\\Pdual/S}\\otimes\\Ocal_Z(0,-1)$ 的箭头；本版依法39页、英27页的原图和对偶欧拉列补齐。}'+r'\ednote{请询问 A.G.：上面的 $G$ 实际是一个难辨的字母，后接 $P^\vee/S$；这是什么？〔英编稿脚注38。〕}')
s=replace(s,'正是 $\\Psi$ 的拉回。','正是 $\\Psi$ 的拉回。'+r'\ednote{Blass：请检查这里的字母是否正确。〔英编稿脚注39。〕}'+report_pointer(104,'欧拉核坐标下的局部比对'))
s=replace(s,'由零概形的定义，复合为零','（这一验证应当基本上是机械的。）由零概形的定义，复合为零')
body[104]=s

# 105: the incomplete sentence remains incomplete, and the independent argument stays separate.
s=body[105]
s=replace(s,r'\subsection*{定理8.7：微分判据}',r'\egas{8.7}{定理}')
s=replace(s,'该段判别二次型的极化是否非退化；特征二时不能改用除以2的公式。',
'该段判别二次型的极化是否非退化；特征二时不能改用除以2的公式。英编稿后文物理73--74页另说明，这里的“普通”与惯常用语有冲突，宜称“非超奇异的奇异零”或“二次型非退化的奇异零”。因此本处普通奇异零只按极化型非退化理解；例如特征二的 $u^2+vw$ 可给出通常的普通二次奇异点，但其极化型退化，不能混同。')
s=replace(s,'可知定理条目与后续命题应分开。}','可知定理条目与后续命题应分开。}'+r'\ednote{请询问 A.G.。〔英编稿脚注40。〕}')
s=s.rstrip()+report_pointer(105,'像维数、极化型以及后文所需对偶切空间事实的独立补证')
body[105]=s

# 106: explicitly mark the hypotheses supplied by the translator.
s=body[106]
s=replace(s,r'\subsection*{8.8：等价条件与维数}',r'\egas{8.8}{命题（明示译校工作假设）}')
s=replace(s,'正余维。记',r'''正余维。\transnote{法文物理第40页止于8.7(c)的切映射引出语，第41页从“像的闭包”起，8.8的标题和设定起首未完整保存；英编稿第28页将这两处误接。本段的“几何整、局部闭浸入、正余维”是第106批为使陈述及证明有明确适用范围而补入的工作假设，不声称恢复了遗失的法文原句。后证由 $f(x)$ 恢复 $x$ 用到浸入；仅无分歧时，旧稿所列二次平展覆盖反例使泛平展推出双有理失败，完整反例保存在本版报告的旧注档案中。}记''')
s=replace(s,r'\subsection*{8.8 的证明与 8.9 的引出}',r'\subsection*{证明及推论的引出}')
s=replace(s,'由8.7(c)将得到下述更强的结论。',
'由8.7(c)将得到下述更强的结论。'+r'\transnote{这是原稿的回指；8.7(c)的后半原句仍缺。证明在此需要的对偶切空间事实，由核查报告“D18-105”另列完整译校补证。泛点微分判据及几何底扩的详细核算收入“D18-106”；均不冒称作者遗失的文字。}')
s=replace(s,r'\subsection*{推论8.9：光滑开集上的开浸入}',r'\egas{8.9}{推论}')
s=replace(s,'并且适当','并且适当') if '并且适当' in s else s
s=replace(s,'由8.7(c)，$x=',r'由8.7(c)所回指的切空间事实（本版的独立补证见核查报告），$x=')
s=replace(s,'符号 $Y^1$ 和其概形闭包在此分别写作 $Z$ 和 $\\overline Z$。}',
'符号 $Y^1$ 和其概形闭包在此分别写作 $Z$ 和 $\\overline Z$。}'+r'\ednote{请询问 A.G.。〔英编稿脚注41，原图态射及闭包段的疑读标记。〕}'+report_pointer(106,'从点的描述落实为态射及闭子概形分解的译校补证'))
s=replace(s,'其像闭包维数不会增加。','其像闭包维数不会增加。'+r'\ednote{请询问 A.G.。〔英编稿脚注42，原稿此处的截面与零集记号。〕}')
body[106]=s

# 107: recover omitted authorial prose and keep all original editorial footnotes.
s=body[107]
s=replace(s,lines[107][17],
r'\noindent\textbf{记号。}承接8.8、8.9所明示的工作假设：'+lines[107][17].split('承接8.8、8.9：',1)[1])
s=replace(s,r'\subsection*{注8.10：无分歧但不 étale 的点}',r'\egas{8.10}{备注}')
s=replace(s,r'\subsection*{推论8.11：特征零}',r'\egas{8.11}{推论}')
s=replace(s,r'\subsection*{注8.12：一般线性笔}',r'\egas{8.12}{备注}')
s=replace(s,'$Z=D$ 可用一个可逆模的行列式截面恒等于零来表达。',r'''$Z=D$ 可用一个可逆模的行列式截面恒等于零来表达；这个可逆模为
\[
 \omega_{X/k}^{\otimes2}|_Z\otimes
       \mathcal O_Z(1,1)^{\otimes d},\qquad d=\dim X .
\]
''')
s=replace(s,'此处限制符号表示沿 $Z\\to X$ 拉回。正文采用不歧义的行列式描述，不把可见的一次扭转当作一般公式。',
'此处限制符号表示沿 $Z\\to X$ 拉回。正文按行列式的实际变换规律写出一般秩的公式，并在本注保留原稿一次扭转的读法；不把一次扭转误当作任意 $d$ 的公式。')
# Keep the correction note attached to the lead-in, not on a line after the display.
note_start=s.index(r'\transnote{法44及英30')
depth=1;note_end=note_start+len(r'\transnote{')
while depth:
    ch=s[note_end]
    if ch=='{':depth+=1
    elif ch=='}':depth-=1
    note_end+=1
note=s[note_start:note_end]
s=s[:note_start]+s[note_end:]
s=replace(s,'这个可逆模为\n','这个可逆模为'+note+'\n')
s=replace(s,'下页特征零实例','核查报告“D18-107”的特征零实例')
s=replace(s,'双切线的存在也不自动断言对偶点恰为普通节点。}',
'双切线的存在也不自动断言对偶点恰为普通节点。}'+r'\ednote{字迹不清。〔英编稿脚注43，第二接触点处的 $x/x^1$ 读法。〕}')
full_author=r'''这第二种情形，无论我们是否处于特征零，都应当完全视为例外情形。〔页顶手迹残段：“簇 $L$ 在 $1\ldots T=L$”；其余字迹不清。〕\ednote{字迹不清。〔英编稿脚注44。〕}
用古典语言来说，如果没有弄错，就是说：相对于所考虑的射影浸入，$X$ 是“直纹的”（ruled）。\transnote{这是作者此处暂用的术语，不能径直等同于通常的直纹簇。后文8.17也提醒此处用法与传统用法不同。上句对“很例外”的评价可以不依特征，但“足够一般的笔全光滑”在任意特征下都需全部奇异参数像的闭包余维至少二，不能只由 $Z=D$ 推出。}
〔而且，如果我们愿意，〕由8.5及其推论，这里已有把这一术语明确化并加以论证所需的一切；如果你有兴致，也可把它同〔法文：\emph{la taupe}〕联系起来。\transnote{法45页保留这一词组，英31页照录而未说明指代；不猜作某个数学定理或术语。}
例如，若 $\dim X=1$，这意味着 $X$ 是一条直线〔字迹不清〕\ednote{字迹不清。〔英编稿脚注45。〕}，$x\in X(k)$，所以 $T$ 包含〔缺文〕\ednote{字迹不清。〔英编稿脚注46。〕}。\transnote{法45页有“在一条直线上”一类手写补句以及 $T=L$ 边注，连接关系仍未完全读定。这里保留可辨原句和缺文标记，不将其提升为任意浸入下完整的分类定理。}
'''
s=replace(s,clean(lines[107][57]),full_author)
s=replace(s,'原稿说此处没有构造例子，却相信例子存在。',
'我太懒了，不愿构造这些例子，但我不怀疑它们存在。'+r'\ednote{把它做出来。——Blass。〔英编稿脚注47。〕}')
s=replace(s,r'\noindent\textbf{原稿编排提示与接续。}',r'\subsection*{原稿编排备忘}')
memo=r'''在(a)中加一条脚注，指向后面的编号小节或段落；在那里我们证明：如果出现这一例外的“直纹”情形，那么对射影浸入作一个简单的修改，就能重新回到8.8的“一般”情形。\transnote{这是作者对后文的编排指示，不是本版在此另行宣称已经完成该修改及证明。}

本节从8.6到这里的部分，无疑可以独立成一个具有微分性质的小节；而本编号小节的开头，应当与接下来的部分合并成一个讨论例外〔超平面？〕\ednote{请询问 A.G.。〔英编稿脚注48。〕}之维数的小节。我这里只用了 $\Ys$ 的维数是 $r-1$ 这一事实。
'''
s=replace(s,lines[107][70],memo)
s=s.rstrip()+report_pointer(107,'两个点集的比较、特征零双切线、一般笔的至多一个奇异点及正特征 Fermat 曲线')
body[107]=s

# 108: retain corrections and remove a mistaken source attribution to English footnote48.
s=body[108]
s=replace(s,lines[108][17],
r'\noindent\textbf{译校记号约定。}下文用'+lines[108][17].split('下文用',1)[1])
s=replace(s,r'\subsection*{命题8.13：经译校的陈述}',r'\egas{8.13}{命题（经译校的陈述）}')
s=replace(s,'见末页反例。','见核查报告“D18-108”的第二个反例。')
s=replace(s,'末页有检验该差别的例子。','核查报告“D18-108”收有检验该差别的二次曲面例子。')
s=replace(s,'不要求抽象簇带有给定的直纹结构。',
'不要求抽象簇带有给定的直纹结构。'+r'\transnote{这里明确采用切参数像的余维条件，作为本条及补证中“直纹型”的工作含义；不是把作者试探性的临时术语改成通常直纹簇的定义。下标为 $n-1$ 的(a)按 $n\ge1$ 阅读；原页未说明负下标 Serre 条件的约定，本版不据此另设 $(R_{-1})$。}')
s=replace(s,r'\subsection*{证明译文}',r'\subsection*{原稿证明译文}')
s=replace(s,'由此及8.4可以得到结论。','由此及8.4可以得到结论。'+report_pointer(108,'原稿略去的两类奇异集合估计、伴随点前提和两个检验'))
s=replace(s,'英编稿31页标出的第48注也表明其编辑读法有待核。',
'英编稿31页第48注实际附在8.13以前的编排备忘，不属于本命题的证明；第108批将它误指到这里，本版已按原页位置纠正，原注仍保留于8.12后。')
body[108]=s

def separate_adjacent_notes(s):
    """Add visible punctuation only between adjacent independent footnote calls."""
    matches=list(re.finditer(r'\\(?:transnote|ednote|orig)\{',s))
    edits=[]
    last_end=None
    for m in matches:
        start=m.end()-1
        depth=1;i=start+1
        while i<len(s) and depth:
            if s[i]=='\\' and i+1<len(s) and s[i+1] in '{}%':
                i+=2;continue
            if s[i]=='{':depth+=1
            elif s[i]=='}':depth-=1
            i+=1
        if last_end is not None and not s[last_end:m.start()].strip():
            edits.append((last_end,m.start(),r'\textsuperscript{,}'))
        last_end=i
    for a,b,t in reversed(edits):s=s[:a]+t+s[b:]
    return s

for n in body: body[n]=separate_adjacent_notes(body[n])

# All changes are deliberately limited to these new files.
for n,s in body.items():
    s=s.replace('；1158页合订本未改','')
    header=f'% V18 integration from immutable Dot batch {n}: {names[n]}\n'
    origin=rf'\source{{Dot第{n}批；法文底本物理第{pages[n][0]}页，英编稿物理第{pages[n][1]}页}}'
    (OUT/f'v18_batch{n}.tex').write_text(header+local+origin+'\n'+s.strip()+'\n\\endgroup\n')

report=[r'''\head{第十八版回校整合：第一篇（8.1）至（8.13）}
\source{Dot第100--108批；法文物理第30--46页与英编稿物理第21--32页的相应段落}
以下保存各批完整的译校补证和反例，以及被替换的第十七版旧注。补证、具体例子与工作假设均属译校文字，不冒充作者原文。各批封面、批次范围和“下批从何处继续”等旧状态已从正文移出；实际源码及进度原件仍保存在归档目录。

本轮实际读取九份主源码、进度文件及旧8.1--8.13段，重点对读了（8.5）、（8.6）、（8.8）、（8.13）和相关图式的法英页面图像。它是有限范围的对照与整合，未宣称独立复审全部证明或所有外部参考。下面保留的外部网址是各批已有的可追溯来源；未逐一重新访问验证的条目，不据此提升为本轮完成的文献核查。

\subsec{D18-M：这次整合的订正与界限}
\begin{enumerate}
\item （8.5）的余深度集采用严格不等式 $\coprof>n$；（8.6）的坏截面深度为 $<k$。法文第35页可辨的符号与英编稿第24页的错误读法分开保留。
\item 第104批交换图原先漏画了中列 $E_Z$ 向 $T_{P^\vee/S}\otimes\mathcal O_Z(0,-1)$ 的箭头。本版依法39、英27原图及对偶欧拉列补齐；不改变其源、靶或扭转。
\item （8.7）(c)仍为残句。后文使用的对偶切空间事实另有完整的译校补证，但补证不等于恢复作者遗失的后半句。
\item （8.8）明确补入几何整、局部闭浸入和正余维作为工作假设；现存法40--41的页缝没有给出它们的完整原句。仅保留无分歧会有二次平展覆盖反例，不能把这一补假设的版本说成原稿起首已完整复原。
\item （8.12）补回第107批转述中省略的作者编排备忘、\emph{la taupe}、直线及包含关系残句，并保留英编稿第44--48注。未知手迹继续标缺，不补成分类结论。
\item （8.13）按法46的 $R_k$、$k+1$ 和充分性修订层排正文。零维几何伴随点的排除是第108批新增假设，不能归给原作者。第108批把英31脚注48关联到8.13证明的说法已纠正：该脚注实际附在前一编排备忘。
\item （8.13）(a)的 $n-1$ 条件按 $n\ge1$ 阅读；原页未写负下标约定。8.14自身及引用链没有在本段整合中重新审定。
\end{enumerate}
''']
for n in names:
    rs=clean(take(n,report_ranges[n]))
    rs=rs.replace(r'\section*{',r'\subsection*{')
    rs=rs.replace('由上批，','由前述余法射影丛识别，')
    rs=rs.replace('见第105批的直线入射维数论证','见本报告“D18-105”的直线入射维数论证')
    if n==105:
        rs=replace(rs,r''' B_Q(v,w)=Q(v+w)-Q(v)-Q(w),\qquad
 T_{y}(\pi^{-1}(\xi)_K)=\{v:B_Q(v,w)=0\text{ 对所有 }w\}.''',r'''\begin{aligned}
 B_Q(v,w)&=Q(v+w)-Q(v)-Q(w),\\
 T_{y}(\pi^{-1}(\xi)_K)&=\{v:B_Q(v,w)=0\text{ 对所有 }w\}.
\end{aligned}''')
    if n==103:
        rs=r'\paragraph{（8.6）简短充分性原句的展开。}'+'\n'+rs
    if n==104:
        rs=r'\paragraph{局部光滑性判据与线性空间对应的展开。}'+'\n'+rs
    report += [
        rf'\subsec{{D18-{n}：第{n}批译校补证（非原文）}}',
        rf'\hypertarget{{D18-{n}-notes}}{{}}',
        local,rs,r'\endgroup'
    ]

notes=extract_notes(old_segment)
legacy=[r'''\subsec{D18-M-LEGACY：第十七版8.1--8.13旧注原文档案}
以下逐项保留被替换段落中的全部脚注文字，包含当时的反例、译校解释、疑读与英编者注。这里的“未取得”“待核”“原稿条件下不成立”等表述属于第十七版的证据状态；不是第十八版当前进度，也不推翻现行正文已明示补假设的条件版本。具体替代关系以前面的 D18-M 记录为准。旧正文的原段也完整保存在工程的 \path{integration/middle_legacy_segment.tex}，可与原始 \path{v_dot_early.tex} 逐字比对。旧注按原行位置列出，既不删反例，也不将其改称新证明。
''',local]
for i,x in enumerate(notes,1):
    kind={'transnote':'译注','ednote':'英编者注','orig':'原注','cmt':'译校注','footnote':'脚注'}[x['macro']]
    label=(('；原标签'+x['id']) if x['id'] else '')
    legacy.append(rf'\paragraph{{旧注 M-{i:03d}（原文件第{x["line"]}行；{kind}{label}）。}}'+'\n'+x['text'])
legacy.append(r'\endgroup')
report += legacy
(PROJECT/'reports/v18_middle_notes.tex').write_text('\n\n'.join(report)+'\n')
(INTEG/'middle_legacy_notes.json').write_text(json.dumps(notes,ensure_ascii=False,indent=2)+'\n')

hashof=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
manifest={
 'schema_version':1,
 'status':'source_integrated_pending_compilation_and_render_check',
 'scope':'EGA V first part 8.1--8.13; Dot batches100--108; no change to 8.14 onward',
 'input_order':[f'continuations/v18_batch{n}.tex' for n in names],
 'report':'reports/v18_middle_notes.tex',
 'legacy_original':{'path':'continuations/v_dot_early.tex','sha256':hashof(old_path),
                    'replacement_lines_1based':[54,431], 'keep_from_line_1based':432,
                    'extracted_segment':'integration/middle_legacy_segment.tex',
                    'segment_sha256':hashof(INTEG/'middle_legacy_segment.tex'),
                    'notes_count':len(notes)},
 'batches':[],
 'source_pdfs':[],
 'visual_review':{
   'rendered_directory':'integration/middle_source_pages',
   'actually_viewed_physical_pages':{'french':[34,35,39,40,41,42,43,44,45,46],'english':[24,27,28,29,30,31,32]},
   'limits':'Only listed page images were actually inspected. Other rendered pages are not counted as reviewed. This is not a complete review of all mathematics.'},
 'unresolved':[
  '8.7(c) original sentence after the tangent-map introduction remains missing at French40/41 page join.',
  '8.8 preamble/title not recovered; geometric integrality, locally closed immersion and positive codimension are explicit translator working hypotheses.',
  'French36 overwritten paragraph number unresolved; thematic heading retained without invented number.',
  'French35 final rewritten general-criterion sentence and several French45 marginal fragments remain unreadable.',
  '8.13 no-zero-dimensional-geometric-associated-points assumption is a translator addition, not a recovered source statement.',
  '8.13(a) uses n>=1; original negative Serre index convention is unstated.',
  '8.14 and subsequent propositions are retained by parent and not newly audited by this integration.',
  'External references retained from batches have not all been newly verified; independent proof review remains limited.'
 ]
}
for n,name in names.items():
    p=SRC/f'batch{n}'/name
    data={'batch':n,'source':str(p.relative_to(REPO)),'source_sha256':hashof(p),
          'source_bytes':p.stat().st_size,'source_lines':len(lines[n]),
          'body_source_line_ranges_1based':body_ranges[n],
          'report_source_line_ranges_1based':report_ranges[n],
          'removed':'standalone preamble, cover, batch range/next/status; explicit page-break commands',
          'body_file':f'continuations/v18_batch{n}.tex',
          'body_sha256':hashof(OUT/f'v18_batch{n}.tex'),
          'source_pages_physical':{'french':pages[n][0],'english':pages[n][1]}}
    progress=SRC/f'batch{n}'/'PROGRESS.json'
    data['progress_sha256']=hashof(progress)
    data['progress_path']=str(progress.relative_to(REPO))
    manifest['batches'].append(data)
for name in ('EGA5_francais.pdf','EGAVaiello.pdf'):
    p=REPO/'archive_20261121/03_sources'/name
    manifest['source_pdfs'].append({'path':str(p.relative_to(REPO)),'bytes':p.stat().st_size,'sha256':hashof(p)})
manifest['report_sha256']=hashof(PROJECT/'reports/v18_middle_notes.tex')
(INTEG/'middle_integration.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'body_files':len(body),'legacy_notes':len(notes),
 'report_bytes':(PROJECT/'reports/v18_middle_notes.tex').stat().st_size,
 'files':{n:(OUT/f'v18_batch{n}.tex').stat().st_size for n in names}},ensure_ascii=False))
