import re,glob,collections,sys
from html.parser import HTMLParser
class M(HTMLParser):
    def __init__(s): super().__init__(); s.m=0; s.t=[]; s.skip=0; s.aside=0
    def handle_starttag(s,t,a):
        if t=='main': s.m=1
        if t in('script','style'): s.skip=1
        if t=='aside': s.aside=1
    def handle_endtag(s,t):
        if t=='main': s.m=0
        if t in('script','style'): s.skip=0
        if t=='aside': s.aside=0
    def handle_data(s,d):
        if s.m and not s.skip and not s.aside: s.t.append(d)
pages={}
for f in glob.glob('/home/claude/oakley/site/**/index.html',recursive=True):
    n=f.split('/site/')[1][:-11] or 'home'
    if n in('services','blog'): continue
    m=M(); m.feed(open(f).read()); t=re.sub(r'\s+',' ',' '.join(m.t)).lower(); t=re.sub(r'call \(888\) 910-8644','',t); t=re.sub(r'by the oakley 24/7 plumbing team · updated [a-z]+ \d+, \d+','',t); pages[n]=t
idx=collections.defaultdict(set)
for p,t in pages.items():
    for i in range(len(t)-40): idx[t[i:i+40]].add(p)
pair=collections.Counter(); ex={}
for sh,ps in idx.items():
    if len(ps)>1:
        ps=sorted(ps)
        for i in range(len(ps)):
            for j in range(i+1,len(ps)): pair[(ps[i],ps[j])]+=1; ex.setdefault((ps[i],ps[j]),sh)
print('pairs',len(pair),'total shingle hits',sum(pair.values()))
for k,v in pair.most_common(int(sys.argv[1]) if len(sys.argv)>1 else 30): print(v,k,'|',ex[k])
