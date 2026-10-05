const o = {};
const statusOf = m => { const el = $(`#view [data-v3-member="${m}"] .v3-st`); return el ? el.textContent : null; };
for (const [code, m] of [['group2','anya'], ['group3','timur'], ['group3','sveta']]) {
  V3_SCEN[code](); const p = P(); const share = p.share[m], tot = Math.max(1, Math.round((p.dl - p.cr) / DAY));
  let prev = null, flip = null;
  for (let d = 0; d < 200; d++) { S.off = d; render(); const s = statusOf(m); if (prev && s !== prev) { flip = {day:d, from:prev, to:s}; break; } prev = s; }
  // observer only knows share, cr, dl (all visible) and the day of the flip:
  const thr = d => { const el = Math.round((D0 + d * DAY - p.cr) / DAY); return Math.floor(share * el / tot) - 1; };
  o[code + ':' + m] = {actualSaved: p.saved[m], flip, inferredRange: flip ? [thr(flip.day - 1), thr(flip.day)] : null, visibleShare: share};
  S.off = 0; render(); }
// live status vs daily snapshot in group3
V3_SCEN.group3(); const p = P(); const before = {pct: $('#view .v3-big').textContent, sveta: statusOf('sveta')};
p.saved.sveta += 3000; render(); o.liveStatus = {before, after:{pct: $('#view .v3-big').textContent, sveta: statusOf('sveta')}};
// «только начали» = exactly zero
V3_SCEN.group3(); P().saved.timur = 0; render(); o.zero = statusOf('timur');
return o;
