# -*- coding: utf-8 -*-
"""Правки под номинацию №3 «Лучший пользовательский опыт и дизайн» — модуль интегратора, 05.10.

Источники: design/2026-10-05_n3-ux-critique.md (critique: дизайн-ревью + браузерные замеры), независимая переоценка 43/60,
поиск практик (GOV.UK Validation и Error message, Baymard, NN/g Error-Message Rubric, WCAG 3.3.1/3.3.3, 1.4.10, 2.4.11)
и опровержение плана (design/2026-10-05_n3-plan-40.md). Порядок правок — тот, что выдержал опровержение.

1. Общие функции разбора (их зовут все формы ядра):
   parseMoney — числа не склеиваются через пробел («80000 10 и 25» → 80 000, было 8 000 010), группы тысяч «90 000» — одно число,
   «1,5 тысячи» → 1 500, «к»/«k» — единица только вплотную к числу («7к» → 7 000; «40000 к 19 ноября» — предлог срока);
   parseDate — понимает год, не принимает несуществующие даты («31.02», «32 декабря»).
2. Проверка ввода до обработчиков ядра (фаза захвата): фраза, уточнение, «Поправить», «Я отложил(а)», «Поменять свою часть»,
   «Перенести срок», «Взял из отложенного», «Влезет ли», трата, приход. Пусто, нет суммы, слова вместо цифр, валюта, минус,
   прошедший срок, часть больше цены — строка под полем (до 15 слов, ТЗ 5.1) и aria-invalid; лист не закрывается, ввод не стирается;
   при ошибке «Влезет ли» прошлый ответ убирается.
3. «Проверьте поля»: подзаголовок правдив (раньше «Пустое подсвечено» и при заполненных полях); одно название поля — «Сколько отложите сами».
4. Приход: подсказка-пример над полем (не placeholder — NN/g, GOV.UK); обязательные больше прихода — сообщение; дни зарплаты — в «Как я посчитал».
5. «Сегодня»: после «Влезет до зарплаты» → «Купил» сумма «Завтра на себя» — та же, что в ответе «влезет ли» (было 939 ₽ против 401 ₽), плюс «До зарплаты хватит».
6. Вёрстка: кнопка «Где лежат деньги» оформлена как строка (в тёмной теме был контраст 1:1); «Сменить фото» слева — подпись «отложено»
   её не перекрывает; отступ прокрутки под нижнюю зону (WCAG 2.4.11); при тексте 200 % вкладки и крупные числа не вылезают; альбомная — компактнее;
   подпись строки не уходит под сумму; область касания ссылок 44 px; системная «назад» — по экранам.
"""
R = [
    ('<textarea class="inp" id="income" aria-label="Приходы и обязательные траты">получаю 80 тысяч 10 и 25 числа, обязательные 30 тысяч</textarea>',
     '<p class="xs mut" id="income-hint">Например: получаю 80 тысяч 10 и 25 числа, обязательные 30 тысяч.</p><textarea class="inp" id="income" aria-label="Приходы и обязательные траты" aria-describedby="income-hint"></textarea>'),
]
CSS = r"""
.v3h-err{margin:6px 0 0;font-size:.875rem;line-height:1.35;color:var(--warm)}
.inp[aria-invalid="true"]{border-color:var(--warm);box-shadow:0 0 0 2px color-mix(in srgb,var(--warm) 25%,transparent)}
#income-hint{margin:0 0 6px}
/* подпись строки не сжимается под сумму: сумма переносится сама */
.rowl>span:first-child{min-width:min-content}
.rowl>b.num{white-space:normal;text-align:right;min-width:0}
/* «Где лежат деньги» — строка, а не системная кнопка */
button.v3-where{width:100%;background:transparent;border:0;border-bottom:1px solid var(--line);border-radius:0;color:var(--ink);font:inherit;text-align:left;cursor:pointer}
/* «Сменить фото» слева: подпись «отложено» едет справа и её не перекрывает */
.photo .swap{right:auto;left:8px}
/* фокус и прокрутка не уводят элемент под закреплённую нижнюю зону */
.view{scroll-padding-bottom:180px}
/* текст 200 %: вкладки переносятся, крупные числа не вылезают за край */
.tabs button{white-space:normal;line-height:1.15;padding:0 2px}
.big{font-size:min(calc(1.875rem*var(--d-k)),12vw)}
[data-out="left-today"]{font-size:min(calc(2.5rem*var(--d-k)),14vw)}
/* альбомная ориентация телефона — как узкий экран, нижняя зона компактнее */
@media (max-height:500px) and (orientation:landscape){
  .stage{padding:0;display:block}
  .app{width:100%;height:100dvh;border-radius:0;box-shadow:none}
  .panel{position:fixed;right:10px;top:10px;bottom:10px;z-index:80;width:min(290px,calc(100vw - 20px));background:var(--card);border:1px solid var(--line);border-radius:16px;padding:14px;display:none;max-height:none}
  .panel.open{display:block}
  .fab{display:grid;place-items:center;position:fixed;right:22px;top:20px;z-index:81;width:44px;height:44px;border-radius:50%;border:1px solid var(--line);background:var(--card);color:var(--ink);opacity:.92}
  .tabs{height:52px}.bottom{bottom:52px;padding:6px 16px}.bottom .main{min-height:44px}.bottom .sec2{min-height:44px;margin-top:4px}
  .view{scroll-padding-bottom:120px}
  .bottom{display:flex;gap:8px;align-items:stretch}.bottom .main,.bottom .sec2{flex:1 1 0;margin-top:0}
}
/* область касания ссылок-действий — 44 px, вёрстка не меняется */
button.link{position:relative}
button.link::after{content:'';position:absolute;inset:-10px -6px}
/* текст 200 %: заголовок истории переносится, вкладки не слипаются */
.stxt h2{overflow-wrap:anywhere;hyphens:auto;font-size:min(calc(2.25rem*var(--d-k)),10vw)}
.tabs button{font-size:min(.875rem,3.6vw)}
"""
JS = r"""/* 1. общие функции разбора */
parseMoney = function(s){ const out = [], re = /(\d{1,3}(?:[  ]\d{3})+|\d+)(?:[.,](\d+))?(?:\s*(тыс(?:яч[аиу]?)?\.?|т\.?\s?р\.?|млн)|(к|k)(?![а-яёa-z]))?/gi; let m;
  while ((m = re.exec(String(s || '')))) { let v = parseFloat(m[1].replace(/[  ]/g, '') + (m[2] ? '.' + m[2] : '')); if (!isFinite(v)) continue;
    const u = (m[3] || m[4] || '').toLowerCase(); if (u.startsWith('млн')) v *= 1e6; else if (u) v *= 1000; out.push({v:Math.round(v), i:m.index, unit:!!u, raw:m[0]}); }
  return out; };
const hPD0 = parseDate;
parseDate = function(s){ const m = String(s || '').match(new RegExp('к\\s+(\\d{1,2})\\s+' + edgeMON + '(?:\\s+(20\\d\\d))?', 'i')); if (!m) return hPD0(s);
  const mi = edgeMI(m[2]), d = +m[1], dim = y => new Date(Date.UTC(y, mi + 1, 0)).getUTCDate(), y0 = new Date(now()).getUTCFullYear();
  if (m[3]) { const y = +m[3]; return d >= 1 && d <= dim(y) ? Date.UTC(y, mi, d) : null; }
  if (d < 1 || d > dim(y0)) return null; let t = Date.UTC(y0, mi, d); if (t <= now()) { if (d > dim(y0 + 1)) return null; t = Date.UTC(y0 + 1, mi, d); } return t; };
const hMoney = t => { const n = parseMoney(String(t || '')).filter(x => x.v > 0); return n.length ? n[0].v : 0; };
const hCur = t => /долл|\$|usd|евро|€|eur|юан|¥|cny/i.test(String(t || ''));
const hToday = () => Math.floor(now() / DAY) * DAY;
function hErr(inp, msg){ if (!inp) return; const id = (inp.id || 'f') + '-err'; let p = document.getElementById(id);
  if (!p) { p = document.createElement('p'); p.className = 'v3h-err'; p.id = id; p.setAttribute('role', 'alert'); const host = inp.closest('form') || inp; host.after(p); }
  $$('[aria-busy="true"]').forEach(b => { b.disabled = false; b.removeAttribute('aria-busy'); if (b.dataset.hLabel) b.textContent = b.dataset.hLabel; });
  p.textContent = msg; inp.setAttribute('aria-invalid', 'true'); inp.setAttribute('aria-describedby', id); inp.focus();
  inp.addEventListener('input', () => { inp.removeAttribute('aria-invalid'); inp.removeAttribute('aria-describedby'); p.remove(); }, {once:true}); }
const hDate = v => { const m = String(v).trim().match(/^(?:к\s+)?(\d{1,2})[.\/](\d{1,2})(?:[.\/](\d{2,4}))?$/i); if (!m || +m[2] < 1 || +m[2] > 12) return null;
  return 'к ' + (+m[1]) + ' ' + MON[+m[2] - 1] + (m[3] ? ' ' + (m[3].length === 2 ? '20' + m[3] : m[3]) : ''); };
/* проверка суммы: {n} или {err}; проверка даты: {t, str} или {err} */
function hSum(v, ex){ const s = String(v || '').trim(); if (!s) return {err:'Напишите сумму цифрами — например, ' + ex + '.'};
  if (hCur(s)) return {err:'Считаю только в рублях — сколько это в рублях?'};
  if (/(^|[^\d])[-−]\s*\d/.test(s)) return {err:'Сумма не может быть отрицательной.'};
  const n = hMoney(s); return n ? {n} : {err:'Не нашёл сумму — напишите цифрами, например ' + ex + '.'}; }
function hDay(v){ const s = String(v || '').trim(); if (!s) return {err:'Напишите дату — например, «к 15 ноября».'};
  const str0 = hDate(s) || s, str = /^к\s/i.test(str0) ? str0 : 'к ' + str0, t = parseDate(str);
  if (!t) return {err:'Не понял дату — например, «к 15 ноября» или 15.11.'};
  if (t <= hToday()) return {err:'Срок уже прошёл — выберите дату позже сегодняшней.'};
  return {t, str}; }
/* 2. проверка до обработчиков ядра (фаза захвата); при ошибке форма дальше не идёт */
document.addEventListener('submit', e => { const id = e.target.id, stop = (inp, msg) => { e.preventDefault(); e.stopImmediatePropagation(); hErr(inp, msg); };
  if (id === 'phrasef') { const inp = $('#phrase'); if (!(inp.value || '').trim()) return stop(inp, 'Напишите цель и срок — например, «ноутбук к 1 марта».'); }
  else if (id === 'clarf') { const inp = $('#clar'), f = inp.dataset.f, v = inp.value.trim();
    if (f === 'dl') { const r = hDay(v); if (r.err) return stop(inp, r.err); inp.value = r.str; }
    else if (!/сам|полов/i.test(v)) { const pr0 = S.draft && S.draft.price, r = hSum(v, f === 'share' && pr0 ? fmt(Math.max(1000, Math.round(pr0 / 2000) * 1000)) : '95 000'); if (r.err) return stop(inp, r.err); inp.value = String(r.n); } }
  else if (id === 'savef') { const inp = $('#saveamt'), r = hSum(inp.value, '5 000'); if (r.err) return stop(inp, r.err); inp.value = String(r.n); }
  else if (id === 'inputf') { const inp = $('#inputv'), k = e.target.dataset.k, p = P(), w = S.who;
    if (k === 'dl') { const r = hDay(inp.value); if (r.err) return stop(inp, r.err); inp.value = r.str; }
    else { const r = hSum(inp.value, k === 'took' ? '3 000' : '80 000'); if (r.err) return stop(inp, r.err);
      if (k === 'share' && p && r.n > p.price) return stop(inp, 'Хватит ' + rubT(p.price) + ' — впишите столько или меньше.');
      if (k === 'took' && p && r.n > (p.saved[w] || 0)) return stop(inp, 'Отложено ' + rubT(p.saved[w] || 0) + ' — больше взять нельзя.');
      inp.value = String(r.n); } }
  else if (id === 'spendf' || id === 'afff') { const inp = $(id === 'spendf' ? '#spend' : '#price'), v = inp.value;
    const r = hSum(v, id === 'spendf' ? '«кофе 300»' : '7 000');
    if (r.err) { if (id === 'afff') { S.aff = null; const a = $('[data-out="afford"]'); if (a) a.textContent = ''; const kb = a && a.nextElementSibling; if (kb && kb.classList.contains('kb')) kb.remove(); }
      return stop(inp, id === 'spendf' && !v.trim() ? 'Напишите трату — например, «кофе 300».' : r.err); }
    if (id === 'spendf') { const label = v.replace(/(\d{1,3}(?:[  ]\d{3})+|\d+)(?:[.,]\d+)?(?:\s*(?:тыс(?:яч[аиу]?)?\.?|т\.?\s?р\.?|млн)|(?:к|k)(?![а-яёa-z]))?/i, ' ').replace(/[₽]|руб\S*/gi, ' ').replace(/\s+/g, ' ').trim(); inp.value = (label ? label + ' ' : '') + r.n; }
    else inp.value = String(r.n); }
}, true);
/* главная кнопка «Посчитать» зовёт ACT.phraseGo мимо отправки формы — та же проверка */
const hValPhrase = () => { const inp = $('#phrase'); if (inp && !(inp.value || '').trim()) { hErr(inp, 'Напишите цель и срок — например, «ноутбук к 1 марта».'); return false; } return true; };
const hPhrase0 = ACT.phraseGo;
ACT.phraseGo = function(){ if (!hValPhrase()) return; return hPhrase0.apply(this, arguments); };
/* «Поправить» (форма полей): та же проверка; значения приводятся к цифрам и дате до ядра */
const hValFields = () => { const fp = $('#f-price'), fd = $('#f-dl'), fs = $('#f-share'); let price = null;
  if (fp && fp.value.trim()) { const r = hSum(fp.value, '90 000'); if (r.err) { hErr(fp, r.err); return false; } fp.value = String(r.n); price = r.n; }
  if (fd && fd.value.trim()) { const r = hDay(fd.value); if (r.err) { hErr(fd, r.err); return false; } fd.value = r.str.replace(/^к\s+/i, ''); }
  if (fs && fs.value.trim()) { const r = hSum(fs.value, '40 000'); if (r.err) { hErr(fs, r.err); return false; }
    if (price && r.n > price) { hErr(fs, 'Больше цены на ' + rubT(r.n - price) + ' — впишите не больше ' + rubT(price) + '.'); return false; } fs.value = String(r.n); }
  return true; };
const hFields0 = ACT.fieldsGo;
ACT.fieldsGo = function(){ if (!hValFields()) return; return hFields0.apply(this, arguments); };
/* приход: пусто, валюта, обязательные больше прихода */
const hValIncome = () => { const inp = $('#income'), v = inp ? inp.value : ''; if (!inp) return true;
  if (hCur(v)) { hErr(inp, 'Считаю только в рублях — сколько это в рублях?'); return false; }
  const i = parseIncome(v); if (!i.m) { hErr(inp, 'Напишите приход и дни — например, «80 тысяч 10 и 25 числа».'); return false; }
  if (i.mand >= i.m) { hErr(inp, 'Обязательные не меньше прихода — проверьте суммы.'); return false; } return true; };
const hIncome0 = ACT.incomeGo;
ACT.incomeGo = function(){ if (!hValIncome()) return; return hIncome0.apply(this, arguments); };
/* главная кнопка: проверка до «Считаю» — при ошибке кнопка не блокируется (раньше оставалась «Считаю» навсегда) */
const HVAL = {phraseGo:hValPhrase, fieldsGo:hValFields, incomeGo:hValIncome};
document.addEventListener('click', e => { const b = e.target.closest && e.target.closest('[data-main]'); if (!b) return;
  if (!b.dataset.hLabel) b.dataset.hLabel = b.textContent;
  const v = HVAL[b.dataset.main]; if (v && !v()) { e.preventDefault(); e.stopImmediatePropagation(); } }, true);
/* 3. «Проверьте поля»: правдивый подзаголовок, одно название поля */
const hScrF0 = SCR.fields;
scrFields = SCR.fields = function(){ const r = hScrF0.apply(this, arguments), d = S.draft || {}, miss = !d.name || !d.price || !d.dl || d.share == null;
  r.html = r.html.replace('Фраза сохранена. Пустое подсвечено.', S.flags.limit ? 'Фраза сохранена. Пустое подсвечено.' : miss ? 'Пустое подсвечено — впишите.' : 'Проверьте и поправьте, если нужно.')
    .replace('Сколько вносите вы, ₽', 'Сколько отложите сами, ₽');
  return r; };
/* 4–5. «Сегодня»: дни зарплаты в «Как я посчитал»; после «Купил» — без противоречия с «влезет до зарплаты» */
const hScrT0 = SCR.today;
scrToday = SCR.today = function(){ const r = hScrT0.apply(this, arguments), w = S.who, m = me();
  if (!m || !m.income || !r || !r.html) return r;
  const pays = (m.income.pay || []).join(' и ');
  r.html = r.html.replace(/(<div class="rowl"><span>Приход в месяц<\/span><b class="num">[^<]*<\/b><\/div>)/, '$1<div class="rowl"><span>Дни зарплаты</span><b class="num">' + pays + ' числа</b></div>');
  const l = leftToday(w), tp = toPay(w), u = untilPay(w);
  /* подпись — из ТЗ 5.5 («Сегодня потрачено больше плана», случай БТ 11); сумма на завтра — та же, что в ответе «влезет ли» */
  if (l < 0 && tp && u >= 0) r.html = r.html.replace(/<p class="mut">Завтра на себя[^<]*<\/p>/, '<p class="mut">Завтра на себя ≈ ' + rubT(Math.floor(u / Math.max(1, tp - 1))) + '. До зарплаты хватит.</p>');
  return r; };
function hAfter(){
  const HF = {'f-name':'Напишите, что покупаете.', 'f-price':'Сколько стоит — цифрами, например 90 000.', 'f-dl':'К какой дате — например, «15 ноября».', 'f-share':'Сколько отложите сами — например, 40 000.'};
  $$('#view .inp.miss').forEach(inp => { if (HF[inp.id] && !document.getElementById(inp.id + '-err')) { const p = document.createElement('p'); p.className = 'v3h-err'; p.id = inp.id + '-err'; p.textContent = HF[inp.id]; inp.after(p); inp.setAttribute('aria-invalid', 'true'); inp.setAttribute('aria-describedby', p.id);
    inp.addEventListener('input', () => { inp.classList.remove('miss'); inp.removeAttribute('aria-invalid'); inp.removeAttribute('aria-describedby'); p.remove(); }, {once:true}); } });
  /* цифровая клавиатура у полей сумм (Baymard, GOV.UK: text + inputmode, не type=number) */
  ['#price', '#saveamt', '#f-price', '#f-share'].forEach(q => { const el = $(q); if (el) el.setAttribute('inputmode', 'decimal'); });
  const iv = $('#inputv'), ivf = iv && iv.closest('form'); if (iv && ivf && ivf.dataset.k !== 'dl') iv.setAttribute('inputmode', 'decimal');
  const cl = $('#clar'); if (cl && cl.dataset.f !== 'dl') cl.setAttribute('inputmode', 'decimal');
  const pr = $('#price'); if (pr && S.aff != null) pr.value = fmt(S.aff);   /* цена остаётся в поле — видно, к какой сумме ответ */
}
const hRender0 = render;
render = function(){ const r = hRender0.apply(this, arguments); try { hAfter(); } catch(e) {} return r; };
/* системная «назад»: история браузера по экранам; открытый лист закрывается первым */
const hStack = []; let hBack = false;
const hGo0 = go;
go = function(scr){ const prev = S && S.scr; const r = hGo0.apply(this, arguments); if (!hBack && prev && prev !== scr) { hStack.push(prev); try { history.pushState({v3h:hStack.length}, ''); } catch(e) {} } return r; };
addEventListener('popstate', () => { const sw = $('#sheetwrap'); if (sw && sw.classList.contains('open')) { closeSheet(); return; }
  /* экраны черновика (ответ, уточнение, поля) без черновика не строятся — их пропускаем */
  let prev = hStack.pop(); while (prev && !S.draft && ['answer', 'clarify', 'fields'].includes(prev)) prev = hStack.pop();
  if (prev) { hBack = true; try { go(prev); } finally { hBack = false; } } });
/* 7. вердикт «сходится» — только с доходом (решение владельца 05.10; Google PAIR, Microsoft HAX G2/G10): без дохода — сумма в день без вердикта */
const hFree = (w, exclude) => { const i = S.people[w].income; if (!i) return null; return Math.floor((i.m - i.mand) / 30) - reserve(w) + (exclude ? perDayPlan(exclude, w) : 0); };
const hAns0 = SCR.answer;
scrAnswer = SCR.answer = function(){ const r = hAns0.apply(this, arguments), d = S.draft; if (!d || !r || !r.html || !d.dl) return r;
  const days = Math.max(1, Math.round((d.dl - now()) / DAY)), per = Math.ceil((d.share || 0) / days), free = hFree(S.who), re = /<p class="big disp([^"]*)">Сходится<\/p>(\s*)<p class="mut([^"]*)">([^<]*)<\/p>/;
  if (!re.test(r.html)) return r;
  if (free == null) r.html = r.html.replace(re, '<p class="big disp num$1">' + rubT(per) + ' в день</p>$2<p class="mut$3">$4</p><p class="xs mut$3">Сойдётся ли — скажу, когда узнаю доход.</p>');
  else if (per > free) r.html = r.html.replace(re, '<p class="big disp$1">Пока не сходится</p>$2<p class="mut$3">Нужно ' + rubT(per) + ' в день, свободно ≈ ' + rubT(Math.max(0, free)) + '.</p>');
  return r; };
const hPur0 = SCR.purchase;
scrPurchase = SCR.purchase = function(){ const r = hPur0.apply(this, arguments), p = P(), w = S.who; if (!p || !r || !r.html || p.share[w] == null) return r;
  const re = /<div class="rowl"><span><b>Сходится<\/b> к ([^<]*)<\/span><\/div>/; if (!re.test(r.html)) return r;
  const free = hFree(w, p), per = perDayPlan(p, w);
  r.html = r.html.replace(re, free == null ? '<div class="rowl"><span>План: ' + rubT(per) + ' в день к $1. Сойдётся ли — скажу, когда узнаю доход.</span></div>'
    : per > free ? '<div class="rowl"><span><b>Пока не сходится</b> к $1: нужно ' + rubT(per) + ' в день, свободно ≈ ' + rubT(Math.max(0, free)) + '.</span></div>' : '$&');
  return r; };
/* 8. приход: обязательные из «аренда, кредит, ипотека…», порядок любой, «500 рублей» не умножается на 1000, дни зарплаты 1–31 */
const HMAND = /обязат|аренд|кредит|ипотек|коммун|квартплат|садик|школ|связь|интернет|налог|алимент|страхов|рассрочк/i;
const hAmt = seg => { const n = parseMoney(seg).filter(x => x.v > 0)[0]; if (!n) return 0; return !n.unit && n.v < 1000 && !/руб|₽|р\.(?!\w)/i.test(seg) ? n.v * 1000 : n.v; };
parseIncome = function(s){ s = String(s || ''); const pm = s.match(/(\d{1,2})\s*(?:и|,)\s*(\d{1,2})\s*числ[а-яё]*/i) || s.match(/(\d{1,2})\s*числ[а-яё]*/i);
  const pay = pm ? pm.slice(1).filter(Boolean).map(Number) : [10, 25], s2 = pm ? s.replace(pm[0], ' ') : s;
  let m = null, mand = 0;
  s2.split(/[,;\n]+|\sи\s(?=[а-яё]+\s+\d)/i).forEach(seg => { const v = hAmt(seg); if (!v) return; if (HMAND.test(seg)) mand += v; else if (m == null) m = v; });
  return {m, mand, pay, src:'manual'}; };
const hValIncome1 = hValIncome;
HVAL.incomeGo = function(){ const inp = $('#income'); if (inp) { const pm = (inp.value || '').match(/(\d{1,2})\s*(?:и|,)\s*(\d{1,2})\s*числ/i) || (inp.value || '').match(/(\d{1,2})\s*числ/i);
    if (pm && pm.slice(1).filter(Boolean).some(x => +x < 1 || +x > 31)) { hErr(inp, 'Дни зарплаты — от 1 до 31, например «10 и 25 числа».'); return false; } }
  return hValIncome1(); };
const hIncome1 = ACT.incomeGo;
ACT.incomeGo = function(){ if (!HVAL.incomeGo()) return; return hIncome1.apply(this, arguments); };
/* 9. название цели без висящего предлога («Ноутбук за») */
const hParse1 = parsePhrase;
parsePhrase = function(t){ const r = hParse1(t); if (r && r.name) r.name = r.name.replace(/\s+(за|на|до|к|в|около|примерно|где-то)$/i, '').trim(); return r; };
/* 10. крупные суммы: «Я отложил(а)» больше остатка — вопрос; трата больше дохода месяца — подтверждение вторым нажатием */
let hBig = null;
document.addEventListener('submit', e => { const id = e.target.id, w = S.who;
  if (id === 'savef') { const p = P(), inp = $('#saveamt'), n = +inp.value; if (p && n > leftOf(p, w) && leftOf(p, w) > 0) { e.preventDefault(); e.stopImmediatePropagation(); hErr(inp, 'Осталось отложить ' + rubT(leftOf(p, w)) + ' — впишите столько или меньше.'); } }
  else if (id === 'spendf') { const inp = $('#spend'), n = hMoney(inp.value), i = me().income, lim = i ? i.m : 100000;
    if (n > lim && hBig !== n) { hBig = n; e.preventDefault(); e.stopImmediatePropagation(); hErr(inp, 'Записать ' + rubT(n) + '? Нажмите «Записать» ещё раз.'); } else hBig = null; }
}, true);"""
