const o = {}; const vt = () => $('#view').innerText.replace(/\n+/g, ' | ').slice(0, 900);
V3_SCEN.groupShare(); o.share = vt(); $('#view [data-act="v3asGuest"]').click(); o.guestView = vt();
$('#v3accept').value = 'беру 40'; $('#v3acceptf').requestSubmit(); closeSheet();
const p = P(); o.after = {who:S.who, share:p.share, promised:v3promised(p), price:p.price, note: ($('#v3accnote')||{}).textContent};
S.who = 'oleg'; go('purchase'); o.ownerView = vt();
// toast persists across pult jumps
V3_SCEN.example(); $('#view [data-act="v3exStep"]').click(); V3_SCEN.group2(); o.toastAfterJump = {on: $('#toast').classList.contains('on'), text: $('#toast').textContent, scr:S.scr};
o.warn = demo.v3.warn();
return o;
