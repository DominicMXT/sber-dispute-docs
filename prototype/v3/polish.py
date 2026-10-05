# -*- coding: utf-8 -*-
"""Вторая волна правок под номинацию №3 — модуль интегратора, 05.10. Стоит после harden.

Основание: две независимые переоценки 42/60 и 42/60 (review/2026-10-05_n3-rescore2-rater1.md, -rater2.md, заметки там же).
Правила — те же, что у harden: GOV.UK Validation (все ошибки сразу, у каждого поля своя), Baymard, NN/g Error-Message Rubric,
WCAG 2.2 — 1.4.4 (текст 200 %), 2.4.11 (фокус не под закреплённой зоной), 2.5.8 (размер цели касания).

1. Ввод не теряется молча: «миллионов», «миллиардов», «млрд»; минус во фразе — ошибка; прошедшая или несуществующая дата во фразе —
   вопрос с причиной, а в форме полей — дата остаётся в поле с ошибкой; «завтра», «через 3 месяца», «15.11» — срок; «0» — «больше нуля»;
   номер карты убирается со словом об этом; неизвестная ссылка — «Страница не открылась. Сколько стоит?», а не выдуманный товар;
   цена больше 50 млн и «уже есть N» — с пояснением; в эхе уточнения виден срок.
2. «Проверьте поля»: все ошибки сразу, каждая под своим полем; подзаголовок правдив; одно название — «Ваша часть».
3. Приход: «1,5 тысячи, обязательные 500» — 500 ₽, а не 500 000; минус и ноль — ошибки; обязательные больше прихода —
   с суммами и выходом (второе нажатие считает как есть); «Сегодня» без трат при нехватке не пишет «потрачено больше плана».
4. Цифры: один план в день на экране цели (после отметки было 967 и 994); «Подтверждено 0 ₽ из N» → понятная строка;
   первая отметка — «неделя началась», а не «неделя засчитана»; минус — знаком «−»; «1 010 101 день» с разрядами.
5. Вёрстка: нижняя зона не закрывает конец экрана; если она выше трети экрана (320×568, альбомная, текст 200 %) — уходит в поток;
   поле и кнопки переносятся при крупном тексте; подписи вкладок растут; в альбомной строка не шире 640 px; кнопки-ссылки — 44 px;
   тост — сверху, не на главной кнопке; «Дальше», «Записать», «Код» — того же цвета, что главная кнопка; «Удалить всё» — как опасное.
6. Листы и «назад»: у листа почты — «Не сейчас»; «назад» с цели не возвращает на развилку «Копить вместе?»;
   легенда значков на согласии — двумя одинаковыми строками; вопрос о своей части — «Какую часть цены отложите вы?».
"""
R = [
    # минус — знаком минуса, не дефисом (типографика; «-7 967 ₽» читалось как тире)
    ("const fmt = n => String(Math.round(n)).replace(/\\B(?=(\\d{3})+(?!\\d))/g, NB);",
     "const fmt = n => String(Math.round(n)).replace(/\\B(?=(\\d{3})+(?!\\d))/g, NB).replace(/^-/, '−');"),
    ('placeholder="потратил… кофе 300"', 'placeholder="кофе 300"'),
    ("h:'Вместе с кем-то — по желанию'", "h:'Вместе с <span style=\"white-space:nowrap\">кем-то</span> — по желанию'"),
    ('<button class="main press" data-act="delAll">Удалить всё</button>', '<button class="main press p-danger" data-act="delAll">Удалить всё</button>'),
]
CSS = r"""
/* 2. ошибка в форме полей — у своего поля, а не у следующей подписи */
#fieldsf .v3h-err{margin:-6px 0 12px}
/* 5. кнопки-ссылки — цель касания 44 px (WCAG 2.5.8); инлайновый min-height:0 перекрыт */
button.link,button.link[style*="min-height:0"]{min-height:44px !important;display:inline-flex;align-items:center;vertical-align:middle}
/* поле и кнопки рядом: при крупном тексте кнопки уходят на новую строку, поле не сжимается до «потр» */
form.field{flex-wrap:wrap}
form.field>.inp{flex:1 1 8em;min-width:0}
/* подписи вкладок растут вместе с текстом; высота — по содержимому */
.tabs{height:auto !important;min-height:64px}
.tabs button{font-size:max(.75rem,min(.875rem,3.6vw)) !important;padding:6px 2px !important}
@media (max-height:500px) and (orientation:landscape){
  .tabs{min-height:52px}
  /* строка не растягивается на всю ширину альбомного экрана */
  .view{padding-left:max(16px,calc((100% - 640px) / 2));padding-right:max(16px,calc((100% - 640px) / 2))}
}
/* низкий экран (320×568, альбомная): фото цели не выталкивает сумму «Осталось отложить» за край */
@media (max-height:700px){.cardp .photo{aspect-ratio:auto;height:34vh}}
/* нижняя зона в потоке, когда она выше трети экрана */
.view .bottom.p-flow{position:static;background:none;-webkit-backdrop-filter:none;backdrop-filter:none;padding:16px 0 0;display:block}
.view .bottom.p-flow .sec2{margin-top:8px}
/* тост — сверху: не закрывает главную кнопку и заголовок листа */
.toast{bottom:auto !important;top:calc(10px + env(safe-area-inset-top));transform:translateY(-8px)}
.toast.on{transform:none}
/* одна главная заливка: «Дальше», «Записать», «Код» — как главная кнопка */
.go{background:var(--accent);color:var(--on-accent)}
/* опасное действие — не как обычная главная кнопка */
.main.p-danger{background:transparent;color:var(--warm);border:2px solid var(--warm)}
.p-leg{display:flex;align-items:center;gap:6px;margin:4px 0 0}.p-leg .vis{margin-left:0}
"""
JS = r"""/* v3 · polish — вторая волна правок под №3 */
/* 1. суммы: «миллионов», «миллиардов», «млрд», «тыщ» */
parseMoney = function(s){ const out = [], re = /(\d{1,3}(?:[  ]\d{3})+|\d+)(?:[.,](\d+))?(?:\s*(тыс(?:яч[аиу]?)?\.?|тыщ[а-яё]*|т\.?\s?р\.?|млн|миллион[а-яё]*|млрд|миллиард[а-яё]*)|(к|k)(?![а-яёa-z]))?/gi; let m;
  while ((m = re.exec(String(s || '')))) { let v = parseFloat(m[1].replace(/[  ]/g, '') + (m[2] ? '.' + m[2] : '')); if (!isFinite(v)) continue;
    const u = (m[3] || m[4] || '').toLowerCase(); if (/^(млрд|миллиард)/.test(u)) v *= 1e9; else if (/^(млн|миллион)/.test(u)) v *= 1e6; else if (u) v *= 1000;
    out.push({v:Math.round(v), i:m.index, unit:!!u, raw:m[0]}); }
  return out; };
const P_UNITW = /\s*(миллион|миллиард|млрд|тыщ)[а-яё]*/gi;
/* «0» — не «не нашёл», а «больше нуля» */
hSum = function(v, ex){ const s = String(v || '').trim(); if (!s) return {err:'Напишите сумму цифрами — например, ' + ex + '.'};
  if (hCur(s)) return {err:'Считаю только в рублях — сколько это в рублях?'};
  if (/(^|[^\d])[-−]\s*\d/.test(s)) return {err:'Сумма не может быть отрицательной.'};
  const n = hMoney(s); if (n) return {n};
  return parseMoney(s).length ? {err:'Сумма должна быть больше нуля.'} : {err:'Не нашёл сумму — напишите цифрами, например ' + ex + '.'}; };
/* срок словами и цифрами → «к D месяца [ГГГГ]»; прошедшая и несуществующая дата не выбрасываются молча */
const pDayStr = t => { const d = new Date(t); return 'к ' + d.getUTCDate() + ' ' + MON[d.getUTCMonth()] + ' ' + d.getUTCFullYear(); };
const pAddM = (t, n) => { const d = new Date(t); return Date.UTC(d.getUTCFullYear(), d.getUTCMonth() + n, Math.min(d.getUTCDate(), 28)); };
const P_CARD = /(?:\d{4}[ -]?){3}\d{4}(?:\d{0,3})/g;
function pPrep(txt){ let s = String(txt || ''); const card = P_CARD.test(s); P_CARD.lastIndex = 0; s = s.replace(P_CARD, ' ');
  const t0 = hToday();
  s = s.replace(/(?:к\s+)?послезавтра(?![а-яё])/i, () => ' ' + pDayStr(t0 + 2 * DAY) + ' ').replace(/(?:к\s+)?(?<![а-яё])завтра(?![а-яё])/i, () => ' ' + pDayStr(t0 + DAY) + ' ')
    .replace(/через\s+(\d{1,3})\s+(дн[а-яё]*|день|недел[а-яё]*|месяц[а-яё]*|год[а-яё]*|лет)/i, (_, n, u) => ' ' + pDayStr(/^д/i.test(u) ? t0 + n * DAY : /^н/i.test(u) ? t0 + n * 7 * DAY : /^м/i.test(u) ? pAddM(t0, +n) : pAddM(t0, 12 * n)) + ' ')
    .replace(/(?:к\s+)?(?<![\d.,])(\d{1,2})[.\/](\d{1,2})(?:[.\/](\d{2,4}))?(?!\d)(?![.,]\d)(?!\s*(?:тыс|тыщ|млн|млрд|миллион|миллиард|руб|₽|р\b|к(?![а-яё])|k\b))/i,(all, d, m, y) => +m >= 1 && +m <= 12 ? ' к ' + (+d) + ' ' + MON[+m - 1] + (y ? ' ' + (y.length === 2 ? '20' + y : y) : '') + ' ' : all);
  return {s, card}; }
const pParse0 = parsePhrase;
parsePhrase = function(txt){ const pr = pPrep(txt), r = pParse0(pr.s), s = pr.s;
  if (pr.card) r.card = true;
  /* неизвестная ссылка — честно «не открылась», а не выдуманный «Диван Осло» */
  if (r.link && !/(divan|shop|blog)\.example/i.test(s)) { const u = (s.match(/https?:\/\/\S+/i) || [''])[0], last = decodeURIComponent((u.split(/[?#]/)[0].split('/').filter(Boolean).pop() || '')).replace(/[-_]+/g, ' ').trim();
    r.price = null; r.linkFail = true; r.twoPrices = null; r.name = /^[\w.-]+\.[a-z]{2,}$/i.test(last) || !last || /^\d+$/.test(last) ? 'Товар' : last[0].toUpperCase() + last.slice(1); }
  if (r.dl == null && !r.pastDl) {
    const m = s.match(new RegExp('к\\s+(\\d{1,2})\\s+' + edgeMON + '[а-яё]*(?:\\s+(20\\d\\d))?', 'i'));
    if (m) r.badDl = m[0].replace(/^к\s+/i, '');
    else if (/(^|\s)вчера(\s|$|[,.])/i.test(s)) r.pastDl = hToday() - DAY;
  }
  if (r.name) r.name = r.name.replace(P_UNITW, '').replace(/\s+(за|на|до|к|в)$/i, '').trim();
  return r; };
/* фраза: пусто, минус, очень большая цена (подтверждение вторым нажатием) */
let pBigOk = null;
const pValPhrase = () => { const inp = $('#phrase'); if (!inp) return true; const v = (inp.value || '').trim();
  if (!v) { hErr(inp, 'Напишите цель и срок — например, «ноутбук к 1 марта».'); return false; }
  if (/(^|[\s,:(])[-−]\s*\d/.test(v.replace(/https?:\/\/\S+/gi, ''))) { hErr(inp, 'Сумма не может быть отрицательной — уберите минус.'); return false; }
  const r = parsePhrase(v); if (r.price > 5e7 && pBigOk !== v) { pBigOk = v; hErr(inp, 'Цена ' + rubT(r.price) + ' — верно? Нажмите «Посчитать» ещё раз.'); return false; }
  return true; };
HVAL.phraseGo = pValPhrase;
const pPhraseGo0 = ACT.phraseGo;
ACT.phraseGo = function(){ if (!pValPhrase()) return; const v = ($('#phrase') || {}).value || ''; P_CARD.lastIndex = 0; const card = P_CARD.test(v); P_CARD.lastIndex = 0;
  const r = pPhraseGo0.apply(this, arguments); if (card) setTimeout(() => toast('Номер карты убрал — он здесь не нужен.'), 50); return r; };
/* уточнение: срок в эхе; несуществующая дата — с причиной; вопрос о своей части понятен тому, кто копит один */
const pClar0 = SCR.clarify;
scrClarify = SCR.clarify = function(){ const d = S.draft;
  if (d && d.badDl && d.dl == null && d.price && !(d.cur && d.price == null))
    return edgeAsk(`${esc(d.name || 'покупка')} · ${rubT(d.price)}`, 'Такой даты нет: «' + esc(d.badDl) + '». К какой дате копим?', 'dl', ['к 15 ноября', 'к 31 декабря', 'к 1 июня']);
  const r = pClar0.apply(this, arguments); if (!r || !r.html) return r; const dd = S.draft;
  if (dd && dd.dl && !/· к \d/.test(r.html)) r.html = r.html.replace(/(<p class="ai sm">Я понял так: [^<]*?)(<\/p>)/, (_, a, b) => a + ' · к ' + fxDl(dd.dl) + b);
  r.html = r.html.replace(/Сколько отложите сами к сроку\?/g, 'Какую часть цены отложите вы?').replace(/>всю сумму сам</g, '>всю сумму<');
  if (/Какую часть цены отложите вы\?<\/h1>/.test(r.html)) r.html = r.html.replace(/(Какую часть цены отложите вы\?<\/h1>)/, '$1<p class="mut">Остальное можно собрать с кем-то вместе.</p>');
  return r; };
/* ответ: «уже есть N» и номер карты — с пояснением */
const pAns0 = SCR.answer;
scrAnswer = SCR.answer = function(){ const r = pAns0.apply(this, arguments), d = S.draft; if (!d || !r || !r.html) return r;
  if (/(уже\s+(?:есть|отложен[а-яё]*|накоплен[а-яё]*|скопил[а-яё]*)|отложено|накоплено)\s*\d/i.test(d.text || ''))
    r.html = r.html.replace(/(<p class="ai sm">Я понял так:[\s\S]*?<\/p>)/, '$1<p class="xs mut">Уже отложенное отметьте после сохранения — «Я отложил(а)».</p>');
  return r; };
/* 2. «Проверьте поля»: все ошибки сразу, у каждого поля */
function pErrAt(inp, msg){ const id = inp.id + '-err'; let p = document.getElementById(id);
  if (!p) { p = document.createElement('p'); p.className = 'v3h-err'; p.id = id; inp.after(p); }
  p.setAttribute('role', 'alert'); p.textContent = msg; inp.setAttribute('aria-invalid', 'true'); inp.setAttribute('aria-describedby', id);
  $$('[aria-busy="true"]').forEach(b => { b.disabled = false; b.removeAttribute('aria-busy'); if (b.dataset.hLabel) b.textContent = b.dataset.hLabel; });
  inp.addEventListener('input', () => { inp.classList.remove('miss'); inp.removeAttribute('aria-invalid'); inp.removeAttribute('aria-describedby'); p.remove(); }, {once:true}); }
const pValFields = () => { const fp = $('#f-price'), fd = $('#f-dl'), fs = $('#f-share'), fn = $('#f-name'), bad = []; let price = null;
  if (fn && !fn.value.trim()) bad.push([fn, 'Напишите, что покупаете.']);
  if (fp) { const r = hSum(fp.value, '90 000'); if (r.err) bad.push([fp, fp.value.trim() ? r.err : 'Сколько стоит — цифрами, например 90 000.']); else { fp.value = String(r.n); price = r.n; } }
  if (fd) { const r = hDay(fd.value); if (r.err) bad.push([fd, fd.value.trim() ? r.err : 'К какой дате — например, «15 ноября».']); else fd.value = r.str.replace(/^к\s+/i, ''); }
  if (fs) { const r = hSum(fs.value, '40 000'); if (r.err) bad.push([fs, fs.value.trim() ? r.err : 'Ваша часть — например, 40 000.']);
    else if (price && r.n > price) bad.push([fs, 'Больше цены на ' + rubT(r.n - price) + ' — впишите не больше ' + rubT(price) + '.']); else fs.value = String(r.n); }
  if (!bad.length) return true;
  bad.forEach(([i, m]) => pErrAt(i, m)); bad[0][0].focus();
  const sub = $('#view h1 + p.mut'); if (sub) sub.textContent = bad.length > 1 ? 'Поправьте подсвеченное — ' + bad.length + ' ' + plural(bad.length, 'поле', 'поля', 'полей') + '.' : 'Поправьте подсвеченное поле.';
  return false; };
HVAL.fieldsGo = pValFields;
ACT.fieldsGo = function(){ if (!pValFields()) return; return hFields0.apply(this, arguments); };
const pScrF0 = SCR.fields;
scrFields = SCR.fields = function(){ const r = pScrF0.apply(this, arguments); if (r && r.html) r.html = r.html.replace('Сколько отложите сами, ₽', 'Ваша часть, ₽'); return r; };
/* 3. приход: суммы по сегментам; голое «500» у обязательных — рубли, если ×1000 больше прихода */
parseIncome = function(s){ s = String(s || ''); const pm = s.match(/(\d{1,2})\s*(?:и|,)\s*(\d{1,2})\s*числ[а-яё]*/i) || s.match(/(\d{1,2})\s*числ[а-яё]*/i);
  const pay = pm ? pm.slice(1).filter(Boolean).map(Number) : [10, 25], s2 = pm ? s.replace(pm[0], ' ') : s, segs = [];
  s2.split(/[;\n]+|,(?!\d)|\sи\s(?=[а-яё]+\s+\d)/i).forEach(seg => { const n = parseMoney(seg).filter(x => x.v > 0)[0]; if (n) segs.push({v:n.v, bare:!n.unit && n.v < 1000 && !/руб|₽|р\.(?!\w)/i.test(seg), mand:HMAND.test(seg)}); });
  const inc = segs.find(x => !x.mand), m = inc ? (inc.bare ? inc.v * 1000 : inc.v) : null; let mand = 0;
  segs.filter(x => x.mand).forEach(x => { mand += x.bare && (m == null || x.v * 1000 < m) ? x.v * 1000 : x.v; });
  return {m, mand, pay, src:'manual'}; };
let pMandOk = null;
const pValIncome = () => { const inp = $('#income'); if (!inp) return true; const v = inp.value || '';
  if (!v.trim()) { hErr(inp, 'Напишите приход и дни — например, «80 тысяч 10 и 25 числа».'); return false; }
  if (hCur(v)) { hErr(inp, 'Считаю только в рублях — сколько это в рублях?'); return false; }
  if (/(^|[^\d])[-−]\s*\d/.test(v)) { hErr(inp, 'Сумма не может быть отрицательной.'); return false; }
  const pm = v.match(/(\d{1,2})\s*(?:и|,)\s*(\d{1,2})\s*числ/i) || v.match(/(\d{1,2})\s*числ/i);
  if (pm && pm.slice(1).filter(Boolean).some(x => +x < 1 || +x > 31)) { hErr(inp, 'Дни зарплаты — от 1 до 31, например «10 и 25 числа».'); return false; }
  const i = parseIncome(v);
  if (!i.m) { hErr(inp, parseMoney(v.replace(pm ? pm[0] : '', ' ')).some(x => x.v === 0) ? 'Приход должен быть больше нуля — например, «80 тысяч 10 и 25 числа».' : 'Напишите приход и дни — например, «80 тысяч 10 и 25 числа».'); return false; }
  if (i.mand >= i.m && pMandOk !== v) { pMandOk = v; hErr(inp, 'Обязательные ' + rubT(i.mand) + ' — не меньше прихода ' + rubT(i.m) + '. Всё верно — нажмите «Посчитать» ещё раз.'); return false; }
  return true; };
HVAL.incomeGo = pValIncome;
ACT.incomeGo = function(){ if (!pValIncome()) return; return hIncome0.apply(this, arguments); };
/* «Сегодня» без трат: нехватка — от плана, а не «потрачено больше плана» */
const pScrT0 = SCR.today;
scrToday = SCR.today = function(){ const r = pScrT0.apply(this, arguments), w = S.who, m = me(); if (!m || !m.income || !r || !r.html) return r;
  const l = leftToday(w); if (!(l < 0) || (m.spent || []).length) return r;
  const i = m.income, gap = i.mand >= i.m;
  r.html = r.html.replace(/Сегодня потрачено больше плана/, gap ? 'Обязательные больше прихода' : 'На цели не хватает в день')
    .replace(/(<p class="big disp num" data-out="left-today">[\s\S]*?<\/p>\s*)<p class="mut">[^<]*<\/p>/, '$1<p class="mut">' + (gap ? 'На себя и на цели сейчас не остаётся. Проверьте приход в «Мои данные».' : 'Приход без обязательных не покрывает план. Перенесите срок или уменьшите свою часть — «⋯» в цели.') + '</p>');
  return r; };
/* 4. экран цели: один план в день; строка о подтверждении выпиской — понятная */
const pPur0 = SCR.purchase;
scrPurchase = SCR.purchase = function(){ const r = pPur0.apply(this, arguments), p = P(), w = S.who; if (!p || !r || !r.html || p.share[w] == null) return r;
  const per = perDay(p, w);
  r.html = r.html.replace(/План: [^<]*?₽ в день к/, 'План: ' + rubT(per) + ' в день к').replace(/(<b>Пока не сходится<\/b> к [^:]*: нужно )[^<]*?₽( в день)/, (_, a, b) => a + rubT(per) + b)
    .replace(/Подтверждено 0[  ]₽ из ([^<]*?)(\s*<button)/, 'Отмечено $1 — сверю с выпиской, когда загрузите её.$2')

  return r; };
/* первая отметка — «неделя началась», а не «неделя засчитана» */
const pStep0 = step;
step = function(a){ const p = P(), w = S.who, first = p && p.share[w] != null && !((p.saved[w] || 0) > 0); const r = pStep0.apply(this, arguments);
  if (first && /^Неделя засчитана/.test(($('#toast') || {}).textContent || '')) toast('Первая отметка есть — неделя началась.');
  return r; };
/* «Это 1010101 день копилки» — с разрядами */
v3dayPriceShort = function(w, v){ const p = active(w).find(q => leftOf(q, w) > 0); if (!p || !(v > 0)) return '';
  const per = perDay(p, w); if (!(per > 0)) return ''; const n = Math.round(v / per);
  return n < 1 ? `Это меньше дневного плана на «${esc(p.name)}».` : `Это ${fmt(n) + NB + plural(n, 'день', 'дня', 'дней')} копилки «${esc(p.name)}».`; };
/* ошибка «влезет ли» убирает и хвост прошлого ответа */
const pErr0 = hErr;
hErr = function(inp, msg){ if (inp && inp.id === 'price') $$('#view .v3-dayprice').forEach(x => x.remove()); return pErr0.apply(this, arguments); };
/* трата «шуба 10 миллионов»: в подписи не остаётся «миллионов» */
document.addEventListener('submit', e => { if (e.target.id !== 'spendf') return; const inp = $('#spend'); if (inp) inp.value = inp.value.replace(P_UNITW, '').replace(/\s+/g, ' ').trim(); }, true);
/* 6. лист почты — с «Не сейчас»; согласие — легенда двумя строками */
const pEmail0 = SH.email;
SH.email = a => { const h = pEmail0(a); return /data-close/.test(h) ? h : h + '<button class="sec2 press" data-close>Не сейчас</button>'; };
const pCons0 = SCR.consent;
scrConsent = SCR.consent = function(){ const r = pCons0.apply(this, arguments); if (!r || !r.html) return r;
  r.html = r.html.replace(/Ваши деньги видите только вы (<span class="vis[^"]*"[^>]*>[\s\S]*?<\/span>)<br><span class="fx-leg">([\s\S]*?) — видят участники<\/span>/,
    '<span class="p-leg">$1 Ваши деньги видите только вы</span><span class="p-leg">$2 — видят участники</span>');
  return r; };
/* «назад» с цели не возвращает на уже пройденную развилку «Копить вместе?» */
const pGo0 = go;
go = function(scr){ const r = pGo0.apply(this, arguments); const top = hStack[hStack.length - 1]; if (top === 'together' && scr !== 'together') hStack.pop(); return r; };
/* 5. нижняя зона: отступ под неё; выше трети экрана — в поток */
function pLayout(){ const app = $('#app'), view = $('#view'), host = $('#bottom'), tabs = $('#tabs'); if (!app || !view || !host) return;
  const fresh = $('#bottom .bottom'); if (fresh) $$('#view .bottom.p-flow').forEach(x => x.remove());
  const bar = fresh || $('#view .bottom.p-flow'); const th = tabs && getComputedStyle(tabs).display !== 'none' ? tabs.offsetHeight : 0;
  if (bar && bar.parentNode !== host) { bar.classList.remove('p-flow'); host.appendChild(bar); }
  if (bar) bar.style.bottom = bar.classList.contains('notabs') ? '' : th + 'px';
  const bh = bar ? bar.offsetHeight : 0, H = app.clientHeight || innerHeight;
  if (bar && bh + th > H / 3) { bar.classList.add('p-flow'); bar.style.bottom = ''; view.appendChild(bar); view.style.paddingBottom = (th + 16) + 'px'; }
  else view.style.paddingBottom = Math.max(150, bh + th + 16) + 'px'; }
const pRender0 = render;
render = function(){ const r = pRender0.apply(this, arguments);
  try { pLayout(); const sh = document.getElementById('f-share-err'); if (sh && /^Сколько отложите сами/.test(sh.textContent)) sh.textContent = 'Ваша часть — например, 40 000.';
    /* прошедшая или несуществующая дата из фразы — в поле с причиной */
    const d = S.draft, fd = $('#f-dl');
    if (fd && d && !d.dl && (d.pastDl || d.badDl) && !fd.value.trim()) { fd.value = d.pastDl ? fxDl(d.pastDl) : d.badDl;
      fd.classList.remove('miss'); pErrAt(fd, d.pastDl ? 'Срок уже прошёл — выберите дату позже сегодняшней.' : 'Такой даты нет — проверьте число и месяц.');
      const sub = $('#view h1 + p.mut'); if (sub && /Пустое подсвечено/.test(sub.textContent)) sub.textContent = 'Поправьте подсвеченное.'; }
  } catch(e) { console.warn('polish:', e); }
  return r; };
addEventListener('resize', () => { try { pLayout(); } catch(e) {} });
"""
