"""Download selected open papers locally and extract page-indexed text."""
from pathlib import Path
import json,sys
from concurrent.futures import ThreadPoolExecutor
from urllib.request import Request,urlopen
from pypdf import PdfReader
R=Path(__file__).resolve().parents[1]; C=R/'.local/sources'
rows=json.loads((R/'.local/source-records.json').read_text(encoding='utf-8'))
keys={'Bai2022','Li2023','Marks2024','LookingInward2024','Turpin2023','Huang2023','Sharma2023','Greenblatt2024','Colas2020','Park2023','Shinn2023','HadfieldMenell2016','OffSwitch2017','Ganguli2023','ModelEditing2024','Rationality2024','IntrospectionCheck2026','Values2026','Archetypes2026','Story2026','MoralConvergence2025'}
def fetch(r):
    if r['key'] not in keys or not r.get('arxiv'):return None
    p=C/(r['key']+'.pdf')
    try:
        if not p.exists():
            with urlopen(Request('https://arxiv.org/pdf/'+r['arxiv'],headers={'User-Agent':'ScholarlyNotebook/0.1'}),timeout=55) as f:p.write_bytes(f.read())
        reader=PdfReader(p); text='\n\n'.join('=== PDF PAGE '+str(i+1)+' ===\n'+(page.extract_text() or '') for i,page in enumerate(reader.pages))
        (C/(r['key']+'-full.txt')).write_text(text,encoding='utf-8')
        return {'key':r['key'],'pages':len(reader.pages),'characters':len(text),'path':p.name}
    except Exception as e:return {'key':r['key'],'error':str(e)}
with ThreadPoolExecutor(max_workers=3) as pool: out=[x for x in pool.map(fetch,rows) if x]
(R/'.local/fulltext-retrieval.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
for x in out:print(json.dumps(x),flush=True)
