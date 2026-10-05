# -*- coding: utf-8 -*-
"""Решения владельца 05.10 (вечер) — модуль интегратора, стоит после polish2.

1. «Уже есть 20 тысяч» во фразе — уже отложенное: план в день — от остатка, в эхе «уже есть N ₽», при сохранении — в отложенное.
2. Нейтрально по роду: «Согласен, дальше» → «Принимаю, дальше», «Купил» → «Куплено».
3. Вкладка «Покупки» → «Цели»; «Изменить покупку», «К моей покупке», «Отменить покупку» — «цель».
4. После сохранения можно поменять название и цену цели («⋯» → «Поменять название», «Поменять цену»), план пересчитывается.
5. Вход: Сбер ID (нужна организация) и Max (нужна регистрация бота) отложены — на листе входа VK ID и Яндекс ID.
   Код Сбер ID и Max — в login.py (ACT.loginSber, ACT.loginMax); вернуть — добавить кнопки в SH.login ниже.
"""
R = []
CSS = r""
JS = r"""/* v3 · decisions — решения владельца 05.10 */
/* 5. вход — VK ID и Яндекс ID; Сбер ID и Max — после организации и регистрации бота */
SH.login = () => `<h3 class="disp">Войдите, чтобы цель не пропала</h3><p class="mut sm">Сохраним только номер входа, без имени и телефона.</p>
  <button class="main press l-btn-main" data-act="loginVk">Войти через VK ID</button>
  <button class="sec2 press l-btn" data-act="loginYa">Войти с Яндекс ID</button>
  <button class="link" data-close>Не сейчас</button>`;
/* 1. «уже есть N» — уже отложенное */
const D_HAVE = /(?:уже\s+(?:есть|отложен[а-яё]*|накоплен[а-яё]*|скопил[а-яё]*|собран[а-яё]*)|отложено|накоплено|скопил[а-яё]*)\s*(\d[\d\s ]*(?:[.,]\d+)?\s*(?:тыс[а-яё]*|тыщ[а-яё]*|к(?![а-яё])|k\b|млн)?)/i;
const dParse0 = parsePhrase;
parsePhrase = function(t){ const r = dParse0(t), m = String(t || '').match(D_HAVE);
  if (r && m) { const n = parseMoney(m[1])[0]; if (n && n.v > 0) { const v = !n.unit && n.v < 1000 ? n.v * 1000 : n.v; r.have = r.price ? Math.min(v, r.price) : v; } }
  return r; };
const dAns0 = SCR.answer;
scrAnswer = SCR.answer = function(){ const d = S.draft; if (!d || !(d.have > 0) || !d.price || d.share == null) return dAns0.apply(this, arguments);
  const h = Math.min(d.have, d.share), p0 = d.price, s0 = d.share; d.price = p0 - h; d.share = s0 - h; let r;
  try { r = dAns0.apply(this, arguments); } finally { d.price = p0; d.share = s0; }
  if (!r || !r.html) return r;
  r.html = r.html.replace(/(<p class="ai sm[^"]*">Я понял так:[\s\S]*?)(<\/p>)/, (all, a, b) => {
      a = a.replace(rubT(p0 - h).replace(/ /g, '&nbsp;'), rubT(p0).replace(/ /g, '&nbsp;')).replace(rubT(p0 - h), rubT(p0));
      a = a.replace(/ваша часть [^<·]*?₽/, 'ваша часть ' + rubT(s0).replace(/ /g, '&nbsp;') + ' · уже есть ' + rubT(h).replace(/ /g, '&nbsp;'));
      return a + b; })
    .replace(/<p class="xs mut">Уже отложенное отметьте после сохранения — «Я отложил\(а\)»\.<\/p>/g, '');
  return r; };
const dCommit0 = commitDraft;
commitDraft = function(){ const d = S.draft, w = S.who, n0 = S.purchases.length, have = d && d.have > 0 ? Math.min(d.have, d.share || d.have) : 0;
  const r = dCommit0.apply(this, arguments);
  if (have && S.purchases.length > n0) { const p = S.purchases[S.purchases.length - 1]; if (p && p.share[w] != null) { p.saved[w] = Math.min(have, p.share[w]); try { v3log('have_on_save'); } catch(e) {} } }
  return r; };
/* 4. поменять название и цену после сохранения */
const dChange0 = SH.change;
SH.change = a => { const h = dChange0(a); return h.replace(/(<h3 class="disp">[^<]*<\/h3>)/, '$1<button class="sec2 press" data-act="dEditName">Поменять название</button><button class="sec2 press" data-act="dEditPrice">Поменять цену</button>'); };
SH.dEdit = k => { const p = P(); if (!p) return ''; const name = k === 'name';
  return `<h3 class="disp">${name ? 'Название цели' : 'Цена цели'}</h3><form id="deditf" class="field" data-k="${k}"><input class="inp" id="deditv" value="${name ? esc(p.name) : fmt(p.price)}" ${name ? 'maxlength="60"' : 'inputmode="decimal"'} aria-label="${name ? 'Название цели' : 'Цена цели, ₽'}"><button class="go press">Сохранить</button></form>${name ? '' : '<p class="xs mut">План в день пересчитаю.</p>'}`; };
ACT.dEditName = () => openSheet('dEdit', 'name');
ACT.dEditPrice = () => openSheet('dEdit', 'price');
document.addEventListener('submit', e => { if (e.target.id !== 'deditf') return; e.preventDefault(); e.stopImmediatePropagation();
  const p = P(), w = S.who, k = e.target.dataset.k, inp = $('#deditv'); if (!p || !inp) return;
  if (k === 'name') { const v = inp.value.replace(/\s+/g, ' ').trim(); if (!v) return hErr(inp, 'Напишите название — например, «Ноутбук».'); if (v.length > 60) return hErr(inp, 'Название — до 60 знаков.');
    p.name = v; p.cap = v; closeSheet(); render(true); return toast('Название изменено.'); }
  const r = hSum(inp.value, '90 000'); if (r.err) return hErr(inp, r.err);
  const saved = Object.values(p.saved || {}).reduce((s, x) => s + (x || 0), 0);
  if (r.n < saved) return hErr(inp, 'Уже отложено ' + rubT(saved) + ' — цена не может быть меньше.');
  const old = p.price; p.price = r.n;
  Object.keys(p.share || {}).forEach(m => { if (p.share[m] != null && (p.share[m] === old || p.share[m] > r.n)) p.share[m] = p.share[m] === old ? r.n : Math.min(p.share[m], r.n); });
  if (p.state === 'done' && saved < r.n) p.state = 'active';
  closeSheet(); render(true); toast('Цена изменена — план пересчитан.'); }, true);
/* 2–3. слова: «цель» вместо «покупки», нейтрально по роду */
const D_TXT = [['Покупки', 'Цели'], ['Изменить покупку', 'Изменить цель'], ['К моей покупке', 'К моей цели'], ['К покупке', 'К цели'], ['Отменить покупку', 'Отменить цель'], ['Отменить покупку?', 'Отменить цель?'],
  ['Согласен, дальше', 'Принимаю, дальше'], ['Купил', 'Куплено'], ['Новая покупка', 'Новая цель']];
const D_MAP = new Map(D_TXT);
function dWords(root){ if (!root) return; const tw = document.createTreeWalker(root, NodeFilter.SHOW_TEXT); let n;
  while ((n = tw.nextNode())) { const t = n.nodeValue, k = t.trim(); if (D_MAP.has(k)) n.nodeValue = t.replace(k, D_MAP.get(k)); else if (/Покупка уйдёт в архив/.test(t)) n.nodeValue = t.replace('Покупка уйдёт в архив', 'Цель уйдёт в архив'); }
  root.querySelectorAll('[aria-label]').forEach(el => { const a = el.getAttribute('aria-label'); if (D_MAP.has(a)) el.setAttribute('aria-label', D_MAP.get(a)); }); }
const dRender0 = render;
render = function(){ const r = dRender0.apply(this, arguments); try { ['#view', '#bottom', '#tabs'].forEach(q => dWords($(q))); } catch(e) {} return r; };
const dOpen0 = openSheet;
openSheet = function(){ const r = dOpen0.apply(this, arguments); try { dWords($('#sheet')); } catch(e) {} return r; };
"""
