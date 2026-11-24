#!/usr/bin/env python3
"""Integrate the received Dot 88--99 texts without mutating originals.

Every extracted range and every explicit text edit is recorded.  The record is a
preservation/migration record, not an independent mathematical certification.
"""
from pathlib import Path
import hashlib
import json
import re

WORK = Path(__file__).resolve().parents[1]
REPO = WORK.parents[1]
RAW = REPO / 'dot_updates_20261124/batches'
OUT = WORK / 'continuations'
REPORT = WORK / 'reports/v18_early_notes.tex'
RECORD = WORK / 'integration/early_migration.json'
OUT.mkdir(exist_ok=True)
REPORT.parent.mkdir(exist_ok=True)

def sha(s):
    return hashlib.sha256(s if isinstance(s, bytes) else s.encode()).hexdigest()

LOCAL = r'''\begingroup
% These definitions have only group-local scope; the shared preamble is untouched.
\def\OO{\mathcal O}\def\FF{\mathcal F}\def\GG{\mathcal G}
\def\PP{\mathbf P}\def\calP{\mathcal P}\def\dd{\delta}
\def\Div{\operatorname{Div}}\def\depth{\operatorname{depth}}
\def\pr{\operatorname{pr}}\def\coker{\operatorname{coker}}
'''
END = '\n\\endgroup\n'
data = {'schema': 1, 'scope': 'EGA V first manuscript, sections 1--7; Dot labels 88--99',
        'full_mathematical_reaudit': False, 'batches': [], 'edits': [], 'old_annotations': []}
report_parts = []

class Batch:
    def __init__(self, number):
        self.number = number
        d = RAW / f'batch{number:03}'
        candidates = [p for p in d.glob('*.tex') if not p.name.startswith('基线_')]
        assert len(candidates) == 1, candidates
        self.path = candidates[0]
        self.s = self.path.read_text()
        self.rec = {'batch': number, 'source': str(self.path.relative_to(REPO)),
                    'source_sha256': sha(self.path.read_bytes()), 'source_bytes': self.path.stat().st_size,
                    'progress': json.loads((d / 'PROGRESS.json').read_text()), 'ranges': []}
        self.used = []
        data['batches'].append(self.rec)

    def index(self, marker):
        assert self.s.count(marker) == 1, (self.number, marker, self.s.count(marker))
        return self.s.index(marker)

    def take(self, start, end, destination, label):
        a = self.index(start) if isinstance(start, str) else start
        b = self.index(end) if isinstance(end, str) else end
        assert b >= a
        text = self.s[a:b]
        rec = {'label': label, 'destination': destination, 'start_offset': a, 'end_offset': b,
               'start_line': self.s.count('\n', 0, a) + 1,
               'end_line': self.s.count('\n', 0, b - 1) + 1 if b > a else self.s.count('\n', 0, a) + 1,
               'bytes': len(text.encode()), 'sha256': sha(text)}
        self.rec['ranges'].append(rec); self.used.append((a, b))
        return text

    def edit(self, text, old, new, reason):
        assert text.count(old) == 1, (self.number, old[:80], text.count(old))
        data['edits'].append({'batch': self.number, 'old': old, 'new': new, 'reason': reason})
        return text.replace(old, new, 1)

    def finish(self):
        # Preserve all non-migrated source bytes, including covers and old progress,
        # verbatim in the machine-readable record as well as in immutable originals.
        merged = []
        for a, b in sorted(self.used):
            if merged and a <= merged[-1][1]: merged[-1][1] = max(b, merged[-1][1])
            else: merged.append([a,b])
        cursor = 0; omitted = []
        for a,b in merged + [[len(self.s), len(self.s)]]:
            if a > cursor:
                t = self.s[cursor:a]
                omitted.append({'start_offset': cursor, 'end_offset': a,
                    'start_line': self.s.count('\n', 0, cursor)+1,
                    'end_line': self.s.count('\n', 0, a-1)+1, 'sha256': sha(t), 'text': t,
                    'reason': 'Standalone preamble/cover, repeated heading, historical batch scope or continuation instructions; source remains immutable.'})
            cursor = max(cursor,b)
        self.rec['excluded_from_running_text'] = omitted

def markup(t, batch, report=False):
    # Formula and footnote bodies are not rewritten by these structural changes.
    def tag(m):
        title, number = m.group(1), m.group(2)
        if not number: return r'\egap{' + title + '}'
        nm = re.fullmatch(r'(\d+(?:\.\d+)*)(（.*）)?', number)
        assert nm, (batch, number)
        return r'\egas{' + nm.group(1) + '}{' + title + (nm.group(2) or '') + '}'
    t = re.sub(r'\\tagitem\{([^{}]*)\}\{([^{}]*)\}', tag, t)
    headings = {
        r'\section*{IV.20\quad 超平面截面与锥形投影}': r'\par\medskip\noindent\textbf{原手稿 IV.20：超平面截面与锥形投影。}',
        r'\section*{20.1\quad 预备知识与记号}': r'\egasection{§1\quad 预备知识与记号（法文原号20.1）}',
        r'\section*{20.2\quad 泛超平面截面：局部性质}': r'\egasection{§2\quad 泛超平面截面：局部性质（法文原号20.2）}',
        r'\section*{20.2\quad 泛超平面截面：局部性质（续）}': '',
        r'\section*{20.3\quad 泛超平面截面：几何不可约性与连通性}': r'\egasection{§3\quad 泛超平面截面：几何不可约性与连通性（法文原号20.3）}',
        r'\section*{20.4\quad 变动超平面截面的研究：“充分一般”的截面}': r'\egasection{§4\quad 变动超平面截面的研究：“充分一般”的截面（法文原号20.4）}',
        r'\section*{20.4（续）\quad “充分一般”的截面}': '',
        r'\section*{5\quad Seidenberg 型定理}': r'\egasection{§5\quad Seidenberg 型定理}',
        r'\section*{5（续）\quad Seidenberg 型定理}': '',
        r'\section*{6\quad 任意超平面截面的连通性}': r'\egasection{§6\quad 任意超平面截面的连通性}',
        r'\section*{7\quad 应用于构造指定类型的超平面截面或多截面}': r'\egasection{§7\quad 应用于构造指定类型的超平面截面或多截面}',
        r'\section*{几何性质（英编稿标题）}': r'\subsec{几何性质（英编稿标题）}',
        r'\paragraph{命题 6.1.}': r'\egas{6.1}{命题}',
        r'\paragraph{7.1.}': r'\egap{7.1}',
        r'\section*{7.1 末尾的补记：允许一部分坏点}': r'\par\medskip\noindent\textbf{（7.1）末尾的作者补记：允许一部分坏点。}',
        r'\section*{命题7.2：模层版本}': r'\egas{7.2}{命题（模层版本）}',
        r'\section*{命题7.3：概形版本及其范围}': r'\egas{7.3}{命题（概形版本及其范围）}',
        r'\section*{7.5\quad 关于射影性的备注}': r'\egas{7.5}{备注（关于射影性）}',
    }
    for old,new in headings.items():
        if old in t:
            data['edits'].append({'batch': batch, 'old': old, 'new': new, 'reason':'Heading/statement adaptation; retains original item numbers and V-H anchors; continuation headings are not new sections.'})
            t=t.replace(old,new)
    # Other headings mark deleted manuscript material or translator commentary.
    t = t.replace(r'\section*{', r'\subsection*{')
    t = t.replace(r'\clearpage', '')
    return t.strip() + '\n'

def save_body(b, t):
    p=OUT/f'v18_batch{b.number:03}.tex'
    t=markup(t,b.number)
    p.write_text(f'% V18 integration of Dot batch {b.number:03}; immutable source SHA256 {b.rec["source_sha256"]}\n'+LOCAL+t+END)
    b.rec['output']={'path':str(p.relative_to(WORK)),'sha256':sha(p.read_bytes()),'bytes':p.stat().st_size}

def add_report(b,title,text):
    if text.strip():
        anchor=f'D18-{b.number:03}-notes'
        report_parts.append(r'\subsec{D18-'+f'{b.number:03}'+r'：'+title+'}\n'+
                            r'\hypertarget{'+anchor+'}{}\n'+LOCAL+markup(text,b.number,True)+END)

def report_pointer(number,subject):
    return r'\par\noindent\textit{译校补证另见核查报告。}\cmt{D18-'+f'{number:03}'+r'-R}{'+subject+r'完整保存在本版核查报告“D18-'+f'{number:03}'+r'”条；其中译校补证为非原文。}'

for n in range(88,100):
    b=Batch(n); end=b.index(r'\end{document}')
    if n==88:
        body=b.take(r'\section*{IV.20\quad 超平面截面与锥形投影}',end,'body','IV.20.1 through 2.7 inclusive')
        body=b.edit(body,'作者预告：在通常的非退化射影丛情形，相对除子函子由各次数对应的射影丛\n\\(\\PP(\\operatorname{Sym}^k(E^\\vee))\\) 的不交并表示，',
                    '作者在此预告相对除子函子的表示。按商线约定订正其参数模后，在 $E$ 的秩处处至少为二的情形，\n相应的各次数参数丛应写为 $\\PP((\\operatorname{Sym}^k E)^\\vee)$；作者预告它们的不交并表示该函子，',
                    'French physical p4 visibly prints P(Sym^k(E dual)); in arbitrary characteristic the degree-k coefficient module is Sym^k E and its line parameters use the dual of that module. Preserve representation as an unproved forecast and explicitly exclude rank-one degeneration.')
        body=b.edit(body,'公式采用商线约定；秩一的射影丛不能把多个同样的空除子按各个 \\(k\\) 重复表示。这里按作者所写保留为后文预告，不把它当成本段已证的表征定理。',
                    '法稿原式为 \\(\\PP(\\operatorname{Sym}^k(E^\\vee))\\)，对偶放在 $E$ 上。按 $p_*\\OO_P(k)=\\operatorname{Sym}^k E$ 的商线约定，次数 $k$ 的方程给出 $\\operatorname{Sym}^k E$ 中的一条局部直和因子线，故其参数模是 $(\\operatorname{Sym}^k E)^\\vee$。任意底上不能无条件把对偶与对称幂交换；$k!$ 可逆时的对称化识别不能直接用于任意特征。正文只订正这一预告的参数模，$k=1$ 的超平面构造不受影响。秩一的射影丛不能把多个同样的空除子按各个 \\(k\\) 重复表示。这里未证明一般相对除子函子的表示性，旧注 P03 的历史记录仍保留在核查报告中。',
                    'Explain the dual-position correction and retain the original formula and the explicit limit of this source audit; do not silently mark old P03 resolved in its entirety.')
        body=b.edit(body,r'\begin{proof}'+'\n先取 \\(Z=\\{z\\}\\)',r'\begin{proof}[原稿论证与译校展开]'+'\n先取 \\(Z=\\{z\\}\\)','Label the expanded proof of 2.2; the source draft states the affine/projective step briefly.')
        body=b.edit(body,r'\begin{proof}'+'\n对每个有非空截面的分支',r'\begin{proof}[原稿论证与译校展开]'+'\n对每个有非空截面的分支','Label the expanded reduced/component proof of 2.6.')
        body=b.edit(body,r'\begin{proof}'+'\n逆像与集合差及对称差相容',r'\begin{proof}[原包含判据的证明及译校补证]'+'\n逆像与集合差及对称差相容','Distinguish the corrected equality criterion proof from the original proof.')
        old='原等号句却没有同步修改。'
        new=r'原等号句却没有同步修改：它仍称 $Z_\eta=Z\prime_\eta$ 当且仅当 $Z=Z\prime$ 或 $f(Z),f(Z\prime)$ 都有限。'
        # Use proper prime notation in the added verbatim mathematical claim.
        new=new.replace(r'Z\prime',r"Z'")
        body=b.edit(body,old,new,'State the rejected original equality claim explicitly in the correction footnote.')
        marker=r'\tagitem{命题}{2.6}'
        restored='注意，若 $\\dim X_i=d_i$，则对上述非空分支有 $\\dim Y_{i\\eta}=d_i-1$。更一般地：\\cmt{D18-088-P25}{这是法文物理第8页（2.5）证明之后的过渡句；原稿写 $Y_i$，依泛截面语境补明下标 $\\eta$。第88批将其解释并入（2.6）脚注，本次恢复其独立位置。}\n\n'
        body=b.edit(body,marker,restored+marker,'Restore the separate original 2.5-to-2.6 transition, confirmed on French p8 and retained in the old translation.')
    elif n==89:
        body=b.take(r'\section*{20.2\quad 泛超平面截面：局部性质（续）}',r'\noindent 下一处为','body','2.8--2.13')
        notation=b.take('沿用第88批记号：','正式出版 EGA IV.1','body','Mathematical notation previously inside the batch-scope paragraph')
        notation=b.edit(notation,'沿用第88批记号：','沿用前述记号：','Preserve mathematical setup while removing the batch-specific reference.')
        body=notation+'\n'+body
        a=body.index(r'\noindent\emph{原证明异文。}'); z=body.index(r'\tagitem{推论}{2.13}')
        part=body[a:z]; body=body[:a]+body[z:]
        b.rec['ranges'].append({'label':'Original proof variant and correction analysis for 2.12','destination':'report','start_offset':b.s.index(part),'end_offset':b.s.index(part)+len(part),'sha256':sha(part),'start_line':b.s.count('\n',0,b.s.index(part))+1,'end_line':b.s.count('\n',0,b.s.index(part)+len(part)-1)+1,'bytes':len(part.encode())})
        add_report(b,'（2.12）的原证明异文及订正依据',part)
        body=b.edit(body,r'\begin{proof}[订正后的证明]',r'\begin{proof}[译校订正证明，非原文]','Make authorship of the replacement proof explicit.')
        body=b.edit(body,'如非平凡有限可分域扩张的谱到点。','如非平凡有限可分域扩张的谱到点。原证明的完整旧译及其错误步骤说明见核查报告“D18-089：（2.12）的原证明异文及订正依据”。','Direct the reader to the fully retained original proof.')
    elif n==90:
        body=b.take(r'\section*{20.2\quad 泛超平面截面：局部性质（续）}',r'\section*{补充核查：两个不能省略的限制}','body','2.14--2.18')
        notation=b.take(r'记 $P=\PP^n_k$','下一处为法14页','body','K_eta and other mathematical notation from the scope paragraph')
        body=notation+'\n'+body
        extra=b.take(r'\section*{补充核查：两个不能省略的限制}',r'\noindent 法14在2.18后','report','Two explicit counterexamples')
        add_report(b,'几何性质的两项限制与反例',extra)
        ending=b.take(r'\noindent 法14在2.18后',end,'body','Deleted transition record')
        ending=b.edit(ending,'第3节起及其页下方划销草稿留待下一批，不能因英编稿换页而跳过。','第3节及其页下方划销草稿的校记接在下文。','Replace obsolete batch continuation with current reading relation.')
        body=body+report_pointer(n,'纯不可分覆盖及特征零下常值态射的两个反例')+'\n'+ending
    elif n==91:
        body=b.take(r'\section*{20.3\quad 泛超平面截面：几何不可约性与连通性}',end,'body','3.1--3.3 and deleted manuscript layers')
        body=b.edit(body,'下一批以法文页为准保留编号。','下文以法文页为准保留编号。','Remove obsolete batch scheduling.')
        body=b.edit(body,'原稿说，这一引理或近似版本在文献中颇常见，把证明出处留给收信人选择，自己不另找一份证明。','这一引理，或者同它如同兄弟般相似的引理，在文献中几乎随处可见。因此，我把选取一份证明出处的工作留给你；也就是说，我没有兴致凭自己的办法再找一个证明。','Restore the complete author editorial remark from the retained old translation; no additional proof is invented.')
        old=r'\begin{proof}'+'\n原稿援引拟与 Hartshorne 定理同列于第6段的分支链引理。'
        new=r'\begin{proof}[原稿论证与译校展开]'+'\n原稿援引拟与 Hartshorne 定理同列于第6段的分支链引理。'
        body=b.edit(body,old,new,'Identify the expanded component-graph proof as translator elaboration.')
    elif n==92:
        body=b.take(r'\section*{20.4\quad 变动超平面截面的研究：“充分一般”的截面}',r'\section*{译校补证：充分一般的三个等价条件}','body','4.1--4.3')
        extra=b.take(r'\section*{译校补证：充分一般的三个等价条件}','\\medskip\n\\noindent\\textbf{接续点。}','report','Constructibility equivalences proof')
        add_report(b,'充分一般的三个等价条件',extra)
        body+=report_pointer(n,'关于泛点、非空开集及闭点的三个等价条件之补证')+'\n'
    elif n==93:
        body=b.take(r'\section*{20.4（续）\quad “充分一般”的截面}',r'\section*{译校补证：为什么要量像的维数}','body','4.4, author note, 5.1 and discarded 4.6 layer')
        extra=b.take(r'\section*{译校补证：为什么要量像的维数}','\\medskip\n\\noindent\\textbf{接续点。}','report','Image dimension supplement and counterexample')
        add_report(b,'（4.4）的像维数补证及反例',extra)
        body+=report_pointer(n,'像维数版本的图判据、泛截面补证与一般态射反例')+'\n'
    elif n==94:
        body=b.take(r'\section*{5（续）\quad Seidenberg 型定理}',r'\section*{译校补证}','body','5.2--5.4')
        extra=b.take(r'\section*{译校补证}','\\medskip\n\\noindent\\textbf{接续点。}','report','Zero scheme, regularity, constructibility supplements')
        add_report(b,'（5.2）—（5.4）的补证',extra)
        body+=report_pointer(n,'零概形与余核、（5.3）(b)局部代数证明及（5.4）可构造性和开性补证')+'\n'
    elif n==95:
        body=b.take(r'\section*{5（续）\quad Seidenberg 型定理}',r'\section*{正式出版对应与译校补证}','body','5.5--5.7 and author editorial instructions')
        body=b.edit(body,r'\begin{proof}'+'\n按定义 $U_{\\calP}\\subseteq U$',r'\begin{proof}[译校订正证明]'+'\n按定义 $U_{\\calP}\\subseteq U$','The quotient on Y, rather than the ambient module in the original proof, is the object used by the corrected argument; original wording remains in the attached note.')
        extra=b.take(r'\section*{正式出版对应与译校补证}',r'\clearpage','report','Published reference correspondence and supplementary proofs')
        add_report(b,'（5.5）—（5.7）的出版对应及补证',extra)
        body+=report_pointer(n,'正式 EGA IV 的性质清单、Cohen--Macaulay 商及支撑固有性的补证')+'\n'
        body+=b.take(r'\section*{法第24页上部：划销的旧稿}','\\medskip\n\\noindent\\textbf{接续点。}','body','French p24 deleted author comments')
    elif n==96:
        body=b.take(r'\section*{6\quad 任意超平面截面的连通性}',r'\section*{译校补证：如何从泛纤维推出全部纤维}','body','6.1 and author instructions')
        extra=b.take(r'\section*{译校补证：如何从泛纤维推出全部纤维}',r'\section*{法25页末的版面校记}','report','Connectedness proof and properness counterexample')
        add_report(b,'（6.1）的补证和固有性反例',extra)
        body+=report_pointer(n,'从泛纤维推出全部纤维的补证及删去固有性的反例')+'\n'
        tail=b.take(r'\section*{法25页末的版面校记}',end,'body','Deleted title evidence')
        tail=b.edit(tail,'本批只登记页末标题，不将划销标题计作另一节，不声称已经译校第7.1条。','这里只登记页末标题，不将划销标题计作另一节；第7.1条接在下文。','Remove obsolete partial progress claim while preserving the deleted title.')
        body+=tail
    elif n==97:
        body=b.take(r'\section*{7\quad 应用于构造指定类型的超平面截面或多截面}',r'\section*{译校补证}','body','7.1')
        extra=b.take(r'\section*{译校补证}',r'\clearpage','report','Infinite-field selection and finite etale neighbourhood proof')
        add_report(b,'（7.1）的参数提升与有限平展换底',extra)
        body+=report_pointer(n,'无限域选点、局部坐标提升及有限平展覆盖的补证')+'\n'
        tail=b.take(r'\section*{法文划销旧稿：不并入正文}',end,'body','French pp26--27 discarded drafts')
        tail=b.edit(tail,r'\section*{法文划销旧稿：不并入正文}',r'\section*{法文划销旧稿的校记（非定稿）}','Keep deleted draft evidence in reading order with an explicit non-final status.')
        tail=b.edit(tail,'法28起笔是另一个未删的关于4.2与4.3的补记，留待下批。','法28起笔是另一个未删的关于4.2与4.3的补记，接在下文。','Replace obsolete next-batch instruction.')
        body+=tail
    elif n==98:
        body=b.take(r'\section*{7.1 末尾的补记：允许一部分坏点}',r'\section*{译校补证：从单纤维选取截面}','body','7.1 addendum, 7.2--7.3')
        body=b.edit(body,'对4.3中逐点定义且能应用第5节开性判据的(i)至(iv)',r'\par\noindent\textit{译校范围说明（非原文）。}对4.3中逐点定义且能应用第5节开性判据的(i)至(iv)','Distinguish the translator scope analysis from the manuscript statement of 7.3.')
        extra=b.take(r'\section*{译校补证：从单纤维选取截面}',r'\section*{法28末至法29开头：划销的另一条证明思路}','report','Bad-set dimension and flatness supplements/counterexample')
        add_report(b,'（7.2）—（7.3）的适用范围与补证',extra)
        body+=report_pointer(n,'单纤维选择、坏集维数、模平坦性和缺少（7.2）(v)限制的反例')+'\n'
        tail=b.take(r'\section*{法28末至法29开头：划销的另一条证明思路}',end,'body','Discarded Stein argument')
        tail=b.edit(tail,'下一条命题7.4不属于本批。','下接（7.4）的译校采用版本与原稿范围说明。','Remove obsolete batch boundary instruction.')
        body+=tail
    elif n==99:
        original=b.take(r'\section*{7.4\quad 原稿的命题与证明设想}',r'\section*{7.5\quad 关于射影性的备注}','report','7.4 general manuscript claim and induction route')
        original=b.edit(original,'下文另给出有明确附加假设的版本。','正文（7.4）采用另有明确附加假设的译校版本。','Update the direction of the reference after moving the adopted projective version into the main body.')
        remark=b.take(r'\section*{7.5\quad 关于射影性的备注}',r'\section*{译校补证}','body','7.5')
        before=b.take(r'\section*{译校补证}',r'\paragraph{一个可核验的射影版本.}','report','Non-strict inequality counterexample and zero-dimensional/local conclusions')
        projective=b.take(r'\paragraph{一个可核验的射影版本.}',r'\clearpage','body','Projective version; moved from translator supplement to explicitly identified adopted body')
        after=b.take(r'\clearpage',end,'report','Quasiprojective etale counterexample')
        projective=projective.replace(r'\paragraph{一个可核验的射影版本.}','',1).strip()
        assumptions,proof=projective.split('选取嵌入',1)
        body=r'''\egas{7.4}{命题：译校采用的附加条件版本}
'''+assumptions.strip()+r'''
则存在 $s$ 的开邻域 $U$ 及有限、平展、满射的 $S'\to U$，使 $X\times_S S'\to S'$ 有截面；
若 $k(s)$ 无限，还可取 $S'$ 为 $X_U$ 的闭子概形。\cmt{D18-099-7.4}{
这是第99批译校补证中的射影、有限表示、纯维版本，不是恢复出的法文原命题。
法文物理第29页原写固有、平坦，并要求不可分点集的维数严格小于 $n$；英文物理第20页误作 $\le n$。
纯不可分反例否定的是英译的放宽，不能据此否定法稿的严格不等号版本。
法稿一般陈述及原归纳路线完整见本版核查报告“D18-099：（7.4）一般原陈述、证明路线及限制”；
在一般固有情形，所给切割证明仍待核。}
\begin{proof}[译校补证，非原文]
选取嵌入'''+proof.strip()+r'''
\end{proof}

'''+remark
        body=b.edit(body,'假定 $g$ 射影、平坦、有限表示，$X_s$ 非空且纯维 $n$，并假定 $X_s$ 的非光滑轨迹维数小于 $n$。','假定 $g:X\\to S$ 射影、平坦、有限表示，取 $s\\in S$，并令 $n=\\dim X_s$。再假定 $X_s$ 非空且纯维 $n$，且 $X_s$ 的非光滑轨迹维数小于 $n$。','Restore g, s, and n definitions after moving the general manuscript statement to the report; no change to the adopted hypotheses.')
        old='作者接着提到，若只固有、光滑而不射影，同样结论可能失败；并提出可从非有限的 étale 态射寻找拟射影情形下的反例。'
        new='作者接着声称，可以给出固有、光滑但非射影而使同样结论失败的例子；他还说，一般不能把射影假设减弱为拟射影假设，并提出取非有限的 étale 态射作为反例的方向。'
        body=b.edit(body,old,new,'French p29 and English p21 both assert examples can be given; preserve the author claim without asserting an actual construction was supplied.')
        original+=r'\par\noindent\textbf{英译编辑层。}英文第20页在原命题末有脚注27：“不清楚，请询问 A.G.”；原证明的完整旧译仍见既有核查报告 D17-E01（该历史译文的 $\le n$ 只代表英文读法）。'+'\n'
        add_report(b,'（7.4）一般原陈述、证明路线及限制',original+before+after)
        body+=report_pointer(n,'英译不等号反例、零维基例、较弱的局部结论及拟射影反例')+'\n'
    save_body(b,body); b.finish()

# Preserve every old note in the replaced sections, including ones not repeated by
# the new batches.  The complete old body remains in the immutable archive.
old_specs=[('text/v5_01_02.tex',r'\egasection{§1',None),
           ('text/v5_03_06.tex',None,None),
           ('continuations/v_dot_early.tex',None,'% DOT_IMPORT 02')]
def brace_arg(s,pos):
    assert s[pos]=='{'; depth=1; i=pos+1
    while depth:
        assert i<len(s)
        if s[i]=='\\':
            if i+1<len(s) and s[i+1] in '{}%': i+=2; continue
        if s[i]=='{': depth+=1
        elif s[i]=='}': depth-=1
        i+=1
    return s[pos+1:i-1],i

old_report=[r'\subsec{D18-OLD：被替换的 §§1—7 旧注释保全清单}',
r'''下列各条逐字保留旧稿中的英译编注、译校注及原脚注内容，供核对修订沿革。
它们不是本版的新结论。其中“未见法文”“仍待核”“底本写”等说法只描述当时所据的英文载体；
第88—99批及上列本版源页核验给出的后续证据另行适用。旧报告的全部正文仍由原报告输入链保留。
特别是关于（7.4）的旧错误判定只针对英稿 $\le n$，不得迁移成对法稿 $<n$ 的判定。''']
count=0
for rel,start,end in old_specs:
    p=WORK/rel; s=p.read_text(); a=s.index(start) if start else 0; z=s.index(end) if end else len(s)
    src=s[a:z]; note_matches=list(re.finditer(r'\\(cmt|ednote|transnote|orig|origfootnote|footnote)\{',src))
    for m in note_matches:
        arg,e=brace_arg(src,m.end()-1); ident=''
        if m.group(1)=='cmt':
            ident=arg; arg,e=brace_arg(src,e)
        count+=1
        prefix=src[:m.start()]
        anchors=list(re.finditer(r'\\ega[ps]\{([^{}]+)\}',prefix))
        at=anchors[-1].group(1) if anchors else '§1／节首'
        title=f'旧注 {count:02}：{at}，{m.group(1)}'+('〔'+ident+'〕' if ident else '')
        old_report.extend([r'\paragraph{'+title+'}',arg])
        data['old_annotations'].append({'ordinal':count,'source':rel,'source_sha256':sha(p.read_bytes()),
            'line':s.count('\n',0,a+m.start())+1,'item':at,'macro':m.group(1),'old_id':ident,
            'text_sha256':sha(arg),'text':arg,'destination':'reports/v18_early_notes.tex / D18-OLD',
            'treatment':'Verbatim historical note, not asserted as current status.'})

# The full original proof of 2.12 is longer than the new batch's variant summary.
# Preserve the existing complete translation with its notes, explicitly as a
# historical source layer.  This does not duplicate any adopted body theorem.
old=(WORK/'text/v5_01_02.tex').read_text(); a=old.index(r'\begin{proof}[原文证明]',old.index(r'\egas{2.12}')); z=old.index(r'\egas{2.13}')
proof=old[a:z].strip()
fullproof=r'\subsection*{（2.12）原证明完整旧译（仅供对照，不予采用）}'+'\n'+proof+'\n'
for i,t in enumerate(report_parts):
    if 'D18-089：' in t: report_parts[i]=t+fullproof

intro=r'''% V18 early-manuscript integration report. Source archives remain unchanged.
\head{第一篇 §§1—7 回校整合}
\source{Dot第88—99批；法文物理第3—29页、英文物理第4—21页；（7.4）的后文说明另见英文第46页}
本章收入原批次的译校补证、反例及被替换的旧注释。正文中的法文删划层继续按其原位置标明。
整合核验读取了12份实际主源码与进度，逐段保存其内容；只对（2.4）、（2.12）、（7.4）等列明的源页作本轮独立图像核对，
不宣称已独立重审这12批全部证明或正式 EGA 的全部引用。
（2.12）的新增证明、（7.4）的射影附加条件版本以及各项明确标示的补证均属译校文字，不是原作者已写成的证明。
旧报告中关于未取得法文、只见英文等记录仍按历史原样保存；当前校勘结论以本版所列来源与范围为限。
'''
REPORT.write_text(intro+'\n\n'.join(report_parts)+'\n\n'+ '\n\n'.join(old_report)+'\n')
data['report']={'path':str(REPORT.relative_to(WORK)),'sha256':sha(REPORT.read_bytes()),'bytes':REPORT.stat().st_size}
data['old_annotation_count']=count
data['input_order']=[f'continuations/v18_batch{n:03}.tex' for n in range(88,100)]
data['macro_scope']='Every body module and migrated batch report block is grouped. OO/FF/GG/PP/calP/dd/Div/depth/pr/coker are local definitions only.'
data['untouched_old_sources']={rel:sha((WORK/rel).read_bytes()) for rel,_,_ in old_specs}
data['source_pdfs']={p.name:{'path':str(p.relative_to(REPO)),'sha256':sha(p.read_bytes()),'bytes':p.stat().st_size} for p in (REPO/'archive_20261121/03_sources').iterdir() if p.name in ['EGA5_francais.pdf','EGAVaiello.pdf']}
RECORD.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'modules':12,'old_notes_retained':count,'report_bytes':REPORT.stat().st_size,'record':str(RECORD)},ensure_ascii=False))
