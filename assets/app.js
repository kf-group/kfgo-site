(function(){
const C = window.KFGO;
const $ = s => document.querySelector(s);
const $$ = s => [...document.querySelectorAll(s)];
const inr = n => n==null ? '' : '₹' + Number(n).toLocaleString('en-IN');
const esc = s => String(s??'').replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const wa = (num, text) => 'https://wa.me/' + num + '?text=' + encodeURIComponent(text);
const qs = new URLSearchParams(location.search);
const TYPE_LABEL = {'Shared day tour':'Shared day tour','Private trip':'Private trip','Airport transfer':'Airport transfer'};
const typeTag = t => t==='Shared day tour' ? '' : (t==='Airport transfer' ? 't' : 'p');
let TRIPS = null;
async function trips(){ if(!TRIPS){ TRIPS = await (await fetch('/data/trips.json')).json(); } return TRIPS; }
async function detail(city,id){ const d = await (await fetch('/data/city-'+city.toLowerCase()+'.json')).json(); return d[id]; }

// mobile menu
const mb = $('.menu-btn'); if(mb) mb.onclick = () => $('nav.main').classList.toggle('open');
// whatsapp links
$$('[data-wa]').forEach(a => { a.href = wa(C.whatsapp.orders, a.dataset.wa || 'Hi kfGo, I would like to book a trip.'); a.target='_blank'; a.rel='noopener'; });

function card(t){
  const price = t.type==='Shared day tour' && t.seat ? `<div class="price">${inr(t.seat)}<small>per seat</small></div>` : `<div class="price">${inr(t.from)}<small>from, per vehicle</small></div>`;
  return `<a class="trip" href="/trip?id=${encodeURIComponent(t.id)}" style="color:inherit;text-decoration:none">
   <div class="hd"><span class="tag ${typeTag(t.type)}">${esc(t.type)}</span><h3>${esc(t.name)}</h3><div class="city">From ${esc(t.city)}</div></div>
   <div class="bd"><div class="meta">${esc(t.dur)}${t.km?' · about '+t.km+' km':''}${t.inter?' · interstate':''}</div>
   <div class="hl">${esc(t.hl)}</div>
   <div class="ft">${price}<span class="btn n sm">View & book</span></div></div></a>`;
}

/* ---------- home: featured + finder ---------- */
async function home(){
  const box = $('#featured'); if(!box) return;
  const all = await trips();
  const pick = ['TVM_CITY','TVM_COASTAL'];
  let f = all.filter(t=>pick.includes(t.id));
  const more = all.filter(t=>t.type==='Private trip' && t.days>1).slice(0,2);
  const at = all.filter(t=>t.type==='Airport transfer').slice(0,2);
  f = f.concat(more, at).slice(0,6);
  box.innerHTML = f.map(card).join('');
  const cities=[...new Set(all.map(t=>t.city))].sort();
  const sel=$('#f-city'); if(sel){ sel.innerHTML = cities.map(c=>`<option ${c==='Trivandrum'?'selected':''}>${c}</option>`).join(''); }
  let ft='Shared day tour';
  $$('#f-tabs button').forEach(b=>b.onclick=()=>{ $$('#f-tabs button').forEach(x=>x.classList.remove('on')); b.classList.add('on'); ft=b.dataset.t; });
  const go=$('#f-go'); if(go) go.onclick=()=>{ location.href='/trips?city='+encodeURIComponent(sel.value)+'&type='+encodeURIComponent(ft); };
}

/* ---------- catalogue ---------- */
async function catalogue(){
  const list = $('#trip-list'); if(!list) return;
  const all = await trips();
  const cities=[...new Set(all.map(t=>t.city))].sort();
  $('#c-city').innerHTML = '<option value="">All cities</option>' + cities.map(c=>`<option>${c}</option>`).join('');
  if(qs.get('city')) $('#c-city').value = qs.get('city');
  if(qs.get('type')) $('#c-type').value = qs.get('type');
  if(qs.get('q')) $('#c-q').value = qs.get('q');
  const run = () => {
    const c=$('#c-city').value, ty=$('#c-type').value, q=$('#c-q').value.trim().toLowerCase(), so=$('#c-sort').value;
    let r = all.filter(t => (!c||t.city===c) && (!ty||t.type===ty) && (!q || (t.name+' '+t.hl+' '+t.city).toLowerCase().includes(q)));
    const p = t => t.type==='Shared day tour' && t.seat ? t.seat : (t.from||0);
    if(so==='low') r.sort((a,b)=>p(a)-p(b)); else if(so==='high') r.sort((a,b)=>p(b)-p(a)); else if(so==='days') r.sort((a,b)=>(a.days||0)-(b.days||0));
    $('#c-count').textContent = r.length + ' trip' + (r.length===1?'':'s');
    list.innerHTML = r.map(card).join('') || '<p>No trips match. Try another city or type, or message us on WhatsApp for a custom trip.</p>';
    const u = new URLSearchParams(); if(c)u.set('city',c); if(ty)u.set('type',ty); if(q)u.set('q',q);
    history.replaceState(null,'','?'+u.toString());
  };
  ['#c-city','#c-type','#c-sort'].forEach(s=>$(s).onchange=run); $('#c-q').oninput=run; run();
}

/* ---------- trip detail ---------- */
function pickups(t){
  if(t.city==='Trivandrum' && t.type==='Shared day tour') return ['Trivandrum Central','East Fort','Trivandrum Airport'];
  if(t.type==='Shared day tour') return [t.city+' town (pickup point confirmed on WhatsApp)'];
  return null;
}
async function trip(){
  const root = $('#trip'); if(!root) return;
  const id = qs.get('id'); const all = await trips(); const t = all.find(x=>x.id===id);
  if(!t){ root.innerHTML='<div class="wrap" style="padding:60px 18px"><h2>Trip not found</h2><p><a href="/trips">See all trips</a></p></div>'; return; }
  document.title = t.name + ' from ' + t.city + ' | kfGo';
  const d = await detail(t.city, t.id) || {};
  const itin = (d.itin||'').split('\n').filter(Boolean).map(l=>{ const m=l.split(': '); return `<li><b>${esc(m[0])}</b>${m.length>1?'<br>'+esc(m.slice(1).join(': ')):''}</li>`; }).join('');
  const bullets = (s,semi=true) => (s||'').split(semi?/\n|; /:/\n/).map(x=>x.trim()).filter(Boolean).map(x=>`<li>${esc(x)}</li>`).join('');
  const shared = t.type==='Shared day tour' && t.seat;
  const multi = (t.days||1) > 1;
  const vehicles = Object.entries(d.prices||{}).filter(([k,v])=>v);
  const pk = pickups(t);
  const today = new Date(Date.now()+86400000).toISOString().slice(0,10);
  root.innerHTML = `
  <div class="dhero"><div class="wrap"><a href="/trips?city=${encodeURIComponent(t.city)}" style="color:#BFD0F5">← All trips from ${esc(t.city)}</a>
   <div class="eyebrow" style="margin-top:14px">${esc(t.type)} · from ${esc(t.city)}</div><h1>${esc(t.name)}</h1>
   <div class="meta"><span>🕒 ${esc(t.dur)}</span>${t.km?`<span>🛣️ about ${t.km} km</span>`:''}${t.inter?'<span>🗺️ Interstate</span>':''}${t.oneway?'<span>➡️ One way</span>':''}</div></div></div>
  <div class="wrap dgrid"><div>
   <p style="font-size:18px">${esc(d.desc||t.head)}</p>
   ${t.hl?`<div class="box"><b>Highlights:</b> ${esc(t.hl)}</div>`:''}
   ${itin?`<h3>Itinerary</h3><ul class="itin">${itin}</ul>`:''}
   ${d.gtk?`<h3>Good to know</h3><ul class="gtk">${bullets(d.gtk,false)}</ul>`:''}
   ${d.inc?`<h3>Included</h3><ul class="lst">${bullets(d.inc)}</ul>`:''}
   ${d.exc?`<h3>Not included</h3><ul class="lst">${bullets(d.exc)}</ul>`:''}
   ${d.carry?`<h3>What to carry</h3><ul class="lst">${bullets(d.carry)}</ul>`:''}
   <p class="note" style="margin-top:24px">Cancellations follow our <a href="/refund-policy">cancellation & refund policy</a>.</p>
  </div>
  <aside><div class="buy">
   <h3>Book this trip</h3>
   <label>Travel date</label><input type="date" id="b-date" min="${today}">
   ${shared ? `<label>Seats</label><select id="b-qty">${[1,2,3,4,5,6,7,8,9,10].map(n=>`<option>${n}</option>`).join('')}</select>
      <div class="note">${inr(t.seat)} per seat</div>`
    : `<label>Choose your vehicle</label>${vehicles.map(([k,v],i)=>`<label class="vopt ${i===0?'on':''}"><input type="radio" name="veh" value="${esc(k)}" data-p="${v}" ${i===0?'checked':''}><span>${esc(k)}</span><b>${inr(v)}</b></label>`).join('')}
      <div class="note">Price per vehicle for the whole trip, with driver, fuel and driver allowance. Tolls and parking are extra.${multi?' Stay is booked by you.':''}</div>`}
   ${pk?`<label>Pickup point</label><select id="b-pick">${pk.map(p=>`<option>${esc(p)}</option>`).join('')}</select>`:`<label>Pickup location</label><input id="b-pick" placeholder="Your address or landmark in ${esc(t.city)}">`}
   <div class="total"><span>Total</span><b id="b-total"></b></div>
   ${multi?'<div class="note">Multi-day trip: pay an advance to confirm; the balance is paid before the trip starts.</div>':''}
   <button class="btn y" style="width:100%;margin-top:14px" id="b-go">Continue to checkout</button>
   <a class="btn w" style="width:100%;margin-top:8px" target="_blank" rel="noopener" href="${wa(C.whatsapp.orders,'Hi kfGo, I have a question about '+t.name+' from '+t.city+' ('+t.id+').')}">Ask on WhatsApp</a>
  </div></aside></div>`;
  const total = () => {
    if(shared) return t.seat * Number($('#b-qty').value);
    const r = document.querySelector('input[name=veh]:checked'); return r ? Number(r.dataset.p) : 0;
  };
  const upd = () => { $('#b-total').textContent = inr(total()); $$('.vopt').forEach(v=>v.classList.toggle('on', v.querySelector('input').checked)); };
  $$('input[name=veh]').forEach(r=>r.onchange=upd); if($('#b-qty')) $('#b-qty').onchange=upd; upd();
  $('#b-go').onclick = () => {
    const date=$('#b-date').value, pick=$('#b-pick').value.trim();
    if(!date){ alertBox('Please choose a travel date.'); return; }
    if(!pick){ alertBox('Please enter your pickup location.'); return; }
    const o = { kind:'trip', id:t.id, name:t.name, city:t.city, type:t.type, date, pickup:pick, multi,
      qty: shared?Number($('#b-qty').value):1, vehicle: shared?null:(document.querySelector('input[name=veh]:checked')||{}).value,
      unit: shared?t.seat:total(), total: total() };
    sessionStorage.setItem('kfgo_order', JSON.stringify(o)); location.href='/checkout';
  };
}
function alertBox(msg){ let b=$('#b-msg'); if(!b){ b=document.createElement('div'); b.id='b-msg'; b.className='warn'; $('#b-go').before(b);} b.textContent=msg; }

/* ---------- generic request forms (taxi, logistics, partner) ---------- */
$$('form[data-request]').forEach(f => f.onsubmit = e => {
  e.preventDefault();
  const fd = new FormData(f); const lines=[f.dataset.request];
  for(const [k,v] of fd.entries()){ if(String(v).trim()) lines.push(k+': '+v); }
  sendLead({kind:f.dataset.kind||'request', fields:Object.fromEntries(fd.entries())});
  window.open(wa(C.whatsapp.orders, lines.join('\n')), '_blank');
});

/* ---------- checkout ---------- */
function orderId(){ const d=new Date(); const p=n=>String(n).padStart(2,'0'); return 'KFG-'+String(d.getFullYear()).slice(2)+p(d.getMonth()+1)+p(d.getDate())+'-'+Math.random().toString(36).slice(2,6).toUpperCase(); }
function sendLead(payload){ if(!C.leadEndpoint) return; try{ fetch(C.leadEndpoint,{method:'POST',mode:'no-cors',headers:{'Content-Type':'text/plain'},body:JSON.stringify(Object.assign({brand:'kfGo',page:location.pathname,ts:new Date().toISOString()},payload))}); }catch(e){} }
function checkout(){
  const root=$('#checkout'); if(!root) return;
  const o = JSON.parse(sessionStorage.getItem('kfgo_order')||'null');
  if(!o){ root.innerHTML='<div class="panel"><h3>Your basket is empty</h3><p>Pick a trip first.</p><a class="btn n" href="/trips" style="margin-top:12px">Browse trips</a></div>'; return; }
  const what = o.vehicle ? `${o.vehicle} (whole vehicle)` : `${o.qty} seat${o.qty>1?'s':''} × ${inr(o.unit)}`;
  $('#sum').innerHTML = `<h3>${esc(o.name)}</h3><p class="note" style="margin-top:0">${esc(o.type)} from ${esc(o.city)}</p>
   <table class="rates" style="margin-top:12px"><tr><td>Date</td><td>${esc(o.date)}</td></tr><tr><td>Pickup</td><td>${esc(o.pickup)}</td></tr><tr><td>Booking</td><td>${esc(what)}</td></tr><tr><td><b>Total</b></td><td class="r">${inr(o.total)}</td></tr></table>
   ${o.multi?'<div class="warn">Multi-day trip: our team will confirm the advance amount on WhatsApp. The balance is paid before the trip starts.</div>':''}
   <p class="note">Hotels, entry tickets, boating and other third-party costs are not included unless listed. <a href="/refund-policy" target="_blank">Cancellation & refund policy</a>.</p>`;
  $('#co-form').onsubmit = e => {
    e.preventDefault();
    const fd=new FormData(e.target); o.customer=Object.fromEntries(fd.entries()); o.ref=orderId();
    sessionStorage.setItem('kfgo_order', JSON.stringify(o)); sendLead({kind:'order', order:o});
    const msg = [`New booking ${o.ref}`, `${o.name} (${o.id}) from ${o.city}`, `Date: ${o.date}`, `Pickup: ${o.pickup}`, `Booking: ${what}`, `Total: ${inr(o.total)}`, `Name: ${o.customer.name}`, `Phone: ${o.customer.phone}`, o.customer.email?`Email: ${o.customer.email}`:'', o.customer.notes?`Notes: ${o.customer.notes}`:''].filter(Boolean).join('\n');
    $('#co-form').classList.add('hidden'); const p=$('#pay'); p.classList.remove('hidden');
    let h = `<div class="ok"><b>Booking reference: ${o.ref}</b><br>Keep this reference for payment and any changes.</div>`;
    const payNow = !o.multi;
    if(payNow && C.upi.id){
      const link=`upi://pay?pa=${encodeURIComponent(C.upi.id)}&pn=${encodeURIComponent(C.upi.payee)}&am=${o.total}&cu=INR&tn=${encodeURIComponent(o.ref)}`;
      h += `<div class="paybox"><h4>Pay ${inr(o.total)} by UPI</h4><p class="note" style="margin-top:4px">GPay, PhonePe, Paytm or any UPI app. Use reference <b>${o.ref}</b>.</p>
        <a class="btn n" href="${link}" style="margin-top:12px">Open UPI app</a><div id="qr" class="qr"></div><p class="note">UPI ID: <b>${esc(C.upi.id)}</b> · ${esc(C.upi.payee)}</p>
        <label>UPI transaction ID (after paying)</label><input id="utr" placeholder="12-digit UTR / transaction ID"></div>`;
    }
    if(payNow && C.razorpayKey){ h += `<div class="paybox"><h4>Pay by card, netbanking or wallet</h4><button class="btn n" id="rzp" style="margin-top:10px">Pay ${inr(o.total)} securely</button></div>`; }
    if(!payNow || (!C.upi.id && !C.razorpayKey)){ h += `<div class="warn">Send your booking to us on WhatsApp. Our team confirms availability and shares the payment details right away.</div>`; }
    h += `<a class="btn w" id="send" target="_blank" rel="noopener" style="width:100%;margin-top:14px">${payNow&&(C.upi.id||C.razorpayKey)?'I have paid: send confirmation on WhatsApp':'Send booking on WhatsApp'}</a>`;
    p.innerHTML = h;
    if($('#qr') && window.QRCode){ new QRCode($('#qr'),{text:`upi://pay?pa=${C.upi.id}&pn=${encodeURIComponent(C.upi.payee)}&am=${o.total}&cu=INR&tn=${o.ref}`,width:196,height:196}); }
    const setSend=()=>{ const u=$('#utr')?$('#utr').value.trim():''; $('#send').href=wa(C.whatsapp.orders, msg+(u?`\nPaid by UPI, transaction ID: ${u}`:'')); };
    if($('#utr')) $('#utr').oninput=setSend; setSend();
    if($('#rzp')) $('#rzp').onclick=()=>{ const r=new Razorpay({key:C.razorpayKey,amount:o.total*100,currency:'INR',name:'kfGo Travel & Logistics',description:o.ref+' · '+o.name,prefill:{name:o.customer.name,contact:o.customer.phone,email:o.customer.email||''},notes:{ref:o.ref},theme:{color:'#0B2A6B'},handler:res=>{ $('#send').href=wa(C.whatsapp.orders,msg+'\nPaid online, payment ID: '+res.razorpay_payment_id); $('#send').textContent='Paid: send confirmation on WhatsApp'; sendLead({kind:'payment',ref:o.ref,payment:res.razorpay_payment_id}); }}); r.open(); };
  };
}

home(); catalogue(); trip(); checkout();
})();
