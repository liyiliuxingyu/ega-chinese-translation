from pathlib import Path
import shutil,json,re,hashlib,datetime
W=Path('/workspace/scratch/a886fd56dd2f/edition19_work')
R=Path('/workspace/scratch/a886fd56dd2f/ega-recovery')
P=R/'current/EGA_v19'
# All mutations are confined to the new edition.
newmods=['v19_8_14_18.tex','v19_8_end.tex','v19_section9.tex','v19_section10.tex','v19_section11.tex']
for name in newmods:
 src=W/'sections'/name
 if src.is_file(): shutil.copy2(src,P/'continuations'/name)
for src in (W/'reports').glob('*.tex'): shutil.copy2(src,P/'reports'/src.name)
p=P/'main.tex';s=p.read_text();s=s.replace(r'\input{continuations/v18_first_8_14_onward.tex}', '\n'.join(r'\input{continuations/'+n+'}' for n in newmods));p.write_text(s)
p=P/'preamble.tex';s=p.read_text().replace('第十八版·Dot续稿与回校整合','第十九版·第一篇8.14至第11节法英回校').replace('第十八版（Dot续稿与回校整合）','第十九版（第一篇续校）');p.write_text(s)
p=P/'frontmatter.tex';s=p.read_text();a=s.index('第十八版在');b=s.index('\\section*{正文次序}',a)
s=s[:a]+'''第十九版以已发布的第十八版实际源码为基础，继续对读第五卷预备笔记第一篇的8.14至第11节末：法文物理46页下部至63页，英文32至43页第12节以前。旧译按段替换，作者证明、脚注、删划与编辑注继续保存。本轮修复固定分支和维数条件等实质问题，也恢复英译漏失的法稿条件；译者补证均另标身份。此前已收入的Dot原批号69--108及所有其他已译正文保留。\n\n''' +s[b:]
s=s.replace('本版接入英文物理78--112页的','既有英文物理78--112页的').replace('并收入法文物理150页提纲和153页异扫说明。第一篇§§1--7与8.1--8.13采用新增回校稿；后续原有段落保留。','以及法文物理150页提纲和153页异扫说明均保留。第一篇§§1--7及8.1--8.13沿用第十八版回校稿；本版继续回校8.14至第11节，§§12--15沿用旧稿。')
a=s.index('本轮把已经实存的Dot译稿');b=s.index('已确认的原文错误',a)
s=s[:a]+'''本轮续校针对原稿和现存译文，不把已经收入的Dot译稿重新计为新译。主要改动包括：8.16与8.18原条件的反例及明确加强范围；一般线性系的固定分支和投影维数；9.3的附加条件；爆破条目的正则性范围；第11节法稿中被英译遗漏的条件。每项错误、原说法与订正依据见正文脚注及累计核查报告的新篇。旧第十八版工程与报告全部另行保存。\n\n''' +s[b:]
a=s.index('第一篇最新法英回校止于');b=s.index('正式第IV章仍另从',a)
s=s[:a]+'''第一篇本版法英回校止于第11节末（法文物理63页；英文物理43页第12节以前）。下一回校位置为法文物理64页的第12节，对读英文物理43页中段；既有对应源码为\\texttt{continuations/v\\_dot\\_middle.tex}。这些后文已经有译文，下一步是据底本严谨回校。\n\n''' +s[b:]
p.write_text(s)
p=P/'report.tex';s=p.read_text().replace('第十八版·Dot续稿与回校整合','第十九版·第一篇续校').replace('Dot第69--108批整合、来源对读与历史核查档案','第一篇8.14至第11节法英回校、反例与历史核查档案')
a=s.index('本报告首先记录');b=s.index('\\tableofcontents',a)
s=s[:a]+'''本报告首先记录第十九版对第一篇8.14至第11节的法英对读。确证原文错误的订正及反例、英译误读的恢复、译者补证和未审范围分别列明。正文采用有依据的表述，原说法和理由进入脚注；未能恢复的残文不根据后文补造。\n\n本轮核查还纠正了旧报告的若干归责：法稿本来正确而英译漏失的公式或条件，不再归为原作者错误。历史报告完整保留，其“本轮”“未见法稿”和旧判断均指制作当时；涉及本次回校范围时，以本版直接对读的证据为准。\n\n第I、II、III章、第0章、第五卷其余篇章及Dot原批稿继续保留，未被重新宣称为本轮全部数学审定。全书尚未完结；技术构建、逐页输出比对和抽样版面检查也不等同于数学完备性。\n\n''' +s[b:]
marker='\\mainmatter\n'
intro='''\\input{reports/v19_integration_audit.tex}
\\input{reports/v19_8_14_18_audit.tex}
\\input{reports/v19_8_end_audit.tex}
\\input{reports/v19_sections9_10_audit.tex}
\\input{reports/audit_section11.tex}
\\setcounter{secnumdepth}{-2}
\\part{历史核查记录：第十八版}
\\setcounter{secnumdepth}{2}
\\NewNote{以下保留第十八版报告，所指新回校范围止于8.13。第十九版已继续至第11节，涉及法稿异文的最新判断见本报告前部。}
'''
s=s.replace(marker,marker+intro,1);s=s.replace('不自动代表第十八版状态','不自动代表第十九版状态');p.write_text(s)
# Move only version-bound current result records aside; preserve historical records.
h=P/'checks/history_v18';h.mkdir(exist_ok=True)
for q in list((P/'checks').glob('current_*.json'))+[P/'checks/visual_verification_summary.json']:
 if q.is_file(): shutil.move(str(q),str(h/q.name))
p=P/'checks/check_current_project.py';s=p.read_text().replace('BASE = REPO / "archive_20261121/01_project/EGA_v17"','BASE = REPO / "current/EGA_v18"').replace('"edition": 18','"edition": 19')
s=s.replace('if "continuations/v18_first_8_14_onward.tex" not in book_inputs:\n        errors.append("existing text from 8.14 onward is missing")', '''revised = ["continuations/" + name for name in ["v19_8_14_18.tex", "v19_8_end.tex", "v19_section9.tex", "v19_section10.tex", "v19_section11.tex"]]
    for name in revised:
        if book_inputs.count(name) != 1:
            errors.append("revised module not included exactly once: " + name)
    if "continuations/v18_first_8_14_onward.tex" in book_inputs:
        errors.append("superseded 8.14-section11 module is still input")
    for name in ["continuations/v_dot_middle.tex", "continuations/v_dot_late.tex"]:
        if book_inputs.count(name) != 1:
            errors.append("inherited later sections missing: " + name)''')
p.write_text(s)
# Never present the inherited PDF metadata as new results while building.
for name in ['HANDOVER_STATE.json','ARTIFACTS.json']:
 q=P/name
 shutil.copy2(q,P/'checks/history_v18'/name)
state={'edition':19,'date':'2026-11-25','time_zone':'Asia/Shanghai','status':'recollation_in_progress','all_books_finished':False,'current_project':'current/EGA_v19','base_commit':'f1ade3db412d2167779d4b8f9fa2ed04a4daf0c3','base_project':'current/EGA_v18','immutable_dot_source':'dot_updates_20261124','integrated_existing_dot_batches':list(range(69,109)),'recollated_this_round':{'work':'EGA V first essay','range':'8.14 through end of section11','french_physical_pages':'46 lower–63','english_physical_pages':'32–43 before section12'},'next':{'work':'EGA V first essay §12','french_physical_page':64,'english_physical_page':43,'existing_source':'continuations/v_dot_middle.tex'},'other_unfinished_branch':'EGAIV.1 physical221 synopsis,222–223 introduction,223 (1.1.1)','technical_checks':'pending actual v19 build; inherited metadata saved as history_v18'}
(P/'HANDOVER_STATE.json').write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n')
(P/'ARTIFACTS.json').write_text(json.dumps({'edition':19,'status':'pending actual build','files':[]},indent=2)+'\n')
print('Integrated available v19 modules and updated versioned drivers; old edition untouched.')
print('Pending modules:',[n for n in newmods if not (P/'continuations'/n).exists()])
