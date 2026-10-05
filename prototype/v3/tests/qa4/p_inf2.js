// Наблюдатель — Олег. Каждые сутки — снимок (как при смене дня). Ищем момент смены видимого статуса цели и выводим диапазон чужой суммы.
const o = {};
const vis = m => { const r = $(`#view [data-v3-member="${m}"]`); const st = r && r.querySelector('.v3-st'); return (st ? st.textContent : '—') + ' | ' + ($('#view .cap .stamp') || {}).textContent + ' | ' + (($('#view .v3-big') || {}).textContent || ''); };
for (const [code, m] of [['group2','anya'], ['group3','timur'], ['group3','sveta']]) {
  S.who = 'oleg'; V3_SCEN[code](); const p = P(), share = p.share[m], c0 = v3from(p, m), tot = Math.max(1, Math.round((p.dl - c0) / DAY));
  let prev = null, flip = null;
  for (let d = 0; d < 200; d++) { S.off = d; v3snap(p); render(); const s = vis(m).split(' | ')[0]; if (prev !== null && s !== prev) { flip = {day:d, from:prev, to:s}; break; } prev = s; }
  const thr = d => { const el = Math.max(0, Math.round((D0 + d * DAY - c0) / DAY)); return Math.floor(share * el / tot) - 1; };
  o[code + ':' + m] = {actualSaved: p.saved[m], flip, inferredRange: flip ? [thr(flip.day - 1), thr(flip.day)] : null, rangeWidth: flip ? thr(flip.day) - thr(flip.day - 1) : null, dailyPlanStep: Math.round(share / tot)};
  S.off = 0; }
// внутри суток чужие отметки не меняют ничего видимого
const intraday = {};
for (const [code, m] of [['group2','anya'], ['group3','sveta'], ['group3','timur']]) { S.who = 'oleg'; V3_SCEN[code](); const p = P(); const before = vis(m); const seen = new Set([before]);
  for (const dv of [-3000, -500, 0, 200, 1000, 5000, 20000]) { p.saved[m] = Math.max(0, p.saved[m] + dv); render(); seen.add(vis(m)); }
  intraday[code + ':' + m] = {distinctViews: seen.size, before}; }
o.intraday = intraday;
// ноль: «только начали» у чужих не виден ни в день, ни после снимка
S.who = 'oleg'; V3_SCEN.group3(); P().saved.timur = 0; render(); const z1 = vis('timur'); v3snap(P()); render(); o.zero = {sameDay: z1, afterSnap: vis('timur')};
// №7: участник вошёл вчера, ничего не отложил — по плану
V3_SCEN.group2(); const q = P(); q.join = {anya: now() - DAY}; q.saved.anya = 0; v3snap(q); render(); o.joinedYesterday = {fits: v3fits(q), stamp: $('#view .cap .stamp').textContent};
return o;
