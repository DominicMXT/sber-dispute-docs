const sleep = ms => new Promise(r => setTimeout(r, ms));
const W = s => (s.match(/[A-Za-zА-Яа-яЁё0-9]+/g) || []).length;
const sents = s => s.split(/[.!?\n…]+/).map(x => x.replace(/\s+/g, ' ').trim()).filter(Boolean);
const fold = () => { const v = $('#view'); v.scrollTop = 0; const r = v.getBoundingClientRect(), b = $('#bottom .bottom'), lim = b ? b.getBoundingClientRect().top : r.bottom, tw = document.createTreeWalker(v, NodeFilter.SHOW_TEXT); let s = '', n;
  while ((n = tw.nextNode())) { if (!n.textContent.trim() || n.parentElement.closest('[data-sheet="feedback"]') || (n.parentElement.closest('details:not([open])') && !n.parentElement.closest('summary'))) continue; const rg = document.createRange(); rg.selectNodeContents(n); const q = rg.getBoundingClientRect();
    if (q.height && q.bottom > r.top && q.top < lim) s += ' ' + n.textContent; } return s; };
const allText = el => { const ds = $$('details', el), was = ds.map(d => d.open); ds.forEach(d => d.open = true); const t = el.innerText; ds.forEach((d, i) => d.open = was[i]); return t; };
const CODES = ['fresh','mid','payday','partner','price','week','recon','done','offline','limit','format','botoff','used','example','solo','together','group2','group3','anya-group2','anya-group3','groupInvite','groupShare','empty','dayprice','slip','weeks','weeksum3','nextgoal','themeSet','anya-purchase','anya-mid'];
const run = c => { let k = c; S = seed('mid'); S.who = 'oleg'; if (k.startsWith('anya-')) { k = k.slice(5); S.who = 'anya'; }
  if (V3_SCEN[k]) V3_SCEN[k](); else if (['fresh','mid','payday','partner','price','week','recon','done','offline','limit','format','botoff','used'].includes(k)) scenario(k); else go(k); endStory(); };
const out = [];
for (const c of CODES) { run(c); await sleep(30);
  const vtx = allText($('#view')).replace('Что не так?', ''), fw = W(fold()), long = sents(vtx).filter(x => W(x) > 15);
  const mx = sents(vtx).sort((a, b) => W(b) - W(a))[0] || ""; const row = {mx: W(mx) + ": " + mx, c, scr:S.scr, sheet:S.sheet, firstWords:fw, long, warn:demo.v3.warn().slice()};
  if (S.sheet) { const st = $('#sheet').innerText; row.sheetWords = W(st); row.sheetLong = sents(st).filter(x => W(x) > 15); }
  out.push(row); }
// sheets in representative states
const SHS = Object.keys(SH).filter(k => !['input'].includes(k));
const sheetRows = [];
for (const c of ['mid','solo','group2','group3','anya-group3','groupInvite']) { run(c);
  for (const k of SHS) { try { openSheet(k); const st = $('#sheet').innerText; const w = W(st), l = sents(st).filter(x => W(x) > 15); if (w > 30 || l.length) sheetRows.push({c, k, w, long:l}); } catch (e) { sheetRows.push({c, k, err:String(e).slice(0,150)}); } closeSheet(); }
  for (const k of ['share','dl','took']) { openSheet('input', k); const st = $('#sheet').innerText; if (W(st) > 30 || sents(st).some(x => W(x) > 15)) sheetRows.push({c, k:'input:' + k, w:W(st), long:sents(st).filter(x => W(x) > 15)}); closeSheet(); } }
return out.map(r => r.c + " | first " + r.firstWords + " | maxSent " + r.mx);
