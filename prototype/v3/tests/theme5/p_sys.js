// «Как в системе» при системной тёмной: тема, meta, вуаль тумана; затем ручная светлая и обратно
const sleep = ms => new Promise(r => setTimeout(r, ms)); const r = document.documentElement, meta = () => document.querySelector('meta[name="theme-color"]').content;
const o = {mode: themeMode, theme: r.dataset.theme, meta: meta()}; go('purchase'); await sleep(300);
const fog = () => { const f = $('.photo .fog'); return f ? (f.classList.contains('fogfb') ? 'запасной' : f.src.slice(0, 30)) : 'нет'; };
const f0 = $('.photo .fog') && $('.photo .fog').src; setTheme('light'); await sleep(400); o.light = r.dataset.theme + ' ' + meta() + ' fogChanged=' + ($('.photo .fog').src !== f0) + ' toast=' + $('#toast').textContent;
setTheme('system'); await sleep(400); o.back = r.dataset.theme + ' ' + meta() + ' fogBack=' + ($('.photo .fog').src === f0) + ' toast=' + $('#toast').textContent; return o;
