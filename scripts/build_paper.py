"""Build citation-checked LaTeX, bibliography and a conceptual figure."""
from pathlib import Path
import re, json, unicodedata, hashlib, csv
R = Path(__file__).resolve().parents[1]
P, S = R/'03-论文', R/'02-文献'
sources = json.loads((S/'sources.json').read_text(encoding='utf-8-sig'))
bykey = {x['key']: x for x in sources}
md = (P/'manuscript.md').read_text(encoding='utf-8-sig')
version = json.loads((P/'version.json').read_text(encoding='utf-8'))
keys = list(dict.fromkeys(re.findall(r'@([A-Za-z0-9]+)', md)))
missing = [k for k in keys if k not in bykey or bykey[k].get('error')]
if missing:
    raise ValueError('Unresolved citations: '+str(missing))

def tex(s):
    s = str(s).translate(str.maketrans({'\u2013':'--','\u2014':'---','\u2018':"'",'\u2019':"'",'\u201c':'"','\u201d':'"'}))
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode()
    return ''.join({'\\':r'\textbackslash{}','&':r'\&','%':r'\%','$':r'\$','#':r'\#','_':r'\_','{':r'\{','}':r'\}','~':r'\textasciitilde{}','^':r'\textasciicircum{}'}.get(c,c) for c in s)

def inline(s):
    stash = []
    def keep(t):
        stash.append(t)
        return 'ZZTOKEN'+str(len(stash)-1)+'ZZ'
    s = re.sub(r'\$([^$]+)\$', lambda m: keep('$'+m[1]+'$'), s)
    s = re.sub(r'\[(@[^\]]+)\]', lambda m: keep(r'\cite{'+','.join(re.findall(r'@([A-Za-z0-9]+)',m[1]))+'}'), s)
    s = re.sub(r'\[([^\]]+)\]\((https?://[^)]+)\)', lambda m: keep(r'\href{'+tex(m[2])+'}{'+tex(m[1])+'}'), s)
    s = re.sub(r'\*\*(.+?)\*\*', lambda m: keep(r'\textbf{'+tex(m[1])+'}'), s)
    s = re.sub(r'\*([^*]+)\*', lambda m: keep(r'\emph{'+tex(m[1])+'}'), s)
    s = tex(s)
    for i,t in enumerate(stash):
        s = s.replace('ZZTOKEN'+str(i)+'ZZ', t)
    return s

bib, bbl = [], [r'\begin{thebibliography}{99}',r'\raggedright']
catalog = ['# 文献索引\n', '元数据、实际阅读版本和位置见 `sources.json`；人工核验仍待完成。引文键不代表最终出版年份。\n']
for r in sources:
    key = r['key']
    typ = r.get('entry_type') or ('article' if r.get('journal') else 'misc')
    fields = {'title':r['title'], 'author':' and '.join(r['authors']), 'year':str(r['year']), 'url':r['url']}
    if r.get('doi'):
        fields['doi'] = r['doi']
    if typ == 'article':
        fields['journal'] = r['journal']
        for field in ['volume','number','pages']:
            if r.get(field):
                fields[field] = str(r[field])
        if r.get('article_number'):
            fields['eid'] = str(r['article_number'])
        absent = (['volume'] if not r.get('volume') else []) + (['pages or article number'] if not (r.get('pages') or r.get('article_number')) else [])
        if absent:
            fields['note'] = 'Publisher metadata lacks '+', '.join(absent)+'; not invented.'
    elif typ == 'inproceedings':
        fields['booktitle'] = r['journal']
        if r.get('pages'):
            fields['pages'] = str(r['pages'])
    elif r.get('arxiv'):
        fields.update(eprint=r['arxiv'],archivePrefix='arXiv',note='Preprint; actual reading version recorded in source register.')
    elif r.get('journal'):
        fields['howpublished'] = r['journal']
        fields['note'] = 'Accessed 18 September 2026; no DOI verified.'
    if 'pages' in fields:
        fields['pages'] = re.sub(r'(?<=\d)-(?!-)(?=\d)','--',fields['pages'])
    bib.append('@'+typ+'{'+key+',\n'+',\n'.join('  '+k+' = {'+('{'+tex(v)+'}' if k=='title' else tex(v))+'}' for k,v in fields.items())+'\n}\n')
    catalog.append(f"- **{key}** ({r['year']}). [{r['title']}]({r['url']}) — {r.get('read_level','metadata')}\n")
for key in keys:
    r = bykey[key]
    authors = [(a.split(',',1)[1].strip()+' '+a.split(',',1)[0].strip()) if ',' in a else a for a in r['authors']]
    short = ', '.join(authors[:3])+(' et al.' if len(authors)>3 else '')
    venue = r.get('journal') or ('arXiv:'+r['arxiv'] if r.get('arxiv') else 'Online publication')
    detail = (' '+str(r['volume'])) if r.get('volume') else ''
    if r.get('pages'):
        detail += ', '+str(r['pages'])
    elif r.get('article_number'):
        detail += ', Article '+str(r['article_number'])
    target = 'https://doi.org/'+r['doi'] if r.get('doi') else r['url']
    linklabel = 'doi:'+r['doi'] if r.get('doi') else r['url']
    bbl.append(r'\bibitem{'+key+'} '+tex(short.rstrip('.'))+'. '+tex(r['title'])+'. '+r'\emph{'+tex(venue)+'}'+tex(detail)+', '+str(r['year'])+'. '+r'\href{'+tex(target)+'}{'+tex(linklabel)+'}.')
bbl.append(r'\end{thebibliography}')
(S/'references.bib').write_text('\n'.join(bib),encoding='utf-8')
(P/'main.bbl').write_text('\n\n'.join(bbl),encoding='utf-8')
(S/'文献索引.md').write_text('\n'.join(catalog),encoding='utf-8')

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch,FancyArrowPatch
F = P/'figures'
F.mkdir(exist_ok=True)
fig,ax = plt.subplots(figsize=(7.2,3.1))
ax.set(xlim=(0,10),ylim=(0,4.2))
ax.axis('off')
boxes=[
(0.1,2.3,3.0,1.4,'Formation','Norms, experience, reasons\nCandidate comparison','#e7eef8'),
(3.5,2.3,2.7,1.4,'Commitment state','Scope and uncertainty\nRetention and revision','#e4f2ee'),
(6.6,2.3,3.2,1.4,'Action and review','Authorized choices and effects\nFeedback and correction','#f4eee3')]
for x,y,w,h,title,sub,color in boxes:
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.05,rounding_size=0.08',facecolor=color,edgecolor='#334155',linewidth=1))
    ax.text(x+w/2,y+h*.78,title,ha='center',va='center',fontsize=9.5,fontweight='bold',color='#152238')
    ax.text(x+w/2,y+h*.34,sub,ha='center',va='center',fontsize=7.8,linespacing=1.5,color='#263746')
ax.add_patch(FancyBboxPatch((1.4,.25),7.2,1.12,boxstyle='round,pad=0.06,rounding_size=0.08',facecolor='#f3f4f6',edgecolor='#334155'))
ax.text(5,1.00,'Evidence profile + ethical and corrigibility checks',ha='center',fontsize=8.8,fontweight='bold')
ax.text(5,.58,'Matched comparisons; prompt withdrawal; state interventions',ha='center',fontsize=7.8)
for x,d in [(1.6,3),(4.85,5),(8.2,7)]:
    ax.add_patch(FancyArrowPatch((x,2.18),(d,1.51),arrowstyle='->',mutation_scale=13,color='#334155'))
for a,b in [(3.17,3.42),(6.29,6.53)]:
    ax.add_patch(FancyArrowPatch((a,3),(b,3),arrowstyle='->',mutation_scale=11,color='#334155'))
fig.savefig(F/'framework.pdf',bbox_inches='tight')
fig.savefig(F/'framework.png',bbox_inches='tight',dpi=180)
plt.close(fig)

preamble=r'''\documentclass[11pt]{article}
\usepackage[margin=1in]{geometry}
\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage{lmodern}
\usepackage{amsmath,amssymb,graphicx,microtype,longtable,booktabs,array}
\usepackage{xurl}
\usepackage[colorlinks=true,linkcolor=blue,citecolor=blue,urlcolor=blue]{hyperref}
\setlength{\parskip}{0.35em}
\setlength{\parindent}{1em}
\setlength{\emergencystretch}{2em}
\widowpenalty=10000
\clubpenalty=10000
'''
preamble += '\\title{'+tex(version['title'])+'}\n\\author{CongWang\\\\ZhejiangLab}\n\\date{'+tex(version['date_display'])+'}\n'
preamble += '\\begin{document}\n\\maketitle\n\\begin{center}\\small\\textbf{'+tex(version['version'])+' public working position-paper draft. No new model experiments reported.}\\end{center}\n'
out, claimrows = [preamble], []
started = inabstract = appendix = False
section = ''
for para in md.split('\n\n'):
    para = para.strip()
    if para == '## Abstract':
        started = inabstract = True
        out.append(r'\begin{abstract}')
        continue
    if not started:
        continue
    if para.startswith('## '):
        if inabstract:
            out.append(r'\end{abstract}')
            inabstract = False
        section = para[3:]
        if section.startswith('Appendix '):
            if not appendix:
                out.append(r'\appendix')
                appendix = True
            label = re.sub(r'^Appendix [A-Z]\.\s*','',section)
            out.append(r'\section{'+tex(label)+'}')
        elif section == 'Declarations':
            out.append(r'\section*{Declarations}')
        else:
            out.append(r'\section{'+tex(re.sub(r'^\d+\.\s*','',section))+'}')
        if para.startswith('## 6.'):
            out.append(r'''\begin{figure}[htbp]
\centering\includegraphics[width=0.98\linewidth]{figures/framework.pdf}
\caption{Proposed research process and its evaluation. Formation, retained commitments, and action are examined together. Ethical acceptability and corrigibility are assessed separately from the evidence profile. Conceptual diagram, not experimental results.}
\label{fig:framework}
\end{figure}''')
    elif para.startswith('### '):
        label = re.sub(r'^(?:\d+\.\d+|[A-Z]\.\d+)\s*','',para[4:])
        out.append(r'\subsection{'+tex(label)+'}')
    elif para.startswith('|'):
        rows = [[c.strip() for c in line.strip().strip('|').split('|')] for line in para.splitlines() if not re.fullmatch(r'[\s|:\-]+',line)]
        if any(len(row)!=3 for row in rows):
            raise ValueError('Comparison table must have three columns')
        cols = r'@{}>{\raggedright\arraybackslash}p{0.19\linewidth}>{\raggedright\arraybackslash}p{0.375\linewidth}>{\raggedright\arraybackslash}p{0.365\linewidth}@{}'
        out.extend([r'\begingroup\small',r'\setlength{\LTleft}{0pt}',r'\setlength{\LTright}{0pt}',r'\begin{longtable}{'+cols+'}',r'\caption{Selected overlaps and boundaries. The entries summarize reported contributions, not comparable performance estimates.}\label{tab:overlap}\\',r'\toprule'])
        header = ' & '.join(r'\textbf{'+tex(c)+'}' for c in rows[0])+r' \\'
        out.extend([header,r'\midrule\endfirsthead',r'\toprule',header,r'\midrule\endhead',r'\bottomrule\endfoot'])
        out.extend(' & '.join(inline(c) for c in row)+r' \\[0.4em]' for row in rows[1:])
        out.extend([r'\end{longtable}',r'\endgroup'])
    else:
        out.append(inline(para.replace('\n',' ')))
    cites = list(dict.fromkeys(re.findall(r'@([A-Za-z0-9]+)',para)))
    if cites:
        claimrows.append({'claim_id':'C'+str(len(claimrows)+1).zfill(3),'claim_sha256':hashlib.sha256(' '.join(para.split()).encode()).hexdigest(),'section':section,'evidence_keys':';'.join(cites),'evidence_ids':';'.join(bykey[k].get('evidence_id','') for k in cites),'status':'agent_source_checked_human_review_pending'})
out.extend([r'\clearpage',r'\input{main.bbl}',r'\end{document}'])
(P/'main.tex').write_text('\n\n'.join(out),encoding='utf-8')
with (S/'claim-map.csv').open('w',encoding='utf-8',newline='') as f:
    fields=['claim_id','claim_sha256','section','evidence_keys','evidence_ids','status']
    writer=csv.DictWriter(f,fieldnames=fields)
    writer.writeheader()
    writer.writerows(claimrows)
print(json.dumps({'version':version['version'],'manuscript_words':len(md.split()),'cited_sources':len(keys),'catalogued_sources':len(sources),'claim_paragraphs':len(claimrows),'missing_citations':missing}))

register=[]
for i,para in enumerate(md.split('\n\n'),1):
    para=para.strip()
    if not para or para.startswith('#'): continue
    cites=list(dict.fromkeys(re.findall(r'@([A-Za-z0-9]+)',para)))
    kind='literature_supported_paragraph' if cites else ('disclosure_or_proposal_or_argument')
    register.append({'paragraph':i,'sha256':hashlib.sha256(' '.join(para.split()).encode()).hexdigest(),'kind':kind,'evidence_keys':cites,'human_reviewed':False})
(S/'claim-register.json').write_text(json.dumps(register,indent=2),encoding='utf-8')
