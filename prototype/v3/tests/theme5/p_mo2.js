// QA №15, расширенно: после каждого нажатия через 220 мс число на экране = истина; интервалы 30…400 мс
const sleep = ms => new Promise(r => setTimeout(r, ms));
const val = () => $('#view [data-v3-money]').textContent, truth = () => rubT(V3_EX.price - S.v3.ex);
const out = {rm: reduce(), runs: []};
for (const gap of [30, 80, 150, 230, 400]) {
  V3_SCEN.example(); await sleep(60); let bad = 0, n = 0, late = [];
  for (let i = 0; i < 6; i++) { const b = $('#view [data-act="v3exStep"]'); if (!b) break; b.click(); const want = truth(); n++;
    const t0 = performance.now(); let hit = null;
    while (performance.now() - t0 < Math.max(gap, 240)) { if (hit === null && val() === want) hit = Math.round(performance.now() - t0); await sleep(10); if (performance.now() - t0 >= gap && hit !== null) break; }
    if (hit === null || hit > 220) { bad++; late.push(i + ':' + hit); } }
  out.runs.push(`gap ${gap} мс: нажатий ${n}, позже 220 мс: ${bad} ${late.join(' ')} · итог ${val()} = ${truth()}`);
}
return out;
