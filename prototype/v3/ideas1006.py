# -*- coding: utf-8 -*-
"""Эталон Р2 по ТЗ 1.4.5 (идеи ментора 06.10) — модуль интегратора, стоит после mentor1006. Всё здесь — РЕЛИЗ Р2.

1. ФТ-204 (Р2): «не влезет до зарплаты» → «Из своих — примерно через N дней, к D» и две кнопки одного веса:
   «Сделать целью» (открывает поля цели с ценой и датой) и «Не буду».
2. ФТ-206 (Р2): несколько трат одной фразой («кофе 300 и такси 450»); подсказка про микрофон клавиатуры — под полем, при фокусе.
3. ФТ-82, ФТ-210 (Р2): лист «Где напоминать?» — только уведомления на телефоне; Max и Telegram — «скоро» (боты — этап 2, Р4).
Не показано в эталоне: QR чека (ФТ-207) и «Поделиться» на Android (ФТ-208) — нужны камера и установленное приложение.
"""
R = [
    ('placeholder="кофе 300"', 'placeholder="кофе 300 и такси 450"'),
]
CSS = r"""
#i-hint{display:none;margin:-4px 0 8px}
form#spendf:focus-within + #i-hint{display:block}
"""
JS = r"""/* v3 · ideas1006 — эталон Р2 по ТЗ 1.4.5 */
/* 1. ФТ-204: «не влезет» → через сколько дней из своих */
function iDays(w, v){ const sd = selfDay(w), tp = toPay(w), u = untilPay(w);
  if (!(sd > 0)) return null; const short = Math.max(0, v - Math.max(0, u == null ? leftToday(w) : u));
  return (tp || 0) + Math.ceil(short / sd); }
const iToday0 = SCR.today;
scrToday = SCR.today = function(){ const r = iToday0.apply(this, arguments), w = S.who; if (!r || !r.html || !me().income) return r;
  r.html = r.html.replace(/(<form class="field" id="spendf">[\s\S]*?<\/form>)/, '$1<p class="xs mut" id="i-hint">Можно голосом: микрофон на клавиатуре — «кофе 300 и такси 450».</p>');
  if (S.aff != null && afford(w, S.aff).k === 'no') { const n = iDays(w, S.aff);
    const line = n == null ? 'Из своих сейчас не сходится — проверьте приход в «Мои данные».' : 'Из своих — примерно через ' + daysW(n) + ', к ' + dStr(now() + n * DAY) + '.';
    r.html = r.html.replace(/(<p class="ans" data-out="afford"[^>]*>[\s\S]*?<\/p>)/, '$1<p class="sm" data-out="afford-days">' + line + '</p>' + (n == null ? '' : '<div class="kb"><button data-act="iGoal">Сделать целью</button><button data-act="affNo">Не буду</button></div>')); }
  return r; };
ACT.iGoal = function(){ const w = S.who, v = S.aff, n = iDays(w, v); if (v == null || n == null) return;
  S.draft = {name:'', price:v, dl:Math.floor((now() + n * DAY) / DAY) * DAY, share:v, done:false, text:''}; S.aff = null; try { v3log('afford_to_goal'); } catch(e) {}
  go('fields'); setTimeout(() => { const f = $('#f-name'); if (f) f.focus(); }, 50); };
/* 2. ФТ-206: несколько трат одной фразой — раньше проверок формы (window, фаза захвата) */
window.addEventListener('submit', e => { const f = e.target; if (!f || f.id !== 'spendf') return; const inp = $('#spend'), v = (inp && inp.value || '').trim(); if (!v) return;
  const parts = v.split(/\s+и\s+|[,;]\s*/i).map(x => x.trim()).filter(Boolean); if (parts.length < 2) return;
  const items = parts.map(x => ({x, n:hMoney(x)})); if (items.some(it => !(it.n > 0))) return;
  e.preventDefault(); e.stopImmediatePropagation();
  items.forEach(it => { const t = it.x.replace(/(\d{1,3}(?:[  ]\d{3})+|\d+)(?:[.,]\d+)?(?:\s*(?:тыс[а-яё]*\.?|тыщ[а-яё]*|т\.?\s?р\.?|млн|миллион[а-яё]*)|(?:к|k)(?![а-яёa-z]))?/i, ' ').replace(/[₽]|руб\S*/gi, ' ').replace(/\s+/g, ' ').trim(); me().spent.push({v:it.n, t}); });
  inp.value = ''; render(true); toast('Записал ' + items.length + ' ' + plural(items.length, 'трату', 'траты', 'трат') + '.'); }, true);
/* 3. ФТ-82, ФТ-210: напоминания — только уведомления */
SH.remind = () => `<h3 class="disp">Где напоминать?</h3><button class="main press" data-act="linkPush">Уведомления на телефоне</button>
  <p class="xs mut">Утром — «Посмотрите, сколько сегодня можно на себя», без сумм. В Max и Telegram — скоро.</p>`;
"""
