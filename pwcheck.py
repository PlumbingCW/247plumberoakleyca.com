import subprocess,time,glob,json,sys
from playwright.sync_api import sync_playwright
site='/home/claude/oakley/site'
srv=subprocess.Popen(['python3','-m','http.server','8766','-d',site],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(1)
paths=['/']+['/'+f[len(site)+1:-10] for f in sorted(glob.glob(site+'/*/index.html'))]
res=[]
with sync_playwright() as pw:
    b=pw.chromium.launch()
    for w in (320,390,768,1280):
        ctx=b.new_context(viewport={'width':w,'height':900}); pg=ctx.new_page()
        fails=[]; errs=[]
        pg.on('response',lambda r: fails.append((r.url,r.status)) if r.status>=400 else None)
        pg.on('pageerror',lambda e: errs.append(str(e)))
        for p in paths:
            pg.goto('http://localhost:8766'+p,wait_until='load'); pg.wait_for_timeout(120)
            o=pg.evaluate("""()=>{const W=document.documentElement.clientWidth;const bad=[];document.querySelectorAll('body *').forEach(e=>{const r=e.getBoundingClientRect();if(r.width>0&&r.right>W+1&&!e.closest('.table-wrap')&&!e.closest('.mob-drawer')&&!e.closest('.dropdown')&&!e.closest('.map-wrap')){bad.push(e.tagName+'.'+e.className+' '+Math.round(r.right))}});return [document.documentElement.scrollWidth-W,bad.slice(0,3)]}""")
            broken=pg.evaluate("()=>[...document.images].filter(i=>i.complete&&i.naturalWidth==0).map(i=>i.src)")
            if o[0]>0 or o[1] or broken: res.append((w,p,o,broken))
        res.append((w,'404s',[f for f in fails if 'google' not in f[0]],errs))
        ctx.close()
    # sticky sidecard check 1280
    pg=b.new_context(viewport={'width':1280,'height':900}).new_page(); pg.goto('http://localhost:8766/water-heater-replacement/'); pg.evaluate('window.scrollTo(0,1400)'); pg.wait_for_timeout(200)
    r=pg.evaluate("()=>{const e=document.querySelector('.sidecard').getBoundingClientRect();return [e.top,e.bottom,innerHeight]}")
    res.append(('sticky sidecard after 1400px scroll',r))
    b.close()
srv.terminate()
for r in res: print(r)
print('paths',len(paths))
