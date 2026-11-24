#!/usr/bin/env python3
"""Read-only archive/source inclusion audit; writes audit results only.

Run from the recovered workspace root. No supplied build or verify script is run.
"""
from __future__ import annotations
import csv
import hashlib
import io
import json
import re
import stat
import unicodedata
import zipfile
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath

ROOT = Path.cwd()
OUT = ROOT / 'integration_20261121'
EXTRACT = OUT / 'dot_audit_extract'
LATEST = ROOT / 'restored_20261121/latest/EGA_v17_V_supplement_III'
PROJECT = LATEST / 'project'
BASELINE = ROOT / 'restored_20261121/baseline/EGA_v17_handover'
ARCHIVES = ROOT / 'recovered_20261121/dot_new'

def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def file_digest(path: Path) -> str:
    return digest(path.read_bytes())

def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()

def dump(path: Path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

def normmap(s: str):
    """Formatting-only normalizer, retaining original source offset for each char."""
    offsets = list(range(len(s)))
    def replace(pattern, replacement):
        nonlocal s, offsets
        pieces, maps, end = [], [], 0
        for m in re.finditer(pattern, s):
            pieces.append(s[end:m.start()]); maps.extend(offsets[end:m.start()])
            value = replacement(m) if callable(replacement) else replacement
            pieces.append(value)
            maps.extend([offsets[m.start()]] * len(value))
            end = m.end()
        pieces.append(s[end:]); maps.extend(offsets[end:])
        s, offsets = ''.join(pieces), maps
    replace(r'\\(?:note|transnote|footnote)\b', r'\FN')
    replace(r'\\enlargethispage\{[^}]*\}', '')
    replace(r'\\clearpage\b', '')
    replace(re.escape(r'\noindent\textbf{英译编者说明：}'), r'\noindent')
    replace(r'\\(?:chapter|section|subsection|paragraph)\*?\{([^{}\n]*)\}',
            lambda m: 'HEAD{' + m[1].rstrip('。') + '}')
    chars, kept = [], []
    for c, pos in zip(s, offsets):
        if not c.isspace():
            chars.append(c); kept.append(pos)
    return ''.join(chars), kept

def norm(s: str):
    return normmap(s)[0]

def source_sections(s: str):
    chapters = list(re.finditer(r'\\chapter\*\{[^\n]*\}', s))
    if len(chapters) < 2:
        raise ValueError('Expected scope chapter followed by body chapter')
    body_start = chapters[1].end()
    notes_match = re.search(r'\\(?:chapter|section)\*\{译校说明（非原文）\}', s)
    end = s.index(r'\end{document}')
    body_end = notes_match.start() if notes_match else end
    notes_start = notes_match.end() if notes_match else end
    def line_span(start, stop):
        while start < stop and s[start].isspace(): start += 1
        while stop > start and s[stop-1].isspace(): stop -= 1
        return [s.count('\n', 0, start)+1, s.count('\n', 0, stop-1)+1] if stop > start else None
    return (s[body_start:body_end].strip(), s[notes_start:end].strip(),
            line_span(body_start, body_end), line_span(notes_start, end))

def strip_inline_notes(s: str):
    pat = re.compile(r'\\(?:footnote|transnote|note)\b\s*\{')
    while (m := pat.search(s)):
        pos, depth = m.end(), 1
        while pos < len(s) and depth:
            if s[pos] == '{' and s[pos-1] != '\\': depth += 1
            if s[pos] == '}' and s[pos-1] != '\\': depth -= 1
            pos += 1
        s = s[:m.start()] + s[pos:]
    return re.sub(r'\s+', ' ', s).strip()

def target_match(target_text, needle):
    canonical, offsets = normmap(target_text)
    canon_needle = norm(needle)
    count = canonical.count(canon_needle) if canon_needle else 0
    if count != 1:
        return {'count': count, 'lines': None, 'normalized_sha256': digest(canon_needle.encode())}
    start = canonical.index(canon_needle)
    stop = start + len(canon_needle)
    lines = [target_text.count('\n', 0, offsets[start])+1,
             target_text.count('\n', 0, offsets[stop-1])+1]
    return {'count': count, 'lines': lines, 'normalized_sha256': digest(canon_needle.encode())}

SCOPES = [
    ('66页行列式交换图、符号说明、零点子概形与交模', [66], None, '交模段末：L 是 P 与 Q 在 M 中的交'),
    ('相对情形的行列式线丛及判别式', [66,67], None, '以引理所称交换性得到同态 b'),
    ('非超奇异点的交模说明及两条正合列', [67], [102], '第二条正合列末'),
    ('可逆模扭曲及乘单位变换', [67], [102], 'D(φ) 乘以 u^M，M 为 X/Y 相对维数'),
    ('普通奇异零点备注', [67,68], [102,103], '仿射平面 φ=xy 的例子'),
    ('可逆模截面类比图与划去段起始标记', [68], [103,104], '英译者方括号：以下为作者划去稿'),
    ('作者划去稿：一般增广与普通二次型增广定义', [68,69], [104,105], '素理想纤维乃至极大理想纤维判别句'),
    ('作者划去稿：命题8、引理8.1与证明后的评论', [69], [105], '任意 k≥1 代替2且不提非退化的评论'),
    ('作者划去稿：命题9与自然同态说明', [69,70], [105,106], '命题9的证明几乎是平凡的'),
    ('作者划去稿：推论10与划去段结束标记', [70,71], [106,107], '推论10(iii)之后英译者结束标记'),
    ('恢复正文：奇异零点术语及顶次外幂判别', [71,72], [107,108], 'Ω^m_X/Y ⊗ (det E)^−1 ⊗ O_V0 的截面'),
    ('二阶微分刻画、判别式及恒秩引理', [72], [109,110], '应概括为一个推广命题6的命题'),
    ('推广命题7的光滑塔与分歧、降秩余维附注', [72,73], [110,111], '降秩闭集每个不可约分支的余维附注'),
    ('IV.17.15章首：特征2、光滑型及奇异性术语', [73,74], [112,113], 'SUP 及其第10页相关术语应作修订'),
    ('IV.23.9.2勘误与切超曲面', [74], [113,114], '关于不可分次数恰为2的保留意见'),
    ('15.1 光滑型与相对雅可比判据', [74,75], [114,115], '不满足相对光滑且相对维数 r−1 的点集'),
    ('15.2 初等增广、初等奇点与几何初等奇点', [75,76], [115,160], '通过扩域后的有理提升定义几何初等奇点'),
    ('15.3—15.6 初等奇点的局部刻画', [76,77], [160,159], '零维局部环是离散赋值环模极大理想 n 次幂之商'),
    ('15.7 几何变式及作者编排附记', [77], [159,158], '实际上只取用型之光滑性的定义'),
]

inventory = json.loads((EXTRACT / 'archive_inventory.json').read_text())
pdf_identity = json.loads((EXTRACT / 'source_pdf_identity.json').read_text())
old_index_path = BASELINE / '05_Dot/DOT_BATCHES.json'
old_index = json.loads(old_index_path.read_text())
main_text = (PROJECT / 'main.tex').read_text()
def active_inputs(path, stack=()):
    if path in stack:
        raise ValueError('cyclic TeX input')
    text = path.read_text()
    yield path, text
    uncommented = re.sub(r'(?<!\\)%[^\n]*', '', text)
    for m in re.finditer(r'\\(?:input|include)\{([^{}\n]+)\}', uncommented):
        child = PROJECT / m[1]
        if not child.suffix:
            child = child.with_suffix('.tex')
        if not child.exists():
            raise FileNotFoundError(f'Cannot resolve static input {m[1]} in {path}')
        yield from active_inputs(child, stack+(path,))
active_tree = list(active_inputs(PROJECT / 'main.tex'))
active_canonical = [(path,norm(text)) for path,text in active_tree]
assert len(active_tree)==len({path for path,text in active_tree})
records, target_files, flat_names = [], {}, defaultdict(list)
all_internal_ok = True

for inv, scope, source_pdf in zip(inventory, SCOPES, pdf_identity['batches']):
    n = inv['order']; new_id = f'new{n:03d}'; source_label = n+49
    archive_path = ARCHIVES / inv['filename']
    raw_zip_hash = file_digest(archive_path)
    assert raw_zip_hash == inv['sha256']
    with zipfile.ZipFile(archive_path) as z:
        assert z.testzip() is None
        member_names = [m.filename for m in z.infolist()]
        assert not [name for name,count in Counter(member_names).items() if count>1]
        normalized_names = [unicodedata.normalize('NFC',name.replace('\\','/')) for name in member_names]
        assert not [name for name,count in Counter(normalized_names).items() if count>1]
        for info in z.infolist():
            normalized = info.filename.replace('\\','/')
            path = PurePosixPath(normalized)
            assert not path.is_absolute() and '..' not in path.parts
            assert not re.match(r'^[A-Za-z]:',normalized)
            assert not stat.S_ISLNK(info.external_attr >> 16)
            assert not info.flag_bits & 1
            if not info.is_dir(): flat_names[path.name].append((new_id,digest(z.read(info))))
        entry = inv['tex_files'][0]['path']
        source_bytes = z.read(entry)
        assert digest(source_bytes) == inv['tex_files'][0]['sha256']
        source_text = source_bytes.decode('utf-8')
    body, notes, body_lines, note_lines = source_sections(source_text)
    assert body == (EXTRACT / f'n{n:02d}/BODY_EXTRACT.txt').read_text().strip()
    assert notes == (EXTRACT / f'n{n:02d}/NOTES_EXTRACT.txt').read_text().strip()
    target = 'text/v1_2.tex' if n<=13 else f'continuations/v_suppIII_{source_label}.tex'
    target_path = PROJECT / target
    text = target_path.read_text()
    changes = []
    body_needle, notes_needle = body, notes
    if n == 6:
        old = '本批只到说明为止，未查定整段划去稿的最终边界。'
        new = '第一辑止于这条说明；第二辑已查定整段划去稿的最终边界，并恢复其后的非划去正文。'
        assert old in notes
        notes_needle = notes.replace(old,new)
        changes.append({'type':'historical_status_note','from':old,'to':new,'author_body_changed':False})
    if n == 14:
        title = r'\noindent\textbf{IV.17.15　光滑型：增广与初等奇点。}'
        assert body.startswith(title)
        body_needle = body.removeprefix(title)
        assert r'\chapter*{IV.17.15　光滑型\protect\\增广与初等奇点}' in text
        changes.append({'type':'title_promotion','from':title,'to':'chapter heading + title footnote; full title retained','author_body_changed':False})
    body_match = target_match(text,body_needle)
    notes_match = target_match(text,notes_needle) if notes else None
    assert body_match['count']==1, (new_id,body_match)
    assert notes_match is None or notes_match['count']==1, (new_id,notes_match)
    global_body_matches = [{'path':rel(path),'count':canonical.count(norm(body_needle))}
                           for path,canonical in active_canonical if norm(body_needle) in canonical]
    global_note_matches = ([{'path':rel(path),'count':canonical.count(norm(notes_needle))}
                            for path,canonical in active_canonical if norm(notes_needle) in canonical]
                           if notes else [])
    assert sum(m['count'] for m in global_body_matches)==1
    assert not notes or sum(m['count'] for m in global_note_matches)==1
    input_lines = [i for i,line in enumerate(main_text.splitlines(),1)
                   if re.search(r'\\input\{'+re.escape(target)+r'\}',line)]
    assert len(input_lines)==1
    mirror = LATEST / '05_Dot_new_batches' / inv['filename']
    assert file_digest(mirror)==raw_zip_hash
    for c in inv['internal_checksums']:
        actual = file_digest(ROOT / inv['extracted_directory'] / c['path'])
        assert actual==c['expected_sha256']
    label_provenance = ('原批 PROGRESS.json 的 batch 字段' if n>=3 else
                        '第三辑 aggregate labels 50–68 与连续次序；这两批原 PROGRESS.json 未给数字 batch')
    txt_without_notes = strip_inline_notes(body)
    record = {
        'id':new_id,'source_label':source_label,'source_label_provenance':label_provenance,
        'archive_name':inv['filename'],'zip_sha256':raw_zip_hash,'zip_bytes':archive_path.stat().st_size,
        'library_metadata':inv['metadata'],'local_archive_path':rel(archive_path),
        'same_archive_in_supplement_path':rel(mirror),'same_archive_in_supplement_byte_identical':True,
        'main_tex_entry':entry,'source_tex_sha256':digest(source_bytes),
        'source_tex_path':rel(EXTRACT / f'n{n:02d}' / entry),
        'source_body_lines':body_lines,'source_translator_note_lines':note_lines,
        'scope':scope[0],'english_physical_pages':scope[1],
        'french_body_physical_pages':scope[2],
        'source_range_evidence':'Actual TeX body/endpoints read; source PDF identity and English page text checked; French subset image streams matched to full source.',
        'last_item':scope[3],
        'first_source_body_excerpt_tex':txt_without_notes[:300],
        'last_source_body_excerpt_tex':txt_without_notes[-600:],
        'next_anchor_historical': inv['progress_claim'].get('next',inv['progress_claim'].get('next_anchor')),
        'historical_progress_only':inv['progress_claim'],
        'merged_target_file':target,'merged_target_sha256':file_digest(target_path),
        'merged_body_lines':body_match['lines'],
        'merged_translator_notes_lines':notes_match['lines'] if notes_match else None,
        'normalized_body_occurrences':body_match['count'],
        'normalized_translator_notes_occurrences':notes_match['count'] if notes_match else None,
        'normalized_body_sha256':body_match['normalized_sha256'],
        'normalized_translator_notes_sha256':notes_match['normalized_sha256'] if notes_match else None,
        'direct_main_input_lines':input_lines,
        'all_active_inputs_body_matches':global_body_matches,
        'all_active_inputs_notes_matches':global_note_matches,
        'archive_validation':{
            'crc':'pass','safe_paths':'pass','duplicate_member_names':[],
            'symlinks':0,'encrypted_members':0,'members':inv['member_count'],
            'uncompressed_bytes':inv['uncompressed_bytes'],
            'internal_checksum_records':len(inv['internal_checksums']),
            'internal_checksum_failures':[]},
        'archive_member_inventory':inv['members'],
        'source_pdf_identity':source_pdf,
        'inclusion_exceptions':changes,
        'nonduplicate_criterion':'Distinct ZIP and TeX SHA/name against all 19 and old 56; complete normalized author body and notes occur once in one active main input. Standalone raw archives and single-file build are alternate representations, not additional body insertions.',
        'mathematical_audit_status':'Not independently certified by this archive/inclusion audit; historical batch assertions remain historical.',
    }
    records.append(record)
    target_files[target]=record['merged_target_sha256']

old_checks, old_merge_rows = [], []
new_hashes = {r['source_tex_sha256'] for r in records}
new_names = {r['main_tex_entry'] for r in records}
for old in old_index['batches']:
    source_path=BASELINE / old['packaged_tex_path']
    actual=file_digest(source_path)
    assert actual==old['source_tex_sha256']
    assert actual not in new_hashes and old['original_tex_name'] not in new_names
    old_checks.append({'order':old['order'],'path':rel(source_path),'sha256':actual,
                       'matches_old_index':True,
                       'present_in_latest_package_root':(LATEST / old['packaged_tex_path']).exists()})
    old_merge_rows.append({
        'id':f"old{old['order']:03d}",'series':'baseline56','source_label':old['order'],
        'source_label_provenance':'Existing DOT_BATCHES.json order, not new continuation label',
        'original_record':old,
        'source_tex_sha256':actual,'existing_package_relative_source_path':old['packaged_tex_path'],
        'merged_target_file':old['current_project_input'],
        'integration_treatment':old['integration_treatment'],
    })

assert len({r['zip_sha256'] for r in records})==19
assert len({r['source_tex_sha256'] for r in records})==19
flat_collisions = [{'filename':name,'copies':len(items),'distinct_sha256':len({h for _,h in items}),
                    'batch_ids':[i for i,_ in items]}
                   for name,items in sorted(flat_names.items()) if len(items)>1]

issues=[
    {'id':'ARCH-01','severity':'handover_required','status':'observed_in_input_package',
     'finding':'第三辑包有19个新ZIP，但没有旧05_Dot/batches及original_archives；旧56条索引仍保留，所指56条原TeX相对路径在第三辑包中全部缺失。',
     'evidence':{'old_index_path':rel(old_index_path),'latest_index_path':'project/checks/v17-baseline/DOT_BATCHES.json',
                 'missing_raw_tex_paths_in_latest_count':sum(not c['present_in_latest_package_root'] for c in old_checks)},
     'action':'最终续作包须从已恢复基线原样带回完整旧05_Dot树；根代理已确认处理。本审计不宣称已完成该打包动作。'},
    {'id':'ARCH-02','severity':'handover_clarity','status':'observed_in_input_package',
     'finding':'project/SOURCE_MAP.md 与 PROGRESS.md 的历史段仍指 checks/DOT_BATCHES.json；第三辑实际位置为 checks/v17-baseline/DOT_BATCHES.json。',
     'action':'更新当前索引入口，保留原说明为历史快照。'},
    {'id':'ARCH-03','severity':'handover_clarity','status':'observed_in_input_package',
     'finding':'当前进度标题为英77页/下一78页；下方历史段仍有下一66、68、73页字样。部分合并译校附记中的“本批未译……”也仍指原独立批次状态。',
     'action':'把唯一当前接续点集中到最终START_HERE/PROGRESS，并明确旧批状态仅为历史。'},
    {'id':'ARCH-04','severity':'extraction_layout','status':'documented',
     'finding':'19ZIP间存在README/build/PROGRESS/AUDIT/verify等同名异内容文件，不能平铺解压。',
     'action':'每个newNNN独立目录；完整同名文件碰撞表见flat_name_collisions。'},
    {'id':'ARCH-05','severity':'numbering','status':'documented',
     'finding':'原批标签50–68不是旧56之后的累计计数；new001/new002原PROGRESS无数字batch。',
     'action':'旧56按原DOT_BATCHES顺序保留，新19用new001–new019；source_label单独保留50–68并注明前两项来源。'},
    {'id':'MATH-BOUNDARY','severity':'scope_limit','status':'not_mathematically_certified',
     'finding':'“全部内容已收录”只核验源码包含关系。原批52正合列、54维数阈值、55类比图线丛幂次、57次数待核等在本输入仍带疑义或待核标记。',
     'action':'须由独立数学译校处理；不能用ZIP、SHA或包含检查解除数学待核状态。'},
]

new_merge_rows=[]
for r in records:
    row={k:r[k] for k in ['id','source_label','source_label_provenance','archive_name','zip_sha256',
        'main_tex_entry','source_tex_sha256','local_archive_path','source_tex_path','scope',
        'english_physical_pages','french_body_physical_pages','last_item','next_anchor_historical',
        'merged_target_file','merged_body_lines','merged_translator_notes_lines','nonduplicate_criterion']}
    row.update({'series':'new_20261121','integration_treatment':'new_body_continuation',
                'suggested_archive_relative_path':f"05_Dot/new_20261121/{r['id']}/{r['archive_name']}",
                'suggested_source_relative_path':f"05_Dot/new_20261121/{r['id']}/{r['main_tex_entry']}",
                'suggested_paths_status':'Proposal for final package; not created by this audit'})
    new_merge_rows.append(row)

summary={
    'new_archive_count':19,'archive_members':sum(r['archive_validation']['members'] for r in records),
    'compressed_bytes':sum(r['zip_bytes'] for r in records),
    'uncompressed_bytes':sum(r['archive_validation']['uncompressed_bytes'] for r in records),
    'internal_checksum_records':sum(r['archive_validation']['internal_checksum_records'] for r in records),
    'all_crc_safe_paths_internal_checksums_pass':True,
    'identical_archive_mirrors_in_latest_package':19,
    'distinct_new_tex_sources':19,'old_tex_sources_verified':56,
    'old_new_source_sha_or_filename_collisions':0,
    'combined_source_batches':75,
    'old_new_body_batches':old_index['new_body_batches'],
    'old_same_text_collation_batches':old_index['same_text_collation_batches'],
    'new_author_body_inclusion_count_one':19,'new_separate_notes_inclusion_count_one':17,
    'new_first_two_notes_inline_in_body':2,
    'old_raw_paths_missing_from_latest_package':sum(not c['present_in_latest_package_root'] for c in old_checks),
}
audit={
    'schema':'dot_archive_inclusion_audit/1','created_at':datetime.now(timezone.utc).isoformat(),
    'scope':'19 current independent Dot continuation ZIPs and their inclusion in recovered supplement III; old56 source identity boundary.',
    'summary':summary,
    'inputs':{'latest_package_root':rel(LATEST),'old_baseline_root':rel(BASELINE),
              'source_library_metadata':{'path':'integration_20261121/library_sources.json','sha256':file_digest(OUT/'library_sources.json')},
              'old_index':{'path':rel(old_index_path),'sha256':file_digest(old_index_path)},
              'active_main':{'path':rel(PROJECT/'main.tex'),'sha256':file_digest(PROJECT/'main.tex')},
              'active_input_tree':[{'path':rel(path),'sha256':file_digest(path)} for path,text in active_tree],
              'target_source_sha256':target_files},
    'method':{
        'archives':'Reopened each ZIP; CRC all members; checked absolute/traversal/drive paths, normalized duplicate names, symlinks and encryption; compared byte SHA to supplied same-name package mirror; checked each internal checksum record.',
        'body':'Read actual TeX after scope chapter, stopping before separate translator-note heading; kept all formulas, diagrams and inline notes. Whole normalized body searched in indicated target and across the complete static main input tree, exactly once.',
        'notes':'Whole separate translator notes searched once after formatting normalization; first two have inline notes only.',
        'format_normalization':['Whitespace removed','note/transnote/footnote macro names unified only','enlargethispage and clearpage omitted','editor explanatory label treated as wrapper','heading command/level and terminal Chinese full stop normalized'],
        'substantive_exceptions':'Only new006 historical-status sentence replaced as explicitly recorded; new014 title promoted, not omitted. No mathematical formulas rewritten by the audit.',
        'source_pdfs':'English complete PDF SHA identity; each supplied French subset page mapped by ordered image stream hashes to full French PDF physical page, all unique; this is page identity evidence, not independent handwritten transcription verification.',
        'not_performed':['No compilation or PDF layout review in this subtask','No archive-supplied scripts executed','No full independent mathematical proof verification','No original ZIP or translation edited'],
    },
    'records':records,'old56_source_verification':old_checks,
    'old_boundary':{
        'baseline_actual_short_source_path':rel(BASELINE/'01_project/EGA_v17/text/v1_2.tex'),
        'baseline_actual_short_source_sha256':file_digest(BASELINE/'01_project/EGA_v17/text/v1_2.tex'),
        'baseline_actual_short_source_tail_tex':(BASELINE/'01_project/EGA_v17/text/v1_2.tex').read_text()[-2000:],
        'actual_merged_short_source':'baseline text/v1_2.tex ends at English66 immediately before determinant commuting diagram',
        'old55_56':'Same-text collation at English62; original next4(d) is historical and is already covered by earlier PS short translation.',
        'new001':'Begins with English66 determinant commuting diagram; not restart of English62.',
        'non_dot_gap_translation':old_index.get('new_translation_not_from_Dot'),
    },
    'current_continuation':{
        'actual_last_source_record':'new019','last_source_label':68,'last_entry':'15.7 and author arrangement note',
        'last_english_physical_page':77,'french_body_physical_pages':[159,158],
        'last_author_sentence':'另一节刻画光滑的二次型，而从前一节只取用15.1，也就是实际上只取用型之光滑性的定义。',
        'next_english_physical_page':78,'next_french_physical_page':161,
        'next_heading':'Appendix 17.16 / Smooth Quadratic Forms','next_entry':'16.1',
        'evidence':'Actual new019 author body ends at arrangement note; English77 end and English78 heading/16.1 read from embedded complete PDF.',
        'not_entire_EGA_V_complete':True,
    },
    'source_pdf_identity':pdf_identity,
    'flat_name_collisions':flat_collisions,'issues':issues,
    'stable_new_merge_index':new_merge_rows,
}
dump(OUT/'dot_new_audit.json',audit)
dump(OUT/'dot_new_index.json',{'schema':'dot_new_index/1','records':new_merge_rows})
dump(OUT/'dot_combined_index.json',{
    'schema':'dot_combined_index/1','baseline_index_sha256':file_digest(old_index_path),
    'counts':{'baseline56':56,'new_20261121':19,'combined':75},
    'note':'stable namespace old001–old056 plus new001–new019; source_label50–68 is not cumulative count; final paths proposed only for new records',
    'records':old_merge_rows+new_merge_rows})
fields=['id','source_label','archive_name','zip_sha256','main_tex_entry','source_tex_sha256',
        'merged_target_file','merged_body_lines','merged_translator_notes_lines','last_item','next_anchor_historical']
with (OUT/'dot_new_index.tsv').open('w',encoding='utf-8',newline='') as f:
    writer=csv.DictWriter(f,fields,delimiter='\t');writer.writeheader()
    for r in new_merge_rows:
        writer.writerow({k:json.dumps(r[k],ensure_ascii=False) if isinstance(r[k],(list,dict)) else r[k] for k in fields})

md=[]
md += ['# Dot 新19批工程档案与正文收录审核','',
       '审核对象是本次恢复的19个独立续译ZIP及第三辑工程中的实际收录。此报告核验档案完整性、版本身份、正文包含关系与接续边界；不把历史批次的数学核查自述升级为本轮独立证明认证。','',
       '## 结论','',
       f"- 19个ZIP全部通过CRC、安全路径、成员重名及内部校验检查。共{summary['archive_members']}个成员，{summary['internal_checksum_records']}条内部SHA-256记录全通过。",
       '- 19个ZIP与第三辑 `05_Dot_new_batches` 内同名档案逐字节一致，包括“二阶判别与恒秩引理”的当前 version 1。',
       '- 19份实际TeX正文全部找到一次完整收录：前13份在 `project/text/v1_2.tex`，后6份在 `project/continuations/v_suppIII_63.tex` 至 `_68.tex`。17份独立译校附记也各完整收录一次，前两份附记本已在正文脚注中。',
       '- 已恢复的旧56份TeX全部与旧 `05_Dot/DOT_BATCHES.json` 的散列一致；与新19份没有同名或同散列碰撞。旧56由54份新增正文与2份同文校订组成。合计75份来源批次，不是75个独立数学章节。',
       '- 第三辑包缺旧 `05_Dot` 原始档案树：56个旧TeX相对路径全部缺失，只有旧索引和合入正文仍在。最终续作包须补回已恢复基线中的旧树。根代理已接手；本报告不宣称已经完成最终打包。',
       '', '## 本轮实际完成的边界','',
       '新19批从英译物理第66页行列式交换图起，连续至第77页15.7及作者编排附记末。最后一句止于“实际上只取用型之光滑性的定义”。下一原文是英译物理第78页附录17.16《光滑二次型》的16.1，对读法文物理第161页。',
       '',
       '旧最后两批的“下一注4(d)”只是独立稿当时进度：旧主稿的PS短篇已包含第62—66页前部，不能据其历史PROGRESS重新翻译第62页。',
       '', '## 稳定索引与源码定位','',
       '旧56条按原索引保留，另加命名空间 `old001`—`old056`；新19条使用 `new001`—`new019`。原补篇标签50—68放在 `source_label`，不当作全档案累计编号。前两份原PROGRESS没有数字batch；其50、51来源于第三辑总标签与连续顺序，并已在JSON注明。以下行号只对应本次输入文件散列，若主稿再校订应重新定位。','',
       '| 稳定ID / 原标签 | 实际内容 | 英译物理页 | 目标正文与译校附记行段 | 实际末条 |',
       '|---|---|---|---|---|']
for r in records:
    target=r['merged_target_file']
    spans='正文'+str(r['merged_body_lines'])
    if r['merged_translator_notes_lines']:spans+='；附记'+str(r['merged_translator_notes_lines'])
    md.append(f"| {r['id']} / {r['source_label']} | {r['scope']} | {','.join(map(str,r['english_physical_pages']))} | `{target}`；{spans} | {r['last_item']} |")
md += ['', '每条ZIP名称、完整ZIP SHA-256、原TeX成员名称、原TeX SHA-256、版本标识、目标文件SHA、输入位置、正文首末摘录、历史下一锚点及不重复收录判据均列在 `dot_new_audit.json`。可直接合并的19条轻量表为 `dot_new_index.json` / `.tsv`；保留旧记录的75条合并索引为 `dot_combined_index.json`。','',
       '## 内容包含检查的界限与允许的格式变化','',
       f'比较从各独立稿范围章之后的正文开始，到“译校说明（非原文）”之前结束，保留正文中的全部公式、交换图、脚注和英译者说明。把空白、脚注宏名、标题级别和局部分页指令标准化后，搜索整段内容的唯一出现位置。已遍历当前main的全部{len(active_tree)}个静态输入文件，99个文件均只输入一次，所有19段正文和17段独立附记在整个输入树里仍各只找到一次。`main.tex` 中七个目标模块各直接输入一次。封面、独立稿范围章和重复临时标题不作正文重复插入。',
       '',
       '仅有两处需要显式说明：new006的一句独立批次历史状态改为第一辑止点、第二辑已查定划去段边界；new014首题名升为主稿章标题，题名脚注仍完整保留。new018/new019的小标题级别调整不删内容。JSON逐项保留这些变动；没有把数学公式差异纳入宽松匹配。',
       '',
       '单文件TeX、原始独立ZIP与模块工程是同一内容的不同可用载体，不因另存一份就认定正文重复。反过来，文件名相异也不自动说明内容独立，本轮已同时检查散列、完整正文与旧批边界。','',
       '## 底本与末页证据','',
       f"19批所附完整英文底本都与第三辑 `03_sources/EGAVaiello.pdf` 相同，SHA-256为 `{pdf_identity['full_english']['sha256']}`。",
       '',
       '各法文子集的每一页均以有序图像流SHA匹配完整法文PDF，均唯一匹配，无空缺。最后三批的实际页序是115→160、160→159、159→158；不能按扫描物理页的数字大小重排。该检查证明所携带扫描页的身份，不代替对法文手写全部字词的辨读。前两批ZIP没有法文子集；本报告没有虚构为它们补做法文校读。','',
       '## 最终打包需要处理的项目','']
for issue in issues:
    md.append(f"- **{issue['id']}**：{issue['finding']} {issue['action']}")
md += ['', '跨ZIP常见同名文件必须按批隔离，尤其19份 `README.txt`、`build.sh`、`PROGRESS.json`、`AUDIT.txt` 与校验清单均含多版本内容。完整碰撞表已写JSON。',
       '', '## 数学核验状态','',
       '本文的“完整收录一次”只关于档案与源码。原批52的正合列、54的维数阈值、55类比图中的可逆模幂次、57引理的“次数待核”等仍须独立数学译校。本轮没有执行各ZIP里的build/verify脚本，没有编译主稿，也没有重审全段证明或作PDF版式检查；这些不能由CRC、SHA或文本包含检查推得。',
       '', '## 可复核材料','',
       '- `dot_audit_extract/archive_inventory.json`：19个ZIP完整成员与内部SHA清单。',
       '- `dot_audit_extract/source_pdf_identity.json`：英文整本身份及法文逐页图像流匹配。',
       '- `dot_audit_extract/n01`—`n19`：隔离解压的原始文件；`BODY_EXTRACT.txt` 和 `NOTES_EXTRACT.txt` 为本轮派生摘取。',
       '- `dot_audit_extract/finalize_audit.py`：重新检查档案与源码并生成本报告/索引的只读核查脚本。',
       '', '没有修改原ZIP、翻译正文或第三辑工程。']
(OUT/'dot_new_audit.md').write_text('\n'.join(md)+'\n',encoding='utf-8')
print(json.dumps(summary,ensure_ascii=False,indent=2))
for r in records:
    print(r['id'],r['source_label'],r['merged_target_file'],r['merged_body_lines'],r['merged_translator_notes_lines'])
