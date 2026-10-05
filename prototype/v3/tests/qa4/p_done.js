const o = {};
V3_SCEN.group3(); let p = P(); for (const m of p.group.members) p.saved[m] = p.share[m]; p.saved.oleg -= 100; render(); step(100);
o.group3 = {state:p.state, left: p.group.members.map(m => m + ':' + leftOf(p, m)).join(' '), gapOf: gapOf(p), v3gap: v3gap(p), main: $('#bottom').innerText.trim(), stamp: $('#view .stamp').textContent, header: $('#view .head p').textContent};
setDay(1); o.group3_tomorrow = {pct: $('#view .v3-big').textContent, state:p.state};
V3_SCEN.group2(); p = P(); for (const m of p.group.members) p.saved[m] = p.share[m]; p.saved.oleg -= 100; render(); step(100);
o.group2 = {state:p.state, main: $('#bottom').innerText.trim(), big: $('#view .v3-big').textContent};
return o;
