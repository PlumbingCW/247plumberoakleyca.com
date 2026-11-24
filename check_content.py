import json,re,sys,os
R=json.load(open('/home/claude/oakley/registry.json'))
SV={s['slug']:s for s in R['services']}; BL={b['slug']:b for b in R['blogs']}
STD={s['slug'] for s in R['standard']}
HD={h['slug']:h for h in R.get('hoods',[])}
VALID=set(SV)|set(BL)|STD|{'plumber-brentwood-ca'}|set(HD)
BANNED="delve into|navigate the complexities|fast-paced world|important to note|worth noting|it's important|tapestry|realm|robust|comprehensive|seamless|cutting-edge|state-of-the-art|meticulous|underscore|leverage|elevate|transform|unlock|at the forefront|whether you're|look no further|rest assured|we pride ourselves|peace of mind|top-notch|nestled|boasts|game-changer|a wide range of|when it comes to".split("|")
FORB=[r"free estimate",r"guarantee[ds]? arrival",r"family[- ]owned",r"locally owned",r"\bsince (19|20)\d\d",r"\$\s?\d",r"within \d+ (minutes|hours)",r"\bthe best\b",r"#1",r"\bfree quote"]
def strs(o):
    if isinstance(o,str): yield o
    elif isinstance(o,list):
        for x in o: yield from strs(x)
    elif isinstance(o,dict):
        for k,v in o.items():
            if k in('slug','kind','link','source_type'): continue
            yield from strs(v)
def paras(d):
    out=[]
    out+=d.get('lead',[])+d.get('intro',[])
    for s in d.get('sections',[]):
        out+=s.get('paras',[])
    for f in d.get('faqs',[]):
        a=f['a']; out+= a if isinstance(a,list) else [a]
    if 'localnote' in d: out+=d['localnote'].get('paras',[])
    return out
def wc(d): return sum(len(re.sub(r'\[\[[^|\]]+\|([^\]]+)\]\]',r'\1',x).split()) for x in strs({k:v for k,v in d.items() if k not in('meta','cta_mid','cta_end','side')}))
def check(slug):
    p=f'/home/claude/oakley/content/{slug}.json'; errs=[]
    try: d=json.load(open(p))
    except Exception as e: return 0,[f'JSON: {e}']
    allt=" ".join(strs(d))
    if re.search('[—–]|&mdash;|&ndash;|---',allt): errs.append('dash')
    if ';' in allt: errs.append(f'semicolons={allt.count(";")}')
    for b in BANNED:
        if re.search(r'\b'+re.escape(b)+r'\b',allt,re.I): errs.append('banned:'+b)
    for f in FORB:
        if re.search(f,allt,re.I): errs.append('forbidden:'+f)
    for x in paras(d):
        n=len(re.sub(r'\[\[[^|\]]+\|([^\]]+)\]\]',r'\1',x).split())
        if n>80: errs.append(f'para>{80}: {n}w "{x[:40]}"')
    m=len(d.get('meta','')); 
    if not 140<=m<=160: errs.append(f'meta len {m}')
    kind='hood' if slug in HD else 'service' if slug in SV else 'blog' if slug in BL else 'loc' if slug=='plumber-brentwood-ca' else 'home' if slug=='home' else 'std'
    links=re.findall(r'\[\[([^|\]]+)\|',allt)
    for l in links:
        if l not in VALID: errs.append('bad link '+l)
        if l in BL: errs.append('links to blog '+l)
    sec=d.get('sections',[]); kinds=[s.get('kind') for s in sec]
    for s in sec:
        if s.get('kind') not in('prose','urgent','checklist','compare','cost','local'): errs.append('bad kind '+str(s.get('kind')))
        if not s.get('h2'): errs.append('section missing h2')
    nf=len(d.get('faqs',[]))
    if kind=='hood':
        if not 5<=nf<=8: errs.append(f'faq count {nf}')
        if 'compare' not in kinds: errs.append('no compare table')
        if len(links)<4: errs.append(f'links {len(links)}<4')
        if re.search(r'licensed|insured|24/7|same-day|we are based|our base',allt,re.I): errs.append('unverified claim word')
        if not (d.get('side') or {}).get('link'): errs.append('side incomplete')
        if wc(d)<450: errs.append('words low')
    if kind in('service','loc'):
        if not 5<=nf<=8: errs.append(f'faq count {nf}')
        if 'compare' not in kinds: errs.append('no compare table')
        if len(links)<3: errs.append(f'links {len(links)}<3')
    if kind=='service':
        if kinds.count('cost')!=1: errs.append('cost section count')
        if SV[slug]['emergency']:
            if 'urgent' not in kinds: errs.append('no urgent section')
            nm=SV[slug]['name'].lower()
            if not any(f['q'].startswith('Do you handle') and f['q'].endswith('emergencies at night or on weekends in Oakley?') for f in d.get('faqs',[])): errs.append('no emergency faq')
        if not d.get('side') or not all(d['side'].get(k) for k in('h3','copy','link','link_text')): errs.append('side incomplete')
        first=" ".join(d.get('lead',[])+d.get('intro',[])).split()[:100]
        if 'Oakley' not in " ".join(first): errs.append('Oakley not in first 100w')
        if wc(d)<(1300 if slug in('water-heater-replacement','drain-cleaning','water-heater-repair','leak-detection','sewer-line-repair') else 900): errs.append('words low')
    if kind=='blog':
        if not 4<=nf<=6: errs.append(f'faq count {nf}')
        if 'localnote' not in d: errs.append('no localnote')
        if not any(f.get('kind')=='local' for f in d.get('faqs',[])): errs.append('no local faq')
        if wc(d)<1050: errs.append('words low')
        if not (d.get('side') or {}).get('link'): errs.append('side incomplete')
    if not d.get('cta_mid') or not d.get('cta_end'): errs.append('cta lines')
    return wc(d),errs
if __name__=='__main__':
    bad=0
    for s in sys.argv[1:]:
        w,e=check(s); print(s,w,'OK' if not e else 'FAIL '+' | '.join(e)); bad+=bool(e)
    sys.exit(1 if bad else 0)
