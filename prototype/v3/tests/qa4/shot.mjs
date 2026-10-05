// node cdp.mjs <hash-or-empty> <probe.js> [features-json] [w,h]
import { spawn } from 'node:child_process';
import { readFileSync, mkdtempSync } from 'node:fs';
import { tmpdir } from 'node:os'; import { join } from 'node:path';
const CH = 'C:/Program Files/Google/Chrome/Application/chrome.exe';
const FILE = process.env.QA_FILE || decodeURIComponent(new URL('../../../2026-10-04_fog-prototype-v3.html', import.meta.url).pathname.replace(/^\/([A-Za-z]:)/, '$1'));
const [hash = '', probe, feats = '[]', size = '420,860'] = process.argv.slice(2);
const port = 9300 + Math.floor(Math.random() * 500);
const prof = mkdtempSync(join(process.env.TEMP || process.env.TMPDIR || '.', 'qa4p-'));
const ch = spawn(CH, ['--headless=new', '--disable-gpu', `--remote-debugging-port=${port}`, `--user-data-dir=${prof}`, `--window-size=${size}`, 'about:blank'], { stdio: 'ignore' });
const sleep = ms => new Promise(r => setTimeout(r, ms));
let targets; for (let i = 0; i < 50; i++) { try { targets = await (await fetch(`http://127.0.0.1:${port}/json`)).json(); if (targets.find(t => t.type === 'page')) break; } catch (e) {} await sleep(200); }
const t = targets.find(t => t.type === 'page'); const ws = new WebSocket(t.webSocketDebuggerUrl);
await new Promise(r => ws.onopen = r);
let id = 0; const pend = {}; const logs = [];
ws.onmessage = m => { const d = JSON.parse(m.data); if (d.id && pend[d.id]) { pend[d.id](d); delete pend[d.id]; }
  else if (d.method === 'Runtime.consoleAPICalled') logs.push(d.params.type + ': ' + d.params.args.map(a => a.value ?? a.description).join(' '));
  else if (d.method === 'Runtime.exceptionThrown') logs.push('EXC: ' + JSON.stringify(d.params.exceptionDetails).slice(0, 400)); };
const send = (method, params = {}) => new Promise(r => { const i = ++id; pend[i] = r; ws.send(JSON.stringify({ id: i, method, params })); });
await send('Runtime.enable'); await send('Page.enable');
await send('Emulation.setEmulatedMedia', { features: JSON.parse(feats) });
const [w, h] = size.split(',').map(Number);
await send('Emulation.setDeviceMetricsOverride', { width: w, height: h, deviceScaleFactor: 1, mobile: false });
await send('Page.navigate', { url: 'file:///' + FILE + (hash ? '#' + hash : '') });
await sleep(1500);
const src = readFileSync(probe, 'utf8');
const r = await send('Runtime.evaluate', { expression: `(async () => { ${src} })()`, awaitPromise: true, returnByValue: true });
if (r.result && r.result.exceptionDetails) console.log("EXC", JSON.stringify(r.result.exceptionDetails).slice(0, 1500));
const shot = await send('Page.captureScreenshot', {format:'png'}); (await import('node:fs')).writeFileSync(process.env.SHOT, Buffer.from(shot.result.data, 'base64')); console.log('shot', process.env.SHOT);
if (process.env.AX) { await send('Accessibility.enable'); const ax = await send('Accessibility.getFullAXTree'); const re = new RegExp(process.env.AX);
  const nodes = ax.result.nodes; const pick = nodes.filter(n => n.name && re.test(n.name.value || ''));
  console.log('AX total', nodes.length, 'ignored', nodes.filter(n => n.ignored).length);
  for (const n of pick.slice(0, 60)) console.log('AX', n.ignored ? 'IGNORED' : 'exposed', (n.role||{}).value, JSON.stringify((n.name||{}).value).slice(0,80), n.ignored ? JSON.stringify((n.ignoredReasons||[]).map(r => r.name)) : ''); }
if (logs.length) console.log('CONSOLE:\n' + logs.join('\n'));
ws.close(); ch.kill(); process.exit(0);
