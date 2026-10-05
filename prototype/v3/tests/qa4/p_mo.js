const sleep = ms => new Promise(r => setTimeout(r, ms)); const o = {theme: document.documentElement.dataset.theme, mode: themeMode, rm: reduce()};
await sleep(50);
// money swap under rapid taps in the example
V3_SCEN.example(); await sleep(50); const val = () => $('#view [data-v3-money]').textContent;
const seq = []; const b = () => $('#view [data-act="v3exStep"]');
b().click(); seq.push('t0 after 1st: ' + val()); await sleep(80); b().click(); seq.push('t80 after 2nd: ' + val()); await sleep(80); b().click(); seq.push('t160 after 3rd: ' + val());
await sleep(100); seq.push('t260: ' + val()); await sleep(400); seq.push('t660: ' + val()); o.seq = seq; o.truth = rubT(V3_SCEN && (V3_EX.price - S.v3.ex));
// animations names on screen change and example exit
V3_SCEN.solo(); await sleep(20); go('today'); o.viewAnim = getComputedStyle($('#view')).animationName + ' ' + getComputedStyle($('#view')).animationDuration;
V3_SCEN.example(); await sleep(20); ACT.v3own(); const g = $('.view.v3-ghost'); o.ghost = g ? getComputedStyle(g).animationName + ' ' + getComputedStyle(g).animationDuration + ' inert=' + g.inert : 'none';
o.exin = getComputedStyle($('#view')).animationName;
// theme switch transition
setTheme('dark'); o.themeAnimClass = document.documentElement.classList.contains('theme-anim'); o.bodyTransition = getComputedStyle(document.body).transitionProperty; setTheme('system'); o.afterSystem = document.documentElement.dataset.theme;
o.sheetTransition = getComputedStyle($('#sheet')).transitionDuration;
return o;
