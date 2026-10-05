// Повторная проверка замечаний maccheck: туман на file://, доска через http, ширина onboarding.html
import { webkit, devices } from 'playwright';
import { pathToFileURL } from 'node:url';
import { join, resolve } from 'node:path';
const ROOT = resolve(import.meta.dirname, '../../../..'), HTTP = process.argv[2] || 'http://localhost:8767';
const b = await webkit.launch();
for (const [vn, vo] of [['iphone', devices['iPhone 13']], ['mac', { viewport: { width: 1440, height: 900 } }]]) {
  const c = await b.newContext(vo);
  for (const code of ['group2', 'group2step', 'nextgoal', 'anya-group2', 'mid']) {
    const p = await c.newPage(), errs = []; p.on('console', m => m.type() === 'error' && errs.push(m.text().slice(0, 90))); p.on('pageerror', e => errs.push('pageerror ' + e.message));
    await p.goto(pathToFileURL(join(ROOT, 'prototype/2026-10-04_fog-prototype-v3.html')).href + `?s=${code}&clean`); await p.waitForTimeout(900);
    const fog = await p.evaluate(() => [...document.querySelectorAll('.photo .fog')].map(f => f.classList.contains('fogfb') ? 'запасной' : (f.src.startsWith('data:image/jpeg') ? 'канвас' : 'ещё нет')).join(','));
    console.log(vn, code, 'ошибок:', errs.length, '| туман:', fog); await p.close();
  }
  const pb = await c.newPage(), berrs = []; pb.on('pageerror', e => berrs.push(e.message));
  const t0 = Date.now(); await pb.goto(`${HTTP}/design/board/index.html`, { waitUntil: 'load', timeout: 180000 });
  await pb.evaluate(() => document.querySelectorAll('iframe').forEach(f => f.loading = 'eager')); await pb.waitForTimeout(15000);
  let empty = 0, ok = 0; for (const f of pb.frames().slice(1)) { const n = await f.evaluate(() => { const v = document.querySelector('#view'), s = document.querySelector('#story.on'); return (v ? v.innerText.trim().length : 0) + (s ? s.innerText.trim().length : 0); }).catch(() => -1); n > 0 ? ok++ : empty++; }
  console.log(vn, 'доска http: загрузка', Math.round((Date.now() - t0) / 1000), 'с · экранов с текстом', ok, '· пустых', empty, '· ошибок', berrs.length); await pb.close();
  if (vn === 'iphone') { const po = await c.newPage(); await po.goto(pathToFileURL(join(ROOT, 'onboarding.html')).href); await po.waitForTimeout(500);
    console.log('onboarding шире экрана:', JSON.stringify(await po.evaluate(() => { const w = document.documentElement.clientWidth; return [...document.querySelectorAll('body *')].filter(e => e.getBoundingClientRect().right > w + 1).slice(0, 4).map(e => e.tagName + '.' + e.className + ' ' + Math.round(e.getBoundingClientRect().right) + ' «' + (e.textContent || '').trim().slice(0, 30) + '»'); }))); await po.close(); }
  await c.close();
}
await b.close();
