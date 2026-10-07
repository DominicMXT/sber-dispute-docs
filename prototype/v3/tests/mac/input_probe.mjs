// Проба эталона Р2 по ТЗ 1.4.6 (input1007.py): node input_probe.mjs <путь к html>
import { createRequire } from 'module';
import { pathToFileURL } from 'url';
const require = createRequire(process.cwd() + '/package.json');
const { chromium } = require('playwright');
const f = pathToFileURL(process.argv[2]).href;
const b = await chromium.launch({ executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe' });
const errs = [], res = [];
const ok = (n, c, d) => res.push((c ? 'PASS ' : 'FAIL ') + n + (c ? '' : ' :: ' + d));
const p = await b.newPage({ viewport: { width: 375, height: 812 } }); p.on('pageerror', e => errs.push(e.message));

// ФТ-212: плашки
await p.goto(f + '?clean&s=chips'); await p.waitForTimeout(300);
let r = await p.evaluate(() => [...document.querySelectorAll('#sp-chips button')].map(x => x.textContent.replace(/\s+/g, ' ')));
ok('ПК-151: плашки «кофе · 300 ₽», «такси · 450 ₽», «Как вчера»; «обед» (1 запись) — нет', r.some(x => /^кофе · 300/.test(x)) && r.some(x => /^такси · 450/.test(x)) && r.includes('Как вчера') && !r.some(x => /обед/.test(x)), JSON.stringify(r));
r = await p.evaluate(() => { const n0 = me().spent.length; document.querySelector('[data-chip="0"]').click(); const v = $('#spend').value; const n1 = me().spent.length;
  $('#spend').value = v.replace(/\d+$/, '350'); $('#spendf').requestSubmit(); const s = me().spent.slice(n0); return { v, beforeSubmit: n1 - n0, s }; });
ok('ПК-151: касание подставляет фразу, сумму можно поменять до записи', r.beforeSubmit === 0 && /\d+$/.test(r.v) && r.s.length === 1 && r.s[0].v === 350, JSON.stringify(r));

// ФТ-213: «Как вчера»
r = await p.evaluate(() => { const n0 = me().spent.length; ACT.spYd(); const rows = [...document.querySelectorAll('#sheet [data-yd]')];
  const t = $('#sheet').innerText; rows[1].checked = false; ACT.spYdGo(); return { rows: rows.length, t: /кофе/.test(t) && /такси/.test(t), s: me().spent.slice(n0) }; });
ok('ПК-152: «Как вчера» — обе вчерашние, снята такси → записан только кофе', r.rows === 2 && r.t && r.s.length === 1 && r.s[0].t === 'кофе', JSON.stringify(r));
r = await p.evaluate(() => { me().hist = me().hist.filter(x => x.d !== 1); render(true); return [...document.querySelectorAll('#sp-chips button')].map(x => x.textContent); });
ok('ПК-152: вчера пусто → нет «Как вчера»', !r.includes('Как вчера'), JSON.stringify(r));
r = await p.evaluate(() => { me().hist = []; render(true); return !!document.getElementById('sp-chips'); });
ok('новый человек без истории — плашек нет', r === false, String(r));

// ФТ-216: карточка для 2+ трат
r = await p.evaluate(() => { const n0 = me().spent.length; $('#spend').value = 'кофе 300 и такси 450 и обед 400'; $('#spendf').requestSubmit();
  const rows = document.querySelectorAll('#sheet .ms-row').length, written = me().spent.length - n0; document.querySelector('#sheet [data-msrm="1"]').click();
  const rows2 = document.querySelectorAll('#sheet .ms-row').length; ACT.msAll(); return { rows, written, rows2, s: me().spent.slice(n0) }; });
ok('ПК-153: 3 траты → карточка, до «Записать все» ничего не записано; «убрать» такси → записаны кофе и обед',
  r.rows === 3 && r.written === 0 && r.rows2 === 2 && r.s.length === 2 && r.s[0].v === 300 && r.s[1].v === 400, JSON.stringify(r));
r = await p.evaluate(() => { const n0 = me().spent.length; $('#spend').value = 'кофе 300'; $('#spendf').requestSubmit(); return { n: me().spent.length - n0, sheet: S.sheet }; });
ok('ПК-153: одна трата — без карточки, сразу', r.n === 1 && !r.sheet, JSON.stringify(r));

// ФТ-214–215: пропущенные дни
await p.goto(f + '?clean&s=gap'); await p.waitForTimeout(300);
r = await p.evaluate(() => { const g = document.getElementById('sp-gap'); return g && g.innerText.replace(/\s+/g, ' '); });
ok('ПК-154: 3 дня без записей → приглашение загрузить выписку', r && /Пропустили дни/.test(r) && /Загрузить/.test(r) && /Не сейчас/.test(r), String(r));
r = await p.evaluate(() => { ACT.gapSkip(); return !!document.getElementById('sp-gap'); });
ok('ПК-154: «Не сейчас» → больше не показывается', r === false, String(r));
r = await p.evaluate(() => { const m = me(); m.gapSkip = false; render(true); ACT.gapLoad(); const t = $('#sheet').innerText.replace(/\s+/g, ' ');
  ACT.gapOk(); return { t, gap: !!document.getElementById('sp-gap'), days: m.gapDays.length, keys: Object.keys(m.gapDays[0]) }; });
ok('ПК-154: выписка → суммы по 3 дням, без описаний; приглашение ушло', /Подставил траты за 3 дня/.test(r.t) && /5 110|5 110/.test(r.t) && !r.gap && r.days === 3 && r.keys.join() === 'd,v', JSON.stringify(r));
r = await p.evaluate(() => { V3_SCEN.gap(); $('#spend').value = 'кофе 300'; $('#spendf').requestSubmit(); return !!document.getElementById('sp-gap'); });
ok('запись сегодня → приглашения нет', r === false, String(r));

console.log(res.join('\n')); console.log('PASS', res.filter(x => x.startsWith('PASS')).length, '/', res.length, '· errors', errs.length, errs.slice(0, 3));
await b.close();
