// node shot.mjs <out.png> <js-to-run-after-load> [theme] — снимок полной сборки 420×860
import { spawn } from 'node:child_process';
import { mkdtempSync, writeFileSync, rmSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
const CH = 'C:/Program Files/Google/Chrome/Application/chrome.exe';
const FILE = decodeURIComponent(new URL('../../../2026-10-04_fog-prototype-v3.html', import.meta.url).pathname.replace(/^\/([A-Za-z]:)/, '$1'));
const [out, js, theme = 'light'] = process.argv.slice(2);
const here = dirname(fileURLToPath(import.meta.url)), prof = mkdtempSync(join(here, 'shp-')), port = 9960 + Math.floor(Math.random() * 30);
const ch = spawn(CH, ['--headless=new', '--disable-gpu', `--remote-debugging-port=${port}`, `--user-data-dir=${prof}`, '--window-size=500,960', 'about:blank'], { stdio: 'ignore' });
const sleep = ms => new Promise(r => setTimeout(r, ms));
let tg; for (let i = 0; i < 60; i++) { try { tg = await (await fetch(`http://127.0.0.1:${port}/json`)).json(); if (tg.find(t => t.type === 'page')) break; } catch (e) {} await sleep(200); }
const ws = new WebSocket(tg.find(t => t.type === 'page').webSocketDebuggerUrl); await new Promise(r => ws.onopen = r);
let id = 0; const pend = {}; ws.onmessage = m => { const d = JSON.parse(m.data); if (d.id && pend[d.id]) { pend[d.id](d); delete pend[d.id]; } };
const send = (method, params = {}) => new Promise(r => { const i = ++id; pend[i] = r; ws.send(JSON.stringify({ id: i, method, params })); });
await send('Page.enable'); await send('Runtime.enable');
await send('Emulation.setEmulatedMedia', { features: [{ name: 'prefers-color-scheme', value: theme }, { name: 'prefers-reduced-motion', value: 'reduce' }] });
await send('Emulation.setDeviceMetricsOverride', { width: 420, height: 860, deviceScaleFactor: 1, mobile: false });
await send('Page.navigate', { url: 'file:///' + FILE }); await sleep(1500);
const r = await send('Runtime.evaluate', { expression: `(() => { ${js}; return 'ok'; })()`, returnByValue: true });
if (r.result.exceptionDetails) console.log('EXC', JSON.stringify(r.result.exceptionDetails).slice(0, 500));
await sleep(900);
const s = await send('Page.captureScreenshot', { format: 'png' }); writeFileSync(out, Buffer.from(s.result.data, 'base64'));
console.log('saved', out); ws.close(); const gone = new Promise(r => ch.once('exit', r)); ch.kill(); await Promise.race([gone, sleep(3000)]); try { rmSync(prof, { recursive: true, force: true, maxRetries: 10, retryDelay: 200 }); } catch (e) {} process.exit(0);
