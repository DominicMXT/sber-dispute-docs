// Проверка «откроется ли на Mac»: движок WebKit (как Safari) через Playwright, вид iPhone и Safari на ноутбуке.
// Запуск из этой папки: node maccheck.mjs [http://localhost:8767]  — без аргумента только file://
// Ловит: ошибки скриптов, console.error, неудачные загрузки, пустой экран, горизонтальную прокрутку.
import { webkit, devices } from 'playwright';
import { pathToFileURL } from 'node:url';
import { join, resolve } from 'node:path';
import { existsSync } from 'node:fs';

const ROOT = resolve(import.meta.dirname, '../../../..');          // корень продукта Sber500xDisrupt
const HTTP = process.argv[2] || null;
const PROTO = 'prototype/2026-10-04_fog-prototype-v3.html';
const PAGES = ['prototype/2026-10-04_fog-prototype-v2.html', 'dossier.html', 'landing/index.html', 'onboarding.html', 'zayavka.html', 'design/board/index.html'];
const VIEWS = { iphone: devices['iPhone 13'], mac: { viewport: { width: 1440, height: 900 }, deviceScaleFactor: 2 } };

const url = (rel, q = '') => HTTP ? `${HTTP}/${rel}${q}` : pathToFileURL(join(ROOT, rel)).href + q;
const out = [];
const browser = await webkit.launch();

const withTimeout = (p, ms, what) => Promise.race([p, new Promise((_, rej) => setTimeout(() => rej(new Error('тайм-аут ' + what)), ms))]);
async function probe(ctx, rel, q, kind) { try { return await withTimeout(probe0(ctx, rel, q, kind), 45000, rel + q); } catch (e) { return { rel, q, errs: [e.message] }; } }
async function probe0(ctx, rel, q, kind) {
  const page = await ctx.newPage(), errs = [];
  page.on('dialog', d => d.dismiss().catch(() => {}));
  process.stderr.write(`· ${rel}${q}
`);
  page.on('pageerror', e => errs.push('pageerror: ' + e.message));
  page.on('console', m => { if (m.type() === 'error') errs.push('console: ' + m.text().slice(0, 160)); });
  page.on('requestfailed', r => { const u = r.url(); if (!/fonts\.(googleapis|gstatic)/.test(u)) errs.push('failed: ' + u.slice(0, 120) + ' ' + (r.failure() || {}).errorText); });
  try { await page.goto(url(rel, q), { waitUntil: 'load', timeout: 20000 }); } catch (e) { errs.push('goto: ' + e.message.slice(0, 120)); }
  await page.waitForTimeout(kind === 'board' ? 2500 : 700);
  const r = await page.evaluate(() => {
    const vw = document.documentElement.clientWidth, sw = document.documentElement.scrollWidth;
    const view = document.querySelector('#view'), story = document.querySelector('#story.on');
    return { overflow: sw > vw + 1 ? sw - vw : 0, empty: view ? !(view.innerText.trim() || (story && story.innerText.trim())) : !document.body.innerText.trim(),
             frames: document.querySelectorAll('iframe').length, theme: document.documentElement.dataset.theme || '' };
  }).catch(e => ({ evalErr: e.message.slice(0, 120) }));
  if (kind === 'board') {
    let emptyFrames = 0;
    for (const f of page.frames().slice(1)) { const t = await withTimeout(f.evaluate(() => { const v = document.querySelector('#view'); return v ? v.innerText.trim().length : -1; }), 3000, 'кадр').catch(() => -2); if (t === 0) emptyFrames++; }
    r.emptyFrames = emptyFrames; r.checkedFrames = page.frames().length - 1;
  }
  await page.close().catch(() => {});
  return { rel, q, errs, ...r };
}

for (const [vname, vopt] of Object.entries(VIEWS)) {
  const ctx = await browser.newContext({ ...vopt });
  // прототип v3: все состояния
  const p0 = await ctx.newPage(); await p0.goto(url(PROTO)); await p0.waitForTimeout(500);
  const codes = await p0.evaluate(() => [...new Set(['fresh', 'mid', 'payday', 'partner', 'price', 'week', 'recon', 'done', 'offline', 'limit', 'format', 'botoff', 'used', ...Object.keys(V3_SCEN), 'anya-group2', 'anya-group3'])]);
  await p0.close();
  for (const c of codes) out.push({ view: vname, ...(await probe(ctx, PROTO, `?s=${encodeURIComponent(c)}&clean`, 'proto')) });
  // тёмная тема и переключатель (localStorage в WebKit на file://)
  const pt = await ctx.newPage(); await pt.goto(url(PROTO, '?s=themeSet&clean')); await pt.waitForTimeout(500);
  const dark = await pt.evaluate(async () => { const b = [...document.querySelectorAll('#view button')].find(x => x.textContent.trim() === 'Тёмная'); if (!b) return 'нет кнопки'; b.click(); await new Promise(r => setTimeout(r, 400)); return document.documentElement.dataset.theme; });
  await pt.reload(); await pt.waitForTimeout(500); const kept = await pt.evaluate(() => document.documentElement.dataset.theme);
  out.push({ view: vname, rel: PROTO, q: 'тема', errs: [], darkAfterClick: dark, darkAfterReload: kept }); await pt.close();
  for (const rel of PAGES) if (existsSync(join(ROOT, rel))) out.push({ view: vname, ...(await probe(ctx, rel, '', rel.includes('board') ? 'board' : 'page')) });
  await ctx.close();
}
await browser.close();

const bad = out.filter(x => (x.errs && x.errs.length) || x.overflow || x.empty || x.evalErr || x.emptyFrames || (x.darkAfterClick && (x.darkAfterClick !== 'dark' || x.darkAfterReload !== 'dark')));
console.log(`WebKit ${webkit.name()} · режим ${HTTP ? 'http' : 'file://'} · проверок ${out.length} · с замечаниями ${bad.length}`);
for (const x of bad) console.log(JSON.stringify(x));
const board = out.filter(x => x.checkedFrames != null).map(x => `${x.view}: доска — кадров ${x.checkedFrames}, пустых ${x.emptyFrames}`);
board.forEach(s => console.log(s));
out.filter(x => x.darkAfterClick).forEach(x => console.log(`${x.view}: тема — после нажатия ${x.darkAfterClick}, после перезагрузки ${x.darkAfterReload}`));
