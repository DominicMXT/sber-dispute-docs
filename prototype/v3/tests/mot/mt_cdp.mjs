// node mt_cdp.mjs <file-url> <w,h> — открыть страницу с тестом при точном размере окна (headless Chrome не даёт окно уже 500 px),
// дождаться <pre id="T"> и напечатать JSON {res, cons}. Основа — scratchpad/qa4/cdp.mjs.
import { spawn } from 'node:child_process';
import { mkdtempSync, rmSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
const CH = 'C:/Program Files/Google/Chrome/Application/chrome.exe';
const [url, size = '420,860'] = process.argv.slice(2);
const [w, h] = size.split(',').map(Number);
const here = dirname(fileURLToPath(import.meta.url));
const prof = mkdtempSync(join(here, 'cdpp-'));
const port = 9800 + Math.floor(Math.random() * 150);
const ch = spawn(CH, ['--headless=new', '--disable-gpu', `--remote-debugging-port=${port}`, `--user-data-dir=${prof}`, `--window-size=${Math.max(500, w)},${h + 100}`, 'about:blank'], { stdio: 'ignore' });
const sleep = ms => new Promise(r => setTimeout(r, ms));
let targets; for (let i = 0; i < 60; i++) { try { targets = await (await fetch(`http://127.0.0.1:${port}/json`)).json(); if (targets.find(t => t.type === 'page')) break; } catch (e) {} await sleep(200); }
const t = targets.find(t => t.type === 'page'); const ws = new WebSocket(t.webSocketDebuggerUrl);
await new Promise(r => ws.onopen = r);
let id = 0; const pend = {}, cons = [];
ws.onmessage = m => { const d = JSON.parse(m.data); if (d.id && pend[d.id]) { pend[d.id](d); delete pend[d.id]; }
  else if (d.method === 'Runtime.consoleAPICalled') cons.push(d.params.type + ': ' + d.params.args.map(a => a.value ?? a.description).join(' ').slice(0, 300));
  else if (d.method === 'Runtime.exceptionThrown') cons.push('EXC: ' + JSON.stringify(d.params.exceptionDetails).slice(0, 300)); };
const send = (method, params = {}) => new Promise(r => { const i = ++id; pend[i] = r; ws.send(JSON.stringify({ id: i, method, params })); });
await send('Runtime.enable'); await send('Page.enable');
await send('Emulation.setDeviceMetricsOverride', { width: w, height: h, deviceScaleFactor: 1, mobile: false });
await send('Page.navigate', { url });
let res = null;
for (let i = 0; i < 60 && res == null; i++) { await sleep(250);
  const r = await send('Runtime.evaluate', { expression: "(document.getElementById('T') || {}).textContent ?? null", returnByValue: true });
  res = r.result && r.result.result ? r.result.result.value : null; }
console.log(JSON.stringify({ res: res ?? 'FAIL NO RESULT', cons }));
ws.close(); const gone = new Promise(r => ch.once('exit', r)); ch.kill(); await Promise.race([gone, sleep(3000)]); try { rmSync(prof, { recursive: true, force: true, maxRetries: 10, retryDelay: 200 }); } catch (e) {}
process.exit(0);
