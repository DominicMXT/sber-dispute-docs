// Проверка карты покрытия v3: каждый код состояния из карты открывается в прототипе «Туман» v3 без сбоев.
// Запуск из любой папки:  node prototype/v3/tests/cov/covcheck.mjs [путь к карте .md] [--widths 375,1200]
// По умолчанию карта — prototype/2026-10-05_coverage-v3.md, ширины 375 и 1200.
// Браузер — Chromium из установленного Chrome (Playwright берётся из tests/mac/node_modules; путь к Chrome — переменная CHROME).
//
// На каждый код (?clean&s=<код>) проверяется:
//   js       — нет pageerror и console.error (кроме недоступных шрифтов Google);
//   known    — код понимает маршрутизатор прототипа (V3_SCEN, сценарии пульта, экраны SCR, листы SH, ссылки), иначе экран молча остаётся «mid»;
//   text     — нет NaN / undefined / Invalid Date / null / [object / Infinity ни в видимом тексте, ни в свёрнутых блоках экрана;
//   overflow — нет горизонтальной прокрутки страницы и ни один видимый элемент не выходит за рамку экрана #app
//              (элементы внутри контейнеров с overflow-x ≠ visible не считаются: они обрезаны или прокручиваются внутри);
//   one      — показан ровно один экран: один непустой #view, поверх — не больше одного слоя (лист или сторис),
//              лист/экран совпадает с кодом, пульт скрыт (?clean).
// Плюс сценарии нажатиями K1–K7 для пограничных случаев БТ, у которых нет своего кода состояния (только на 375 px).
import { createRequire } from 'node:module';
import { pathToFileURL } from 'node:url';
import { readFileSync, existsSync } from 'node:fs';
import { resolve, join } from 'node:path';

const HERE = import.meta.dirname;
const PROTO_DIR = resolve(HERE, '../../..');                       // папка prototype
const ROOT = resolve(PROTO_DIR, '..');                            // корень продукта
const HTML = resolve(process.env.COV_HTML || join(PROTO_DIR, '2026-10-04_fog-prototype-v3.html'));   // COV_HTML — подменить файл (фальсификация проверок)
const BOARD = join(ROOT, 'design/board/build_board.py');
const require = createRequire(join(HERE, '../mac/package.json'));
const { chromium } = require('playwright');
const CHROME = process.env.CHROME || 'C:/Program Files/Google/Chrome/Application/chrome.exe';

const args = process.argv.slice(2);
const wi = args.indexOf('--widths');
const WIDTHS = wi >= 0 ? args.splice(wi, 2)[1].split(',').map(Number) : [375, 1200];
const MAP = resolve(args[0] || join(PROTO_DIR, '2026-10-05_coverage-v3.md'));
if (!existsSync(MAP)) { console.error('нет карты: ' + MAP); process.exit(2); }

// ── коды из карты: столбец «Состояния (код)» в разделах «Требования» и «Пограничные случаи»
const md = readFileSync(MAP, 'utf8');
const body = md.split('## Требования')[1].split('## Решения')[0];
const decisions = md.split('## Решения')[1] || '';
const codes = [];
for (const line of body.split('\n')) {
  if (!/^\| [0-9]/.test(line)) continue;
  const cells = line.split('|').map(s => s.trim());
  const cell = cells[cells.length - 3];                          // предпоследний столбец таблицы — «Состояния (код)»
  for (const m of cell.matchAll(/`([A-Za-z0-9-]+)`/g)) if (!codes.includes(m[1])) codes.push(m[1]);
}
const nTable = codes.length;                                       // коды раздела «Решения прототипа» тоже открываются
for (const m of decisions.matchAll(/`([A-Za-z][A-Za-z0-9-]*)`/g)) if (!codes.includes(m[1])) codes.push(m[1]);

// ── что понимает маршрутизатор ?s= (сценарии пульта и ссылки объявлены внутри IIFE — читаем из исходника)
const src = readFileSync(HTML, 'utf8');
const mSC = src.match(/const SC = \[([^\]]*)\]/), mLINK = src.match(/const LINK = \{([^}]*)\}/);   // объявлены один раз — в маршрутизаторе ?s=
if (!mSC || !mLINK) { console.error('в прототипе не найден маршрутизатор ?s= (const SC / const LINK) — сборка изменилась'); process.exit(2); }
const SC = [...mSC[1].matchAll(/'([^']+)'/g)].map(m => m[1]);
const LINK = [...mLINK[1].matchAll(/(\w+):'/g)].map(m => m[1]);
const boardSrc = existsSync(BOARD) ? readFileSync(BOARD, 'utf8') : '';  // только список GROUPS, без палитры SW
const BOARD_CODES = [...(boardSrc.split('GROUPS = [')[1] || '').split('n_states =')[0].matchAll(/\("([A-Za-z0-9-]+)", "/g)].map(m => m[1]);

const base = pathToFileURL(HTML).href;
const browser = await chromium.launch({ executablePath: CHROME });
const BAD = /NaN|undefined|Invalid Date|\bnull\b|\[object|Infinity/;
const isFontNoise = t => /fonts\.(googleapis|gstatic)/.test(t);

async function openPage(ctx, q) {
  const page = await ctx.newPage(), errs = [];
  page.on('pageerror', e => errs.push('pageerror: ' + e.message.slice(0, 160)));
  page.on('console', m => { if (m.type() === 'error' && !isFontNoise(m.text() + (m.location().url || ''))) errs.push('console: ' + m.text().slice(0, 160)); });
  page.on('dialog', d => d.dismiss().catch(() => {}));
  try { await page.goto(base + q, { waitUntil: 'domcontentloaded', timeout: 20000 }); }
  catch (e) { errs.push('goto: ' + e.message.slice(0, 120)); }
  await page.evaluate(() => Promise.race([document.fonts ? document.fonts.ready : 0, new Promise(r => setTimeout(r, 3000))])).catch(() => {});
  await page.waitForTimeout(600);
  return { page, errs };
}

async function probe(ctx, code) {
  const { page, errs } = await openPage(ctx, '?clean&s=' + encodeURIComponent(code));
  const k = code.startsWith('anya-') ? code.slice(5) : code;
  const r = await page.evaluate(({ k, SC, LINK }) => {
    const open = !!document.querySelector('#sheetwrap.open'), story = document.querySelector('#story').classList.contains('on');
    const known = !!(V3_SCEN[k] || SC.includes(k) || SCR[k] || SH[k] || LINK.includes(k));
    const vis = el => el && el.offsetParent !== null ? el.innerText : '';
    const text = [vis(document.querySelector('#view')), vis(document.querySelector('#bottom')), vis(document.querySelector('#tabs')),
      document.querySelector('#pushwrap').innerText, open ? document.querySelector('#sheet').innerText : '', story ? document.querySelector('#stxt').innerText : ''].join('\n');
    const full = text + '\n' + document.querySelector('#view').textContent + (open ? document.querySelector('#sheet').textContent : '');
    const bad = (full.match(/.{0,30}(NaN|undefined|Invalid Date|\bnull\b|\[object|Infinity).{0,30}/g) || []).slice(0, 3);
    // ширина: страница и элементы относительно рамки экрана
    const de = document.documentElement, app = document.querySelector('#app').getBoundingClientRect();
    const skip = el => (el.closest('#sheetwrap') && !open) || (el.closest('#story') && !story) || (el.closest('#toast') && !el.closest('#toast').classList.contains('on'));
    // Обрезка контейнером экрана (#view: overflow-x:hidden, лист, низ) вылет не исправляет, а прячет — текст срезан у края; такие элементы проверяем.
    // Обрезка или прокрутка внутри компонента (.photo, .seg, полка .v3-shelf) — замысел; вылет внутри них не считаем.
    const SCREEN = new Set(['view', 'sheet', 'sheetwrap', 'bottom', 'tabs', 'pushwrap', 'story']);
    const clipped = el => { for (let a = el.parentElement; a && a.id !== 'app'; a = a.parentElement) if (!SCREEN.has(a.id) && getComputedStyle(a).overflowX !== 'visible') return true; return false; };
    const name = el => `${el.tagName.toLowerCase()}${el.id ? '#' + el.id : ''}${el.className && typeof el.className === 'string' ? '.' + el.className.split(' ')[0] : ''}`;
    const wide = [];
    for (const el of document.querySelectorAll('#app *')) {
      if (skip(el) || clipped(el)) continue;
      const cs = getComputedStyle(el); if (cs.display === 'none' || cs.visibility === 'hidden') continue;
      const b = el.getBoundingClientRect(); if (!b.width || !b.height) continue;
      if (b.right > app.right + 1 || b.left < app.left - 1) wide.push(`${name(el)} ${Math.round(b.left - app.left)}…${Math.round(b.right - app.left)} при ширине ${Math.round(app.width)}`);
    }
    for (const id of SCREEN) { const el = document.getElementById(id); if (el && !skip(el) && el.scrollWidth > el.clientWidth + 1) wide.push(`#${id}: содержимое шире на ${el.scrollWidth - el.clientWidth} px`); }
    const pageOver = de.scrollWidth > de.clientWidth + 1 ? de.scrollWidth - de.clientWidth : 0;
    // ровно один экран
    const views = document.querySelectorAll('#view').length, viewText = document.querySelector('#view').innerText.trim();
    const layers = (open ? 1 : 0) + (story ? 1 : 0);
    const hidden = el => !el || getComputedStyle(el).display === 'none';
    return { known, bad, wide: wide.slice(0, 3), nWide: wide.length, pageOver, views, empty: !viewText && !story, layers, scr: S.scr, sheet: S.sheet, story,
             pultHidden: hidden(document.querySelector('#panel')) && hidden(document.querySelector('#fab')), inSCR: !!SCR[k], inSH: !!SH[k], inV3: !!V3_SCEN[k] };
  }, { k, SC, LINK }).catch(e => ({ evalErr: e.message.slice(0, 160) }));
  await page.close().catch(() => {});
  const fails = [];
  if (r.evalErr) fails.push('eval: ' + r.evalErr);
  else {
    if (errs.length) fails.push('js: ' + errs.join(' | '));
    if (!r.known) fails.push('known: код не понимает маршрутизатор — показан экран по умолчанию (' + r.scr + ')');
    if (r.bad.length) fails.push('text: ' + r.bad.join(' | '));
    if (r.pageOver) fails.push(`overflow: страница шире окна на ${r.pageOver} px`);
    if (r.nWide) fails.push(`overflow: ${r.nWide} элемент(ов) за рамкой экрана: ` + r.wide.join('; '));
    const sheetOk = !r.inSH || r.inV3 || r.sheet === k;
    const scrOk = !r.inSCR || r.inV3 || r.inSH || ['answer', 'stmtResult'].includes(k) || r.scr === k;
    const storyOk = r.story === (k === 'fresh');
    if (r.views !== 1 || r.empty || r.layers > 1 || !sheetOk || !scrOk || !storyOk || !r.pultHidden)
      fails.push(`one: #view×${r.views}${r.empty ? ', пустой' : ''}, слоёв поверх ${r.layers}, экран ${r.scr}, лист ${r.sheet}, сторис ${r.story}${r.pultHidden ? '' : ', пульт виден'}`);
  }
  return fails;
}

// ── сценарии нажатиями: пограничные случаи без своего кода. Ожидание — как в БТ 1.5, раздел 7.
const PH = (text) => () => { $('#phrase').value = text; ACT.phraseGo(); };
const SCEN = [
  { id: 'K1', cs: 'случай 4', what: 'один пропуск — один вопрос, два — поля', start: 'phrase',
    act: () => { const out = {}; $('#phrase').value = 'Ноутбук 90 тысяч к 1 марта'; ACT.phraseGo(); out.one = S.scr + ' :: ' + $('#view').innerText.replace(/\n+/g, ' ').slice(0, 150);
      go('phrase'); $('#phrase').value = 'Ноутбук 90 тысяч'; ACT.phraseGo(); out.two = S.scr; return out; },
    ok: o => /^clarify/.test(o.one) && /Сколько отложите сами/.test(o.one) && o.two === 'fields' },
  { id: 'K2', cs: 'случай 5', what: 'срок в прошлом → «Срок уже прошёл — на какую дату переносим?»', start: 'phrase',
    act: () => { $('#phrase').value = 'Ноутбук 90 тысяч к 1 сентября 2026, я могу 40'; ACT.phraseGo(); return S.scr + ' :: ' + $('#view').innerText.replace(/\n+/g, ' ').slice(0, 150); },
    ok: o => /прош/i.test(o) && !/^answer/.test(o) },
  { id: 'K3', cs: 'случай 6', what: 'своя часть больше цены → «вносите на N больше — уменьшить?»', start: 'phrase',
    act: () => { $('#phrase').value = 'Ноутбук 90 тысяч к 1 марта, я могу 120'; ACT.phraseGo(); return S.scr + ' :: ' + $('#view').innerText.replace(/\n+/g, ' ').slice(0, 170); },
    ok: o => /больше/i.test(o) || !/ваша часть 120\s000/.test(o) },
  { id: 'K4', cs: 'случай 11', what: '«на себя» в минус → нейтральный текст и сумма на завтра, без красного', start: 'today',
    act: async () => { $('#spend').value = 'кофе 2000'; $('#spendf').requestSubmit(); await new Promise(r => setTimeout(r, 800));   // главное число анимируется
      const red = [...document.querySelectorAll('#view *')].some(x => { const m = (getComputedStyle(x).color.match(/\d+/g) || []).map(Number); return m[0] > 150 && m[1] < 90 && m[2] < 90; });
      return { t: $('#view').innerText.replace(/\n+/g, ' ').slice(0, 160), red }; },
    ok: o => /больше плана/.test(o.t) && /Завтра на себя/.test(o.t) && !o.red },
  { id: 'K5', cs: 'случай 12', what: 'трата без подписи «300» записана', start: 'today',
    act: async () => { $('#spend').value = '300'; $('#spendf').requestSubmit(); await new Promise(r => setTimeout(r, 800)); return $('#view').innerText.replace(/\n+/g, ' ').slice(0, 200); },
    ok: o => /без подписи\s+300\s₽/.test(o) },
  { id: 'K6', cs: 'случай 13', what: 'две покупки → «на себя» учитывает «в день» обеих', start: 'today',
    act: () => { const per = () => { const m = $('#view').textContent.match(/На покупки:\s*([\d\s ]+)₽ в день/); return m ? +m[1].replace(/\D/g, '') : null; };
      const a = per(); go('phrase'); $('#phrase').value = 'Ноутбук 90 тысяч к 1 марта, я могу 40'; ACT.phraseGo(); ACT.commit(); go('today'); const b = per();
      return { before: a, after: b, active: S.purchases.filter(p => p.state === 'active').length }; },
    ok: o => o.active === 2 && o.before > 0 && o.after > o.before },
  { id: 'K7', cs: 'случай 22', what: 'сумма в валюте → вопрос «сколько в рублях?»', start: 'phrase',
    act: () => { $('#phrase').value = 'Ноутбук 1000 долларов к 1 марта, я могу 40'; ACT.phraseGo(); return S.scr + ' :: ' + $('#view').innerText.replace(/\n+/g, ' ').slice(0, 150); },
    ok: o => /рубл/i.test(o) && !/^answer/.test(o) },
];

async function runScen(ctx, s) {
  const { page, errs } = await openPage(ctx, '?clean&s=' + s.start);
  let out; try { out = await page.evaluate(s.act); await page.waitForTimeout(200); } catch (e) { out = 'eval: ' + e.message.slice(0, 160); }
  await page.close().catch(() => {});
  const pass = typeof out !== 'string' || !out.startsWith('eval:') ? s.ok(out) && !errs.length : false;
  return { pass, out, errs };
}

const ver = browser.version();
const lines = [];
let okAll = 0, nAll = 0;
const failList = [];
for (const w of WIDTHS) {
  const ctx = await browser.newContext({ viewport: { width: w, height: w < 700 ? 812 : 900 } });
  let ok = 0;
  for (const c of codes) { const f = await probe(ctx, c); if (!f.length) ok++; else failList.push(`${w} px · ${c}: ${f.join(' ; ')}`); }
  await ctx.close();
  lines.push(`${w} px: ${ok} из ${codes.length} ОК`); okAll += ok; nAll += codes.length;
}
const sctx = await browser.newContext({ viewport: { width: 375, height: 812 } });
const sres = [];
for (const s of SCEN) sres.push({ s, ...(await runScen(sctx, s)) });
await sctx.close();
await browser.close();

if (process.env.COV_HTML) console.log('ПОДМЕНА прототипа: ' + HTML);
console.log(`covcheck · Chromium ${ver} · карта ${MAP.replace(ROOT, '').replace(/\\/g, '/').replace(/^\//, '')} · кодов в карте ${codes.length} (в таблицах ${nTable}, только в «Решениях» ${codes.length - nTable})`);
console.log(`Состояния: ${okAll} из ${nAll} ОК (${lines.join('; ')})`);
if (failList.length) { console.log('Провалы состояний:'); failList.forEach(x => console.log('  ' + x)); } else console.log('Провалов состояний нет');
const sp = sres.filter(x => x.pass).length;
console.log(`Сценарии нажатиями (375 px): ${sp} из ${sres.length} ОК`);
for (const x of sres) console.log(`  ${x.pass ? 'ОК  ' : 'FAIL'} ${x.s.id} · ${x.s.cs} · ${x.s.what}${x.pass ? '' : ' :: ' + JSON.stringify(x.out) + (x.errs.length ? ' :: ' + x.errs.join(' | ') : '')}`);
const notInMap = BOARD_CODES.filter(c => !codes.includes(c));
const notOnBoard = codes.filter(c => !BOARD_CODES.includes(c));
console.log(`Доска (build_board.py): кодов ${BOARD_CODES.length}, не привязаны к требованиям карты ${notInMap.length}${notInMap.length ? ': ' + notInMap.join(', ') : ''}`);
console.log(`Коды карты вне доски: ${notOnBoard.length}${notOnBoard.length ? ': ' + notOnBoard.join(', ') : ''}`);
process.exit(failList.length || sp < sres.length ? 1 : 0);
