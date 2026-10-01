// Контрольные расчёты для приложения Б ТЗ. Берёт чистые функции из прототипа и считает на дате 03.10.2026.
// Запуск: node tools/vectors.js > vectors.json  (вызывает tools/build_docs.py)
const fs = require('fs'), path = require('path');
const ROOT = path.join(__dirname, '..');
const L = fs.readFileSync(path.join(ROOT, 'prototype', '2026-09-24_mvp-prototype.html'), 'utf8').split('\n');
const a = L.findIndex(l => l.startsWith('const DAY=864e5')), b = L.findIndex(l => l.startsWith('/* ---------- навигация'));
const c = L.findIndex(l => l.startsWith('const CATS=')), d = L.findIndex(l => l.startsWith('function autoPick'));
let code = [...L.slice(a, b), ...L.slice(c, d + 1)].join('\n')
  .replace('const today=()=>{const d=new Date();d.setHours(0,0,0,0);return d};', 'const today=()=>new Date(2026,9,3);');
global.window = {}; global.localStorage = { getItem() { return null }, setItem() {} }; global.document = { getElementById() { return null } };
const p = new Function(code + ';return {today,addDays,iso,fromIso,parsePhrase,maskPII,calc,daily,afford,nextPay,maskDesc,parseCSV,analyze,tipsFor,autoPick,demoOps,cleanUrl,setS:x=>{S=x},fresh};')();
const I = x => x ? p.iso(x) : null;

// Б.1 фразы — ожидания пишутся руками (это спецификация для GigaChat), правила прототипа — для сравнения
const PH = [
 ['котёл 40 тысяч к 15 ноября, я могу 25', 'Котёл', 40000, '2026-11-15', 25000, ''],
 ['кровать 60к к новому году, моя часть 30', 'Кровать', 60000, '2026-12-31', 30000, ''],
 ['холодильник 55 000 через два месяца, плачу сам', 'Холодильник', 55000, '2026-12-03', 55000, ''],
 ['ремонт ванной 150 тысяч к лету, я внесу 70 тысяч', 'Ремонт ванной', 150000, '2027-06-01', 70000, ''],
 ['диван сорок тысяч к 20.12, с меня 20', 'Диван', 40000, '2026-12-20', 20000, ''],
 ['отпуск 200 тысяч в июле, могу 120', 'Отпуск', 200000, '2027-07-15', 120000, ''],
 ['стиральная машина 35 тыс до 1 ноября, я могу 15 тыс', 'Стиральная машина', 35000, '2026-11-01', 15000, ''],
 ['пылесос 25к через месяц, беру сам', 'Пылесос', 25000, '2026-11-03', 25000, ''],
 ['машина 1,2 млн через полгода, я могу 600 тысяч', 'Машина', 1200000, '2027-04-03', 600000, ''],
 ['котёл 40 тысяч, я могу 25', 'Котёл', 40000, null, 25000, 'нет срока → вопрос'],
 ['котёл к 15 ноября, я могу 25', 'Котёл', null, '2026-11-15', 25000, 'нет суммы → вопрос'],
 ['котёл 40 тысяч к 15 ноября', 'Котёл', 40000, '2026-11-15', null, 'нет своей части → вопрос'],
 ['котёл 40 тысяч к 1 октября 2026, я могу 25', 'Котёл', 40000, '2026-10-01', 25000, 'срок прошёл → вопрос'],
 ['ноутбук 90 тыс к 10 декабря, с меня 50, карта 2202 2000 1234 5678', 'Ноутбук', 90000, '2026-12-10', 50000, 'карта скрыта до модели'],
 ['кухня 300 тысяч к весне, я внесу 100 тысяч, мой номер +7 916 000-00-00', 'Кухня', 300000, '2027-03-01', 100000, 'телефон скрыт до модели'],
 ['телевизор 500 евро к 1 декабря, я могу 250', 'Телевизор', 500, '2026-12-01', 250, 'не рубли → вопрос'],
 ['шуба 80 тысяч к 25 декабря', 'Шуба', 80000, '2026-12-25', null, 'нет своей части → вопрос'],
 ['велосипед 45000 к 1 мая, я могу 45000', 'Велосипед', 45000, '2027-05-01', 45000, ''],
 ['коляска 30 тысяч через 3 недели, могу 10', 'Коляска', 30000, '2026-10-24', 10000, ''],
 ['купить матрас за 28 тысяч к 1 ноября, я могу 18', 'Матрас', 28000, '2026-11-01', 18000, ''],
];
const phrases = PH.map(([t, title, sum, date, share, note]) => { const m = p.maskPII(t), g = p.parsePhrase(m.t);
  return { t, masked: m.t, title, sum, date, share, note, rules_same: g.sum === sum && g.share === share && I(g.date) === date }; });

// Б.2 расчёт покупки
const base = { id: 'p', title: 'Котёл', sum: 40000, share: 25000, partnerShare: null, saved: 0, partnerSaved: 0, date: '2026-11-15', created: '2026-10-03' };
const CV = [['Моя часть, партнёра нет', {}], ['Партнёр вносит 15 000', { partnerShare: 15000 }], ['Вдвоём больше суммы (случай 6)', { partnerShare: 20000 }],
 ['Уже отложено 9 000', { saved: 9000, created: '2026-09-20' }], ['Плачу сам', { share: 40000 }], ['Срок завтра', { date: '2026-10-04' }], ['Отстаёт от плана', { saved: 1000, created: '2026-09-03' }]];
const calc = CV.map(([name, o]) => { const inp = Object.assign({}, base, o), r = p.calc(inp);
  return { name, sum: inp.sum, share: inp.share, partner: inp.partnerShare || 0, saved: inp.saved, date: inp.date, created: inp.created, days: r.days, gap: r.gap, over: r.over, per_day: r.perDay, collected: r.collected, on_plan: r.onPlan }; });

// Б.3 «сегодня на себя»
const act = o => Object.assign({}, base, { status: 'active' }, o || {});
const dv = d => ({ reserve: d.reserve, per: d.per, spent: d.spent, left: d.left, next_pay: I(d.np), to_pay: d.toPay });
p.setS(Object.assign(p.fresh(), { purchases: [act()], inc: 80000, must: 30000, payDays: [10, 25], spends: [{ day: '2026-10-03', v: 300 }, { day: '2026-10-03', v: 450 }, { day: '2026-10-02', v: 900 }] }));
const d1 = dv(p.daily());
p.setS(Object.assign(p.fresh(), { purchases: [act(), act({ id: 'q', title: 'Диван', sum: 30000, share: 15000, date: '2026-12-31' })], inc: 80000, must: 30000, payDays: [10, 25], spends: [{ day: '2026-10-03', v: 1900 }] }));
const d2 = dv(p.daily());

// Б.4 напоминание в день зарплаты: резерв в день × дней до следующей выплаты после ближайшей, до сотни
const pd = (reserve, days) => { const d1 = p.nextPay(days); let d2 = null; for (let k = 1; k < 62; k++) { const x = p.addDays(d1, k); if (days.includes(x.getDate())) { d2 = x; break; } }
  const gap = Math.round((d2 - d1) / 864e5); return { pay: I(d1), next: I(d2), days: gap, reserve, sum: Math.round(reserve * gap / 100) * 100 }; };
const push1 = pd(d1.reserve, [10, 25]), push2 = pd(d2.reserve, [10, 25]);

// Б.8 «влезет ли» — на тех же данных, что первая строка Б.3
p.setS(Object.assign(p.fresh(), { purchases: [act()], inc: 80000, must: 30000, payDays: [10, 25], spends: [{ day: '2026-10-03', v: 300 }, { day: '2026-10-03', v: 450 }] }));
const dA = p.daily(); const afford = [300, 3000, 7000].map(x => Object.assign({ v: x, left: dA.left, per: dA.per, to_pay: dA.toPay }, p.afford(x, dA)));

// Б.5 выписка: синтетика в формате CSV Т-Банка
const ops = p.demoOps(84), fmt = s => s.split('-').reverse().join('.');
const row = (o, st) => [fmt(o.date) + ' 12:00:00', fmt(o.date), '*1234', st || 'OK', String(o.amount).replace('.', ','), 'RUB', String(o.amount).replace('.', ','), 'RUB', o.cat || '', '"' + o.desc.replace(/"/g, '""') + '"'].join(';');
const rows = ops.map(o => row(o)); rows.splice(10, 0, row({ date: ops[5].date, amount: -5000, desc: 'Отклонённая операция', cat: '' }, 'FAILED')); rows.push(rows[rows.length - 1]);
const csv = ['Дата операции;Дата платежа;Номер карты;Статус;Сумма операции;Валюта операции;Сумма платежа;Валюта платежа;Категория;Описание', ...rows].join('\r\n') + '\r\n';
const A = p.analyze(p.parseCSV(csv).ops);
const goalFor = date => { const g = act({ date }); p.setS(Object.assign(p.fresh(), { purchases: [g] })); const G = p.calc(g), T = p.tipsFor(A), pk = p.autoPick(A);
  const cov = T.filter(t => pk[t.id]).reduce((s, t) => s + Math.round(t.monthly * G.days / 30.4), 0);
  return { date, days: G.days, gap: G.gap, picked: Object.keys(pk), covered: cov, left: Math.max(0, G.gap - cov) }; };
const tips43 = (() => { const G = p.calc(act()); return p.tipsFor(A).map(t => ({ id: t.id, title: t.title, monthly: t.monthly, to_deadline: Math.round(t.monthly * G.days / 30.4) })); })();
const statement = { rows_in_file: rows.length, operations: A.count, dups: A.dups, failed: 1, masked: A.masked, days: A.days, from: I(A.from), to: I(A.to),
  income: A.income.monthly, pay_days: A.income.days, recurring: A.recurring.map(r => ({ name: r.name, amount: r.amount, day: r.day })), mandatory: A.mandatory,
  subs: A.subs.map(s => ({ name: s.name, amount: s.amount })), own: A.own, saved: A.saved, from_saved: A.fromSaved, people: A.people, refunds: A.refunds, fx: A.fx, peak: A.peak, leaks: A.leaks.slice(0, 1),
  tips: tips43, goal43: goalFor('2026-11-15'), goal52: goalFor('2026-11-24'), masked_example: p.maskDesc('Перевод по номеру +7 916 000-00-00 Иван И.').d };

const links = ['https://www.ozon.ru/product/kotel-gazovyy-navien-deluxe-s-24k-1234567890/?utm_source=share&sh=abc&from=app', 'https://www.wildberries.ru/catalog/12345678/detail.aspx?targetUrl=GP&ref=partner',
  'market.yandex.ru/product--robot-pylesos/123?clid=999&utm_medium=cpc', 'https://habr.com/ru/articles/1/'].map(u => ({ in: u, out: p.cleanUrl(u).url }));

// «взял из отложенного» и рост цены по ссылке
const bt = act({ saved: 9000, created: '2026-09-20' }), before = p.calc(bt).perDay, after = p.calc(Object.assign({}, bt, { saved: 6000 })).perDay;
const took = { before, after, alt: I(p.addDays(p.today(), Math.ceil((25000 - 6000) / before))) };
const pr0 = p.calc(act({ sum: 41990, share: 41990 })).perDay, pr1 = p.calc(act({ sum: 43990, share: 43990 })).perDay;

if (process.argv[2]) fs.writeFileSync(process.argv[2], csv, 'utf8');
process.stdout.write(JSON.stringify({ today: '2026-10-03', phrases, calc, daily: [d1, d2], push: [push1, push2], statement, afford, links, took, price: { before: pr0, after: pr1 } }));
