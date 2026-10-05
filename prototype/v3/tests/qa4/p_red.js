const CODES = ['example','solo','together','group2','group3','anya-group3','groupInvite','groupShare','empty','dayprice','slip','weeks','weeksum3','nextgoal','themeSet'];
const hue = (r, g, b) => { const mx = Math.max(r, g, b), mn = Math.min(r, g, b); if (mx === mn) return null; let h = mx === r ? (g - b) / (mx - mn) : mx === g ? 2 + (b - r) / (mx - mn) : 4 + (r - g) / (mx - mn); h *= 60; if (h < 0) h += 360; return {h, s:(mx - mn) / mx}; };
const out = [];
for (const th of ['light','dark']) { document.documentElement.dataset.theme = th;
  for (const c of CODES) { let k = c; S = seed('mid'); S.who = 'oleg'; if (k.startsWith('anya-')) { k = k.slice(5); S.who = 'anya'; } V3_SCEN[k]();
    for (const x of $$('#view *, #sheet *, #bottom *')) { if (x.closest('.photo,.mini,svg')) continue; const cs = getComputedStyle(x);
      for (const p of ['color','backgroundColor','borderTopColor','outlineColor']) { const m = (cs[p].match(/[\d.]+/g) || []).map(Number); if (m.length < 3 || (m.length > 3 && m[3] === 0)) continue;
        const hs = hue(m[0], m[1], m[2]); if (hs && (hs.h < 20 || hs.h > 340) && hs.s > 0.35) out.push(th + ' ' + c + ' ' + x.tagName + '.' + x.className + ' ' + p + '=' + cs[p] + ' "' + x.textContent.trim().slice(0, 30) + '"'); } } } }
return [...new Set(out)].slice(0, 40);
