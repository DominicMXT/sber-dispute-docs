# -*- coding: utf-8 -*-
"""Правки под номинацию №3 «Лучший пользовательский опыт и дизайн» — модуль интегратора, 05.10.

Источник — design/2026-10-05_n3-ux-critique.md (impeccable critique: дизайн-ревью A + браузерные замеры B).
P0 «ложный результат на мусорном вводе»:
- пустая фраза больше не подменяется примером «Диван 180 тысяч…» — строка ошибки под полем;
- ответ без суммы или с нулём («асдф» на «Сколько это в рублях?») не принимается — раньше выходило «0 ₽ · Сходится».
P1 «молчаливые формы»:
- «Влезет ли» и трата: сумма разбирается с единицами («1,5 тысячи» → 1 500, раньше 1 ₽); нет суммы, слова вместо цифр,
  валюта — строка под полем «Не нашёл сумму…» и aria-invalid; число «Влезет ли» остаётся в поле — видно, к какой цене ответ;
- уточнение даты понимает «15.12» и «15.12.2026»; непонятная дата — строка под полем;
- форма «Проверьте поля»: у каждого пустого поля — текст, что вписать (раньше только цвет рамки);
- поле прихода — подсказка вместо готового значения: нажать «Посчитать», не заметив чужих чисел, больше нельзя.
P1 вёрстка: подпись «Откладывать» не уходит под сумму на 320–390 px; альбомная ориентация телефона — без рамки 390×800;
системная «назад» возвращает на прошлый экран (история браузера), а не выходит из приложения;
у ссылок-действий («Поправить», «Как это работает?») область касания расширена до 44 px без сдвига вёрстки.
"""
R = [
    # поле прихода — подсказка вместо значения
    ('<textarea class="inp" id="income" aria-label="Приходы и обязательные траты">получаю 80 тысяч 10 и 25 числа, обязательные 30 тысяч</textarea>',
     '<textarea class="inp" id="income" aria-label="Приходы и обязательные траты" placeholder="например: получаю 80 тысяч 10 и 25 числа, обязательные 30 тысяч"></textarea>'),
]
CSS = r"""
.v3h-err{margin:6px 0 0;font-size:.875rem;line-height:1.35;color:var(--warm)}
.inp[aria-invalid="true"]{border-color:var(--warm);box-shadow:0 0 0 2px color-mix(in srgb,var(--warm) 25%,transparent)}
/* подпись строки не сжимается под сумму: сумма переносится сама */
.rowl>span:first-child{min-width:min-content}
.rowl>b.num{white-space:normal;text-align:right;min-width:0}
/* альбомная ориентация телефона — как узкий экран, без рамки 390×800 */
@media (max-height:500px) and (orientation:landscape){
  .stage{padding:0;display:block}
  .app{width:100%;height:100dvh;border-radius:0;box-shadow:none}
  .panel{position:fixed;right:10px;top:10px;bottom:10px;z-index:80;width:min(290px,calc(100vw - 20px));background:var(--card);border:1px solid var(--line);border-radius:16px;padding:14px;display:none;max-height:none}
  .panel.open{display:block}
  .fab{display:grid;place-items:center;position:fixed;right:22px;top:20px;z-index:81;width:44px;height:44px;border-radius:50%;border:1px solid var(--line);background:var(--card);color:var(--ink);opacity:.92}
}
/* область касания ссылок-действий — 44 px, вёрстка не меняется */
button.link{position:relative}
button.link::after{content:'';position:absolute;inset:-10px -6px}
"""
JS = r"""const hMoney = t => { const n = parseMoney(String(t || '')).filter(x => x.v > 0); return n.length ? n[0].v : 0; };
const hCur = t => /долл|\$|usd|евро|€|eur|юан|¥|cny/i.test(String(t || ''));
function hErr(inp, msg){ if (!inp) return; const id = (inp.id || 'f') + '-err'; let p = document.getElementById(id);
  if (!p) { p = document.createElement('p'); p.className = 'v3h-err'; p.id = id; p.setAttribute('role', 'alert'); const host = inp.closest('form') || inp; host.after(p); }
  p.textContent = msg; inp.setAttribute('aria-invalid', 'true'); inp.setAttribute('aria-describedby', id); inp.focus();
  inp.addEventListener('input', () => { inp.removeAttribute('aria-invalid'); inp.removeAttribute('aria-describedby'); p.remove(); }, {once:true}); }
const hDate = v => { const m = String(v).trim().match(/^(?:к\s+)?(\d{1,2})[.\/](\d{1,2})(?:[.\/](\d{2,4}))?$/i); if (!m || +m[2] < 1 || +m[2] > 12) return null;
  return 'к ' + (+m[1]) + ' ' + MON[+m[2] - 1] + (m[3] ? ' ' + (m[3].length === 2 ? '20' + m[3] : m[3]) : ''); };
/* проверка ввода — раньше обработчиков ядра (фаза захвата); при ошибке форма дальше не идёт */
document.addEventListener('submit', e => { const id = e.target.id, stop = (inp, msg) => { e.preventDefault(); e.stopImmediatePropagation(); hErr(inp, msg); };
  if (id === 'phrasef') { const inp = $('#phrase'); if (!(inp.value || '').trim()) return stop(inp, 'Напишите цель — например, «ноутбук 90 тысяч к 1 марта».'); }
  else if (id === 'clarf') { const inp = $('#clar'), f = inp.dataset.f, v = inp.value.trim(); if (!v) return stop(inp, f === 'dl' ? 'Напишите дату — например, «к 15 ноября».' : 'Напишите сумму цифрами — например, 95 000.');
    if (f === 'dl') { const alt = hDate(v); if (alt) inp.value = alt; if (!parseDate(/^к\s/i.test(inp.value) ? inp.value : 'к ' + inp.value)) return stop(inp, 'Не понял дату — например, «к 15 ноября» или 15.11.'); }
    else if (!/сам|полов/i.test(v)) { if (hCur(v)) return stop(inp, 'Считаю только в рублях — сколько это в рублях?'); const n = hMoney(v); if (!n) return stop(inp, 'Не нашёл сумму — напишите цифрами, например 95 000.'); inp.value = String(n); } }
  else if (id === 'spendf' || id === 'afff') { const inp = $(id === 'spendf' ? '#spend' : '#price'), v = inp.value; if (!v.trim()) return stop(inp, id === 'spendf' ? 'Напишите трату — например, «кофе 300».' : 'Напишите цену — например, 7 000.');
    if (hCur(v)) return stop(inp, 'Считаю только в рублях — сколько это в рублях?');
    const n = hMoney(v); if (!n) return stop(inp, 'Не нашёл сумму — напишите цифрами, например ' + (id === 'spendf' ? '«кофе 300».' : '7 000.'));
    if (id === 'spendf') { const label = v.replace(/\d[\d\s]*(?:[.,]\d+)?\s*(?:тыс(?:яч[аи]?)?\.?|т\.?\s?р\.?|к\b|млн)?/i, ' ').replace(/[₽]|руб\S*/gi, ' ').replace(/\s+/g, ' ').trim(); inp.value = (label ? label + ' ' : '') + n; }
    else inp.value = String(n); }
}, true);
/* главная кнопка «Посчитать» зовёт ACT.phraseGo мимо отправки формы — та же проверка */
const hPhrase0 = ACT.phraseGo;
ACT.phraseGo = function(){ const inp = $('#phrase'); if (inp && !(inp.value || '').trim()) return hErr(inp, 'Напишите цель — например, «ноутбук 90 тысяч к 1 марта».'); return hPhrase0.apply(this, arguments); };
/* пустой приход — подсказка, а не чужие числа */
const hIncome0 = ACT.incomeGo;
ACT.incomeGo = function(){ const inp = $('#income'); if (inp && !parseIncome(inp.value || '').m) return hErr(inp, 'Напишите, сколько приходит и когда — например, «получаю 80 тысяч 10 и 25 числа, обязательные 30 тысяч».'); return hIncome0.apply(this, arguments); };
const HFIELD = {'f-name':'Напишите, что покупаете.', 'f-price':'Сколько стоит — цифрами, например 90 000.', 'f-dl':'К какой дате — например, «15 ноября».', 'f-share':'Сколько отложите сами — например, 40 000.'};
function hAfter(){
  $$('#view .inp.miss').forEach(inp => { if (HFIELD[inp.id] && !document.getElementById(inp.id + '-err')) { const p = document.createElement('p'); p.className = 'v3h-err'; p.id = inp.id + '-err'; p.textContent = HFIELD[inp.id]; inp.after(p); inp.setAttribute('aria-invalid', 'true'); inp.setAttribute('aria-describedby', p.id); } });
  const pr = $('#price'), ans = $('[data-out="afford"]');
  if (pr && S.aff != null) pr.value = fmt(S.aff);   /* цена остаётся в поле — видно, к какой сумме ответ (без приставки в ответе: бюджет 45 слов)*/
}
const hRender0 = render;
render = function(){ const r = hRender0.apply(this, arguments); try { hAfter(); } catch(e) {} return r; };
/* системная «назад»: история браузера по экранам; открытый лист закрывается первым */
const hStack = []; let hBack = false;
const hGo0 = go;
go = function(scr){ const prev = S && S.scr; const r = hGo0.apply(this, arguments); if (!hBack && prev && prev !== scr) { hStack.push(prev); try { history.pushState({v3h:hStack.length}, ''); } catch(e) {} } return r; };
addEventListener('popstate', () => { const sw = $('#sheetwrap'); if (sw && sw.classList.contains('open')) { closeSheet(); return; }
  const prev = hStack.pop(); if (prev) { hBack = true; try { go(prev); } finally { hBack = false; } } });"""
