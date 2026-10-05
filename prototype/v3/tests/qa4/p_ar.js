const sleep = ms => new Promise(r => setTimeout(r, ms)); const o = {};
const num = s => +String(s).replace(/[^\d]/g, '');
// 1. M-B: «Как я посчитал» сходится?
for (const c of ['solo','dayprice']) { V3_SCEN[c](); if (S.scr !== 'today') go('today');
  const rows = $$('#view details .rowl').map(r => [r.children[0].textContent.trim(), r.querySelector('b') ? r.querySelector('b').textContent : '']);
  const get = re => { const r = rows.find(x => re.test(x[0])); return r ? num(r[1]) : null; };
  const inc = get(/Приход/), mand = get(/Обязательные/), buy = get(/На покупки/), buf = get(/Запас/), self = get(/На себя/);
  o['MB_' + c] = {rows, recompute: Math.floor((inc - mand - buy - buf) / 30), shown: self, big: $('[data-out="left-today"]').textContent, untilPay: $('[data-out="left-today"]').nextElementSibling.textContent, calc_untilPay: untilPay('oleg'), selfDay: selfDay('oleg'), toPay: toPay('oleg')}; }
// 2. slip edge cases
const slipCase = (savedBefore, took) => { V3_SCEN.solo(); const p = P(); p.saved.oleg = savedBefore; p.conf.oleg = 0; render();
  openSheet('input', 'took'); $('#inputv').value = String(took); $('#inputf').requestSubmit();
  const btns = $$('#view .v3-pair button').map(b => b.innerText.replace(/\n/g, ' | ')); return {savedBefore, took, scr:S.scr, btns, dl:new Date(p.dl).toISOString().slice(0,10), toast:$('#toast').textContent}; };
o.slip = [slipCase(50000, 20000), slipCase(119900, 20000), slipCase(50000, 100), slipCase(50000, 1), slipCase(120000, 5000)];
// apply the extreme shift
{ V3_SCEN.solo(); const p = P(); p.saved.oleg = 119900; render(); openSheet('input','took'); $('#inputv').value = '20000'; $('#inputf').requestSubmit();
  $('#view [data-act="v3slipDate"]').click(); o.slipApplied = {dl:new Date(p.dl).toISOString().slice(0,10), head:$('#view .head p').textContent, toast:$('#toast').textContent}; }
// 3. M-C: dayprice short vs bot full; bot sentence join
V3_SCEN.dayprice(); o.MC_today = [$('[data-out="afford"]').textContent, ($('#view .v3-dayprice')||{}).textContent];
me().bot = 'max'; for (const t of ['влезет ли ужин за 3000?', 'влезет ли телевизор за 90000?', 'влезет ли кофе за 200?']) botSay(t);
o.MC_bot = me().chat.filter(x => x.out === 'afford').map(x => x.b);
// Today with S.aff=90000
S.aff = 90000; go('today'); o.MC_today_no = [$('[data-out="afford"]').textContent, ($('#view .v3-dayprice')||{}).textContent];
return o;
