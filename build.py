import json, os, re, html
E=html.escape
def jsonld(ld):
    base=[ORG]+([ld] if isinstance(ld,dict) else (ld or []))
    return ''.join('<script type="application/ld+json">'+json.dumps(x,ensure_ascii=False)+'</script>' for x in base)
OUT = 'site'
# ---- prep: build from data/packages.json (exported from kfGo_Packages_Database) ----
import shutil
if os.path.exists(OUT): shutil.rmtree(OUT)
os.makedirs(OUT+'/data'); shutil.copytree('src/assets', OUT+'/assets')
def _num(s):
    s=str(s or '').replace(',','').strip()
    try: return int(float(s))
    except: return None
PK=[p for p in json.load(open('data/packages.json')) if str(p.get('is_enabled','TRUE')).upper()=='TRUE']
_light=[];_det={}
for p in PK:
    _light.append({"id":p['Package_ID'],"state":p.get('State',''),"city":p['Origin_City'],"name":p['Package_Name'],"type":p['Type'],"dur":p['Duration'],"days":_num(p['Days']),"km":_num(p['Km']),
      "inter":p['Interstate']=='Yes',"oneway":p['One_Way']=='Yes',"seat":_num(p['Shared_Seat_INR']),"from":_num(p['Price_From_INR']),"hl":p['Highlights'],"head":p['Headline']})
    _det.setdefault(p['Origin_City'],{})[p['Package_ID']]={"desc":p['Description'],"itin":p['Itinerary'],"gtk":p['Good_To_Know'],"inc":p['Inclusions'],"exc":p['Exclusions'],"carry":p['What_To_Carry'],
      "prices":{"Hatchback":_num(p['Price_Hatchback_INR']),"Sedan":_num(p['Price_Sedan_INR']),"MPV":_num(p['Price_MPV_INR']),"Premium SUV":_num(p['Price_Premium_SUV_INR']),"Traveller":_num(p['Price_Traveller_INR'])}}
json.dump(_light,open(OUT+'/data/trips.json','w'),ensure_ascii=False,separators=(',',':'))
for c,v in _det.items(): json.dump(v,open(OUT+'/data/city-'+re.sub(r'[^a-z0-9]+','-',c.lower()).strip('-')+'.json','w'),ensure_ascii=False,separators=(',',':'))
open(OUT+'/CNAME','w').write('kfgo.in\n')
NT=len(_light); NC=len(set((t['city'],t['state']) for t in _light)); NS=len(set(t['state'] for t in _light))
WHERE = 'Kerala' if NS==1 else f'{NS} states'
NTR = f'{NT//10*10}+' if NT>=20 else str(NT)

V = json.load(open('src/vehicles.json'))
LEGAL = "KF Travel and Logistics Private Limited"
GST = "32AAMCK6740Q1ZX"
REG = "12/325, Puthuval House, Veli Road, Pallithura, Thiruvananthapuram, Kerala 695586, India"
OFFICE = "Al-Falah Tower, Menamkulam, Kazhakkoottam P.O., Trivandrum, Kerala 695582, India"
ORG={"@context":"https://schema.org","@type":["TravelAgency","LocalBusiness"],"@id":"https://kfgo.in/#org","name":"kfGo Travel & Logistics","legalName":LEGAL,"url":"https://kfgo.in/","logo":"https://kfgo.in/assets/kfgo-logo.png","image":"https://kfgo.in/assets/kfgo-logo.png",
 "telephone":"+91-9633444723","email":"office@kfgo.in","priceRange":"₹₹","taxID":GST,
 "address":{"@type":"PostalAddress","streetAddress":"Al-Falah Tower, Menamkulam, Kazhakkoottam P.O.","addressLocality":"Thiruvananthapuram","addressRegion":"Kerala","postalCode":"695582","addressCountry":"IN"},
 "areaServed":[{"@type":"Country","name":"India"}],
 "contactPoint":[{"@type":"ContactPoint","telephone":"+91-9633444723","contactType":"reservations","availableLanguage":["English","Malayalam"]},{"@type":"ContactPoint","telephone":"+91-9633444790","contactType":"customer service","availableLanguage":["English","Malayalam"]}],
 "sameAs":["https://www.linkedin.com/company/kfgotravel"],"parentOrganization":{"@type":"Organization","name":"KF Group"}}

def head(title, desc, active='', canon='/', ld=None):
    nav = [('/trips','Trips & tours','trips'),('/taxi','Taxi & cabs','taxi'),('/airport','Airport transfers','airport'),('/logistics','Logistics','logistics'),('/partners','Attach your vehicle','partners'),('/contact','Contact','contact')]
    links = ''.join(f'<a href="{h}" class="{"active" if k==active else ""}">{t}</a>' for h,t,k in nav)
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title><meta name="description" content="{desc}"><meta property="og:title" content="{title}"><meta property="og:description" content="{desc}"><meta property="og:image" content="https://kfgo.in/assets/kfgo-logo.png"><meta property="og:type" content="website"><meta property="og:url" content="https://kfgo.in{canon}"><meta property="og:site_name" content="kfGo Travel &amp; Logistics"><meta property="og:locale" content="en_IN"><meta name="twitter:card" content="summary"><link rel="canonical" href="https://kfgo.in{canon}"><meta name="robots" content="index,follow,max-image-preview:large"><meta name="theme-color" content="#0B2A6B">{jsonld(ld)}
<link rel="icon" href="/assets/favicon.png"><link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Anton&family=Baloo+2:wght@600;700;800&family=Figtree:wght@400;600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/style.css"></head><body>
<div class="top"><div class="wrap"><span>Taxi · Tours · Airport transfers · Logistics, across Kerala and India</span><span>Call / WhatsApp <a href="tel:+919633444723">96334 44723</a> · <a href="tel:+919633444790">96334 44790</a></span></div></div>
<header class="site"><div class="wrap"><a class="brand" href="/" style="text-decoration:none"><img src="/assets/kfgo-logo.png" alt="kfGo Travel &amp; Logistics logo"><span>kfGo<small>TRAVEL &amp; LOGISTICS</small></span></a>
<nav class="main">{links}<a class="btn y sm" href="/trips">Book a trip</a></nav><button class="menu-btn" aria-label="Menu">☰</button></div></header>
'''

FOOT = f'''<div class="cta"><div class="wrap"><div><h2>Plan it in one message</h2><div style="font-weight:700;color:#0B1F4D">Call or WhatsApp our booking desk</div></div><div class="nums">96334 44723 · 44790</div><a class="btn n" data-wa="Hi kfGo, I would like to plan a trip.">WhatsApp us</a></div></div>
<footer class="site"><div class="wrap"><div class="cols">
<div><h4>kfGo Travel &amp; Logistics</h4><p>Taxi, tours, airport transfers and goods transport across India, run by {LEGAL}, part of KF Group.</p><p style="margin-top:10px">GSTIN {GST}</p></div>
<div><h4>Travel</h4><ul><li><a href="/trips?type=Shared+day+tour">Shared day tours</a></li><li><a href="/trips?type=Private+trip">Private trips</a></li><li><a href="/airport">Airport transfers</a></li><li><a href="/taxi">Taxi &amp; rate card</a></li></ul></div>
<div><h4>Business</h4><ul><li><a href="/logistics">Logistics &amp; delivery</a></li><li><a href="/partners">Attach your vehicle</a></li><li><a href="/contact">Corporate travel</a></li><li><a href="https://estimate.kfgo.in">Fare estimator</a></li></ul></div>
<div><h4>Contact</h4><p>{REG}</p><p style="margin-top:8px">Office: {OFFICE}</p><p style="margin-top:8px"><a href="tel:+919633444723">+91 96334 44723</a> · <a href="tel:+919633444790">+91 96334 44790</a><br><a href="mailto:office@kfgo.in">office@kfgo.in</a></p></div>
</div><div class="legal"><span>© 2026 {LEGAL}. All rights reserved.</span><span><a href="/refund-policy">Cancellation &amp; refunds</a> · <a href="/terms">Terms</a> · <a href="/privacy-policy">Privacy</a></span></div></div></footer>
<a class="wa-float" data-wa="Hi kfGo, I would like to book.">WhatsApp</a>
<script src="/assets/config.js"></script><script src="https://cdnjs.cloudflare.com/ajax/libs/qrcodejs/1.0.0/qrcode.min.js"></script><script src="https://checkout.razorpay.com/v1/checkout.js" defer></script><script src="/assets/app.js"></script></body></html>'''

def ico(p): return f'<div class="ico"><svg viewBox="0 0 24 24">{p}</svg></div>'
I = {
 'tour':'<path d="M3 20l6-12 4 7 3-4 5 9z"/><circle cx="17" cy="6" r="2"/>',
 'car':'<path d="M5 17h14v-5l-2-5H7l-2 5z"/><circle cx="8" cy="17" r="2"/><circle cx="16" cy="17" r="2"/>',
 'plane':'<path d="M2 16l20-6-3-3-7 3-6-5-2 1 4 6-4 2z"/>',
 'truck':'<path d="M2 7h11v9H2zM13 10h5l3 3v3h-8z"/><circle cx="6" cy="18" r="2"/><circle cx="17" cy="18" r="2"/>',
 'brief':'<rect x="3" y="7" width="18" height="13" rx="2"/><path d="M8 7V5h8v2"/>',
 'key':'<circle cx="8" cy="15" r="4"/><path d="M11 12l9-9M17 6l3 3"/>'}

SITEMAP=[]
def page(path, title, desc, body, active='', ld=None, sm=True, pri='0.6'):
    fn = os.path.join(OUT, path)
    os.makedirs(os.path.dirname(fn) or '.', exist_ok=True)
    canon = '/' if path=='index.html' else '/'+path[:-5]
    open(fn,'w').write(head(title,desc,active,canon,ld)+body+FOOT)
    if sm: SITEMAP.append((canon,pri))

# ---------- home
home = f'''<section class="hero"><div class="wrap grid"><div>
<div class="eyebrow">Travel &amp; logistics · Kerala and across India</div>
<h1>Travel. Deliver. <span>Connect.</span></h1>
<p class="lead">Book shared day tours, private trips, airport transfers and cabs from {NC} cities across {WHERE}, with clear prices and a real team on WhatsApp.</p>
<div class="chips"><span class="chip">Taxi &amp; Cabs</span><span class="chip">Airport Transfers</span><span class="chip">City Tours</span><span class="chip">Corporate Travel</span><span class="chip y">Last-Mile Delivery</span></div>
<div class="btns"><a class="btn y" href="/trips">Browse {NTR} trips</a><a class="btn o" href="/trip/trivandrum-in-a-day">Trivandrum in a Day: ₹999</a></div></div>
<div class="finder"><h3>Find your trip</h3><div class="tabs" id="f-tabs"><button class="on" data-t="Shared day tour">Shared day tour</button><button data-t="Private trip">Private trip</button><button data-t="Airport transfer">Airport transfer</button></div>
<label>Starting from</label><select id="f-city"></select><button class="btn n" id="f-go" style="width:100%;margin-top:16px">Show trips</button>
<p class="note" style="margin-top:12px">Need a cab right now? <a data-wa="Hi kfGo, I need a cab now.">WhatsApp us</a> or call <a href="tel:+919633444723">96334 44723</a>.</p></div></div></section>

<section><div class="wrap"><div class="eyebrow b">What we do</div><h2>One team for <span>every journey</span></h2><p class="sub">From a seat on a day tour to a truck for your goods, booked the same simple way.</p>
<div class="grid3">
<a class="card a" href="/trips?type=Shared+day+tour" style="color:inherit;text-decoration:none">{ico(I['tour'])}<h3>Shared day tours</h3><p>Join a small group for a full day out: temples, beaches, backwaters and hills. Pay per seat.</p><span class="go">See day tours →</span></a>
<a class="card" href="/trips?type=Private+trip" style="color:inherit;text-decoration:none">{ico(I['car'])}<h3>Private trips</h3><p>Your own vehicle and driver for day trips and multi-day tours: Munnar, Wayanad, Ooty, Thekkady and more.</p><span class="go">See private trips →</span></a>
<a class="card r" href="/airport" style="color:inherit;text-decoration:none">{ico(I['plane'])}<h3>Airport transfers</h3><p>Fixed-price pickups and drops for Trivandrum, Kochi, Kozhikode and Kannur airports.</p><span class="go">Book a transfer →</span></a>
<a class="card" href="/taxi" style="color:inherit;text-decoration:none">{ico(I['car'])}<h3>Taxi &amp; cabs</h3><p>Hatchback to 15-seat Traveller by the kilometre. Clear rate card, no surprises.</p><span class="go">See the rate card →</span></a>
<a class="card a" href="/logistics" style="color:inherit;text-decoration:none">{ico(I['truck'])}<h3>Logistics &amp; delivery</h3><p>Mini trucks and cargo vans for shops, businesses and house moves, with driver.</p><span class="go">Request a vehicle →</span></a>
<a class="card r" href="/partners" style="color:inherit;text-decoration:none">{ico(I['key'])}<h3>Attach your vehicle</h3><p>Own a car, van or Traveller? Drive with kfGo and keep 85% of every trip.</p><span class="go">Join as a partner →</span></a>
</div></div></section>

<section class="alt"><div class="wrap"><div class="eyebrow b">Popular right now</div><h2>Book in <span>minutes</span></h2><div class="trips" id="featured"></div>
<div style="margin-top:24px"><a class="btn n" href="/trips">See all trips</a></div></div></section>

<section><div class="wrap"><div class="eyebrow b">How booking works</div><h2>Four simple <span>steps</span></h2><div class="steps">
<div class="step"><h4>Pick a trip</h4><p>Choose a tour, trip, transfer or cab and see the price up front.</p></div>
<div class="step"><h4>Choose date &amp; vehicle</h4><p>Pick your date, seats or vehicle, and pickup point.</p></div>
<div class="step"><h4>Pay securely</h4><p>Pay by UPI with your booking reference. Multi-day trips need only an advance.</p></div>
<div class="step"><h4>Get confirmation</h4><p>Our team confirms on WhatsApp with driver and vehicle details.</p></div></div></div></section>'''
page('index.html','kfGo Travel & Logistics | Kerala tours, taxi, airport transfers & logistics',f'Book shared day tours, private trips, airport transfers, cabs and goods vehicles from {NC} cities across {WHERE}. kfGo Travel & Logistics, KF Travel and Logistics Pvt Ltd.',home)

# ---------- trips
trips = f'''<div class="page-hero"><div class="wrap"><div class="eyebrow">Trips &amp; tours</div><h1>Find your trip</h1><p>Shared day tours, private trips and airport transfers from {NC} cities across {WHERE}. Every price is shown up front.</p></div></div>
<section style="padding-top:20px"><div class="wrap"><div class="filters">
<div><label>State</label><select id="c-state"></select></div><div><label>From</label><select id="c-city"></select></div>
<div><label>Type</label><select id="c-type"><option value="">All types</option><option>Shared day tour</option><option>Private trip</option><option>Airport transfer</option></select></div>
<div><label>Search</label><input id="c-q" placeholder="Munnar, beach, temple…"></div>
<div><label>Sort</label><select id="c-sort"><option value="">Recommended</option><option value="low">Price: low to high</option><option value="high">Price: high to low</option><option value="days">Shortest first</option></select></div></div>
<div class="count" id="c-count"></div><div class="trips" id="trip-list"></div></div></section>'''
page('trips.html','Trips, tours & tour packages | kfGo',f'Browse {NTR} shared day tours, private trips and airport transfers from {NC} cities across {WHERE}.',trips,'trips')

# ---------- checkout
co = '''<div class="page-hero"><div class="wrap"><div class="eyebrow">Checkout</div><h1>Confirm your booking</h1></div></div>
<div class="wrap" id="checkout"><div class="co"><div class="panel">
<form id="co-form"><h3>Your details</h3>
<div class="row2"><div><label>Full name</label><input name="name" required></div><div><label>Mobile / WhatsApp</label><input name="phone" required pattern="[0-9 +]{10,15}" placeholder="+91"></div></div>
<label>Email (for the receipt)</label><input name="email" type="email">
<label>Notes for the team</label><textarea name="notes" rows="3" placeholder="Flight number, child seats, luggage, preferred language…"></textarea>
<label style="display:flex;gap:8px;align-items:flex-start;font-weight:600;color:var(--ink)"><input type="checkbox" required style="width:auto;margin-top:4px">I agree to the <a href="/terms" target="_blank">terms</a> and the <a href="/refund-policy" target="_blank">cancellation &amp; refund policy</a>.</label>
<button class="btn y" style="width:100%;margin-top:16px">Place booking</button></form>
<div id="pay" class="hidden"></div></div>
<aside class="panel" id="sum"></aside></div></div>'''
page('checkout.html','Checkout | kfGo','Confirm your kfGo booking.',co)

# ---------- taxi
rows = ''.join(f"<tr><td><b>{v['Vehicle']}</b></td><td>{v['Seats'] or '–'}</td><td class='r'>₹{v['First_80km_Rate']}/km</td><td>₹{v['After_80km_Rate']}/km</td><td>₹{v['Waiting_Per_Hr']}/hr</td><td>₹{v['Bata_Per_Day']}/day</td></tr>" for v in V if v['Segment']=='Travel')
taxi = f'''<div class="page-hero"><div class="wrap"><div class="eyebrow">Taxi &amp; cabs</div><h1>Clear rates. Any distance.</h1><p>City rides, outstation trips and full-day hire with a professional driver, priced by the kilometre.</p></div></div>
<section><div class="wrap"><h2>Rate <span>card</span></h2><p class="sub">Each trip day: the first 80 km at the first rate, the rest at the second rate, plus driver allowance (bata). Tolls and parking are extra.</p>
<div class="tblwrap"><table class="rates"><tr><th>Vehicle</th><th>Seats</th><th>First 80 km</th><th>After 80 km</th><th>Waiting</th><th>Driver bata</th></tr>{rows}</table></div>
<p class="note">Night stay on multi-day hire: ₹500 per night. One-way trips are charged for the return distance (×1.5 for cars, ×1.7 for MPV, SUV and Traveller). Waiting: first 30 min free. Get an instant estimate at <a href="https://estimate.kfgo.in">estimate.kfgo.in</a>.</p></div></section>
<section class="alt"><div class="wrap"><h2>Book a <span>cab</span></h2><form class="panel" data-request="Cab booking request" data-kind="taxi" style="max-width:760px">
<div class="row2"><div><label>Pickup</label><input name="Pickup" required></div><div><label>Drop / destination</label><input name="Drop" required></div></div>
<div class="row2"><div><label>Date</label><input name="Date" type="date" required></div><div><label>Time</label><input name="Time" type="time" required></div></div>
<div class="row2"><div><label>Vehicle</label><select name="Vehicle">{''.join(f"<option>{v['Vehicle']}</option>" for v in V if v['Segment']=='Travel')}</select></div><div><label>Trip</label><select name="Trip"><option>One way</option><option>Round trip</option><option>Full-day hire</option><option>Multi-day</option></select></div></div>
<div class="row2"><div><label>Your name</label><input name="Name" required></div><div><label>Mobile</label><input name="Mobile" required></div></div>
<button class="btn y" style="margin-top:16px">Send request on WhatsApp</button><p class="note">We reply with the fare and confirm the vehicle. Payment by UPI after confirmation.</p></form></div></section>'''
page('taxi.html','Taxi & cab rate card | kfGo','kfGo taxi rates per km for Hatchback, Sedan, MPV, Premium SUV and Traveller, with driver. Book on WhatsApp.',taxi,'taxi')

# ---------- airport
air = '''<div class="page-hero"><div class="wrap"><div class="eyebrow">Airport transfers</div><h1>On time, every flight.</h1><p>Fixed-price pickups and drops for Kerala's airports. We track your flight, and wait 30 minutes free.</p></div></div>
<section style="padding-top:20px"><div class="wrap"><div class="count" id="c-count"></div><div class="trips" id="trip-list"></div>
<div class="hidden"><select id="c-city"></select><select id="c-type"><option>Airport transfer</option></select><input id="c-q"><select id="c-sort"><option value=""></option></select></div></div></section>'''
page('airport.html','Airport transfers in Kerala | kfGo','Fixed-price airport pickups and drops for Trivandrum, Kochi, Kozhikode and Kannur airports.',air,'airport')

# ---------- logistics
lrows = ''.join(f"<tr><td><b>{v['Vehicle']}</b></td><td class='r'>₹{v['First_80km_Rate']}/km</td><td>₹{v['Bata_Per_Day']}/day</td></tr>" for v in V if v['Segment']=='Logistics')
logi = f'''<div class="page-hero"><div class="wrap"><div class="eyebrow">kfGo Logistics</div><h1>Move goods, not worries.</h1><p>Mini trucks and cargo vans with driver for shops, distributors, businesses and house moves: within the city, across districts and between states.</p></div></div>
<section><div class="wrap"><div class="grid3">
<div class="card">{ico(I['truck'])}<h3>Last-mile delivery</h3><p>Regular and same-day delivery runs for shops, e-commerce sellers and distributors.</p></div>
<div class="card a">{ico(I['brief'])}<h3>Business contracts</h3><p>Fixed-rate monthly vehicles for your routes, with proof of delivery.</p></div>
<div class="card r">{ico(I['car'])}<h3>One-off moves</h3><p>Doorstep pickup and drop for a house shift, an event or a single load.</p></div></div>
<h2 style="margin-top:50px">Goods vehicle <span>rates</span></h2><div class="tblwrap"><table class="rates"><tr><th>Vehicle</th><th>Rate</th><th>Driver bata</th></tr>{lrows}</table></div><p class="note">Loading and unloading labour, tolls and parking are extra. Monthly contract rates on request.</p></div></section>
<section class="alt"><div class="wrap"><h2>Request a <span>vehicle</span></h2><form class="panel" data-request="Logistics request" data-kind="logistics" style="max-width:760px">
<div class="row2"><div><label>Pickup location</label><input name="Pickup" required></div><div><label>Delivery location</label><input name="Delivery" required></div></div>
<div class="row2"><div><label>Date</label><input name="Date" type="date" required></div><div><label>Vehicle</label><select name="Vehicle">{''.join(f"<option>{v['Vehicle']}</option>" for v in V if v['Segment']=='Logistics')}<option>Not sure</option></select></div></div>
<label>What are you moving?</label><input name="Goods" placeholder="e.g. 40 cartons, household items, furniture">
<div class="row2"><div><label>Your name / business</label><input name="Name" required></div><div><label>Mobile</label><input name="Mobile" required></div></div>
<button class="btn y" style="margin-top:16px">Send request on WhatsApp</button></form></div></section>'''
page('logistics.html','Logistics & goods transport | kfGo','Mini trucks and cargo vans with driver for last-mile delivery, business routes and house moves from Kerala.',logi,'logistics')

# ---------- partners
part = f'''<div class="page-hero"><div class="wrap"><div class="eyebrow">Vehicle partner programme</div><h1>Your vehicle. Our trips.</h1><p>Attach your car, MPV, SUV, Traveller or goods vehicle to kfGo. We bring the bookings; you keep 85% of every trip.</p></div></div>
<section><div class="wrap"><div class="grid4">
<div class="card a"><h3>85% to you</h3><p>Your share is 85% of the total trip revenue. kfGo keeps 15% commission per trip.</p></div>
<div class="card"><h3>Fast settlement</h3><p>Paid within two weeks at most, mostly the next working day.</p></div>
<div class="card r"><h3>You choose</h3><p>Accept or decline any booking. Tolls and parking are charged to the customer.</p></div>
<div class="card"><h3>No driver? No problem</h3><p>Owners without a driver can still join: we arrange a driver on separate terms.</p></div></div>
<div class="box" style="margin-top:28px">To join: a refundable ₹500 deposit (returned in full when you exit) and ₹200 for the agreement stamp paper. You stay fully responsible for your vehicle; kfGo assigns trips.</div></div></section>
<section class="alt"><div class="wrap"><h2>Apply in <span>2 minutes</span></h2><form class="panel" data-request="Vehicle partner application" data-kind="partner" style="max-width:760px">
<div class="row2"><div><label>Owner name</label><input name="Owner" required></div><div><label>Mobile</label><input name="Mobile" required></div></div>
<div class="row2"><div><label>Vehicle type</label><select name="Vehicle"><option>Hatchback</option><option>Sedan</option><option>MPV</option><option>SUV</option><option>Traveller / mini bus</option><option>Mini truck</option><option>Cargo van</option></select></div><div><label>Model &amp; year</label><input name="Model"></div></div>
<div class="row2"><div><label>Board</label><select name="Board"><option>Yellow (taxi)</option><option>White (private)</option></select></div><div><label>Your district</label><input name="District" required></div></div>
<label>Do you drive it yourself?</label><select name="Driver"><option>Yes, I drive</option><option>I have a driver</option><option>I need a driver</option></select>
<button class="btn y" style="margin-top:16px">Send application on WhatsApp</button><p class="note">We will ask for RC, insurance, permit, licence and bank details on WhatsApp.</p></form></div></section>'''
page('partners.html','Attach your vehicle with kfGo | 85% partner share','Attach your car, van or Traveller to kfGo. Keep 85% of every trip, fast settlement, accept or decline bookings.',part,'partners')

# ---------- contact
con = f'''<div class="page-hero"><div class="wrap"><div class="eyebrow">Contact &amp; corporate travel</div><h1>Talk to kfGo</h1><p>Bookings, corporate travel, events and partnerships.</p></div></div>
<section><div class="wrap"><div class="grid3">
<div class="card"><h3>Call / WhatsApp</h3><p><a href="tel:+919633444723">+91 96334 44723</a><br><a href="tel:+919633444790">+91 96334 44790</a></p><a class="btn w sm go" data-wa="Hi kfGo">WhatsApp us</a></div>
<div class="card a"><h3>Email</h3><p><a href="mailto:office@kfgo.in">office@kfgo.in</a></p></div>
<div class="card r"><h3>Office</h3><p>{OFFICE}</p><p style="margin-top:8px"><b>Registered office:</b> {REG}</p></div></div>
<h2 style="margin-top:50px">Corporate <span>travel</span></h2><form class="panel" data-request="Corporate travel enquiry" data-kind="corporate" style="max-width:760px">
<div class="row2"><div><label>Company</label><input name="Company" required></div><div><label>Contact person</label><input name="Contact" required></div></div>
<div class="row2"><div><label>Mobile</label><input name="Mobile" required></div><div><label>Email</label><input name="Email" type="email"></div></div>
<label>What do you need?</label><textarea name="Requirement" rows="3" placeholder="Employee transport, airport runs for guests, event vehicles, monthly cab…"></textarea>
<button class="btn y" style="margin-top:16px">Send enquiry on WhatsApp</button></form></div></section>'''
page('contact.html','Contact kfGo | Corporate travel','Contact kfGo Travel & Logistics for bookings, corporate travel and partnerships.',con,'contact')

# ---------- legal
def legal(path,title,body):
    page(path,title+' | kfGo',title+' of '+LEGAL+'.',f'<div class="page-hero"><div class="wrap"><div class="eyebrow">kfGo · {LEGAL}</div><h1>{title}</h1><p>Last updated: 14 November 2026</p></div></div><article class="legal">{body}</article>')
refund = open('src/content/refund.html').read()
legal('refund-policy.html','Cancellation & refund policy',refund)
legal('terms.html','Terms of use & booking', open('src/content/terms.html').read())
legal('privacy-policy.html','Privacy policy', open('src/content/privacy.html').read())
exec(open('pages.py').read())
for f in ['site/checkout.html']:
    h=open(f).read().replace('content="index,follow,max-image-preview:large"','content="noindex,follow"'); open(f,'w').write(h)
print('built')
