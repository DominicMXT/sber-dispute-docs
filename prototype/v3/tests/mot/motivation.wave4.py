# -*- coding: utf-8 -*-
"""Модуль v3 «Мотивация» (волна 3b, после flow_group): механики Р2 из market/motivation/2026-10-04_D_mechanics.md.

Что делает (по механикам):
  M-B  «Сегодня на себя» с запасом прочности: из суммы вычитается запас 5 % дохода в месяц (V3_BUF), одна строка о запасе
       под числом и строка в «Как я посчитал». Единственная замена R — формула selfDay (она const, обёрткой не взять).
  M-C  Цена траты в днях цели: к ответу «влезет ли» (экран «Сегодня» и бот) — «на «цель» вы откладываете столько за N дней».
  M-D  День зарплаты: в уведомлении и в сообщении бота — «Открыть копилку в своём банке» (или «Завести», если места нет).
  M-E  Срыв без обнуления: «Пришлось взять из отложенного» ведёт на экран slip — «Сдвинуть срок на N дней» и
       «Откладывать +M ₽ в день», две равные кнопки. Тот же экран — «Перестроить план» из прямого разбора.
  M-F  Счёт недель по плану без сгорания: на экране цели сетка недель (.v3-day, закрашенные — .on). Пропуск не обнуляет
       счёт, просто не закрашен. Сводка недели (лист weeksum) переписана в бюджет 30 слов.
  M-G  Сводка недели в общей цели на 3–6: «ваш результат» + «по плану N из M участников»; без имён и чужих сумм.
       На двоих — только «к сроку сходится / пока не сходится», как у flow_group.
  M-I  В общей цели напоминает продукт: строка под участниками и в сводке.
  M-J  Тон: похвала за факт (тост «Неделя засчитана — уже N»), прямота — только по кнопке «Сказать прямо» (лист v3direct).
  M-K  После «Собрано»: полка собранных целей и «Создать следующую цель» → Э-02.
  M-L  Лист «Где будут лежать деньги»: отдельная копилка под эту цель.

Коды: dayprice, slip, weeks, weeksum3, nextgoal. Журнал событий — demo.v3.log() (slip_shown, slip_date, slip_day,
next_goal_started, bank_open). Подмены текста v2 идут через v3sub flow_group — промахи видны в demo.v3.warn().
Проверка: python build_v3.py --only motivation → v3/_test_motivation.html#<код>
"""

R = [
    # M-B: запас прочности вычитается из «на себя» (selfDay — const, обёрткой не переопределить)
    ("const selfDay = w => { const i = S.people[w].income; return i ? Math.floor((i.m - i.mand - reserve(w) * 30) / 30) : null; };",
     "const selfDay = w => { const i = S.people[w].income; return i ? Math.floor((i.m - i.mand - reserve(w) * 30 - v3buf(w)) / 30) : null; };"),
]

CSS = r"""
.v3-wk{display:grid;grid-template-columns:repeat(13,1fr);gap:3px;margin:6px 0 6px}
.v3-day{height:14px;border-radius:3px;background:var(--film)}
.v3-day.on{background:var(--fill)}
.v3-day.v3-fut{background:transparent;box-shadow:inset 0 0 0 1px var(--line)}
.v3-day.v3-now{outline:2px solid var(--ink);outline-offset:1px}
.v3-pair .sec2 small{display:block;font-weight:400;font-size:.8125rem;letter-spacing:.01em;color:var(--ink2);margin-top:2px}
.v3-shelf{display:flex;gap:10px;overflow-x:auto;margin:6px 0 8px;scrollbar-width:none}
.v3-shelf figure{margin:0;width:84px;flex:none}
.v3-shelf .mini{position:relative;display:block;width:84px;height:84px;border-radius:4px;overflow:hidden;background:var(--film)}
.v3-shelf .mini img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}
.v3-shelf figcaption{font-size:.8125rem;letter-spacing:.01em;line-height:1.3;color:var(--ink2);margin-top:4px}
.push .v3-bank{margin-top:4px}
"""

JS = r"""
/* ── v3 · motivation: механики Р2 (M-B…M-L), см. market/motivation/2026-10-04_D_mechanics.md ── */
const V3_BUF = .05;                                  /* M-B: запас прочности — доля дохода в месяц */
const V3_WEEK = 7 * DAY;
const V3_BANK = {'Копилка в банке':'копилку', 'Вклад':'вклад', 'Отдельный счёт':'отдельный счёт'};
function v3buf(w){ const i = S.people[w].income; return i ? Math.round(i.m * V3_BUF / 100) * 100 : 0; }
function v3miss(where){ if (!v3warn.includes(where)) v3warn.push(where); }
const v3goalOf = w => P() && P().share[w] != null ? P() : active(w)[0];

/* ── M-F: счёт недель без сгорания. Неделя — с понедельника, как в weekRow ── */
const v3mon = t => t - ((new Date(t).getUTCDay() + 6) % 7) * DAY;
function v3weeks(p, w){ const m0 = v3mon(p.cr), total = Math.max(1, Math.round((v3mon(p.dl) - m0) / V3_WEEK) + 1),
    ci = Math.min(total - 1, Math.max(0, Math.round((v3mon(now()) - m0) / V3_WEEK)));
  let past = (p.v3wk || {})[w];
  if (!past) {   /* истории нет — доля недель по плану из отложенного против плана; пропуски разнесены равномерно */
    const tot = Math.max(1, Math.round((p.dl - p.cr) / DAY)), el = Math.max(1, Math.round((now() - p.cr) / DAY)), exp = (p.share[w] || 0) * el / tot,
      k = Math.round(ci * Math.min(1, exp > 0 ? (p.saved[w] || 0) / exp : 1)), miss = ci - k;
    past = Array.from({length:ci}, (_, j) => Math.floor((j + 1) * miss / ci) === Math.floor(j * miss / ci)); }
  past = Array.from({length:ci}, (_, j) => !!past[j]);
  const cur = p.state === 'done' || (onPlan(p, w) && weekRow(w).done > 0), cells = past.concat([cur]);
  return {cells, ci, total, n:cells.filter(Boolean).length}; }
const v3wkW = n => plural(n, 'неделя', 'недели', 'недель');
function v3weeksHtml(p, w){ const k = v3weeks(p, w), fut = k.total - k.ci - 1;
  const cells = k.cells.map((on, i) => `<i class="v3-day${on ? ' on' : ''}${i === k.ci && p.state !== 'done' ? ' v3-now' : ''}"></i>`).join('') + '<i class="v3-day v3-fut"></i>'.repeat(fut);
  return `<div class="sec v3-weeks"><h2>Недели по плану ${vis('me')}</h2><p class="v3-big disp"><span class="num">${k.n}</span> ${v3wkW(k.n)} по плану</p>
  <div class="v3-wk" role="img" aria-label="Недель по плану: ${k.n} из ${k.ci + 1}, впереди ${fut}">${cells}</div>
  <p class="xs mut">Пропущенная неделя не обнуляет счёт.</p></div>`; }

/* ── M-C: цена траты в днях цели ── */
function v3dayPrice(w, v, html){ const p = active(w).find(q => leftOf(q, w) > 0); if (!p || !(v > 0)) return '';
  const per = perDay(p, w); if (!(per > 0)) return ''; const n = Math.round(v / per), nm = html ? esc(p.name) : p.name;
  return n < 1 ? `Это меньше дневного плана на «${nm}».` : `На «${nm}» вы откладываете столько за ${daysW(n)}.`; }

/* ── M-E: срыв без обнуления — две равные дороги ── */
function v3slipCalc(p, w, amt){ const days = Math.max(1, daysTo(p) - (S.people[w].stepped ? 1 : 0)), left = leftOf(p, w),
    rate = perDay(p, w), base = Math.max(1, Math.ceil(Math.max(1, left - amt) / days)), shift = Math.max(1, Math.ceil(left / base) - days);
  return {rate, base, plus:Math.max(0, rate - base), shift, dl:p.dl + shift * DAY}; }
function v3took(p, w, amt){ p.saved[w] -= amt; if (p.conf && p.conf[w] > p.saved[w]) p.conf[w] = p.saved[w];
  S.v3.slip = {id:p.id, amt, why:'took'}; v3log('slip_shown'); go('slip'); }
function v3behind(p, w){ const tot = Math.max(1, Math.round((p.dl - p.cr) / DAY)), el = Math.round((now() - p.cr) / DAY);
  return Math.floor((p.share[w] || 0) * el / tot) - (p.saved[w] || 0); }
const v3shared = p => p.group ? p.group.members.length > 1 : p.share[OTHER[p.owner]] != null;
SCR.slip = function(){ const sl = S.v3.slip, p = sl && P(sl.id), w = S.who; if (!p || p.share[w] == null) return scrPurchase();
  const c = v3slipCalc(p, w, sl.amt), took = sl.why === 'took';
  return {notabs:true, html:`${backBtn('purchase', 'К цели')}<p class="mut sm">«${esc(p.name)}» · ${took ? 'взяли из отложенного' : 'до плана не хватает'} <span class="num">${rubT(sl.amt)}</span> ${vis('me')}</p>
  <h1 class="h1 disp">${took ? 'Бывает. Как вернуться к плану?' : 'Как догнать план?'}</h1>
  <p class="mut">${took ? 'Отложенное не сгорело: осталось ' + rubT(p.saved[w] || 0) + '.' : 'Ничего не сгорело.'}</p>
  <div class="v3-pair"><button class="sec2 press" data-act="v3slipDate">Сдвинуть срок на ${daysW(c.shift)}<small>к ${dStr(c.dl)}, ${rubT(c.base)} в день</small></button>
  <button class="sec2 press" data-act="v3slipDay">Откладывать +${rubT(c.plus)} в день<small>к ${dStr(p.dl)}, ${rubT(c.rate)} в день</small></button></div>
  ${v3shared(p) ? '<p class="xs mut">Новый срок увидят все в цели, без причин и сумм.</p>' : ''}`}; };

/* ── M-G / M-F / M-J: сводка недели ── */
function v3weekSolo(p, w){ const wk = weekRow(w), k = p ? v3weeks(p, w) : null;
  return `<h3 class="disp">Итоги недели ${vis('me')}</h3><p class="big disp">${wk.done} ${plural(wk.done, 'шаг', 'шага', 'шагов')} из 7</p>
  ${k ? `<p>Недель по плану: <span class="num">${k.n}</span>. Пропуск не обнуляет счёт.</p>` : ''}${wk.html}
  <button class="main press" data-act="shareWeek" style="margin-top:12px">Поделиться карточкой</button><button class="sec2 press" data-sheet="v3direct">Сказать прямо</button>
  <p class="xs mut" style="margin-top:8px">В карточке нет сумм.</p>`; }
function v3weekGroup(p, w){ const ms = p.group.members, many = ms.length >= 3, wk = weekRow(w), k = v3weeks(p, w),
    on = ms.filter(m => v3stat(p, m) === 'по плану').length;
  return `<h3 class="disp">Итоги недели</h3><div class="sec" style="margin-top:8px"><h2>Ваш результат ${vis('me')}</h2>
  <p class="big disp">${wk.done} ${plural(wk.done, 'шаг', 'шага', 'шагов')} из 7</p><p>Недель по плану: <span class="num">${k.n}</span>.</p></div>
  <div class="sec"><h2>Общая цель ${visG()}</h2><p class="v3-wsum">${many ? `По плану <span class="num">${on}</span> из <span class="num">${ms.length}</span> участников.` : v3fits(p) ? 'К сроку сходится.' : 'Пока не сходится.'}</p>
  <p class="xs mut">Напоминаем мы — без имён и сумм.</p></div>
  <button class="main press" data-close>Закрыть</button><button class="sec2 press" data-sheet="v3direct">Сказать прямо</button>`; }
SH.weeksum = () => { const w = S.who, p = v3goalOf(w); return p && p.group && p.share[w] != null ? v3weekGroup(p, w) : v3weekSolo(p, w); };
/* прямота — только по кнопке: свои цифры, без оценок характера */
SH.v3direct = () => { const w = S.who, p = v3goalOf(w); if (!p) return `<h3 class="disp">Прямо</h3><p>Целей пока нет.</p><button class="main press" data-close>Вернуться</button>`;
  const b = v3behind(p, w), c = v3slipCalc(p, w, Math.max(0, b));
  return `<h3 class="disp">Прямо, раз вы спросили ${vis('me')}</h3>
  ${b > 0 ? `<p>До плана не хватает <b class="num">${rubT(b)}</b>. Догнать — это +${rubT(c.plus)} в день.</p><p class="sm mut">Или сдвинуть срок. Решать вам.</p><button class="main press" data-act="v3slipBehind">Перестроить план</button>`
    : `<p>Вы по плану: отложено на <b class="num">${rubT(-b)}</b> больше нужного.</p><p class="sm mut">Дальше — <span class="num">${rubT(perDay(p, w))}</span> в день.</p><button class="main press" data-close>Вернуться к цели</button>`}`; };

/* ── M-L: отдельная копилка под цель ── */
const v3where0 = SH.where;
SH.where = a => v3sub(v3where0(a), 'Отдельное место помогает не потратить отложенное.', 'Отдельная копилка под эту цель помогает не потратить отложенное.', 'mot:where');

/* ── M-D: ссылка на копилку своего банка ── */
function v3bankBtn(cls, short){ const p = v3goalOf(S.who), wh = p ? (p.where || {})[S.who] : null;
  return `<button class="${cls}" data-act="v3bank">${V3_BANK[wh] ? (short ? 'Открыть ' + V3_BANK[wh] : `Открыть ${V3_BANK[wh]} в своём банке`) : 'Завести копилку в своём банке'}</button>`; }

/* ── экраны v2 и flow_group: дописываем поверх ── */
const v3mToday0 = scrToday;
scrToday = SCR.today = function(){ const r = v3mToday0(), w = S.who; if (!me().income || !r.html) return r;
  r.html = v3dom(r.html, f => {
    const big = f.querySelector('[data-out="left-today"]'); if (!big) return v3miss('mot:today');
    big.setAttribute('data-v3-money', '');
    const sub = big.nextElementSibling; (sub || big).insertAdjacentHTML('afterend', `<p class="xs mut v3-buf">Запас ${rubT(v3buf(w))} в месяц уже вычтен.</p>`);
    const self = [...f.querySelectorAll('details .rowl')].find(x => /На себя в день/.test(x.textContent));
    if (self) self.insertAdjacentHTML('beforebegin', `<div class="rowl"><span>Запас на непредвиденное</span><b class="num">− ${rubT(v3buf(w))}</b></div>`); else v3miss('mot:today-calc');
    const ans = f.querySelector('[data-out="afford"]'), dp = S.aff != null ? v3dayPrice(w, S.aff, true) : '';
    if (ans && dp) ans.insertAdjacentHTML('afterend', `<p class="sm v3-dayprice">${dp}</p>`); });
  return r; };
const v3mBotSay0 = botSay;
botSay = function(text){ const m = me(), n = m.chat.length; v3mBotSay0(text);
  const a = m.chat.slice(n).find(x => x.out === 'afford'), dp = a ? v3dayPrice(S.who, numIn(text.replace(/\d{1,2}\s*числ/g, '')), true) : '';
  if (dp) a.b += ' ' + dp; };
const v3mBot0 = scrBot;
scrBot = SCR.bot = function(){ const r = v3mBot0(); r.html = v3dom(r.html, f => { const s = f.querySelector('[data-out="bot-payday"]'); if (!s) return;
  const kb = s.closest('.bub').querySelector('.kb'); if (kb) kb.insertAdjacentHTML('beforeend', v3bankBtn('', true)); }); return r; };

const v3mPurchase0 = scrPurchase;
scrPurchase = SCR.purchase = function(){ const r = v3mPurchase0(), p = P(), w = S.who; if (!p || p.share[w] == null || !r.html) return r;
  r.html = v3dom(r.html, f => {
    const wk = v3weeksHtml(p, w), row = f.querySelector('.week');
    if (row) row.insertAdjacentHTML('afterend', wk); else f.append(document.createRange().createContextualFragment(wk));
    if (p.group) { const ms = f.querySelector('.v3-members'); if (ms) ms.insertAdjacentHTML('afterend', '<p class="xs mut v3-remind">Напоминаем участникам мы, без сумм. Писать никому не нужно.</p>'); else v3miss('mot:remind'); }
    if (p.state === 'done') { const done = S.purchases.filter(q => q.state === 'done' && q.share[w] != null).sort((a, b) => a.dl - b.dl), sum = done.reduce((s, q) => s + (q.share[w] || 0), 0);
      const shelf = `<div class="sec v3-shelfsec"><h2>Собранные цели ${vis('me')}</h2><div class="v3-shelf">${done.map(q => `<figure><span class="mini" data-pic="${q.photo}" data-pct="1"><img class="fog" alt=""><img class="color" alt=""></span><figcaption>${esc(q.cap || q.name)}<br>${dStr(q.dl)}</figcaption></figure>`).join('')}</div>
        <p class="sm">Вы собрали ${done.length} ${plural(done.length, 'цель', 'цели', 'целей')} — <span class="num">${rubT(sum)}</span>.</p></div>`;
      const note = [...f.querySelectorAll('.left')].find(x => /Собрано/.test(x.textContent)), at = note && note.nextElementSibling && note.nextElementSibling.classList.contains('note') ? note.nextElementSibling : note;
      if (at) at.insertAdjacentHTML('afterend', shelf); else f.prepend(document.createRange().createContextualFragment(shelf)); }
  });
  if (p.state === 'done') r.main = ['Создать следующую цель', 'v3next'];
  return r; };

/* уведомление в день зарплаты: ссылка на копилку и подпись видимости по режиму цели */
const v3mRender0 = render;
render = function(...a){ const r = v3mRender0.apply(this, a);
  try { const pu = $('#pushwrap .push'); if (pu && !pu.querySelector('[data-act="v3bank"]')) { const s = $('.sm', pu), m = v3mode();
      if (s && m !== 'pair') s.textContent = v3sub(s.textContent, 'Партнёр увидит только общий прогресс.', m === 'group' ? 'Участники увидят только статус.' : 'Это видно только вам.', 'mot:push');
      pu.insertAdjacentHTML('beforeend', v3bankBtn('link sm v3-bank')); } } catch (e) { console.warn('v3 motivation:', e); }
  return r; };

/* M-J: похвала за факт — когда неделя только что засчиталась */
const v3mStep0 = step;
step = function(a){ const w = S.who, p = P() && P().share[w] != null ? P() : active(w)[0], b = p ? v3weeks(p, w).n : 0; v3mStep0(a);
  if (!p) return; const n = v3weeks(p, w).n; if (n > b) toast(`Неделя засчитана — уже ${n} ${v3wkW(n)} по плану.`); };

/* M-E: «Пришлось взять из отложенного» — вместо тоста экран с двумя дорогами. Захват раньше обработчика v2 */
document.addEventListener('submit', e => { const f = e.target; if (f.id !== 'inputf' || f.dataset.k !== 'took') return;
  e.preventDefault(); e.stopImmediatePropagation(); const p = P(), w = S.who, v = numIn($('#inputv').value); if (!p || !v) return;
  const took = Math.min(v, p.saved[w] || 0); if (!(took > 0)) { closeSheet(); return toast('Отложенного пока нет — план прежний'); }
  v3took(p, w, took); }, true);

Object.assign(ACT, {
  v3slipDate(){ const sl = S.v3.slip, p = P(sl.id), c = v3slipCalc(p, S.who, sl.amt); p.dl = c.dl; v3log('slip_date'); S.v3.slip = null; go('purchase');
    toast(`Новый срок — ${dStr(p.dl)}. ${rubT(perDay(p, S.who))} в день.`); },
  v3slipDay(){ const p = P(S.v3.slip.id); v3log('slip_day'); S.v3.slip = null; go('purchase'); toast(`Срок прежний. ${rubT(perDay(p, S.who))} в день.`); },
  v3slipBehind(){ const w = S.who, p = v3goalOf(w); S.cur = p.id; S.v3.slip = {id:p.id, amt:Math.max(1, v3behind(p, w)), why:'behind'}; v3log('slip_shown'); go('slip'); },
  v3next(){ v3log('next_goal_started'); S.v3.back = null; S.draftText = ''; go('phrase'); },
  v3bank(){ const p = v3goalOf(S.who), wh = p ? (p.where || {})[S.who] : null; v3log('bank_open');
    if (!V3_BANK[wh]) { if (p) S.cur = p.id; return openSheet('where'); }
    toast('Откроется приложение вашего банка. Деньги остаются у вас.'); }
});

/* ── коды состояний ── */
Object.assign(V3_SCEN, {
  dayprice(){ V3_SCEN.solo(); S.aff = 7000; go('today'); const el = $('#view .v3-dayprice'); if (el) $('#view').scrollTop = Math.max(0, el.offsetTop - 260); },
  slip(){ V3_SCEN.solo(); const p = P(); p.saved.oleg = 50000; p.conf.oleg = 45000; v3took(p, 'oleg', 20000); },
  weeks(){ V3_SCEN.solo(); const p = P(); p.v3wk = {oleg:[1, 1, 0, 1]}; Object.assign(S.people.oleg, {week:[0, 0, 0], stepped:false}); go('purchase');
    const el = $('#view .v3-weeks'); if (el) $('#view').scrollTop = Math.max(0, el.offsetTop - 300); },
  weeksum3(){ V3_SCEN.group3(); openSheet('weeksum'); },
  nextgoal(){ v3reset();
    v3goal({id:'n1', name:'Новый телефон', cap:'Телефон', photo:'phone-dark', price:45000, cr:Date.UTC(2026, 1, 1), dl:Date.UTC(2026, 5, 1),
      share:{oleg:45000, anya:null}, saved:{oleg:45000, anya:0}, conf:{oleg:45000}, where:{oleg:'Копилка в банке'}, state:'done'});
    v3goal({id:'n2', name:'Отпуск на море', cap:'Море', photo:'sea', price:120000, cr:Date.UTC(2026, 0, 12), dl:Date.UTC(2026, 9, 1),
      share:{oleg:120000, anya:null}, saved:{oleg:120000, anya:0}, conf:{oleg:120000}, where:{oleg:'Копилка в банке'}, state:'done'});
    go('purchase'); const el = $('#view .v3-shelfsec'); if (el) $('#view').scrollTop = Math.max(0, el.offsetTop - 300); }
});
"""
