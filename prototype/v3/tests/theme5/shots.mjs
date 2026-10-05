// node shots.mjs — скриншоты тёмной темы и замеры (туман, слова, поверхности); тема через localStorage fogp-theme-mode
import { spawn } from 'node:child_process';
import { mkdtempSync, writeFileSync } from 'node:fs';
const DIR = (process.env.SHOT_DIR || '.');
const CH = 'C:/Program Files/Google/Chrome/Application/chrome.exe';
const URL0 = 'http://localhost:8767/prototype/2026-10-04_fog-prototype-v3.html';
const port = 9800 + Math.floor(Math.random() * 150), prof = mkdtempSync(DIR + '/prof-');
const ch = spawn(CH, ['--headless=new', '--disable-gpu', `--remote-debugging-port=${port}`, `--user-data-dir=${prof}`, '--window-size=420,860', 'about:blank'], { stdio: 'ignore' });
const sleep = ms => new Promise(r => setTimeout(r, ms));
let tg; for (let i = 0; i < 50; i++) { try { tg = await (await fetch(`http://127.0.0.1:${port}/json`)).json(); if (tg.find(t => t.type === 'page')) break; } catch (e) {} await sleep(200); }
const ws = new WebSocket(tg.find(t => t.type === 'page').webSocketDebuggerUrl); await new Promise(r => ws.onopen = r);
let id = 0; const pend = {}, logs = [];
ws.onmessage = m => { const d = JSON.parse(m.data); if (d.id && pend[d.id]) { pend[d.id](d); delete pend[d.id]; } else if (d.method === 'Runtime.exceptionThrown') logs.push('EXC ' + JSON.stringify(d.params.exceptionDetails).slice(0, 300)); };
const send = (method, params = {}) => new Promise(r => { const i = ++id; pend[i] = r; ws.send(JSON.stringify({ id: i, method, params })); });
const ev = async e => { const r = await send('Runtime.evaluate', { expression: `(async () => { ${e} })()`, awaitPromise: true, returnByValue: true }); return r.result.result.value ?? r.result.exceptionDetails; };
const shot = async name => { const r = await send('Page.captureScreenshot', { format: 'png' }); writeFileSync(`${DIR}/${name}.png`, Buffer.from(r.result.data, 'base64')); return `${DIR}/${name}.png`; };
await send('Runtime.enable'); await send('Page.enable');
await send('Emulation.setDeviceMetricsOverride', { width: 420, height: 860, deviceScaleFactor: 1, mobile: false });
const open = async (q, mode) => { await send('Page.navigate', { url: URL0 }); await sleep(600);
  await ev(`localStorage.setItem('fogp-theme-mode', ${JSON.stringify(mode)}); return 1`);
  await send('Page.navigate', { url: URL0 + '?s=' + q }); await sleep(1600); };
const out = { files: [] };
// замер тумана: средняя относительная яркость копии-тумана и проявленного фото (с brightness(.88) в тёмной)
const FOGM = `const lum = src => new Promise(res => { const im = new Image(); im.onload = () => { const c = document.createElement('canvas'); c.width = c.height = 40; const x = c.getContext('2d'); x.drawImage(im, 0, 0, 40, 40); const d = x.getImageData(0, 0, 40, 40).data; let L = 0; const f = v => { v /= 255; return v <= .04045 ? v / 12.92 : ((v + .055) / 1.055) ** 2.4; }; for (let i = 0; i < d.length; i += 4) L += .2126 * f(d[i]) + .7152 * f(d[i+1]) + .0722 * f(d[i+2]); res(L / 1600); }; im.src = src; });
  const th = document.documentElement.dataset.theme, k = th === 'dark' ? .88 : 1, rows = [];
  for (const ph of $$('.photo[data-pic]')) { const f = $('.fog', ph), c = $('.color', ph); if (!f || !c || f.classList.contains('fogfb')) { rows.push(ph.dataset.pic + ': запасной вариант'); continue; }
    const a = await lum(f.src), b = await lum(c.src) * k; rows.push(ph.dataset.pic + ': туман ' + a.toFixed(3) + ' · проявленное ' + b.toFixed(3) + ' → ' + (th === 'dark' ? (b > a ? 'проявленное ярче' : 'ТУМАН ЯРЧЕ') : (a > b ? 'туман светлее (молочный)' : 'туман темнее'))); }
  return th + ' · ' + rows.join(' | ');`;
for (const mode of ['dark', 'light']) for (const q of ['mid', 'group3']) { await open(q, mode); out[q + ':' + mode] = await ev(FOGM); if (mode === 'dark') out.files.push(await shot(q + '-dark')); }
// themeSet в тёмной: блок «Тема», выбранная кнопка, слова на первом экране «Моих данных»
await open('themeSet', 'dark'); out.files.push(await shot('themeSet-dark'));
out.themeSet = await ev(`const W = s => (s.match(/[A-Za-zА-Яа-яЁё0-9]+/g) || []).length; const b = $('#v3-theme');
  const fold = () => { const v = $('#view'); v.scrollTop = 0; const r = v.getBoundingClientRect(), bb = $('#bottom .bottom'), lim = bb ? bb.getBoundingClientRect().top : r.bottom, tw = document.createTreeWalker(v, NodeFilter.SHOW_TEXT); let s = '', n;
    while ((n = tw.nextNode())) { if (!n.textContent.trim()) continue; const rg = document.createRange(); rg.selectNodeContents(n); const q = rg.getBoundingClientRect(); if (q.height && q.bottom > r.top && q.top < lim) s += ' ' + n.textContent; } return s; };
  const sel = $('#v3-theme [aria-pressed="true"]'), cs = getComputedStyle(sel), sys = $('#v3-theme [data-th="system"]');
  const o = {blockWords: W(b.innerText), blockText: b.innerText.split(String.fromCharCode(10)).join(' / '), dataFirstScreenWords: W(fold()), dataAllWords: W($('#view').innerText),
    pressed: sel.dataset.th + ' bg ' + cs.backgroundColor + ' color ' + cs.color + ' ring ' + cs.boxShadow, systemTitle: sys.title,
    ariaPressed: $$('#v3-theme [data-th]').map(x => x.dataset.th + '=' + x.getAttribute('aria-pressed')).join(' '), meta: document.querySelector('meta[name="theme-color"]').content,
    main: getComputedStyle($('#bottom .main') || document.body).backgroundColor, inp: (() => { const i = $('.inp'); return i ? getComputedStyle(i).borderTopWidth + ' ' + getComputedStyle(i).borderTopColor : 'нет поля'; })() };
  setTheme('system'); o.toastSystem = $('#toast').textContent + ' · role=' + $('#toast').getAttribute('role'); return o;`);
// лист и тост в тёмной теме
await open('mid', 'dark'); await ev(`openSheet('how'); return 1`); await sleep(500); out.files.push(await shot('sheet-dark'));
out.sheet = await ev(`const s = getComputedStyle($('#sheet')); return 'sheet bg ' + s.backgroundColor + ' shadow ' + s.boxShadow`);
await ev(`closeSheet(); go('today'); return 1`); await sleep(300);
out.today = await ev(`const g = $('#view .go:not(.go2)'), g2 = $('#view .go2'), m = $('#bottom .main'); toast('Тёмная тема'); return {go: g ? getComputedStyle(g).backgroundColor + ' / ' + getComputedStyle(g).boxShadow : 'нет', go2: g2 ? getComputedStyle(g2).backgroundColor + ' / ' + getComputedStyle(g2).boxShadow : 'нет', main: m ? getComputedStyle(m).backgroundColor : 'нет', inp: getComputedStyle($('#view .inp')).border, cardp: (() => { const c = $('.cardp'); return c ? getComputedStyle(c).boxShadow : 'нет на экране'; })()};`);
await sleep(300); out.files.push(await shot('today-toast-dark'));
if (logs.length) out.logs = logs;
console.log(JSON.stringify(out, null, 1)); ws.close(); ch.kill(); process.exit(0);
