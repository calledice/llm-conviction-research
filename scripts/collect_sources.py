"""Public scholarly retrieval; no human verification inferred."""
from pathlib import Path
import json, sys, hashlib
from urllib.request import Request, urlopen
from urllib.parse import quote, urlencode
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from bs4 import BeautifulSoup
R=Path(__file__).resolve().parents[1]
C=R/'.local'/'sources'; C.mkdir(parents=True,exist_ok=True)
O=R/'02-文献'
def get(url,name):
    p=C/name
    if p.exists(): return p.read_text(encoding='utf-8')
    with urlopen(Request(url,headers={'User-Agent':'ScholarlyNotebook/0.1'}),timeout=40) as f:
        t=f.read().decode('utf-8','replace')
    p.write_text(t,encoding='utf-8')
    return t
def collect(s):
    r=dict(s,accessed_at=datetime.now(timezone.utc).isoformat(),human_verified=False)
    try:
        if 'arxiv' in s:
            url='https://arxiv.org/abs/'+s['arxiv']; raw=get(url,s['key']+'.html'); b=BeautifulSoup(raw,'html.parser'); m={}
            for x in b.select('meta[name^="citation_"]'): m.setdefault(x['name'],[]).append(x.get('content',''))
            a=b.select_one('blockquote.abstract'); j=b.select_one('td.tablecell.jref'); v=b.select_one('.dateline')
            r.update(url=url,title=m.get('citation_title',[''])[0],authors=m.get('citation_author',[]),year=m.get('citation_date',[''])[0][:4],doi=m.get('citation_doi',[''])[0],journal_reference=j.get_text(' ',strip=True) if j else '',version=v.get_text(' ',strip=True) if v else '',abstract=a.get_text(' ',strip=True).removeprefix('Abstract:').strip() if a else '',read_level='abstract',locator='arXiv abstract and metadata')
        elif 'doi' in s:
            raw=get('https://api.crossref.org/works/'+quote(s['doi'],safe=''),s['key']+'.json'); d=json.loads(raw)['message']
            r.update(url='https://doi.org/'+s['doi'],title=d.get('title',[''])[0],authors=[' '.join([a.get('given',''),a.get('family','')]).strip() for a in d.get('author',[])],year=str(d.get('published',d.get('created',{}))['date-parts'][0][0]),journal=d.get('container-title',[''])[0],volume=d.get('volume',''),number=d.get('issue',''),pages=d.get('page',''),article_number=d.get('article-number',''),type=d.get('type',''),abstract=BeautifulSoup(d.get('abstract',''),'html.parser').get_text(' ',strip=True),read_level='abstract' if d.get('abstract') else 'metadata',locator='Crossref record')
        else:
            raw=get(s['url'],s['key']+'.html'); b=BeautifulSoup(raw,'html.parser'); main=b.select_one('#main-text') or b.select_one('main') or b
            r.update(title=s.get('title') or b.title.get_text(' ',strip=True),read_level='full_web_text',locator='webpage')
            (C/(s['key']+'.txt')).write_text(main.get_text('\n',strip=True),encoding='utf-8')
        r['sha256']=hashlib.sha256(raw.encode()).hexdigest()
        if not r.get('title'): raise ValueError('Missing title')
    except Exception as e: r['error']=str(e)
    return r
def sources():
    seeds=json.loads((O/'seed-sources.json').read_text(encoding='utf-8-sig'))
    with ThreadPoolExecutor(max_workers=4) as pool: records=list(pool.map(collect,seeds))
    for i,r in enumerate(records,1): r['evidence_id']='E'+str(i).zfill(3)
    (R/'.local'/'source-records.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8')
    target = (O/'sources.json') if not (O/'sources.json').exists() else (R/'.local'/'candidate-sources.json')
    target.write_text(json.dumps([{k:v for k,v in r.items() if k!='abstract'} for r in records],ensure_ascii=False,indent=2),encoding='utf-8')
    for r in records: print(json.dumps({k:r.get(k) for k in ['key','title','year','abstract','journal_reference','error']},ensure_ascii=False),flush=True)
def search():
    records=[]
    for key,q in [('belief','language model belief revision'),('value','language model value internalization'),('conviction','language model conviction commitment'),('introspection','language model introspection'),('moral','language model moral self correction'),('character','language model character training')]:
        url='https://arxiv.org/search/?'+urlencode(dict(query=q,searchtype='all',abstracts='show',order='-announced_date_first',size=50))
        r={'query':q,'provider':'arXiv','url':url,'accessed_at':datetime.now(timezone.utc).isoformat(),'results':[]}
        try:
            b=BeautifulSoup(get(url,'search-'+key+'.html'),'html.parser')
            for x in b.select('li.arxiv-result'):
                t=x.select_one('p.title'); a=x.select_one('p.list-title a')
                if t and a: r['results'].append({'title':t.get_text(' ',strip=True),'url':a.get('href')})
        except Exception as e:r['error']=str(e)
        records.append(r); print(json.dumps(r,ensure_ascii=False),flush=True)
    for key,q in [('wang','Wang Yangming knowledge action artificial intelligence'),('values','artificial intelligence value alignment autonomy')]:
        url='https://api.crossref.org/works?'+urlencode({'query':q,'rows':8})
        r={'query':q,'provider':'Crossref','url':url,'accessed_at':datetime.now(timezone.utc).isoformat()}
        try:
            items=json.loads(get(url,'search-crossref-'+key+'.json'))['message']['items']
            r['results']=[{'title':x.get('title',[''])[0],'doi':x.get('DOI','')} for x in items]
        except Exception as e:r['error']=str(e)
        records.append(r); print(json.dumps(r,ensure_ascii=False),flush=True)
    (O/'search-log.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8')
if __name__=='__main__': globals()[sys.argv[1]]()
