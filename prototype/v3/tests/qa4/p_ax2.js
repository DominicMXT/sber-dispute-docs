const CODES = ['example','solo','together','group2','group3','anya-group3','groupInvite','groupShare','empty','dayprice','slip','weeks','weeksum3','nextgoal','themeSet'];
const bad = [];
const nm = x => (x.getAttribute('aria-label') || x.innerText || x.getAttribute('title') || (x.labels && x.labels[0] && x.labels[0].innerText) || '').trim();
for (const c of CODES) { let k = c; S = seed('mid'); S.who = 'oleg'; if (k.startsWith('anya-')) { k = k.slice(5); S.who = 'anya'; } V3_SCEN[k]();
  const roots = ['#view', '#bottom', '#pushwrap'].concat(S.sheet ? ['#sheet'] : []);
  for (const r of roots) $$(r + ' button, ' + r + ' input, ' + r + ' textarea, ' + r + ' [role=img], ' + r + ' [role=group]').forEach(x => { if (!nm(x)) bad.push(c + ' ' + r + ' ' + x.tagName + '.' + x.className + ' ' + x.outerHTML.slice(0, 120)); });
  // aria-label of visibility icons in state
  $$('#view .vis').forEach(x => { if (!x.getAttribute('aria-label')) bad.push(c + ' vis without label'); });
  // v3-time / v3-wk value conveyed?
  const t = $('#view .v3-time'); if (t) bad.push(c + ' INFO v3-time label: ' + t.getAttribute('aria-label'));
  const steps = $('#view .v3-steps'); if (steps) bad.push(c + ' INFO v3-steps aria-hidden=' + steps.getAttribute('aria-hidden'));
  // aria-pressed in theme seg
  if (c === 'themeSet') $$('#view [data-th]').forEach(b => bad.push('themeSet INFO ' + b.textContent + ' pressed=' + b.getAttribute('aria-pressed')));
}
return bad;
