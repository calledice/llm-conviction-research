"""Offline checks; these do not certify scientific validity."""
from pathlib import Path
import json,re,hashlib
R=Path(__file__).resolve().parents[1]
rows=json.loads((R/'02-文献/sources.json').read_text(encoding='utf-8')); bykey={r['key']:r for r in rows}
md=(R/'03-论文/manuscript.md').read_text(encoding='utf-8-sig'); keys=set(re.findall(r'@([A-Za-z0-9]+)',md));errors=[]
if len(rows)!=len(bykey):errors.append('Duplicate source key')
for k in keys:
    if k not in bykey:errors.append('Missing source '+k);continue
    r=bykey[k]
    for f in ['title','authors','year','url','evidence_id','read_level']:
        if not r.get(f):errors.append(k+' missing '+f)
    if r.get('error'):errors.append(k+' retrieval failed')
    if r.get('read_level')=='metadata':errors.append(k+' cited from metadata only')
tex=(R/'03-论文/main.tex').read_text(encoding='utf-8'); texkeys={k for g in re.findall(r'\\cite\{([^}]+)\}',tex) for k in g.split(',')}
if keys!=texkeys:errors.append('Markdown/TeX citation mismatch')
if 'No new model experiments reported' not in tex:errors.append('Missing no-experiment label')
version=json.loads((R/'03-论文/version.json').read_text(encoding='utf-8'))
if not version.get('authors_confirmed') or version.get('authors')!=[{'name':'CongWang','affiliation':'ZhejiangLab'}]:errors.append('Author identity mismatch')
if r'\author{CongWang\\ZhejiangLab}' not in tex:errors.append('LaTeX author mismatch')
if 'No specific funding was received' not in md or 'declares no competing interests' not in md:errors.append('Confirmed declarations missing')
register=json.loads((R/'02-文献/claim-register.json').read_text(encoding='utf-8'))
expected=[p for p in md.split('\n\n') if p.strip() and not p.strip().startswith('#')]
if len(register)!=len(expected) or not register:errors.append('Claim registry does not cover non-heading paragraphs')
log=(R/'03-论文/main.log').read_text(encoding='utf-8',errors='replace') if (R/'03-论文/main.log').exists() else ''
if 'Overfull' in log or 'undefined citations' in log:errors.append('LaTeX warning')
allmd=[p for p in R.rglob('*.md') if '.local' not in p.parts];stems={p.stem for p in allmd}
for p in allmd:
    for t in re.findall(r'\[\[([^\]]+)\]\]',p.read_text(encoding='utf-8-sig')):
        t=t.split('|')[0].split('#')[0]
        if t and not (R/(t+'.md')).exists() and Path(t).name not in stems:errors.append(str(p.relative_to(R))+': '+t)
pdf=R/'03-论文/main.pdf'
if not pdf.exists():errors.append('Missing PDF')
report={'paper_words':len(md.split()),'research_notes':len(list((R/'01-调研笔记').glob('*.md'))),'registered_sources':len(rows),'cited_sources':len(keys),'selected_fulltext_sources':sum(r['read_level']=='selected_fulltext' for r in rows),'human_verified_sources':sum(r.get('human_verified',False) for r in rows),'errors':errors,'submission_ready':False,'scientific_review':'pending','pdf_sha256':hashlib.sha256(pdf.read_bytes()).hexdigest() if pdf.exists() else None}
(R/'05-发布').mkdir(exist_ok=True)
(R/'05-发布/project-check.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2));raise SystemExit(1 if errors else 0)
