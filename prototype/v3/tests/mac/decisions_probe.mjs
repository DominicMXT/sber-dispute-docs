// Проба решений владельца 05.10 (decisions.py): node decisions_probe.mjs <путь к html>
import { createRequire } from 'module';
import { pathToFileURL } from 'url';
const require = createRequire(process.cwd() + '/package.json');
const { chromium } = require('playwright');
const f = pathToFileURL(process.argv[2]).href;
const b = await chromium.launch({ executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe' });
const errs = [], res = [];
const ok = (n, c, d) => res.push((c ? 'PASS ' : 'FAIL ') + n + (c ? '' : ' :: ' + d));
const pg = async q => { const p = await b.newPage({ viewport: { width: 375, height: 812 } }); p.on('pageerror', e => errs.push(e.message)); await p.goto(f + q); await p.waitForTimeout(300); return p; };
const vt = p => p.evaluate(() => document.querySelector('#view').innerText.replace(/\s+/g, ' '));
/* «уже есть N» */
let p = await pg('?clean&s=fresh');
let r = await p.evaluate(() => { me().consent = true; S.draft = null; go('phrase'); render(); $('#phrase').value = 'Ноутбук 95 000 к 1 марта, уже есть 20 тысяч, плачу сам'; ACT.phraseGo();
  return { scr: S.scr, have: S.draft && S.draft.have, share: S.draft && S.draft.share, price: S.draft && S.draft.price }; });
ok('«уже есть 20 тысяч» → have 20 000, цена и часть 95 000', r.have === 20000 && r.price === 95000 && r.share === 95000 && r.scr === 'answer', JSON.stringify(r));
let t = await vt(p);
const days = await p.evaluate(() => Math.max(1, Math.round((S.draft.dl - now()) / DAY)));
const per = Math.ceil(75000 / days);
ok('план от остатка: ' + per + ' ₽ в день, в эхе «уже есть 20 000 ₽» и цена 95 000', t.includes(per.toLocaleString('ru-RU').replace(/\u00a0/g, ' ')) && /уже есть 20\s000\s₽/.test(t) && /95\s000\s₽/.test(t) && !/Уже отложенное отметьте/.test(t), 'per=' + per + ' :: ' + t.slice(0, 400));
r = await p.evaluate(() => { ACT.v3save(); ACT.loginVk(); const q = S.purchases[S.purchases.length - 1]; return { saved: q.saved[S.who], name: q.name }; });
ok('после сохранения отложено 20 000', r.saved === 20000, JSON.stringify(r));
/* название и цена после сохранения */
r = await p.evaluate(() => { const q = S.purchases[S.purchases.length - 1]; S.cur = q.id; S.pid = q.id; go('purchase'); openSheet('change'); const btns = $('#sheet').innerText;
  ACT.dEditName(); $('#deditv').value = 'Ноутбук для учёбы'; $('#deditf').requestSubmit(); const n = P().name;
  ACT.dEditPrice(); $('#deditv').value = '10 000'; $('#deditf').requestSubmit(); const err = (document.getElementById('deditv-err') || {}).textContent;
  $('#deditv').value = '120 000'; $('#deditf').requestSubmit(); return { btns: /Поменять название/.test(btns) && /Поменять цену/.test(btns), n, err, price: P().price, share: P().share[S.who], sheet: S.sheet }; });
ok('«⋯» → поменять название и цену', r.btns && r.n === 'Ноутбук для учёбы', JSON.stringify(r));
ok('цена меньше отложенного — ошибка; 120 000 — цена и своя часть пересчитаны', /не может быть меньше/.test(r.err) && r.price === 120000 && r.share === 120000 && !r.sheet, JSON.stringify(r));
/* слова */
r = await p.evaluate(() => ({ tabs: $('#tabs').innerText, view: document.querySelector('#view').innerText }));
ok('вкладка «Цели», нет «Покупки»', /Цели/.test(r.tabs) && !/Покупки/.test(r.tabs), r.tabs);
await p.close();
p = await pg('?clean&s=consent'); t = await p.evaluate(() => document.body.innerText);
ok('согласие: «Принимаю, дальше»', /Принимаю, дальше/.test(t) && !/Согласен, дальше/.test(t), t.slice(0, 200));
await p.close();
p = await pg('?clean&s=dayprice'); r = await p.evaluate(() => document.querySelector('#view').innerText);
ok('«влезет ли»: «Куплено», не «Купил»', /Куплено/.test(r) && !/\bКупил\b/.test(r), r.slice(0, 300));
await p.close();
p = await pg('?clean&s=login'); r = await p.evaluate(() => $('#sheet').innerText);
ok('лист входа: VK ID и Яндекс ID, без Сбер ID и Max', /VK ID/.test(r) && /Яндекс ID/.test(r) && !/Сбер ID/.test(r) && !/Max/.test(r), r);
await p.close();
console.log(res.join('\n')); console.log('PASS', res.filter(x => x.startsWith('PASS')).length, '/', res.length, '· errors', errs.length, errs.slice(0, 3));
await b.close();
