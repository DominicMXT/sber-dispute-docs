# -*- coding: utf-8 -*-
"""Эталон Р2 по ТЗ 1.4.6 (ввод трат проще, разбор трекеров калорий 07.10) — модуль интегратора, стоит после ideas1006. Всё здесь — РЕЛИЗ Р2.

1. ФТ-212: плашки частых трат — по своим записям за 14 дней, подпись с 3 записями и больше, до трёх плашек «подпись · медиана».
   Касание подставляет фразу в поле: сумму можно поменять, запись — кнопкой «Записать».
2. ФТ-213: «Как вчера» — лист со вчерашними тратами, у каждой отметка; записываются только отмеченные.
3. ФТ-214–215: после 3 дней без записей — один раз «Пропустили дни — загрузите выписку»; выписка подставляет суммы по дням.
   Пересчёт «на себя» по 4.3 — на сервере (ТЗ 4.3, ФТ-215); прототип показывает суммы по дням и не пересчитывает.
4. ФТ-216: во фразе 2 траты и больше — карточка до записи: строка на трату, «убрать», «Записать все».
История записей в прототипе — `hist` ({d: дней назад, v, t}); у нового человека она пустая, плашек нет. Сценарии: ?s=chips, ?s=gap.
"""
CSS = r"""
.sp-chips{display:flex;flex-wrap:wrap;gap:8px;margin:-2px 0 10px}
.sp-chips .chip{min-height:44px}
.ms-row{display:flex;align-items:center;justify-content:space-between;gap:10px;min-height:48px;border-bottom:1px solid var(--line)}
.ms-row label{display:flex;align-items:center;gap:10px;min-height:44px;flex:1}
.ms-row input[type=checkbox]{width:22px;height:22px;accent-color:var(--accent,#2f6f5e)}
"""
JS = r"""/* v3 · input1007 — эталон Р2 по ТЗ 1.4.6: ввод трат проще */
const nHist = w => S.people[w].hist || (S.people[w].hist = []);
function spChips(w){ const by = {}; nHist(w).filter(x => x.d >= 1 && x.d <= 14 && x.t).forEach(x => (by[x.t] = by[x.t] || []).push(x.v));
  return Object.keys(by).filter(t => by[t].length >= 3).sort((a, b) => by[b].length - by[a].length).slice(0, 3)
    .map(t => { const v = by[t].slice().sort((a, b) => a - b); return {t, v:v[Math.floor((v.length - 1) / 2)]}; }); }
const spYesterday = w => nHist(w).filter(x => x.d === 1);
function spGap(w){ const m = S.people[w]; if (m.gapDone || m.gapSkip || m.spent.length || !m.income) return false;
  const h = nHist(w); if (!h.length) return false; return Math.min.apply(null, h.map(x => x.d)) >= 4; }
const iToday1 = SCR.today;
scrToday = SCR.today = function(){ const r = iToday1.apply(this, arguments), w = S.who; if (!r || !r.html || !me().income) return r;
  const ch = spChips(w), yd = spYesterday(w);
  if (ch.length || yd.length) { const html = '<div class="sp-chips" id="sp-chips">' + ch.map((c, i) => '<button type="button" class="chip press sm" data-chip="' + i + '">' + esc(c.t) + ' · ' + rubT(c.v) + '</button>').join('')
      + (yd.length ? '<button type="button" class="chip press sm" data-act="spYd">Как вчера</button>' : '') + '</div>';
    r.html = r.html.replace(/(<form class="field" id="spendf">[\s\S]*?<\/form>)/, '$1' + html); }
  if (spGap(w)) { if (!me().gapShown) { me().gapShown = true; try { v3log('gap_prompt_shown'); } catch(e) {} }
    r.html = r.html.replace(/(<form class="field" id="spendf">)/, '<div class="card" id="sp-gap"><p class="sm">Пропустили дни — загрузите выписку, подставлю траты за них.</p><div class="kb"><button data-act="gapLoad">Загрузить</button><button data-act="gapSkip">Не сейчас</button></div></div>$1'); }
  return r; };
/* 1. ФТ-212: плашка подставляет фразу, сумму можно поменять до записи */
document.addEventListener('click', e => { const b = e.target.closest && e.target.closest('[data-chip]'); if (!b) return;
  e.stopImmediatePropagation(); const c = spChips(S.who)[+b.dataset.chip], inp = $('#spend'); if (!c || !inp) return;
  inp.value = c.t + ' ' + c.v; inp.focus(); inp.setSelectionRange(inp.value.length, inp.value.length); me().chipUsed = 'frequent'; }, true);
/* 2. ФТ-213: «Как вчера» — только отмеченные */
SH.spYd = () => { const yd = spYesterday(S.who); return '<h3 class="disp">Как вчера</h3><p class="sm mut">Отметьте, что повторить сегодня.</p>'
  + yd.map((x, i) => '<div class="ms-row"><label><input type="checkbox" data-yd="' + i + '" checked> ' + esc(x.t) + '</label><span>' + rubT(x.v) + '</span></div>').join('')
  + '<button class="main press" data-act="spYdGo">Записать отмеченные</button>'; };
ACT.spYd = () => openSheet('spYd');
ACT.spYdGo = () => { const yd = spYesterday(S.who), on = [...document.querySelectorAll('#sheet [data-yd]')].filter(x => x.checked).map(x => yd[+x.dataset.yd]);
  closeSheet(); if (!on.length) return; on.forEach(x => me().spent.push({v:x.v, t:x.t})); try { v3log('spend_chip_used'); } catch(e) {}
  render(true); toast('Записал ' + on.length + ' ' + plural(on.length, 'трату', 'траты', 'трат') + ' как вчера.'); };
/* 3. ФТ-214–215: пропущенные дни — выписка */
ACT.gapSkip = () => { me().gapSkip = true; render(true); };
ACT.gapLoad = () => { const m = me(); m.gapDays = [{d:3, v:1840}, {d:2, v:960}, {d:1, v:2310}]; m.gapDone = true; try { v3log('gap_statement_used'); } catch(e) {} openSheet('gapDone'); };
SH.gapDone = () => { const g = me().gapDays || [], sum = g.reduce((s, x) => s + x.v, 0);
  return '<h3 class="disp">Подставил траты за ' + daysW(g.length) + '</h3>' + g.map(x => '<div class="ms-row"><span>' + dStr(now() - x.d * DAY) + '</span><span>' + rubT(x.v) + '</span></div>').join('')
    + '<p class="sm">Всего ' + rubT(sum) + '. Дни, где вы записывали сами, не трогал. Учту в «на себя» на следующие дни.</p><p class="xs mut">Из выписки берём только сумму за день, без описаний и получателей.</p>'
    + '<button class="main press" data-act="gapOk">Понятно</button>'; };
ACT.gapOk = () => { closeSheet(); render(true); };
/* 4. ФТ-216: 2 траты и больше — карточка до записи */
const iRecord0 = iRecord;
iRecord = function(items){ S.msItems = items.slice(); const inp = $('#spend'); if (inp) inp.value = ''; openSheet('mSpend'); };
const msTitle = x => x.replace(/(\d{1,3}(?:[  ]\d{3})+|\d+)(?:[.,]\d+)?(?:\s*(?:тыс[а-яё]*\.?|т\.?\s?р\.?|к(?![а-яё])))?/i, ' ').replace(/[₽]|руб\S*/gi, ' ').replace(/\s+/g, ' ').trim();
SH.mSpend = () => { const it = S.msItems || [];
  return '<h3 class="disp">Записать ' + it.length + ' ' + plural(it.length, 'трату', 'траты', 'трат') + '?</h3>'
    + it.map((x, i) => '<div class="ms-row"><span>' + esc(msTitle(x.x) || 'трата') + ' — ' + rubT(x.n) + '</span><button type="button" class="link" data-msrm="' + i + '">убрать</button></div>').join('')
    + '<button class="main press" data-act="msAll"' + (it.length ? '' : ' disabled') + '>Записать все</button>'; };
document.addEventListener('click', e => { const b = e.target.closest && e.target.closest('[data-msrm]'); if (!b) return;
  e.stopImmediatePropagation(); S.msItems.splice(+b.dataset.msrm, 1); if (!S.msItems.length) { closeSheet(); return; } openSheet('mSpend'); }, true);
ACT.msAll = () => { const it = S.msItems || []; S.msItems = null; closeSheet(); try { v3log('multi_spend_card'); } catch(e) {} if (it.length) iRecord0(it); };
/* ФТ-212: запись плашкой — событие при отправке формы */
window.addEventListener('submit', e => { if (e.target && e.target.id === 'spendf' && me().chipUsed) { try { v3log('spend_chip_used'); } catch(x) {} me().chipUsed = null; } }, true);
/* сценарии */
Object.assign(V3_SCEN, {
  chips(){ V3_SCEN.solo(); const m = me(); if (!m.income) m.income = {m:72000, mand:29500, pay:[10,25], src:'manual'};
    m.hist = [{d:1, v:300, t:'кофе'}, {d:1, v:450, t:'такси'}, {d:2, v:450, t:'такси'}, {d:3, v:250, t:'кофе'}, {d:4, v:450, t:'такси'}, {d:5, v:300, t:'кофе'}, {d:6, v:400, t:'обед'}];
    go('today'); },
  gap(){ V3_SCEN.solo(); const m = me(); if (!m.income) m.income = {m:72000, mand:29500, pay:[10,25], src:'manual'};
    m.hist = [{d:4, v:300, t:'кофе'}, {d:5, v:450, t:'такси'}, {d:6, v:300, t:'кофе'}]; go('today'); },
});
"""
