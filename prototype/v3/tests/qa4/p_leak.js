const sleep = ms => new Promise(r => setTimeout(r, ms));
const res = [];
const dump = () => { const parts = [];
  for (const sel of ['#view', '#bottom', '#pushwrap', '#toast', '#sheet']) { const el = $(sel); parts.push(sel + ' TEXT ' + el.textContent);
    el.querySelectorAll('*').forEach(x => { for (const a of x.attributes) if (!['class','style','d','viewBox','fill','stroke','width','height','src','cx','cy','r','rx','ry','x','y','transform','stroke-width','stroke-linecap'].includes(a.name)) parts.push(sel + ' @' + x.tagName + '.' + a.name + '=' + a.value); }); }
  return parts.join('\n'); };
const forb = (p, who) => { const out = []; const ms = p.group ? p.group.members : ['oleg','anya'];
  for (const m of ms) { if (m === who) continue; const sv = p.saved[m] || 0, cf = (p.conf || {})[m] || 0;
    const vals = {saved:sv, conf:cf, left:Math.max(0, (p.share[m] || 0) - sv), perDay: p.share[m] ? Math.ceil(Math.max(0,(p.share[m]-sv))/daysTo(p)) : 0};
    for (const [k, v] of Object.entries(vals)) if (v >= 1000 && v !== p.share[m] && v !== p.price) out.push([m + '.' + k, v]); }
  const othersSum = ms.filter(m => m !== who).reduce((s, m) => s + (p.saved[m] || 0), 0); if (othersSum >= 1000) out.push(['othersSaved', othersSum]);
  return out; };
const scan = (label, p, who) => { const d = dump(), hits = [];
  for (const [k, v] of forb(p, who)) { const f1 = fmt(v), f2 = String(v); for (const line of d.split('\n')) if (line.includes(f1) || new RegExp('(^|\D)' + f2 + '(\D|$)').test(line)) hits.push(k + '=' + v + ' :: ' + line.slice(0, 220)); }
  res.push({label, who, scr:S.scr, sheet:S.sheet, hits}); };
const SHEETS = ['save','change','where','how','weeksum','v3direct','policy','photo','cancelAsk'];
for (const code of ['group2','group3','anya-group2','anya-group3','groupInvite','weeksum3']) {
  const anya = code.startsWith('anya-'), k = anya ? code.slice(5) : code;
  if (anya) S.who = 'anya'; else S.who = 'oleg';
  V3_SCEN[k](); await sleep(50); const p = P(), w = S.who;
  scan(code + ' screen', p, w);
  for (const sh of SHEETS) { try { openSheet(sh); scan(code + ' sheet ' + sh, p, w); } catch (e) { res.push({label: code + ' sheet ' + sh, err: String(e)}); } closeSheet(); }
  for (const inp of ['share','dl','took']) { openSheet('input', inp); scan(code + ' input ' + inp, p, w); closeSheet(); }
  // bot + payday push + today
  me().bot = 'max'; S.flags.push = true; go('bot'); scan(code + ' bot', p, w); botSay('влезет ли ужин за 3000?'); render(true); scan(code + ' bot afford', p, w);
  go('today'); scan(code + ' today+push', p, w); S.flags.push = false;
  go('list'); scan(code + ' list', p, w);
  setDay(1); go('purchase'); scan(code + ' tomorrow', p, w); setDay(0);
}
return res.filter(r => r.err || r.hits.length);
