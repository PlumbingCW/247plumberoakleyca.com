import shutil, os, json
from PIL import Image, ImageDraw, ImageFont
B='/home/claude/oakley'; S=B+'/site'
FN=B+'/fonts_tmp/node_modules/@fontsource'
for src,dst in [('playfair-display/files/playfair-display-latin-700-normal.woff2','pf-700.woff2'),('playfair-display/files/playfair-display-latin-800-normal.woff2','pf-800.woff2'),('playfair-display/files/playfair-display-latin-800-italic.woff2','pf-800i.woff2'),('source-sans-3/files/source-sans-3-latin-400-normal.woff2','ss-400.woff2'),('source-sans-3/files/source-sans-3-latin-600-normal.woff2','ss-600.woff2'),('source-sans-3/files/source-sans-3-latin-700-normal.woff2','ss-700.woff2')]:
    shutil.copy(f'{FN}/{src}',f'{S}/fonts/{dst}')
CHOC=(74,46,30); CHOCD=(51,31,20); TURQ=(31,200,200); WHITE=(255,255,255)
def mark(size):
    s=size*4; im=Image.new('RGBA',(s,s),(0,0,0,0)); d=ImageDraw.Draw(im)
    d.rounded_rectangle([0,0,s-1,s-1],radius=int(s*.22),fill=CHOC+(255,))
    cx,cy=s*.5,s*.60; r=s*.23
    d.ellipse([cx-r,cy-r,cx+r,cy+r],fill=TURQ+(255,))
    d.polygon([(cx,s*.17),(cx-r*.93,cy-r*.35),(cx+r*.93,cy-r*.35)],fill=TURQ+(255,))
    d.arc([cx-r*.6,cy-r*.55,cx+r*.6,cy+r*.65],start=100,end=170,fill=CHOC+(255,),width=max(2,int(s*.035)))
    return im.resize((size,size),Image.LANCZOS)
m=mark(512); m.save(S+'/icon-512.png'); mark(192).save(S+'/icon-192.png'); mark(180).save(S+'/apple-touch-icon.png')
mark(256).save(S+'/favicon.ico',sizes=[(16,16),(32,32),(48,48)])
# SVG favicon / mark
svg_mark='''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="64" height="64"><rect width="64" height="64" rx="14" fill="#4A2E1E"/><path d="M32 11 L19.5 31 A13 13 0 1 0 44.5 31 Z" fill="#1FC8C8"/><path d="M24 36 A8 8 0 0 0 28 43" fill="none" stroke="#4A2E1E" stroke-width="2.4" stroke-linecap="round"/></svg>'''
open(S+'/favicon.svg','w').write(svg_mark)
def logo_svg(light):
    txt='#FFFFFF' if light else '#4A2E1E'; acc='#1FC8C8' if light else '#0C6F6F'
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 420 72" width="420" height="72" role="img" aria-label="Oakley 24/7 Plumbing"><rect x="2" y="4" width="64" height="64" rx="14" fill="#4A2E1E"{' stroke="#1FC8C8" stroke-width="2"' if light else ''}/><path d="M34 15 L21.5 35 A13 13 0 1 0 46.5 35 Z" fill="#1FC8C8"/><text x="82" y="34" font-family="'Playfair Display',Georgia,serif" font-weight="800" font-size="30" fill="{txt}">Oakley 24/7</text><text x="82" y="62" font-family="'Source Sans 3',Arial,sans-serif" font-weight="700" font-size="22" letter-spacing="3" fill="{acc}">PLUMBING</text></svg>'''
open(S+'/logo.svg','w').write(logo_svg(False)); open(S+'/logo-light.svg','w').write(logo_svg(True))
# OG image
W,H=1200,630; im=Image.new('RGB',(W,H),CHOCD); d=ImageDraw.Draw(im)
for y in range(H):
    t=y/H; d.line([(0,y),(W,y)],fill=(int(51+(74-51)*t),int(31+(46-31)*t),int(20+(30-20)*t)))
d.rectangle([0,0,W,10],fill=TURQ); d.rectangle([0,H-10,W,H],fill=TURQ)
pf=ImageFont.truetype(B+'/fonts_tmp/pf800.ttf',92); pfs=ImageFont.truetype(B+'/fonts_tmp/pf800.ttf',54)
ss=ImageFont.truetype(B+'/fonts_tmp/ss700.ttf',40); ss4=ImageFont.truetype(B+'/fonts_tmp/ss400.ttf',34)
im.paste(mark(150),(80,90),mark(150))
d.text((260,92),'Oakley 24/7',font=pf,fill=WHITE); d.text((262,200),'PLUMBING',font=ss,fill=TURQ)
d.text((80,330),'Emergency Plumber in Oakley, CA',font=pfs,fill=WHITE)
d.text((80,420),'Drains, water heaters, leaks and sewer lines.',font=ss4,fill=(237,228,220))
d.text((80,470),'24/7 emergency dispatch. Call (888) 910-8644',font=ss,fill=TURQ)
im.save(S+'/og-image.png',optimize=True)
open(S+'/site.webmanifest','w').write(json.dumps({"name":"Oakley 24/7 Plumbing","short_name":"Oakley Plumbing","start_url":"/","display":"browser","background_color":"#FFFFFF","theme_color":"#4A2E1E","icons":[{"src":"/icon-192.png","sizes":"192x192","type":"image/png"},{"src":"/icon-512.png","sizes":"512x512","type":"image/png"}]},indent=1))
print('assets ok',sorted(os.listdir(S)))
