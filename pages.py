# executed at the end of build.py (shares its globals)
import urllib.parse, datetime
T=json.load(open('site/data/trips.json'))
D={}
for f in os.listdir('site/data'):
    if f.startswith('city-'): D.update(json.load(open('site/data/'+f)))
STATES=sorted(set(t.get('state') or '' for t in T)-{''})
def slug(x): return re.sub(r'[^a-z0-9]+','-',x.lower()).strip('-')
seen=set()
for t in T:
    sl=slug(t['name']) if slug(t['city']) in slug(t['name']) else slug(t['name']+'-from-'+t['city'])
    if sl in seen: sl=sl+'-'+slug(t['id'])
    seen.add(sl); t['url']='/trip/'+sl
json.dump(T,open('site/data/trips.json','w'),ensure_ascii=False,separators=(',',':'))
def inr_in(n):
    s=str(n)
    if len(s)<=3: return '₹'+s
    h=s[:-3]; parts=[]
    while len(h)>2: parts.insert(0,h[-2:]); h=h[:-2]
    if h: parts.insert(0,h)
    return '₹'+','.join(parts)+','+s[-3:]
TT={'Shared day tour':'','Airport transfer':'t','Private trip':'p'}
def card(t):
    price = (f'<div class="price">{inr_in(t["seat"])}<small>per seat</small></div>' if t['type']=='Shared day tour' and t['seat']
             else f'<div class="price">{inr_in(t["from"])}<small>from, per vehicle</small></div>')
    meta=E(t['dur'])+(f' · about {t["km"]} km' if t['km'] else '')+(' · interstate' if t['inter'] else '')
    return (f'<a class="trip" href="{t["url"]}" style="color:inherit;text-decoration:none"><div class="hd"><span class="tag {TT[t["type"]]}">{E(t["type"])}</span>'
            f'<h3>{E(t["name"])}</h3><div class="city">From {E(t["city"])}</div></div><div class="bd"><div class="meta">{meta}</div>'
            f'<div class="hl">{E(t["hl"])}</div><div class="ft">{price}<span class="btn n sm">View &amp; book</span></div></div></a>')
def bl(x,semi=True):
    parts=re.split(r'\n|; ',x or '') if semi else (x or '').split('\n')
    return ''.join(f'<li>{E(y.strip())}</li>' for y in parts if y.strip())
def itin_html(s):
    out=''
    for l in (s or '').split('\n'):
        if not l.strip(): continue
        m=l.split(': ')
        out+=f'<li><b>{E(m[0])}</b>'+(f'<br>{E(": ".join(m[1:]))}' if len(m)>1 else '')+'</li>'
    return out
CITIES=sorted(set((t.get('state') or '',t['city']) for t in T))
_cn={}
for st,c in CITIES: _cn.setdefault(c,[]).append(st)
def cslug(c,st=''): return slug(c) if len(_cn.get(c,[]))<=1 else slug(c+'-'+st)
for t in T: t['cpage']='/from/'+cslug(t['city'],t.get('state',''))
SEP=' › '
for t in T:
    d=D.get(t['id'],{}); shared=t['type']=='Shared day tour' and t['seat']; multi=(t['days'] or 1)>1
    itin=itin_html(d.get('itin'))
    veh=[(k,v) for k,v in (d.get('prices') or {}).items() if v]
    if t['city']=='Trivandrum' and t['type']=='Shared day tour': pk=['Trivandrum Central','East Fort','Trivandrum Airport']
    elif t['type']=='Shared day tour': pk=[t['city']+' town (pickup point confirmed on WhatsApp)']
    else: pk=None
    if shared:
        buy='<label>Seats</label><select id="b-qty">'+''.join(f'<option>{n}</option>' for n in range(1,11))+f'</select><div class="note">{inr_in(t["seat"])} per seat</div>'
    else:
        buy='<label>Choose your vehicle</label>'+''.join(
            f'<label class="vopt {"on" if i==0 else ""}"><input type="radio" name="veh" value="{E(k)}" data-p="{v}" {"checked" if i==0 else ""}><span>{E(k)}</span><b>{inr_in(v)}</b></label>'
            for i,(k,v) in enumerate(veh))
        buy+='<div class="note">Price per vehicle for the whole trip, with driver, fuel and driver allowance. Tolls and parking are extra.'+(' Stay is booked by you.' if multi else '')+'</div>'
    if pk: pick='<label>Pickup point</label><select id="b-pick">'+''.join(f'<option>{E(x)}</option>' for x in pk)+'</select>'
    else: pick=f'<label>Pickup location</label><input id="b-pick" placeholder="Your address or landmark in {E(t["city"])}">'
    wq='https://wa.me/919633444723?text='+urllib.parse.quote(f'Hi kfGo, I have a question about {t["name"]} from {t["city"]} ({t["id"]}).')
    rel=[x for x in T if x['cpage']==t['cpage'] and x['id']!=t['id'] and x['type']==t['type']][:3]
    crumbs=f'<a href="/" style="color:#BFD0F5">Home</a>{SEP}'+(f'<a href="/state/{slug(t["state"])}" style="color:#BFD0F5">{E(t["state"])}</a>{SEP}' if t.get('state') else '')+f'<a href="{t["cpage"]}" style="color:#BFD0F5">{E(t["city"])}</a>{SEP}{E(t["name"])}'
    meta=f'<span>🕒 {E(t["dur"])}</span>'+(f'<span>🛣️ about {t["km"]} km</span>' if t['km'] else '')+('<span>🗺️ Interstate</span>' if t['inter'] else '')+('<span>➡️ One way</span>' if t['oneway'] else '')
    parts=[f'<p style="font-size:18px">{E(d.get("desc") or t["head"])}</p>']
    if t['hl']: parts.append(f'<div class="box"><b>Highlights:</b> {E(t["hl"])}</div>')
    if itin: parts.append(f'<h2 style="font-size:28px;margin-top:26px">Itinerary</h2><ul class="itin">{itin}</ul>')
    if d.get('gtk'): parts.append(f'<h3>Good to know</h3><ul class="gtk">{bl(d["gtk"],False)}</ul>')
    if d.get('inc'): parts.append(f'<h3>Included</h3><ul class="lst">{bl(d["inc"])}</ul>')
    if d.get('exc'): parts.append(f'<h3>Not included</h3><ul class="lst">{bl(d["exc"])}</ul>')
    if d.get('carry'): parts.append(f'<h3>What to carry</h3><ul class="lst">{bl(d["carry"])}</ul>')
    parts.append('<p class="note" style="margin-top:24px">Cancellations follow our <a href="/refund-policy">cancellation &amp; refund policy</a>.</p>')
    if rel: parts.append(f'<h3>More from {E(t["city"])}</h3><div class="trips" style="grid-template-columns:1fr">'+''.join(card(x) for x in rel)+'</div>')
    body=(f'<div class="dhero"><div class="wrap"><nav aria-label="Breadcrumb" style="color:#BFD0F5;font-size:14px">{crumbs}</nav>'
          f'<div class="eyebrow" style="margin-top:14px">{E(t["type"])} · from {E(t["city"])}</div><h1>{E(t["name"])}</h1><div class="meta">{meta}</div></div></div>'
          f'<div class="wrap dgrid"><div>{"".join(parts)}</div>'
          f'<aside><div class="buy"><h3>Book this trip</h3><label>Travel date</label><input type="date" id="b-date">{buy}{pick}'
          f'<div class="total"><span>Total</span><b id="b-total"></b></div>'
          +('<div class="note">Multi-day trip: pay an advance to confirm; the balance is paid before the trip starts.</div>' if multi else '')+
          f'<button class="btn y" style="width:100%;margin-top:14px" id="b-go">Continue to checkout</button>'
          f'<a class="btn w" style="width:100%;margin-top:8px" target="_blank" rel="noopener" href="{wq}">Ask on WhatsApp</a></div></aside></div>'
          f'<script type="application/json" id="trip-data">{json.dumps({k:t[k] for k in ["id","name","city","type","seat","days"]},ensure_ascii=False)}</script>')
    price=t['seat'] if shared else t['from']
    hls=[h.strip() for h in (t['hl'] or '').split(',') if h.strip()]
    ld=[{"@context":"https://schema.org","@type":"TouristTrip","name":t['name']+' from '+t['city'],"description":d.get('desc') or t['head'],"touristType":t['type'],"url":"https://kfgo.in"+t['url'],
         "provider":{"@id":"https://kfgo.in/#org"},
         "itinerary":{"@type":"ItemList","itemListElement":[{"@type":"ListItem","position":i+1,"name":x} for i,x in enumerate(hls)]},
         "offers":{"@type":"Offer","price":price,"priceCurrency":"INR","availability":"https://schema.org/InStock","url":"https://kfgo.in"+t['url'],"seller":{"@id":"https://kfgo.in/#org"}}},
        {"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
          {"@type":"ListItem","position":1,"name":"Home","item":"https://kfgo.in/"},
          {"@type":"ListItem","position":2,"name":"Trips from "+t['city'],"item":"https://kfgo.in"+t['cpage']},
          {"@type":"ListItem","position":3,"name":t['name']}]}]
    kind={'Shared day tour':'shared day tour','Private trip':'private trip','Airport transfer':'airport transfer'}[t['type']]
    nm=t['name'] if t['city'].lower() in t['name'].lower() else t['name']+' from '+t['city']
    title=f"{nm} | {kind} {inr_in(price)}{' per seat' if shared else ''} | kfGo"
    desc=(f"Book {t['name']} from {t['city']}, Kerala. {t['dur']}. "+(f"Highlights: {t['hl']}. " if t['hl'] else '')
          +(f"Shared seat {inr_in(price)}." if shared else f"Private vehicle with driver from {inr_in(price)}.")+" Book online with kfGo.")
    page('trip/'+t['url'].split('/')[-1]+'.html',E(title),E(desc[:300]),body,'trips',ld,pri='0.7')

for st,c in CITIES:
    ct=[t for t in T if t['city']==c and (t.get('state') or '')==st]
    secs=''
    for ty,lbl in [('Shared day tour','Shared day tours'),('Private trip','Private trips'),('Airport transfer','Airport transfers')]:
        g=[t for t in ct if t['type']==ty]
        if g: secs+=f'<h2 style="margin-top:44px">{lbl} <span>from {E(c)}</span></h2><div class="trips">'+''.join(card(t) for t in g)+'</div>'
    seat=[t['seat'] for t in ct if t['seat']]; frm=[t['from'] for t in ct if t['from']]
    bits=[]
    if seat: bits.append(f"shared day tours from {inr_in(min(seat))} per seat")
    if frm: bits.append(f"private trips and transfers from {inr_in(min(frm))} per vehicle")
    lead=f"{len(ct)} trips from {c}: "+', '.join(bits)+". Taxi and cab hire by the kilometre, with a professional driver."
    crumbs=f'<a href="/" style="color:#BFD0F5">Home</a>{SEP}'+(f'<a href="/state/{slug(st)}" style="color:#BFD0F5">{E(st)}</a>{SEP}' if st else '')+E(c)
    body=(f'<div class="page-hero"><div class="wrap"><nav style="color:#BFD0F5;font-size:14px">{crumbs}</nav><div class="eyebrow" style="margin-top:12px">kfGo in {E(c)}</div>'
          f'<h1>Tours, trips &amp; taxi from {E(c)}</h1><p>{E(lead)}</p><div class="btns"><a class="btn y" href="/taxi">Book a cab in {E(c)}</a>'
          f'<a class="btn o" data-wa="Hi kfGo, I need a trip from {E(c)}.">WhatsApp us</a></div></div></div>'
          f'<section style="padding-top:10px"><div class="wrap">{secs}<div class="box" style="margin-top:40px"><b>Taxi in {E(c)}:</b> hatchback ₹23/km, sedan ₹25/km, MPV ₹32/km, Premium SUV ₹48/km and 15-seat Traveller ₹75/km for the first 80 km each day. See the full <a href="/taxi">rate card</a>.</div></div></section>')
    ld={"@context":"https://schema.org","@type":"ItemList","name":f"Trips from {c}","itemListElement":[{"@type":"ListItem","position":i+1,"url":"https://kfgo.in"+t['url'],"name":t['name']} for i,t in enumerate(ct)]}
    page(f'from/{cslug(c,st)}.html',E(f'{c} tour packages, day tours & taxi{(", "+st) if st else ""} | kfGo'),E(lead[:300]),body,'trips',ld,pri='0.8')

for st in STATES:
    cs=[(c,len([t for t in T if t['city']==c and t.get('state')==st])) for s2,c in CITIES if s2==st]
    n=sum(x[1] for x in cs)
    grid=''.join(f'<a class="card" href="/from/{cslug(c,st)}" style="color:inherit;text-decoration:none"><h3>{E(c)}</h3><p>{k} trips: day tours, private trips and transfers from {E(c)}.</p><span class="go">See trips →</span></a>' for c,k in cs)
    body=(f'<div class="page-hero"><div class="wrap"><nav style="color:#BFD0F5;font-size:14px"><a href="/" style="color:#BFD0F5">Home</a>{SEP}{E(st)}</nav><div class="eyebrow" style="margin-top:12px">kfGo in {E(st)}</div>'
          f'<h1>{E(st)} tours, trips &amp; taxi</h1><p>{n} trips from {len(cs)} cities in {E(st)}, with clear prices and a team on WhatsApp.</p></div></div>'
          f'<section style="padding-top:20px"><div class="wrap"><div class="grid4">{grid}</div></div></section>')
    page(f'state/{slug(st)}.html',E(f'{st} tour packages, day tours & taxi | kfGo'),E(f'{n} trips from {len(cs)} cities in {st}: shared day tours, private trips, airport transfers and taxi with kfGo.'),body,'trips',
         {"@context":"https://schema.org","@type":"ItemList","name":f"Cities in {st}","itemListElement":[{"@type":"ListItem","position":i+1,"url":"https://kfgo.in/from/"+cslug(c,st),"name":c} for i,(c,k) in enumerate(cs)]},pri='0.8')
tp=open('site/trips.html').read()
tp=tp.replace('<div class="trips" id="trip-list"></div>','<div class="trips" id="trip-list">'+''.join(card(t) for t in T)+'</div><div class="box" style="margin-top:30px"><b>Browse by place:</b><br>'+'<br>'.join(f'<a href="/state/{slug(st)}"><b>{E(st)}</b></a>: '+' · '.join(f'<a href="/from/{cslug(c,st)}">{E(c)}</a>' for s2,c in CITIES if s2==st) for st in STATES)+'</div>')
open('site/trips.html','w').write(tp)
R=('<!doctype html><meta charset="utf-8"><meta name="robots" content="noindex"><title>kfGo</title><script>fetch("/data/trips.json").then(r=>r.json()).then(a=>{const id=new URLSearchParams(location.search).get("id");const t=a.find(x=>x.id===id);location.replace(t?t.url:"/trips")})</script>')
open('site/trip/index.html','w').write(R); open('site/trip.html','w').write(R)
SITEMAP[:]=[x for x in SITEMAP if x[0] not in ('/trip','/checkout')]
today=datetime.date.today().isoformat()
open('site/sitemap.xml','w').write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+''.join(f'<url><loc>https://kfgo.in{u}</loc><lastmod>{today}</lastmod><priority>{"1.0" if u=="/" else p}</priority></url>\n' for u,p in SITEMAP)+'</urlset>\n')
open('site/robots.txt','w').write('User-agent: *\nAllow: /\nDisallow: /checkout\n\nSitemap: https://kfgo.in/sitemap.xml\n')
print('pages', len(SITEMAP))
