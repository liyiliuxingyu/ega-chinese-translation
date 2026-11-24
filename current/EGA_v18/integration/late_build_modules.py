#!/usr/bin/env python3
"""Assemble Dot 69--87 in the v18 working copy, without changing archived sources.

Run from any directory.  This script only writes this task's newly generated
continuations, report, and late_* evidence files.  The full source ranges and
all editorial adaptations are recorded in late_integration.json.
"""
from __future__ import annotations

import collections
import hashlib
import json
import re
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
REPO = PROJECT.parents[1]
ARCHIVE = REPO / "dot_updates_20261124"
OUT = PROJECT / "integration"

# Original, one-based line intervals.  Every author paragraph and every
# translator supplement in these intervals has been read before assembly.
SPECS = {
    69: ((16,35),(36,55),"极化与判别式：16.1—16.3"),
    70: ((16,64),(65,81),"校正判别式：16.4—16.8"),
    71: ((19,97),(98,111),"光滑二次型判据：16.9—16.11.2"),
    72: ((21,48),(49,71),"正交群、挠子与局部等平凡性：16.12—16.14"),
    73: ((25,143),(144,168),"第三篇卷首与射影丛的 Picard 群"),
    74: ((27,124),(125,140),"射影丛同构与相对有效除子：1.6—2.4"),
    75: ((25,93),(94,110),"多重射影丛：2.5—2.10"),
    76: ((22,119),None,"可逆模指定的相对除子：2.11—2.13"),
    77: ((24,128),None,"第三篇第3节：固定点与转置除子族"),
    78: ((26,88),(89,112),"两个投影与命题3.1"),
    79: ((24,94),(95,123),"命题3.2与深度引理"),
    80: ((25,95),(96,106),"相对伪态射与可逆层延拓：3.3—3.4"),
    81: ((26,87),(88,98),"局部阶乘情形与线性系分类：3.5—4.1"),
    82: ((30,76),(77,90),"线性系与格拉斯曼概形：4.2"),
    83: ((26,70),(71,81),"命题4.3的域底情形与射影标架"),
    84: ((28,86),(87,105),"命题4.3的一般底证明与无穷小差"),
    85: ((27,75),(76,127),"命题4.4的底除子修订与补证"),
    86: ((22,68),None,"致迪厄多内的信及其划删段落"),
    87: ((14,46),(48,75),"法文第150页提纲与第153页卷首异扫"),
}

REPLACEMENTS = {
    71: [("上一批命题16.2", "命题16.2"),
         ("参看第69批的相对 Cartier 平坦性说明", "参看本版核查报告 L18-069 的相对 Cartier 平坦性说明")],
    73: [("校核附记给出这里所需的有限表示下降", "本版核查报告 L18-073 给出这里所需的有限表示下降")],
    74: [("仍采用第73批的商的约定", "仍采用前文的一维商约定"),
         ("这里和上一批的零次情形同样采用商约定", "这里和前述零次情形同样采用商约定")],
    75: [("译校附记给出反例和迭代证明", "本版核查报告 L18-075 给出反例和迭代证明")],
    77: [("法文物理126页先前划销的“除子族”草稿不属于这里的正文。", "法文物理126页先前划销的“除子族”草稿，另见本版“第三篇删划草稿补译”中对应页段，作为非定稿材料保存；仍未辨的笔迹在那里单列。")],
    79: [("原稿简写的降阶见下方补证", "原稿简写的降阶见本版核查报告 L18-079")],
    80: [("见下方译校补证", "见本版核查报告 L18-080")],
    81: [("见下方补证", "见本版核查报告 L18-081"),
         ("下方补证明确在局部诺特情形使用该方法", "本版核查报告 L18-081 明确在局部诺特情形使用该方法"),
         ("见下方说明", "见本版核查报告 L18-081"),
         ("原第79批深度比较", "本版核查报告 L18-079 的深度比较"),
         ("法136大叉划删的后续段落不计入正文。", "法136大叉划删的后续段落，另见本版“第三篇删划草稿补译”中对应页段；其稿层身份及仍未辨的部分单列。")],
    82: [("见下方译校补证", "见本版核查报告 L18-082"),
         ("法140随后大段划删、不收入正文；边栏有不易辨读的手写，暂不补造。", "法140随后划销的旧推论5.3及解释，另见本版“第三篇删划草稿补译”中对应页段；该旧弱假设不能采用，边栏未辨文字另列。")],
    83: [("再用相对 Cartier 判据，见补证", "再用相对 Cartier 判据，见本版核查报告 L18-083"),
         ("补证给出有限仿射开检验", "本版核查报告 L18-083 给出有限仿射开检验"),
         ("见下方矩阵核查", "见本版核查报告 L18-083 的矩阵核查"),
         ("命题4.3的任意底情形在底本下一段另证。", "命题4.3的任意底情形接在正文的域底证明之后；相应补证见本版核查报告 L18-084。")],
    84: [("下文补证明确比较的有限数据", "本版核查报告 L18-084 明确比较的有限数据"),
         ("再用克鲁尔交定理；见补证", "再用克鲁尔交定理；见本版核查报告 L18-084")],
    87: [("现行合订本已收相应目录与编写说明；以下供校勘，不计成新增一节。", "现行合订本已收相应目录与编写说明；对照译文见本版核查报告 L18-087，不计成新增一节。")],
}

READ_SOURCE_PAGES = {
    "english": [78,80,81,86,87,90,106,107,108,109],
    "french": [1,126,136,140,141,143,144,145,150,153,161,162,164],
}

DISPLAY_LAYOUT_PATCHES = {
    70: [(r"""\[
Q=aX^2+bY^2+cZ^2+dXY+eXZ+fYZ
\quad\Longrightarrow\quad
\widetilde d(Q)=4abc-af^2-be^2-cd^2+def .
\]""",r"""\[
\begin{gathered}
Q=aX^2+bY^2+cZ^2+dXY+eXZ+fYZ\\
\quad\Longrightarrow\quad
\widetilde d(Q)=4abc-af^2-be^2-cd^2+def .
\end{gathered}
\]""")],
}

def strip_display_layout(text):
    for token in (r"\begin{gathered}",r"\end{gathered}",r"\\"):
        text=text.replace(token,"")
    return re.sub(r"\s+","",text)

def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def part(lines, interval):
    return "\n".join(lines[interval[0]-1:interval[1]]) + "\n"

def local_macros(source: str) -> str:
    lines = []
    for line in source.split(r"\begin{document}", 1)[0].splitlines():
        m = re.fullmatch(r"\\newcommand\{(\\[A-Za-z]+)\}(\{.*\})", line.strip())
        if m:
            lines.append(r"\def" + m[1] + m[2])
        m = re.fullmatch(r"\\DeclareMathOperator\{(\\[A-Za-z]+)\}\{(.*)\}", line.strip())
        if m:
            lines.append(r"\def" + m[1] + r"{\operatorname{" + m[2] + "}}")
    return "\n".join(lines) + "\n"

def balanced_argument(text: str, start: int) -> tuple[str,int]:
    """start is the first character after the opening brace."""
    level = 1
    i = start
    while i < len(text):
        c = text[i]
        # TeX escaped braces are printed braces.  Count preceding slashes so
        # that a line-break control sequence before a brace is not mistaken.
        k = i - 1
        while k >= 0 and text[k] == "\\":
            k -= 1
        escaped = (i - 1 - k) % 2 == 1
        if not escaped:
            if c == "{": level += 1
            elif c == "}": level -= 1
        i += 1
        if level == 0:
            return text[start:i-1], i
    raise ValueError("Unclosed argument")

def original_notes(text):
    ans=[]
    for m in re.finditer(r"\\footnote\{",text):
        content,end=balanced_argument(text,m.end())
        ans.append(content)
    return ans

def move_display_notes(text: str, changes: list) -> str:
    """Attach a note immediately after a display to its preceding prose.

    Only placement changes.  Note payload is preserved byte for byte.
    Lists are not moved automatically because their last item is the better
    anchor; those are retained and separately exposed by the source audit.
    """
    pat = re.compile(r"(\\\]|\\end\{(?:align\*?|equation\*?|gather\*?)\})(\s*)\\footnote\{")
    while True:
        m = pat.search(text)
        if not m: break
        note_begin=m.end()-len(r"\footnote{")
        payload,end=balanced_argument(text,m.end())
        note=text[note_begin:end]
        close=m[1]
        if close==r"\]":
            begin=text.rfind(r"\[",0,m.start())
        else:
            env=re.search(r"\{([^}]+)\}",close)[1]
            begin=text.rfind(r"\begin{"+env+"}",0,m.start())
        if begin<0: raise ValueError("Display opener missing")
        lead=text[:begin]
        lead_stripped=lead.rstrip()
        if not lead_stripped:
            raise ValueError("No prose anchor before display")
        changes.append({"kind":"note_marker_relocated_before_display", "payload_sha256":sha(payload.encode()),
                        "anchor_suffix":lead_stripped[-100:]})
        text=lead_stripped+note+lead[len(lead_stripped):]+text[begin:note_begin]+text[end:]
    return text

def statements(text,n,changes):
    pat=re.compile(r"(?m)^(?:(?:\\medskip|\\smallskip|\\noindent)\s*)*\\textbf\{(?:(命题|定理|引理|推论|定义|评注)\s*)?(\d+(?:\.\d+)+)(（[^}]*?）)?[.。]\}(?:\\quad)?[ \t]*")
    def replace(m):
        kind,num,qual=m[1],m[2],m[3] or ""
        label=(kind or "")+qual
        scope="V-Q" if n<=72 else "V-L"
        if n==79 and kind=="引理" and num=="3.1":
            scope="V-L-depth"
        cmd=(r"\egas{"+num+"}{"+label+"}" if label else r"\egap{"+num+"}")
        if scope=="V-L-depth":
            cmd=r"\def\newscope{V-L-depth}"+"\n"+cmd
        changes.append({"kind":"numbered_anchor", "number":num,"title":label,"scope":scope})
        return cmd+"\n"
    return pat.sub(replace,text)

def adapt(text,n,changes,*,report=False):
    for old,new in REPLACEMENTS.get(n,[]):
        if old in text:
            changes.append({"kind":"cross_reference_update", "old":old,"new":new,"count":text.count(old)})
            text=text.replace(old,new)
    # The independent PDFs inserted artificial page breaks.  The ctexbook
    # master chooses page and chapter breaks itself.
    for token in (r"\newpage",r"\clearpage"):
        if token in text:
            changes.append({"kind":"layout_command_removed","token":token,"count":text.count(token)})
            text=text.replace(token,"")
    if report and n in (69,70,71):
        for token in (r"\begingroup\small", r"\par\endgroup"):
            if token in text:
                changes.append({"kind":"standalone_note_layout_removed","token":token})
                text=text.replace(token,"")
    if not report:
        text=statements(text,n,changes)
        # Only structural headings that actually begin in this fragment.
        text=text.replace(r"\section*{",r"\egasection{")
    elif n==87:
        text=text.replace(r"\section*{",r"\subsec{")
    text=move_display_notes(text,changes)
    return text

def number_notes(text,n,counter,records,destination):
    pat=re.compile(r"\\footnote\{")
    cursor=0; chunks=[]
    for m in pat.finditer(text):
        counter+=1
        content,end=balanced_argument(text,m.end())
        note_id=f"L18-{n:03}-{counter:02}"
        chunks.extend([text[cursor:m.start()], r"\cmt{"+note_id+"}{"])
        cursor=m.end()
        records.append({"id":note_id,"destination":destination,"content_sha256":sha(content.encode()),
                        "first_text":content[:100]})
    chunks.append(text[cursor:])
    return "".join(chunks),counter

DISPLAY=re.compile(r"\\\[.*?\\\]|\\begin\{(align\*?|equation\*?|gather\*?|tikzcd|CD)\}.*?\\end\{\1\}",re.S)
def display_blocks(text):
    # Regex backreferences refer to the one captured environment name; the
    # \[ branch has no environment name and still yields its full match.
    return [m.group(0) for m in DISPLAY.finditer(text)]

def math_counts(text):
    return collections.Counter(sha(m.encode()) for m in display_blocks(text))

def normalized_cmt_notes(text):
    out=[]
    for m in re.finditer(r"\\cmt\{[^{}]+\}\{",text):
        out.append(balanced_argument(text,m.end())[0])
    return out

def main():
    data=json.loads((ARCHIVE/"INDEX.json").read_text())
    records={r["source_label"]:r for r in data["records"]}
    report_parts=[REPORT_INTRO]
    manifest={
        "schema":"ega-v18-dot69-87-integration/1",
        "status":"modules_assembled_pending_master_build",
        "policy":"原件只读；重排正文、报告迁移及编号锚点，不冒称全篇数学复审。",
        "source_index":"dot_updates_20261124/INDEX.json",
        "source_index_sha256":sha((ARCHIVE/"INDEX.json").read_bytes()),
        "ordered_inputs_after_v_suppIII_68":[f"continuations/v18_batch{n:03}.tex" for n in range(69,73)],
        "ordered_inputs_after_first_essay_section15":[f"continuations/v18_batch{n:03}.tex" for n in range(73,88)],
        "report_input":"reports/v18_late_notes.tex",
        "required_packages":"既有 preamble.tex 足够；amsmath/amssymb、hyperref、enumitem、tikz-cd 已有。新增模块不加载类或宏包。",
        "scope_conventions":{"69-72":"V-Q","73-85":"V-L","79 Lemma 3.1":"V-L-depth，保留原印编号，区分同篇命题3.1","86":"V-L-letter","87":"V-L-source"},
        "source_visual_check":{"viewed_physical_pages":READ_SOURCE_PAGES,"not_a_full_page_or_math_review":True},
        "records":[],
    }
    for language,file in [("french","EGA5_francais.pdf"),("english","EGAVaiello.pdf")]:
        source_path=REPO/"archive_20261121/03_sources"/file
        manifest.setdefault("source_files",{})[language]={"path":str(source_path.relative_to(REPO)),"sha256":sha(source_path.read_bytes())}
    for n,(body_span,report_span,title) in SPECS.items():
        r=records[n]
        src=ARCHIVE/r["main_tex_path"]
        source=src.read_text()
        assert sha(src.read_bytes())==r["source_tex_sha256"], (n,"source changed")
        lines=source.splitlines()
        raw_body=part(lines,body_span)
        raw_report=part(lines,report_span) if report_span else ""
        changes=[]
        # The old report title is replaced by a stable, unique report section.
        if report_span and n!=87:
            old_title=raw_report.splitlines()[0]
            assert old_title.startswith(r"\section*{"),(n,old_title)
            raw_report=raw_report[len(old_title):].lstrip("\n")
            changes.append({"kind":"report_heading_replaced","old":old_title,"new":f"L18-{n:03} {title}"})
        body=adapt(raw_body,n,changes)
        notes=adapt(raw_report,n,changes,report=True) if raw_report else ""
        for old,new in DISPLAY_LAYOUT_PATCHES.get(n,[]):
            assert notes.count(old)==1, (n,"layout patch target missing")
            assert strip_display_layout(old)==strip_display_layout(new), (n,"mathematical token change")
            notes=notes.replace(old,new)
            changes.append({"kind":"display_line_break_only","old":old,"new":new,
                            "mathematical_tokens_unchanged_after_removing_only_gathered_wrapper_and_line_break":True})
        if n==73:
            needle=r"\egasection{§1　射影丛上的可逆层与除子；除子的线性系}"
            assert needle in body
            addition=(needle+"\n"+r"\NewNote{英译编辑者注明：以下自本节开头至零次态射段末的一段，在手稿中已被划去。本版为保存预备笔记而译录，段末另有终止标记；不把这一稿层当作正式刊定文字。}")
            body=body.replace(needle,addition,1)
            changes.append({"kind":"source_status_preserved_from_cover","source_line":23,
                            "meaning":"把§1至零次态射末的划销身份移至对应正文起点，保留已有终止标记。"})
        if n==87:
            body=body.replace(r"\chapter*{法文扫描第150页：手写提纲}", r"\egasection{法文扫描物理第150页：手写提纲}")
            body=body.replace(r"\egasection{正向条目}",r"\subsec{正向条目}")
            body=body.replace(r"\egasection{旋转半周后阅读的笔记}",r"\subsec{旋转半周后阅读的笔记}")
            changes.append({"kind":"duplicate_frontmatter_relocated","source_lines":[48,75],
                            "destination":"reports/v18_late_notes.tex / L18-087","unique_new_author_text":False})
        if n==86:
            body=body.replace(r"\egasection{致迪厄多内的信\quad 1965年9月29日}", r"\egasection{1. 致迪厄多内的信（1965年9月29日）}")
            changes.append({"kind":"structural_heading","meaning":"保留英译编排的第四篇、第1节及书信日期；编辑身份已在第一条原有译校注说明。"})
        # One report description is a factual period-boundary marker, not
        # mathematical content.  The corresponding footer is kept verbatim
        # in the archived source and mapped explicitly here.
        note_records=[]
        body,note_counter=number_notes(body,n,0,note_records,"body")
        notes,note_counter=number_notes(notes,n,note_counter,note_records,"report")
        expected_count=len(original_notes(raw_body+raw_report))
        assert note_counter==expected_count,(n,note_counter,expected_count)
        scope="V-Q" if n<=72 else ("V-L-letter" if n==86 else "V-L-source" if n==87 else "V-L")
        header=(f"% Dot batch {n}; source SHA-256: {r['source_tex_sha256']}\n"
                +f"% Archived source: dot_updates_20261124/{r['main_tex_path']}\n"
                +f"% Original body lines: {body_span[0]}--{body_span[1]}; integration map: integration/late_integration.json\n"
                +r"\begingroup"+"\n"+r"\def\newscope{"+scope+"}\n"+local_macros(source))
        if n==69: header+=r"\head{附录 17.16：光滑二次型}"+"\n"
        if n==73: header+=r"\head{第三篇}"+"\n"
        if n==86: header+=r"\head{第四篇}"+"\n"
        if n==87: header+=r"\head{来源补遗：邻接手稿与卷首异扫}"+"\n"
        output=header+body.rstrip()+"\n"+r"\par\endgroup"+"\n"
        dest=PROJECT/f"continuations/v18_batch{n:03}.tex"
        dest.parent.mkdir(parents=True,exist_ok=True)
        dest.write_text(output)
        if notes:
            prefix=(r"\begingroup"+"\n"+local_macros(source)
                    +r"\egasection{L18-"+f"{n:03}　{title}"+"}\n"
                    +r"\hypertarget{audit:L18-"+f"{n:03}"+"}{}\n"
                    +r"\source{原独立续译第"+str(n)+"批；英稿物理页 "+r['source_scope']['english_physical_pages_description']
                    +"；法稿物理页 "+r['source_scope']['french_physical_pages_description']+"}\n")
            if n==87:
                prefix+=r"\NewNote{下列是法文物理第153页的卷首异扫对照译文，属于同文校勘材料，不是新增一节正文；字迹或扫描缺损标记仍依原独立包保留。}"+"\n"
            report_parts.append(prefix+notes.rstrip()+"\n"+r"\par\endgroup"+"\n")
        combined_body_report=body+notes
        # Layout commands, links and headings change; displayed mathematics
        # and diagrams are checked as raw token strings, multiplicities too.
        expected_math=math_counts(raw_body+raw_report)
        actual_math=math_counts(combined_body_report)
        raw_math_equal=expected_math==actual_math
        adapted_actual=actual_math.copy()
        for old,new in DISPLAY_LAYOUT_PATCHES.get(n,[]):
            assert adapted_actual[sha(new.encode())]==1
            adapted_actual.subtract({sha(new.encode()):1})
            adapted_actual.update({sha(old.encode()):1})
        adapted_actual=+adapted_actual
        assert expected_math==adapted_actual,(n,"displayed mathematical content changed",expected_math-adapted_actual,adapted_actual-expected_math)
        excluded=[]
        included=set(range(body_span[0],body_span[1]+1))
        if report_span:included.update(range(report_span[0],report_span[1]+1))
        for i,line in enumerate(lines,1):
            if i not in included:
                excluded.append({"line":i,"text":line})
        record={
            "batch":n,"source_archive":r['archive_path'],"source_zip_sha256":r['zip_sha256'],
            "source_tex":str(src.relative_to(REPO)),"source_tex_sha256":sha(src.read_bytes()),
            "body_source_lines":list(body_span),"report_source_lines":list(report_span) if report_span else None,
            "body_target":str(dest.relative_to(PROJECT)),"body_target_sha256":sha(dest.read_bytes()),
            "report_target":f"reports/v18_late_notes.tex / L18-{n:03}" if report_span else None,
            "source_scope":r['source_scope'],"original_progress_is_historical":True,
            "edits":changes,"local_macro_definitions":local_macros(source).splitlines(),
            "footnotes":note_records,"footnote_count":expected_count,
            "display_blocks_count":sum(expected_math.values()),"display_blocks_and_diagrams_exact_multiset_preserved":raw_math_equal,
            "display_math_preserved_with_recorded_layout_only_changes":True,
            "excluded_lines":excluded,
            "excluded_material_reason":"独立包文档外壳、封面、旧范围/进度/下一处、重复临时标题、旧入册说明；73第23行的划销身份已转入正文；正文和译校附记的具体区间见上。",
        }
        manifest['records'].append(record)
    report="\n".join(report_parts)
    report_path=PROJECT/"reports/v18_late_notes.tex"
    report_path.write_text(report)
    manifest['report_sha256']=sha(report_path.read_bytes())
    addenda_path=PROJECT/"continuations/v18_deleted_addenda.tex"
    if addenda_path.exists():
        manifest['additional_deleted_draft_translation']={
            "path":str(addenda_path.relative_to(PROJECT)),"sha256":sha(addenda_path.read_bytes()),
            "source_physical_pages":[126,136,140],"scope":"V-D",
            "placement":"after v18_batch087.tex",
            "status":"三块可辨删划主体的本轮补译；父代理已逐块对照原页复核内容；覆打与缺损仍标未辨；全局构建由父代理完成。"}
    manifest['counts']={"batch_modules":19,"report_sections_from_batches":sum(v[1] is not None for v in SPECS.values()),
                        "source_note_count":sum(r['footnote_count'] for r in manifest['records']),
                        "display_blocks_and_diagrams":sum(r['display_blocks_count'] for r in manifest['records'])}
    (OUT/"late_integration.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
    (OUT/"late_input_order.tex").write_text(
        "% These are integration instructions, not a separate standalone document.\n"
        "% Immediately after continuations/v_suppIII_68.tex:\n"
        +"\n".join(r"\input{continuations/v18_batch"+f"{n:03}"+"}" for n in range(69,73))
        +"\n% After the first essay, sections 1--15, before its old backmatter:\n"
        +"\n".join(r"\input{continuations/v18_batch"+f"{n:03}"+"}" for n in range(73,88))
        +"\n% Three explicitly crossed-out French blocks, kept as a draft layer:\n"+r"\input{continuations/v18_deleted_addenda}"+"\n"
        +"\n% In report.tex:\n"+r"\input{reports/v18_late_notes}"+"\n")
    print(json.dumps(manifest['counts'],ensure_ascii=False))

REPORT_INTRO = r"""% Integration report for Dot batches 69--87.  See integration/late_integration.json.
\head{第十八版新增续稿译校附记（Dot 69—87）}
\egasection{本次整合与定点复核范围}
本组把已经存在的十九个独立续译包接入合订稿：第69—72批为第二篇附录17.16，第73—85批为第三篇，第86批为1965年9月29日致迪厄多内的信，第87批为邻接手稿及卷首异扫。作者正文、证明、原稿写作意见、可辨残文及原独立译稿的脚注均保留。独立包末的长篇译校说明移入以下对应小节；这些补证是译校文字，并非格罗滕迪克原稿。本次接入不等于对上述全部数学结论完成新的独立审定。

本次实际查看的底本图像为：英译物理第78、80、81、86、87、90、106—109页；法文物理第1、126、136、140、141、143—145、150、153、161、162、164页。以下只记录由这些页面以及对应译稿逐段读取得到的定点结论；其他脚注中的历史核查、外部文献和补证保留其原有来源身份，不把它们全部改称本轮重新验证的结果。

\begin{enumerate}[label=\arabic*.]
\item \textbf{16.2、16.3及16.9。} 英78、法161的16.2原句没有正秩限定；原独立译稿依15.1的定义补加正秩，并以脚注明示，这一处理予以保留。法162的16.3确写作二次型的二变量记号以及秩减一；正文沿用二次型的单变量记号和射影超曲面维数“秩减二”，原读法及几何理由留在脚注。英80—81、法164把恒秩条件放在16.9的第三项附近，整合稿明确先列前两项的等价，再在恒秩条件下加入后两项；没有把所有局部自由模都无条件换成同一秩的标准型。
\item \textbf{16.8的直和系数。} 法164作直和，英80误作张量积；两页在两奇秩情形都给出系数2。原独立稿改为系数4，并给出两个秩一型的直接检验，本次保留其正确正文及原错脚注。16.6(c)的法稿上标痕迹仍按原独立注的谨慎说法记录；没有把该墨迹强行判定为另一条数学断言。
\item \textbf{第三篇的划销稿层。} 英87在第1节开头注明一段在原稿中已被划去，英90在零次态射段末明确结束该范围。原包把起点说明放在封面范围段，整合时将其移到实际正文起点，并保留终点说明；这样既保留材料，也不混淆其稿层。
\item \textbf{命题4.3。} 法140在总假设中手加“局部”，而(a)另加“有限表示”；法141在(b)明写满射。原包据此区分两层假设，予以保留。法144及英109的无穷小论证有一处将“余切映射满射”漏写为原态射满射；原包已补星号。法145和英109的相应 Hom 式把靶写到射影空间的结构层，整合稿沿用原包按拉回后的定义域改成源空间结构层的订正。原作者关于未来无穷小理论及避免循环依赖的写作说明完整保留；本轮没有把这段略证重新宣称为无条件全证。
\item \textbf{书末材料与同文去重。} 法150的草记和倒写笔记仍单列为来源补遗，未辨定词句及公式保留明确标记。法153与法1的题名、目录和末段为同文异扫，并非新的一章；其完整对照译文移到L18-087。第87批原包中的旧“入册方式”“下一处”不作为本版现行进度，完整原件仍保留在归档中。
\end{enumerate}

另按原页新补译三处先前未录的划销材料：法126页中上部从“设$X$在$S$上平坦且局部有限表示”至“至迟在第五章”的整块旧引入；法136页下部从“命题2(b)向我们表明”至“称为与除子线性系相关联的可逆模”的旧论证；法140页中部带原编号5.3的旧推论及其解释。本版在来源补遗之后另设“第三篇删划草稿补译（非定稿）”一章，完整译出这三块可辨主体。三处原独立稿中的未收入说明已改为对应来源引用。法136上半的密集覆打、两个关于$D$的缺损条件、法140斜边注及法126的小笔迹仍保留未辨标记；这个补译范围不等于对法文171页作了全面遗漏审计，也不以英译编辑稿到达末页宣布全部手稿完成。新章中另外标明了参数模的对偶、恢复可逆模前的负扭转以及旧推论5.3弱假设不足三项处理，具体图像位置和依据见工程的划销块记录。

第三篇保留原印的“命题3.1”和另一个“引理3.1”；电子锚点对后者使用单独范围，以避免超链接混淆，不改动纸面编号。各批的特殊数学宏只在本批局部组内定义，不改变合订稿已有宏的意义。独立包封面、重复的“续”标题及人工分页命令不移入正文；这种版面整理不删数学段落。少量“下方补证”“上一批”改为本报告的确切位置；显示公式之后孤立的脚注引标移到公式前的引导句，脚注内容及公式保持不变。完整行号映射、散列、锚点及脚注编号见工程中的整合记录。
"""

if __name__ == "__main__":
    main()
