import json, os, re, html, shutil, datetime, sys
sys.path.insert(0, '/home/claude/oakley')
import registry as R

OUT = '/home/claude/oakley/site'
CONT = '/home/claude/oakley/content'
SRC = '/home/claude/oakley/src'
TODAY = '2026-11-07'
SITE = R.SITE
BRAND = R.BRAND
TEL = 'tel:' + R.PHONE_DIGITS
SV = {s['slug']: s for s in R.SERVICES}
BL = {b['slug']: b for b in R.BLOGS}
STD = {s['slug']: s for s in R.STANDARD}
LOC = R.LOC
HD = {h['slug']: h for h in R.HOODS}
ALL = set(SV) | set(BL) | set(STD) | {LOC['slug']} | set(HD)

BLOG_IMG = {'gas-water-heater-installation': 'water-heater-installation', 'tankless-water-heater-venting': 'tankless-water-heater', 'toilet-shut-off-valve-repair': 'toilet-repair', 'water-leak-sensors': 'leak-detection', 'trenchless-pipe-lining-cost': 'sewer-line-repair', 'clean-plumbing-vent': 'sewer-line-cleaning', 'winter-plumbing-problems': 'burst-pipe-repair', 'check-plumber-license': 'plumbing-installation', 'copper-pipe-lifespan': 'repiping', 'water-softener-location': 'water-softener-filtration', 'slab-leak-detection': 'slab-leak-repair', 'on-demand-hot-water-heater-install': 'tankless-water-heater', 'toilet-fill-valve-flapper': 'toilet-repair', '110v-tankless': 'tankless-water-heater', 'acid-drain-cleaner': 'drain-cleaning'}
BASE = os.path.dirname(os.path.abspath(__file__))
def _build_hero_images():
    d = {}; imgdir = os.path.join(BASE, 'site', 'img')
    for s in R.SERVICES:
        if os.path.exists(os.path.join(imgdir, s['slug'] + '.webp')): d[s['slug']] = s['slug'] + '.webp'
    for b in R.BLOGS:
        for k, v in BLOG_IMG.items():
            if b['slug'].startswith(k + '-') and v in d: d[b['slug']] = d[v]; break
    if os.path.exists(os.path.join(imgdir, 'home.webp')): d[''] = 'home.webp'
    return d
HERO_IMAGES = _build_hero_images()
IMG_ALT = {'home':'Oakley 24/7 Plumbing service van parked on a quiet Oakley, CA residential street with a technician holding a toolbox','water-heater-replacement': 'Tank water heater in a drain pan in a garage with copper supply pipes', 'water-heater-repair': 'Plumber working on a tank water heater in a utility closet', 'water-heater-installation': 'Strapped tank water heater on a stand with an expansion tank', 'tankless-water-heater': 'Wall-mounted tankless water heater with copper and black pipes', 'drain-cleaning': 'Drain cable entering a yard cleanout beside a house wall', 'hydro-jetting': 'Hydro jetting hose reel and nozzle beside a cleanout', 'sewer-line-repair': 'Sewer line trench with pipe equipment and a worker in a yard', 'sewer-line-cleaning': 'Technician with a camera monitor and cable reel at a sewer cleanout', 'sewer-inspection': 'Gloved hand feeding an inspection camera cable into a cleanout', 'leak-detection': 'Technician in headphones listening for a leak on a concrete floor', 'slab-leak-repair': 'Thermal camera screen showing a warm spot on a concrete floor', 'burst-pipe-repair': 'Open wall cavity with a copper pipe spraying water', 'repiping': 'PEX supply lines run through wall framing, red for hot and blue for cold', 'plumbing-installation': 'Plumbing tools, valves and fittings laid out on a wood surface', 'toilet-repair': 'Open toilet tank showing the fill valve and flapper', 'faucet-repair': 'Hand adjusting a chrome faucet at a stainless steel sink', 'garbage-disposal-repair': 'Garbage disposal installed under a sink with drain connections', 'commercial-plumbing': 'Commercial kitchen sink drain piping and floor tiles', 'water-softener-filtration': 'Water softener tanks and filter setup on a wall'}
def img_alt(f): return IMG_ALT.get(f[:-5], '')


def esc(s): return html.escape(s, quote=False)
def attr(s): return html.escape(s, quote=True)
LINKRE = re.compile(r'\[\[([^|\]]+)\|([^\]]+)\]\]')
LINKERRS = []
def lk(t, where=''):
    def f(m):
        sl = m.group(1).strip()
        if sl not in ALL: LINKERRS.append((where, sl))
        return '<a href="/%s/">%s</a>' % (sl, esc(m.group(2)))
    parts = LINKRE.split(t)
    out = ''; i = 0
    # manual loop to escape non-link text
    pos = 0
    for m in LINKRE.finditer(t):
        out += esc(t[pos:m.start()]) + f(m); pos = m.end()
    return out + esc(t[pos:])
def plain(t): return LINKRE.sub(r'\2', t)

def url(slug): return SITE + '/' + (slug + '/' if slug else '')

HOME_LINES = {
 'water-heater-replacement': 'Tank leaking or no hot water at all',
 'drain-cleaning': 'Sinks, tubs and floor drains that will not clear',
 'water-heater-repair': 'Pilot, thermostat or valve trouble on a working tank',
 'leak-detection': 'A meter that keeps moving or a stain you cannot trace',
 'slab-leak-repair': 'Hot spots in the floor and the sound of running water',
 'burst-pipe-repair': 'Water spraying now and the main valve to find',
 'hydro-jetting': 'Roots and grease that keep bringing a clog back',
 'sewer-line-repair': 'Cracked, rooted or sagging lines between house and street',
 'sewer-line-cleaning': 'Every drain slow at once, or sewage coming up',
 'sewer-inspection': 'A camera look before you buy, sell or dig',
 'tankless-water-heater': 'On-demand heaters that need service or a flush',
 'water-heater-installation': 'Planned swaps, upgrades and fuel changes',
 'repiping': 'Old supply lines, low pressure and repeat leaks',
 'plumbing-installation': 'New fixtures, remodels and gas safety first steps',
 'toilet-repair': 'Overflows, rocking bowls and tanks that never stop',
 'faucet-repair': 'Drips, stuck valves and showers that will not shut off',
 'garbage-disposal-repair': 'Humming, jammed or leaking disposals',
 'commercial-plumbing': 'Shops, offices and rentals with after-hours trouble',
 'water-softener-filtration': 'What can be done about hard Delta water',
}
TOP3 = ['water-heater-replacement', 'drain-cleaning', 'water-heater-repair']

def brand(light=False):
    src = '/logo-light.png' if light else '/logo.png'
    return '', '<img class="brand-logo" src="%s" alt="Oakley 24/7 Plumbing" width="720" height="182">' % src

KNOWS = ["Emergency plumbing","24 hour plumber","Water heater replacement","Water heater repair","Water heater installation","Tankless water heater","Tankless water heater flushing","Descaling","Heat pump water heater","Electric water heater","Gas water heater","Hybrid water heater","Water heater expansion tank","Water heater seismic strapping","Temperature and pressure relief valve","Anode rod","Drain cleaning","Clogged drains","Drain snaking","Kitchen sink clogs","Shower and tub drain clogs","Floor drains","Hydro jetting","Sewer line repair","Sewer line cleaning","Sewer camera inspection","Sewer backup","Sewer cleanout","Trenchless pipe lining","Cast iron pipe repair","Root intrusion","Main line clog","Septic systems","Leak detection","Slab leak repair","Water meter leak test","High water bill leaks","Water service line leaks","Underground pipe leaks","Ceiling and wall leaks","Crawlspace leaks","Irrigation leaks","Burst pipe repair","Copper pipe repair","PEX piping","CPVC piping","Galvanized pipe replacement","Repiping","Low water pressure","Pressure regulators","Main water shutoff valves","Angle stop valves","Toilet repair","Toilet installation","Toilet flange and wax ring","Toilet fill valve","Toilet flapper","Running toilets","Faucet repair","Faucet installation","Shower valve repair","Bathtub faucets","Utility sinks","Garbage disposal repair","Garbage disposal installation","Dishwasher drain connections","Air gaps","Commercial plumbing","Backflow testing","Backflow prevention","Grease trap cleaning","Storm drain cleaning","Water softeners","Water filtration","Water conditioners","Hard water","Whole home filtration","Plumbing installation","Remodel plumbing","New construction rough-in plumbing","Sump pumps","Ejector pumps","Gas line safety","Gas leak response","Plumbing vents","Plumbing vent cleaning","Water leak sensors","Automatic shutoff valves","Plumbing permits","California Plumbing Code","California Health and Safety Code 19211","Contra Costa County plumbing","Diablo Water District","Ironhouse Sanitary District","Sewer lateral compliance certificates","BAAQMD Rule 9-6","Hose bibs","Frozen pipes","Winter plumbing","Water quality","Plumber license verification","Property manager plumbing","After-hours plumbing"]

def hero_bg(slug):
    f = HERO_IMAGES.get(slug)
    if f: return ' has-hero', '<img class="hero-bg" src="/img/%s" alt="%s" width="1600" height="900" fetchpriority="high">' % (f, esc(img_alt(f)))
    return ' hero-fallback', ''

# ---------------- chrome ----------------
def nav_links():
    sv = ''.join('<li><a href="/%s/">%s</a></li>' % (s, esc(SV[s]['name'])) for s in TOP3)
    groups = {}
    for s in R.SERVICES: groups.setdefault(s['group'], []).append(s)
    allsv = ''
    for g, items in groups.items():
        for s in items:
            allsv += '<li><a href="/%s/">%s</a></li>' % (s['slug'], esc(s['name']))
    return sv, allsv

def header(cur=''):
    name, mark = brand()
    sv, allsv = nav_links()
    svc_dd = ('<ul class="dropdown dropdown-wide">' + allsv + '<li class="dd-all"><a href="/services/">All plumbing services</a></li></ul>')
    area_dd = ('<ul class="dropdown"><li><a href="/service-area/">Oakley, CA</a></li>'
               '<li><a href="/plumber-brentwood-ca/">Brentwood</a></li>'
               '<li><a href="/service-area/">Antioch</a></li><li><a href="/service-area/">Knightsen</a></li>'
               '<li><a href="/service-area/">Bethel Island</a></li>'
               '<li class="dd-all"><a href="/service-area/">Full service area</a></li></ul>')
    nav = ('<ul class="nav-links">'
           '<li><a href="/">Home</a></li>'
           '<li class="has-dropdown"><a href="/services/">Services <span class="dd-arrow" aria-hidden="true">&#9662;</span></a>%s</li>'
           '<li class="has-dropdown"><a href="/service-area/">Areas <span class="dd-arrow" aria-hidden="true">&#9662;</span></a>%s</li>'
           '<li><a href="/blog/">Blog</a></li><li><a href="/contact/">Contact</a></li>'
           '<li><a href="%s">Call %s</a></li></ul>') % (svc_dd, area_dd, TEL, R.PHONE_DISPLAY)
    drawer = ('<div class="mob-overlay" id="mob-overlay"></div>'
              '<div class="mob-drawer" id="mob-drawer" hidden aria-label="Site menu">'
              '<button class="drawer-close" id="drawer-close" type="button" aria-label="Close navigation menu">&#10005;</button>'
              '<ul><li><a href="/">Home</a></li>'
              '<li><span class="drawer-h">Services</span></li>')
    for s in TOP3: drawer += '<li><a href="/%s/">%s</a></li>' % (s, esc(SV[s]['name']))
    drawer += ('<li><a href="/services/">All plumbing services</a></li>'
               '<li><span class="drawer-h">Areas</span></li>'
               '<li><a href="/service-area/">Oakley service area</a></li>'
               '<li><a href="/plumber-brentwood-ca/">Brentwood</a></li>'
               '<li><span class="drawer-h">More</span></li>'
               '<li><a href="/blog/">Blog</a></li><li><a href="/about/">About</a></li><li><a href="/contact/">Contact</a></li>'
               '<li><a class="drawer-cta" href="%s">Call %s</a></li></ul></div>') % (TEL, R.PHONE_DISPLAY)
    return ('<a class="skip" href="#main">Skip to main content</a>'
            '<div class="masthead"><div class="wrap"><span><b>24/7</b> emergency dispatch</span>'
            '<span class="m-city">Oakley, CA &middot; Contra Costa County</span>'
            '<span class="m-phone">%s</span></div></div>'
            '<div class="bannerrow"><div class="wrap"><a class="brand" href="/" aria-label="%s home">%s%s</a>'
            '<button class="hamburger" id="mob-toggle" type="button" aria-expanded="false" aria-controls="mob-drawer" aria-label="Open navigation menu"><span></span><span></span><span></span></button></div></div>'
            '<nav class="navrule" aria-label="Main">%s</nav>%s') % (R.PHONE_DISPLAY, attr(BRAND), mark, name, nav, drawer)

def footer():
    name, mark = brand(True)
    sv = ''.join('<li><a href="/%s/">%s</a></li>' % (s, esc(SV[s]['name'])) for s in TOP3)
    return ('<footer><div class="wrap"><div class="foot-grid">'
            '<div><a class="brand foot-brand" href="/" aria-label="%s home" style="flex-direction:row;align-items:center">%s%s</a>'
            '<address><strong>%s</strong><br>%s<br><a class="tel" href="%s">%s</a><br><a href="mailto:%s">%s</a></address></div>'
            '<div><span class="fh">Services</span><ul>%s<li><a href="/services/">All plumbing services</a></li></ul></div>'
            '<div><span class="fh">Areas</span><ul><li><a href="/service-area/">Oakley service area</a></li><li><a href="/plumber-brentwood-ca/">Brentwood</a></li></ul></div>'
            '<div><span class="fh">Company</span><ul><li><a href="/about/">About</a></li><li><a href="/contact/">Contact</a></li><li><a href="/blog/">Blog</a></li><li><a href="/privacy/">Privacy</a></li><li><a href="/terms/">Terms</a></li></ul></div>'
            '</div><div class="foot-bottom">&copy; 2026 %s. 24/7 emergency plumbing dispatch in Oakley, CA.</div></div></footer>'
            '<div class="sticky-cta"><a href="%s">Call %s &middot; 24/7</a></div>'
            '<a class="float-call" href="%s" aria-label="Call %s"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1 1 .4 1.9.7 2.8a2 2 0 0 1-.5 2.1L8.1 9.9a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.4c.9.3 1.8.6 2.8.7a2 2 0 0 1 1.7 2z"/></svg></a>'
            ) % (attr(BRAND), mark, name, esc(BRAND), esc(R.SERVES), TEL, R.PHONE_DISPLAY, R.EMAIL, R.EMAIL, sv, esc(BRAND), TEL, R.PHONE_DISPLAY, TEL, R.PHONE_DISPLAY)

def mapsec(extra=None):
    def m(q, z, title):
        return ('<div class="map-wrap"><iframe src="https://maps.google.com/maps?q=%s&output=embed&z=%d" title="%s" loading="lazy" referrerpolicy="no-referrer-when-downgrade" allowfullscreen></iframe></div>'
                % (q.replace(' ', '+').replace(',', '%2C'), z, attr(title)))
    body = ''
    if extra: body += m(*extra)
    body += m('Oakley, CA', 11, 'Service area map: Oakley, CA and nearby communities')
    return ('<section class="map-sec"><div class="wrap"><h2>Our Oakley service area on the map</h2>'
            '<p>Dispatch covers Oakley and the nearby Contra Costa County communities of Brentwood, Antioch, Knightsen and Bethel Island.</p>%s</div></section>') % body

def head(title, meta, slug, schema, robots=True, og_type='website'):
    can = url(slug)
    h = ['<!DOCTYPE html><html lang="en-US"><head><meta charset="utf-8">',
         '<meta name="viewport" content="width=device-width, initial-scale=1">',
         '<title>%s</title>' % esc(title),
         '<meta name="description" content="%s">' % attr(meta)]
    if robots:
        h.append('<link rel="canonical" href="%s">' % can)
        h.append('<meta name="robots" content="index, follow, max-image-preview:large">')
    else:
        h.append('<meta name="robots" content="noindex, follow">')
    h += ['<meta name="theme-color" content="#4A2E1E">',
          '<meta property="og:type" content="%s"><meta property="og:site_name" content="%s">' % (og_type, attr(BRAND)),
          '<meta property="og:title" content="%s"><meta property="og:description" content="%s">' % (attr(title), attr(meta)),
          '<meta property="og:url" content="%s"><meta property="og:image" content="%s/og-image.png">' % (can, SITE),
          '<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">',
          '<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="%s"><meta name="twitter:description" content="%s">' % (attr(title), attr(meta)),
          '<link rel="icon" href="/favicon.ico" sizes="any"><link rel="icon" href="/favicon-32.png" type="image/png" sizes="32x32"><link rel="icon" href="/favicon-48.png" type="image/png" sizes="48x48">',
          '<link rel="apple-touch-icon" href="/apple-touch-icon.png"><link rel="manifest" href="/site.webmanifest">',
          '<link rel="preload" href="/fonts/pf-800.woff2" as="font" type="font/woff2" crossorigin>',
          '<link rel="preload" href="/fonts/ss-400.woff2" as="font" type="font/woff2" crossorigin>']
    if slug in HERO_IMAGES: h.append('<link rel="preload" as="image" href="/img/%s" fetchpriority="high">' % HERO_IMAGES[slug])
    h.append('<link rel="stylesheet" href="/main.css">')
    for blk in schema:
        h.append('<script type="application/ld+json">%s</script>' % json.dumps(blk, ensure_ascii=False, separators=(',', ':')))
    h.append('</head>')
    return ''.join(h)

def page(title, meta, slug, schema, body, robots=True, og_type='website', mapextra=None, nomap=False):
    return (head(title, meta, slug, schema, robots, og_type) + '<body>' + header() +
            '<main id="main">' + body + '</main>' + ('' if nomap else mapsec(mapextra)) + footer() +
            '<script src="/main.js" defer></script></body></html>')

# ---------------- schema ----------------
def business():
    return {"@type": ["Plumber", "LocalBusiness"], "@id": SITE + "/#business", "name": BRAND, "url": SITE + "/",
            "telephone": R.PHONE_E164, "email": R.EMAIL,
            "image": SITE + "/og-image.png", "logo": SITE + "/icon-512.png",
            "address": {"@type": "PostalAddress", "addressLocality": "Oakley", "addressRegion": "CA", "postalCode": "94561", "addressCountry": "US"},
            "areaServed": [{"@type": "City", "name": n, "containedInPlace": {"@type": "State", "name": "California"}} for n in ("Oakley", "Brentwood", "Antioch", "Knightsen", "Bethel Island")],
            "openingHoursSpecification": [{"@type": "OpeningHoursSpecification", "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"], "opens": "00:00", "closes": "23:59"}],
            "knowsAbout": KNOWS}
def website():
    return {"@type": "WebSite", "@id": SITE + "/#website", "url": SITE + "/", "name": BRAND, "publisher": {"@id": SITE + "/#business"}}
def webpage(slug, title, meta, ptype="WebPage"):
    return {"@type": ptype, "@id": url(slug) + "#webpage", "url": url(slug), "name": title, "description": meta,
            "isPartOf": {"@id": SITE + "/#website"}, "about": {"@id": SITE + "/#business"}, "inLanguage": "en-US"}
def crumbs(items):
    return {"@type": "BreadcrumbList", "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n, "item": u} for i, (n, u) in enumerate(items)]}
def faqld(faqs):
    return {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": f['q'], "acceptedAnswer": {"@type": "Answer", "text": ' '.join(plain(p) for p in (f['a'] if isinstance(f['a'], list) else [f['a']]))}} for f in faqs]}
def graph(*nodes):
    return [{"@context": "https://schema.org", "@graph": list(nodes)}]

# ---------------- content renderers ----------------
def paras(ps, where): return ''.join('<p>%s</p>' % lk(p, where) for p in ps)

def sec_html(s, where):
    k = s['kind']; h2 = '<h2>%s</h2>' % esc(s['h2'])
    ps = paras(s.get('paras', []), where)
    if k == 'prose':
        b = ''
        if s.get('bullets'): b = '<ul class="checks">' + ''.join('<li>%s</li>' % lk(x, where) for x in s['bullets']) + '</ul>'
        c = ''
        if s.get('callout'): c = '<div class="insight-card"><b>%s</b><p>%s</p></div>' % (esc(s['callout']['title']), lk(s['callout']['text'], where))
        return '<section class="panel">%s%s%s%s</section>' % (h2, ps, b, c)
    if k == 'urgent':
        return '<section class="panel urgent"><span class="kick">Urgent</span>%s%s<ol class="donow">%s</ol></section>' % (h2, ps, ''.join('<li>%s</li>' % lk(x, where) for x in s['do_now']))
    if k == 'checklist':
        return '<section class="panel">%s%s<div class="cards3">%s</div></section>' % (h2, ps, ''.join('<div class="ocard"><b>%s</b><p>%s</p></div>' % (esc(i['t']), lk(i['d'], where)) for i in s['items']))
    if k == 'compare':
        t = s['table']
        th = ''.join('<th scope="col">%s</th>' % esc(x) for x in t['head'])
        tr = ''.join('<tr>' + ''.join('<td>%s</td>' % lk(c, where) for c in r) + '</tr>' for r in t['rows'])
        return '<section class="panel">%s%s<div class="table-wrap"><table><thead><tr>%s</tr></thead><tbody>%s</tbody></table></div></section>' % (h2, ps, th, tr)
    if k == 'cost':
        fx = '<ul class="checks">' + ''.join('<li><strong>%s.</strong> %s</li>' % (esc(f['t']), lk(f['d'], where)) for f in s['factors']) + '</ul>'
        ins = '<div class="insight-card"><b>Insurance note</b><p>%s</p></div>' % lk(s['insurance'], where) if s.get('insurance') else ''
        cl = '<p class="sub">%s</p>' % lk(s['call_line'], where) if s.get('call_line') else ''
        return '<section class="panel">%s%s%s%s%s</section>' % (h2, ps, fx, ins, cl)
    if k == 'local':
        st = ''
        if s.get('facts'): st = '<div class="stats">' + ''.join('<div class="stat"><b>%s</b><span>%s</span></div>' % (esc(f['value']), esc(f['label'])) for f in s['facts']) + '</div>'
        return '<section class="panel localnote">%s%s%s</section>' % (h2, ps, st)
    raise ValueError(k)

def faq_html(faqs, where, h2='Frequently asked questions'):
    items = ''
    for i, f in enumerate(faqs):
        a = f['a'] if isinstance(f['a'], list) else [f['a']]
        items += ('<div class="faq-item"><button class="faq-q" type="button" aria-expanded="false">%s</button>'
                  '<div class="faq-answer"><div class="faq-answer-in">%s</div></div></div>') % (esc(f['q']), paras(a, where))
    return '<section class="panel faq-sec"><h2>%s</h2><div class="faq">%s</div></section>' % (esc(h2), items)

def cta_band(text, kick='Talk to dispatch'):
    return ('<div class="cta-band"><span class="kick">%s</span><p class="pq">%s</p><a class="btn" href="%s">Call %s</a></div>' % (esc(kick), esc(text), TEL, R.PHONE_DISPLAY))

def sidecard(side, ptype):
    link = ''
    if side and side.get('link'):
        link = '<p class="more">%s <a href="/%s/">%s</a></p>' % ('', side['link'], esc(side['link_text']))
    head3 = esc(side['h3']) if side else 'Plumbing problem right now?'
    copy = esc(side['copy']) if side else 'Dispatch is open around the clock and the price is explained before work starts.'
    kick, trust = ('24/7 dispatch', '<li>Clear price before work starts</li><li>Same-day appointments when available</li><li>Serving Oakley and nearby towns</li>')
    if ptype == 'hood': kick, trust = ('Call dispatch', '<li>Describe the problem on the phone</li><li>Serving Oakley and nearby towns</li>')
    return ('<aside class="sidecard"><span class="kicker">%s</span><h3>%s</h3><p>%s</p>'
            '<a class="btn btn-block" href="%s">Call %s</a>'
            '<ul class="trust">%s</ul>%s</aside>') % (kick, head3, copy, TEL, R.PHONE_DISPLAY, trust, link)

def pagehead(slug, h1, leads, crumb_items, badge=None, badge_alt=False, extra='', cta=True, byline=''):
    cls, img = hero_bg(slug)
    crumb = '<nav class="crumbs" aria-label="Breadcrumb">' + ' / '.join(
        ('<a href="%s">%s</a>' % (u, esc(n))) if i < len(crumb_items) - 1 else '<span aria-current="page">%s</span>' % esc(n)
        for i, (n, u) in enumerate(crumb_items)) + '</nav>'
    b = ''
    if badge: b = '<span class="badge%s"><span class="dot"></span>%s</span>' % (' badge-alt' if badge_alt else '', esc(badge))
    ls = ''.join('<p class="lead">%s</p>' % lk(x, slug) for x in leads)
    c = '<div class="cta-row"><a class="btn" href="%s">Call %s</a></div>' % (TEL, R.PHONE_DISPLAY) if cta else ''
    return ('<section class="pagehead%s">%s<div class="wrap single"><div>%s%s<h1>%s</h1>%s%s%s%s</div></div></section>'
            % (cls, img, crumb, b, esc(h1), ls, c, extra, byline))

def build_crumbs(items):
    # items: [(name, path)] path '/' style
    return [(n, p) for n, p in items]

def abs_c(items): return [(n, SITE + p) for n, p in items]

# ---------------- page builders ----------------
PAGES = {}   # outpath(dir slug) -> html
SITEMAP = []

def emit(slug, doc, index=True):
    PAGES[slug] = doc
    if index: SITEMAP.append(slug)

def load(slug):
    return json.load(open('%s/%s.json' % (CONT, slug)))

def main_with_sections(d, slug, ctx_sections_extra=''):
    secs = d['sections']; out = ''
    for i, s in enumerate(secs):
        out += sec_html(s, slug)
        if i == 1 and d.get('cta_mid'): out += cta_band(d['cta_mid'])
    return out

def build_service(slug):
    s = SV[slug]; d = load(slug)
    crumb = [('Home', '/'), ('Services', '/services/'), (s['name'], '/' + slug + '/')]
    intro = '<section class="panel lede-panel">%s</section>' % paras(d['intro'], slug)
    body = main_with_sections(d, slug)
    body += faq_html(d['faqs'], slug) + (cta_band(d['cta_end'], 'Dispatch is open') if d.get('cta_end') else '')
    ph = pagehead(slug, s['h1'], d['lead'], crumb, badge='24/7 emergency response' if s['emergency'] else 'Planned service')
    main = ('<section class="sec"><div class="wrap twocol"><div>%s%s</div>%s</div></section>' % (intro, body, sidecard(d.get('side'), 'service')))
    sch = graph(business(), website(), webpage(slug, s['title'], d['meta']),
                {"@type": "Service", "@id": url(slug) + "#service", "name": s['name'], "serviceType": s['name'], "url": url(slug),
                 "description": d['meta'], "provider": {"@id": SITE + "/#business"},
                 "areaServed": {"@type": "City", "name": "Oakley", "containedInPlace": {"@type": "State", "name": "California"}}},
                crumbs(abs_c(crumb)), faqld(d['faqs']))
    emit(slug, page(s['title'], d['meta'], slug, sch, ph + main))

def build_blog(slug):
    b = BL[slug]; d = load(slug)
    crumb = [('Home', '/'), ('Blog', '/blog/'), (b['title'], '/' + slug + '/')]
    by = '<p class="byline">By the Oakley 24/7 Plumbing team &middot; Updated %s</p>' % datetime.date.fromisoformat(TODAY).strftime('%B %d, %Y').replace(' 0', ' ')
    intro = '<section class="panel lede-panel">%s</section>' % paras(d['intro'], slug)
    body = main_with_sections(d, slug)
    ln = d.get('localnote')
    if ln: body += '<section class="panel localnote"><h2>%s</h2>%s</section>' % (esc(ln['h2']), paras(ln['paras'], slug))
    body += faq_html(d['faqs'], slug) + (cta_band(d['cta_end']) if d.get('cta_end') else '')
    side = d.get('side') or {"h3": "Need a plumber now?", "copy": "Dispatch is open 24/7 for Oakley homes.", "link": b['links'][0], "link_text": SV[b['links'][0]]['name']}
    ph = pagehead(slug, d.get('h1') or b['title'], d['lead'], crumb, badge='Plumbing guide', byline=by)
    main = ('<section class="sec"><div class="wrap twocol"><div>%s%s</div>%s</div></section>' % (intro, body, sidecard(side, 'blog')))
    sch = graph(business(), website(), webpage(slug, b['title'], d['meta']),
                {"@type": "BlogPosting", "@id": url(slug) + "#post", "headline": d.get('h1') or b['title'], "description": d['meta'],
                 "mainEntityOfPage": {"@id": url(slug) + "#webpage"}, "url": url(slug),
                 "author": {"@type": "Organization", "name": "Oakley 24/7 Plumbing team", "url": SITE + "/"},
                 "publisher": {"@id": SITE + "/#business"}, "datePublished": TODAY, "dateModified": TODAY,
                 "image": SITE + "/og-image.png", "inLanguage": "en-US"},
                crumbs(abs_c(crumb)), faqld(d['faqs']))
    emit(slug, page(b['title'], d['meta'], slug, sch, ph + main, og_type='article'))

def build_location():
    slug = LOC['slug']; d = load(slug)
    crumb = [('Home', '/'), ('Service Area', '/service-area/'), ('Brentwood', '/' + slug + '/')]
    z = d['zips']
    chips = '<div class="zips"><span class="zl">ZIP codes</span><span class="zip-chip primary">%s</span>%s</div>' % (
        z['primary'], ''.join('<span class="zip-chip">%s %s</span>' % (n['zip'], esc(n['place'])) for n in z['nearby']))
    ph = pagehead(slug, LOC['h1'], d['lead'], crumb, badge='Emergency plumber, 24/7', badge_alt=True, extra=chips)
    intro = '<section class="panel lede-panel">%s<div class="cards3">%s</div></section>' % (
        paras(d['intro'], slug), ''.join('<div class="ocard"><b>%s</b><p>%s</p></div>' % (esc(c['t']), lk(c['d'], slug)) for c in d['overview_cards']))
    secs = main_with_sections(d, slug)
    pc = d['prep_cards']
    prep = '<section class="panel"><h2>%s</h2><div class="prep">%s</div></section>' % (esc(pc['h2']), ''.join('<div class="pcard"><b>%s</b><p>%s</p></div>' % (esc(i['t']), lk(i['d'], slug)) for i in pc['items']))
    # place prep after sections index 2 to keep the cta_mid ordering
    body = secs + prep + faq_html(d['faqs'], slug) + cta_band(d['cta_end'], 'Dispatch is open')
    side = d.get('side')
    main = '<section class="sec"><div class="wrap twocol"><div>%s%s</div>%s</div></section>' % (intro, body, sidecard(side, 'loc'))
    sch = graph(business(), website(), webpage(slug, LOC['title'], d['meta']),
                {"@type": "Service", "@id": url(slug) + "#service", "name": "Emergency plumbing in Brentwood, CA", "serviceType": "Emergency plumbing", "url": url(slug),
                 "description": d['meta'], "provider": {"@id": SITE + "/#business"},
                 "areaServed": {"@type": "City", "name": "Brentwood", "containedInPlace": {"@type": "State", "name": "California"}}},
                crumbs(abs_c(crumb)), faqld(d['faqs']))
    emit(slug, page(LOC['title'], d['meta'], slug, sch, ph + main, mapextra=('Brentwood, CA 94513', 13, 'Map of Brentwood, CA 94513 and surrounding area')))

def build_hood(slug):
    h = HD[slug]; d = load(slug)
    crumb = [('Home', '/'), ('Service Area', '/service-area/'), (h['name'], '/' + slug + '/')]
    ph = pagehead(slug, h['h1'], d['lead'], crumb)
    intro = '<section class="panel lede-panel">%s</section>' % paras(d['intro'], slug)
    body = ''
    for i, s in enumerate(d['sections']):
        body += sec_html(s, slug)
        if i == 1: body += cta_band(d['cta_mid'], 'Call dispatch')
    body += faq_html(d['faqs'], slug) + cta_band(d['cta_end'], 'Call dispatch')
    main = '<section class="sec"><div class="wrap twocol"><div>%s%s</div>%s</div></section>' % (intro, body, sidecard(d['side'], 'hood'))
    sch = graph(business(), website(), webpage(slug, h['title'], d['meta']),
                {"@type": "Service", "@id": url(slug) + "#service", "name": "Plumbing services in %s, Oakley, CA" % h['name'], "serviceType": "Plumbing", "url": url(slug),
                 "description": d['meta'], "provider": {"@id": SITE + "/#business"},
                 "areaServed": {"@type": "Place", "name": "%s, Oakley, CA" % h['name']}},
                crumbs(abs_c(crumb)), faqld(d['faqs']))
    emit(slug, page(h['title'], d['meta'], slug, sch, ph + main, mapextra=('%s, Oakley, CA' % h['name'], 14, 'Map of %s, Oakley, CA' % h['name'])))

def callrow():
    return ('<div class="callrow"><span>Ready to talk to a dispatcher?</span><a class="btn" href="%s">Call dispatch now</a><a class="tel" href="%s">%s</a></div>') % (TEL, TEL, R.PHONE_DISPLAY)

def build_standard(slug):
    s = STD[slug]; d = load(slug)
    crumb = [('Home', '/'), (s['h1'], '/' + slug + '/')]
    ptype = {'about': 'AboutPage', 'contact': 'ContactPage'}.get(slug, 'WebPage')
    ph = pagehead(slug, s['h1'], d['lead'], crumb, cta=True)
    body = ''
    if d.get('intro'): body += '<section class="panel lede-panel">%s</section>' % paras(d['intro'], slug)
    for i, sec in enumerate(d['sections']):
        body += sec_html(sec, slug)
        if i == 1 and d.get('cta_mid'): body += cta_band(d['cta_mid'])
    if d.get('faqs'): body += faq_html(d['faqs'], slug)
    if slug == 'service-area': body += callrow()
    if d.get('cta_end'): body += cta_band(d['cta_end'], 'Dispatch is open')
    main = '<section class="sec"><div class="wrap"><div class="stack">%s</div></div></section>' % body
    nodes = [business(), website(), webpage(slug, s['title'], d['meta'], ptype), crumbs(abs_c(crumb))]
    if d.get('faqs'): nodes.append(faqld(d['faqs']))
    extra = None
    emit(slug, page(s['title'], d['meta'], slug, graph(*nodes), ph + main, mapextra=extra))

def build_home():
    d = load('home'); h = R.HOME
    ph = ''
    cls, img = ' hero-fallback hero-home', ''
    hf = HERO_IMAGES.get('')
    photo = ('<img src="/img/%s" alt="%s" width="1024" height="572" fetchpriority="high">' % (hf, esc(img_alt(hf)))) if hf else ''
    side = ('<div class="herofig">%s<div class="herocall"><div><span class="hc-k">Dispatch, around the clock</span><span class="hc-num">%s</span><span class="hc-n">Open nights, weekends and holidays</span></div>'
            '<a class="btn" href="%s">Call now</a></div></div>') % (photo, R.PHONE_DISPLAY, TEL)
    hero = ('<section class="hero%s">%s<div class="wrap"><div><span class="badge"><span class="dot"></span>24/7 emergency plumber</span><h1>%s</h1>%s'
            '<div class="cta-row"><a class="btn" href="%s">Call %s</a><a class="btn btn-ghost" href="/services/">See all services</a></div></div>%s</div></section>'
            % (cls, img, esc(h['h1']), ''.join('<p class="lead">%s</p>' % lk(x, 'home') for x in d['lead']), TEL, R.PHONE_DISPLAY, side))
    groups = {}
    for s in R.SERVICES: groups.setdefault(s['group'], []).append(s)
    rows = ''; n = 0
    for s in R.SERVICES:
        n += 1
        rows += '<div class="tocrow"><span class="tnum">%02d</span><div><h3><a href="/%s/">%s</a></h3><p>%s</p></div></div>' % (n, s['slug'], esc(s['name']), esc(HOME_LINES[s['slug']]))
    toc = '<section class="sec sec-white"><div class="wrap"><div class="stack"><span class="kick">Plumbing services</span><h2 class="sec-head">What we fix in Oakley, from emergencies to planned work</h2><div class="toc">%s</div></div></div></section>' % rows
    why = '<section class="sec"><div class="wrap"><div class="stack"><span class="kick">How we work</span><h2 class="sec-head">What to expect when you call</h2><div class="whygrid four">%s</div></div></div></section>' % ''.join('<div class="whycard"><b>%s</b><p>%s</p></div>' % (esc(w['t']), lk(w['d'], 'home')) for w in d['why'])
    intro = '<section class="sec sec-white"><div class="wrap"><div class="stack"><div class="panel lede-panel">%s</div></div></div></section>' % paras(d['intro'], 'home')
    secs = ''
    for i, s in enumerate(d['sections']):
        secs += sec_html(s, 'home')
        if i == 1: secs += cta_band(d['cta_mid'])
    secs = '<section class="sec"><div class="wrap"><div class="stack">%s</div></div></section>' % secs
    cv = d['coverage']
    strip = '<div class="areastrip"><span class="zip-chip primary">Oakley 94561</span><a class="zip-chip" href="/plumber-brentwood-ca/">Brentwood 94513</a><span class="zip-chip">Antioch 94509 and 94531</span><span class="zip-chip">Knightsen 94548</span><span class="zip-chip">Bethel Island 94511</span></div>'
    cover = '<section class="sec sec-white"><div class="wrap"><div class="stack"><div class="panel"><h2>%s</h2>%s%s</div></div></div></section>' % (esc(cv['h2']), paras(cv['paras'], 'home'), strip)
    hoods = '<section class="sec"><div class="wrap"><div class="stack"><div class="panel hoods"><h2>Neighborhoods We Serve</h2><p>Plumbing pages for specific parts of Oakley, each written around the local water, sewer and housing details that apply there.</p><div class="hoodgrid">%s</div></div></div></div></section>' % ''.join('<a class="hoodcard" href="/%s/"><b>%s</b><span>%s</span></a>' % (x['slug'], esc(x['name']), esc(x['teaser'])) for x in R.HOODS)
    faq = '<section class="sec"><div class="wrap"><div class="stack">%s%s</div></div></section>' % (faq_html(d['faqs'], 'home'), cta_band(d['cta_end'], 'Dispatch is open'))
    sch = graph(business(), website(), webpage('', h['title'], d['meta']), crumbs([('Home', SITE + '/')]), faqld(d['faqs']))
    emit('', page(h['title'], d['meta'], '', sch, hero + intro + toc + why + secs + cover + hoods + faq))

HUBS = {
 'services': dict(meta="Browse every plumbing service from Oakley 24/7 Plumbing, from drain cleaning to water heater replacement. Emergency dispatch around the clock. Call (888) 910-8644.",
   lead="Every plumbing service we handle in Oakley, CA, grouped by the problem you are trying to solve.",
   note={"Water Heaters": "A tank that leaks or a heater that stops making hot water is the usual reason for a call, and installs and tankless service are planned work.",
         "Drains and Sewer": "Clogs, backups and camera inspections, from a single sink to the line that leaves the house.",
         "Leaks and Pipes": "Hidden leaks, burst pipes and whole-house pipe replacement, found and fixed with a clear scope first.",
         "Installations": "New fixtures, supply and drain runs, and remodel plumbing, plus the gas safety steps that come first.",
         "Fixtures": "Toilets, faucets, shower valves and disposals that leak, run or will not shut off.",
         "Commercial": "After-hours help for shops, offices and rental properties around Laurel Road and Main Street.",
         "Water Quality": "Softening and filtration for the hard Delta water that Diablo Water District reports."}),
 'blog': dict(meta="Plain-language plumbing guides for Oakley, CA homeowners: water heaters, drains, leaks and pipes, written by the Oakley 24/7 Plumbing team. Call (888) 910-8644.",
   lead="Plumbing guides written for Oakley homeowners, with local utility and permit details where they matter.")}

def build_hubs():
    # services hub
    h = STD['services']; hub = HUBS['services']
    crumb = [('Home', '/'), ('Services', '/services/')]
    groups = {}
    for s in R.SERVICES: groups.setdefault(s['group'], []).append(s)
    body = ''; n = 0
    for g, items in groups.items():
        rows = ''
        for s in items:
            n += 1
            rows += '<div class="tocrow"><span class="tnum">%02d</span><div><h3><a href="/%s/">%s</a></h3><p>%s</p></div></div>' % (n, s['slug'], esc(s['name']), esc(s['blurb']))
        body += '<section class="hubgroup panel"><h2>%s</h2><p class="hubnote">%s</p><div class="toc">%s</div></section>' % (esc(g), esc(hub['note'][g]), rows)
    main = '<section class="sec"><div class="wrap"><div class="stack">%s%s%s</div></div></section>' % (body, callrow(), cta_band('Not sure which service fits? Describe what you see and dispatch will point you to the right one.'))
    ph = pagehead('services', h['h1'], [hub['lead']], crumb)
    sch = graph(business(), website(), webpage('services', h['title'], hub['meta'], 'CollectionPage'), crumbs(abs_c(crumb)),
                {"@type": "ItemList", "itemListElement": [{"@type": "ListItem", "position": i + 1, "url": url(s['slug']), "name": s['name']} for i, s in enumerate(R.SERVICES)]})
    emit('services', page(h['title'], hub['meta'], 'services', sch, ph + main))
    # blog hub
    h = STD['blog']; hub = HUBS['blog']
    crumb = [('Home', '/'), ('Blog', '/blog/')]
    rows = ''
    for i, b in enumerate(R.BLOGS):
        d = load(b['slug']); first = plain(d['intro'][0])
        words = first.split(); ex = ' '.join(words[:28]) + ('...' if len(words) > 28 else '')
        hi = HERO_IMAGES.get(b['slug']); th = ''
        if hi:
            th = '<a class="bthumb" href="/%s/" ><img src="/img/thumb-%s" alt="%s" width="480" height="300" loading="lazy"></a>' % (b['slug'], hi, esc(img_alt(hi)))
        rows += '<div class="blogrow"><span class="tnum">%02d</span><div><h2><a href="/%s/">%s</a></h2><p>%s</p></div>%s</div>' % (i + 1, b['slug'], esc(b['title']), esc(ex), th)
    main = '<section class="sec"><div class="wrap"><div class="stack"><div class="panel"><div class="bloglist">%s</div></div></div></div></section>' % rows
    ph = pagehead('blog', h['h1'], [hub['lead']], crumb)
    sch = graph(business(), website(), webpage('blog', h['title'], hub['meta'], 'CollectionPage'), crumbs(abs_c(crumb)),
                {"@type": "ItemList", "itemListElement": [{"@type": "ListItem", "position": i + 1, "url": url(b['slug']), "name": b['title']} for i, b in enumerate(R.BLOGS)]})
    emit('blog', page(h['title'], hub['meta'], 'blog', sch, ph + main))

def build_404():
    body = ('<section class="err"><div class="wrap"><h1>Page not found</h1><p>That page does not exist or has moved. For a plumbing problem right now, call dispatch.</p>'
            '<p style="margin-top:20px"><a class="btn" href="%s">Call %s</a> <a class="btn btn-choc" href="/">Back to home</a></p></div></section>') % (TEL, R.PHONE_DISPLAY)
    doc = head('Page Not Found | Oakley 24/7 Plumbing', 'The page you wanted is not here. Call Oakley 24/7 Plumbing dispatch at (888) 910-8644 for plumbing help any hour of the day.', '404', [], robots=False)
    doc += '<body>' + header() + '<main id="main">' + body + '</main>' + footer() + '<script src="/main.js" defer></script></body></html>'
    PAGES['__404'] = doc

def write_all():
    # clean generated output (keep fonts/img/icons)
    keep = {'fonts', 'img', 'apple-touch-icon.png', 'favicon.ico', 'favicon-32.png', 'favicon-48.png', 'icon-192.png', 'icon-512.png', 'logo.png', 'logo-light.png', 'og-image.png', 'site.webmanifest'}
    for e in os.listdir(OUT):
        if e in keep: continue
        p = os.path.join(OUT, e)
        shutil.rmtree(p) if os.path.isdir(p) else os.remove(p)
    for slug, doc in PAGES.items():
        if slug == '__404': open(OUT + '/404.html', 'w').write(doc); continue
        d = OUT + ('/' + slug if slug else '')
        os.makedirs(d, exist_ok=True)
        open(d + '/index.html', 'w').write(doc)
    shutil.copy(SRC + '/main.css', OUT + '/main.css'); shutil.copy(SRC + '/main.js', OUT + '/main.js')
    sm = ['<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for s in SITEMAP: sm.append('<url><loc>%s</loc><lastmod>%s</lastmod></url>' % (url(s), TODAY))
    sm.append('</urlset>')
    open(OUT + '/sitemap.xml', 'w').write('\n'.join(sm))
    open(OUT + '/robots.txt', 'w').write('User-agent: *\nAllow: /\n\nSitemap: %s/sitemap.xml\n' % SITE)
    open(OUT + '/_redirects', 'w').write('# No redirects needed. Cloudflare Pages serves slug/index.html at /slug/.\n')
    open(OUT + '/_headers', 'w').write('/*\n  Strict-Transport-Security: max-age=31536000; includeSubDomains\n  X-Content-Type-Options: nosniff\n  Referrer-Policy: strict-origin-when-cross-origin\n  Permissions-Policy: geolocation=(), microphone=(), camera=()\n  X-Frame-Options: SAMEORIGIN\n\n/fonts/*\n  Cache-Control: public, max-age=31536000, immutable\n\n/main.css\n  Cache-Control: public, max-age=3600\n\n/main.js\n  Cache-Control: public, max-age=3600\n')

if __name__ == '__main__':
    missing = []
    for s in SV: 
        (build_service if os.path.exists('%s/%s.json' % (CONT, s)) else missing.append)(s)
    for b in BL:
        (build_blog if os.path.exists('%s/%s.json' % (CONT, b)) else missing.append)(b)
    if os.path.exists(CONT + '/' + LOC['slug'] + '.json'): build_location()
    else: missing.append(LOC['slug'])
    for s in ['about', 'contact', 'service-area', 'privacy', 'terms']:
        (build_standard if os.path.exists('%s/%s.json' % (CONT, s)) else missing.append)(s)
    for hs in HD: (build_hood if os.path.exists('%s/%s.json' % (CONT, hs)) else missing.append)(hs)
    if os.path.exists(CONT + '/home.json'): build_home()
    else: missing.append('home')
    if not missing: build_hubs()
    build_404()
    write_all()
    print('pages built:', len(PAGES), 'missing:', missing)
    print('link errors:', LINKERRS)
