# -*- coding: utf-8 -*-
"""Модуль v3 «Мотивация» (волна 3b, после flow_group; правки по ревью — волна 5): механики Р2 из market/motivation/2026-10-04_D_mechanics.md.

Что делает (по механикам):
  M-B  «Сегодня на себя» с запасом прочности: из суммы вычитается запас 5 % дохода в месяц (V3_BUF), одна строка о запасе
       под числом и строка в «Как я посчитал». Единственная замена R — формула selfDay (она const, обёрткой не взять).
  M-C  Цена траты в днях цели: к ответу «влезет ли» (экран «Сегодня» и бот) — «на «цель» вы откладываете столько за N дней».
       В боте фраза идёт отдельным предложением: ответу v2 без точки в конце точка дописывается (QA №8).
  M-D  День зарплаты: в уведомлении и в сообщении бота — «Открыть копилку в своём банке» (или «Завести», если места нет).
  M-E  Срыв без обнуления: «Пришлось взять из отложенного» ведёт на экран slip — «Сдвинуть срок на N дней» и
       «Откладывать +M ₽ в день», две равные кнопки. Тот же экран — «Перестроить план» из разбора «Показать как есть».
       Сдвиг не больше исходного срока цели и не больше года (V3_SHIFT_MAX, QA №3); год в дате — если срок уходит
       в следующий год. Если догонять нечего (+0 ₽) — одна кнопка «Продолжить по плану». Доплата меньше
       V3_SLIP_MIN = 150 ₽ в день — главная кнопка «Догнать: +N ₽ в день» и ссылка «или сдвинуть срок» (в общей цели
       ссылка ведёт к предложению срока); от 150 ₽ — две равные кнопки (решение владельца 05.10).
       Общая цель (решение владельца 05.10): «Предложить новый срок» — предложение без причин и сумм; остальные видят
       на экране цели «Предложено перенести срок на …» и «Согласен(на)» / «Оставить срок»; срок меняется, когда согласны все.
       До согласия у предложившего — «догнать свою часть: +N ₽ в день». В показе участники без своего входа
       (Тимур, Света) соглашаются при смене дня.
  M-F  Счёт недель по плану без сгорания. Блока нет до первой отметки по цели; отметки недели до дня создания цели
       не считаются (QA №14). На экране с v2-плёнкой недели — одна строка «N недель по плану» (третьей полоски нет);
       где плёнки нет (общая цель) — сетка .v3-day (закрашенные .on): прошедшие недели и текущая, не больше 13,
       будущее — строкой «Впереди ещё N недель». Пропуск — сплошная дорожка --film, не пустой контур.
  M-G  Сводка недели в общей цели на 3–6: «ваш результат» + «по плану N из M участников»; без имён и чужих сумм.
       На двоих — только «к сроку сходится / пока не сходится», как у flow_group.
  M-I  В общей цели напоминает продукт: строка под участниками и в сводке.
  M-J  Тон: похвала за факт (тост «Неделя засчитана — уже N»), прямота — только по кнопке «Показать как есть» (лист v3direct).
  M-K  После «Собрано»: полка собранных целей и «Создать следующую цель» → Э-02.
  M-L  Лист «Где будут лежать деньги»: отдельная копилка под эту цель.

Коды: dayprice, slip, slipPropose, weeks, weeksum3, nextgoal. Журнал событий — demo.v3.log() (slip_shown, slip_date,
slip_day, slip_propose, slip_agreed, slip_kept, next_goal_started, bank_open). Подмены текста v2 идут через v3sub
flow_group — промахи видны в demo.v3.warn().
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
.v3-day.v3-now{outline:2px solid var(--ink);outline-offset:1px}
.v3-wkline{margin:8px 0 0}
.v3-pair .sec2 small{display:block;font-weight:400;font-size:.875rem;letter-spacing:0;color:var(--ink2);margin-top:2px}
.v3-pair .sec2 small .num{color:var(--ink);font-weight:600}
.v3-prop{margin:10px 0}
.v3-sliplink{display:block;min-height:44px;margin:4px 0 0}
.v3-shelf{display:flex;gap:10px;overflow-x:auto;margin:6px 0 8px;scrollbar-width:none}
.v3-shelf figure{margin:0;width:84px;flex:none}
.v3-shelf .mini{position:relative;display:block;width:84px;height:84px;border-radius:4px;overflow:hidden;background:var(--film)}
.v3-shelf .mini img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}
.v3-shelf figcaption{font-size:.8125rem;letter-spacing:.01em;line-height:1.3;color:var(--ink2);margin-top:4px}
.push .v3-bank{margin-top:4px}
"""

JS = r"""
/* ── v3 · motivation: механики Р2 (M-B…M-L), см. market/motivation/2026-10-04_D_mechanics.md ── */
const V3_SLIP_MIN = 150;                             /* M-E: доплата меньше — сдвиг срока не предлагается равной кнопкой (решение владельца 05.10) */
const V3_BUF = .05;                                  /* M-B: запас прочности — доля дохода в месяц */
const V3_WEEK = 7 * DAY;
const V3_WKMAX = 13;                                 /* M-F: сколько недель видно в сетке (прошедшие + текущая) */
const V3_SHIFT_MAX = 365;                            /* M-E: сдвиг срока — не больше года и не больше исходного срока цели */
const V3_BANK = {'Копилка в банке':'копилку', 'Вклад':'вклад', 'Отдельный счёт':'отдельный счёт'};
function v3buf(w){ const i = S.people[w].income; return i ? Math.round(i.m * V3_BUF / 100) * 100 : 0; }
function v3miss(where){ if (!v3warn.includes(where)) v3warn.push(where); }
const v3goalOf = w => P() && P().share[w] != null ? P() : active(w)[0];
const v3yr = t => new Date(t).getUTCFullYear();
/* дата с годом, если год другой, чем у ref (старого срока); без ref — как dStr во всём прототипе */
const v3dY = (t, ref) => dStr(t) + (ref != null && v3yr(t) !== v3yr(ref) ? NB + v3yr(t) : '');
const v3N = s => `<span class="num">${s}</span>`;
const v3she = w => w === 'anya' || w === 'sveta';

/* ── M-F: счёт недель без сгорания. Неделя — с понедельника, как в weekRow ── */
const v3mon = t => t - ((new Date(t).getUTCDay() + 6) % 7) * DAY;
/* отметки этой недели по цели: дни до создания цели не считаются (у новой цели нет «1 неделя по плану») */
function v3wkMarks(p, w){ const d = weekRow(w).html.split('<div class="wd').slice(1), st = v3mon(p.cr) === v3mon(now()) ? (new Date(p.cr).getUTCDay() + 6) % 7 : 0;
  return d.filter((x, i) => i >= st && /^ on/.test(x)).length; }
function v3weeks(p, w){ const m0 = v3mon(p.cr), total = Math.max(1, Math.round((v3mon(p.dl) - m0) / V3_WEEK) + 1),
    ci = Math.min(total - 1, Math.max(0, Math.round((v3mon(now()) - m0) / V3_WEEK)));
  let past = (p.v3wk || {})[w];
  const none = !past && !((p.saved[w] || 0) > 0) && p.state !== 'done';   /* до первой отметки считать нечего */
  if (!past) {   /* истории нет — доля недель по плану из отложенного против плана; пропуски разнесены равномерно */
    const tot = Math.max(1, Math.round((p.dl - p.cr) / DAY)), el = Math.max(1, Math.round((now() - p.cr) / DAY)), exp = (p.share[w] || 0) * el / tot,
      k = Math.round(ci * Math.min(1, exp > 0 ? (p.saved[w] || 0) / exp : 1)), miss = ci - k;
    past = Array.from({length:ci}, (_, j) => Math.floor((j + 1) * miss / ci) === Math.floor(j * miss / ci)); }
  past = Array.from({length:ci}, (_, j) => !!past[j]);
  const cur = p.state === 'done' || (!none && onPlan(p, w) && v3wkMarks(p, w) > 0), cells = past.concat([cur]);
  return {cells, ci, total, none, n:cells.filter(Boolean).length}; }
const v3wkW = n => plural(n, 'неделя', 'недели', 'недель');
/* line — на экране уже есть v2-плёнка недели: одна строка вместо третьей полоски */
function v3weeksHtml(p, w, line){ const k = v3weeks(p, w); if (k.none) return '';
  const cnt = `<span class="num">${k.n}</span> ${v3wkW(k.n)} по плану`;
  if (line) return `<div class="v3-weeks v3-wkline"><p class="sm">${cnt}. Пропуск их не обнуляет. ${vis('me')}</p></div>`;
  const fut = Math.max(0, k.total - k.ci - 1), from = Math.max(0, k.cells.length - V3_WKMAX),
    cells = k.cells.slice(from).map((on, j) => `<i class="v3-day${on ? ' on' : ''}${from + j === k.ci && p.state !== 'done' ? ' v3-now' : ''}"></i>`).join('');
  return `<div class="sec v3-weeks"><h2>Недели по плану ${vis('me')}</h2><p class="v3-big disp">${cnt}</p>
  <div class="v3-wk" role="img" aria-label="Недель по плану: ${k.n} из ${k.ci + 1}">${cells}</div>
  <p class="xs mut">${fut ? `Впереди ещё ${fut} ${v3wkW(fut)}. ` : ''}Пропуск не обнуляет счёт.</p></div>`; }

/* ── M-C: цена траты в днях цели ── */
function v3dayPrice(w, v, html){ const p = active(w).find(q => leftOf(q, w) > 0); if (!p || !(v > 0)) return '';
  const per = perDay(p, w); if (!(per > 0)) return ''; const n = Math.round(v / per), nm = html ? esc(p.name) : p.name;
  return n < 1 ? `Это меньше дневного плана на «${nm}».` : `На «${nm}» вы откладываете столько за ${daysW(n)}.`; }

/* ── M-E: срыв без обнуления — две равные дороги ──
   was  — темп до траты (его человек видел на экране цели); rate — темп к прежнему сроку; plus — разница.
   shift — сколько дней нужно, чтобы держать прежний темп, но не больше cap: исходный срок цели и год.
   Дальше — уже другая цель, а не сдвиг. base — темп к новому сроку (при упоре в cap он выше was). */
const v3paceTo = (p, w, dl) => Math.ceil(leftOf(p, w) / Math.max(1, Math.round((dl - now()) / DAY) - (S.people[w].stepped ? 1 : 0)));
function v3slipCalc(p, w, amt){ const st = S.people[w].stepped ? 1 : 0, d0 = daysTo(p), days = Math.max(1, d0 - st), left = leftOf(p, w),
    rate = perDay(p, w), was = Math.ceil(Math.max(0, left - amt) / days), plus = Math.max(0, rate - was),
    cap = Math.max(1, Math.min(V3_SHIFT_MAX, Math.round((p.dl - p.cr) / DAY))),
    shift = Math.min(cap, Math.max(1, was > 0 ? Math.ceil(left / was) - days : cap)),
    base = Math.ceil(left / Math.max(1, d0 + shift - st));
  const keep = plus === 0 || base >= rate;
  return {rate, was, plus, cap, shift, base, dl:p.dl + shift * DAY, keep, small: !keep && plus < V3_SLIP_MIN}; }
function v3took(p, w, amt){ p.saved[w] -= amt; if (p.conf && p.conf[w] > p.saved[w]) p.conf[w] = p.saved[w];
  S.v3.slip = {id:p.id, amt, why:'took'}; v3log('slip_shown'); go('slip'); }
function v3behind(p, w){ const tot = Math.max(1, Math.round((p.dl - p.cr) / DAY)), el = Math.round((now() - p.cr) / DAY);
  return Math.floor((p.share[w] || 0) * el / tot) - (p.saved[w] || 0); }
const v3shared = p => p.group ? p.group.members.length > 1 : p.share[OTHER[p.owner]] != null;
const v3members = p => p.group ? p.group.members.slice() : [p.owner, OTHER[p.owner]].filter(m => p.share[m] != null);
SCR.slip = function(){ const sl = S.v3.slip, p = sl && P(sl.id), w = S.who; if (!p || p.share[w] == null) return scrPurchase();
  const c = v3slipCalc(p, w, sl.amt), took = sl.why === 'took', sh = v3shared(p);
  const why = took ? `Взяли ${v3N(rubT(sl.amt))}. Отложенное не сгорело: осталось ${v3N(rubT(p.saved[w] || 0))}.` : `До плана не хватает ${v3N(rubT(sl.amt))}. Ничего не сгорело.`;
  const top = `${backBtn('purchase', 'К цели')}<h1 class="h1 disp">${c.keep ? 'План почти не изменился' : took ? 'Бывает. Как вернуться к плану?' : 'Как догнать план?'}</h1><p class="mut">${why} ${vis('me')}</p>`;
  if (c.keep) return {notabs:true, html:`${top}<p>По-прежнему ${v3N(rubT(c.rate))} в день, к ${dStr(p.dl)}.</p>`, main:['Продолжить по плану', 'v3slipDay']};
  const note = sh ? '<p class="xs mut">Новый срок сменится, если согласятся все. Без причин и сумм.</p>' : '';
  /* доплата меньше V3_SLIP_MIN: одна главная кнопка «Догнать», сдвиг — вторичной ссылкой */
  if (c.small) return {notabs:true, html:`${top}<p>К ${dStr(p.dl)} — ${v3N(rubT(c.rate))} в день вместо ${v3N(rubT(c.was))}.</p>
  <button class="link sm v3-sliplink" data-act="v3slipDate">или сдвинуть срок</button>${note}`, main:[`Догнать: +${rubT(c.plus)} в день`, 'v3slipDay']};
  const sub = `<small>к ${v3N(v3dY(c.dl, p.dl))}, ${v3N(rubT(c.base))} в день</small>`;
  return {notabs:true, html:`${top}
  <div class="v3-pair"><button class="sec2 press" data-act="v3slipDate">${sh ? 'Предложить новый срок' : 'Сдвинуть срок на ' + daysW(c.shift)}${sub}</button>
  <button class="sec2 press" data-act="v3slipDay">Откладывать +${rubT(c.plus)} в день<small>к ${dStr(p.dl)}, ${v3N(rubT(c.rate))} в день</small></button></div>
  ${sh ? '<p class="xs mut">Сменится, если согласятся все. Без причин и сумм.</p>' : ''}`}; };

/* общая цель: предложение нового срока. Видят все участники — только дату и «согласны k из n», без причин, сумм и автора */
function v3propCheck(p){ const pr = p.v3prop; if (!pr || pr.st !== 'open' || !v3members(p).every(m => pr.ok.includes(m))) return false;
  p.dl = pr.dl; p.v3prop = null; v3log('slip_agreed'); return true; }
function v3propHtml(p, w){ const pr = p.v3prop, ms = v3members(p), k = ms.filter(m => pr.ok.includes(m)).length, d = v3dY(pr.dl, p.dl),
    up = perDay(p, w) - v3paceTo(p, w, pr.dl), cat = up > 0 ? `<br>Пока ждём — догнать свою часть: +${v3N(rubT(up))} в день.` : '';
  if (pr.st === 'kept') return pr.by !== w ? '' : `<div class="note v3-prop">Срок оставили прежним.${up > 0 ? `<br>Догнать свою часть: +${v3N(rubT(up))} в день.` : ''}<div class="kb"><button data-act="v3propSeen">Понятно</button></div></div>`;
  if (pr.by === w || pr.ok.includes(w)) return `<div class="note v3-prop">Предложено перенести срок на ${v3N(d)}. Согласны ${v3N(k)} из ${v3N(ms.length)}.${pr.by === w ? cat : ''}</div>`;
  return `<div class="note v3-prop">Предложено перенести срок на ${v3N(d)}.<div class="kb"><button data-act="v3propYes">${v3she(w) ? 'Согласна' : 'Согласен'}</button><button data-act="v3propNo">Оставить срок</button></div></div>`; }

/* ── M-G / M-F / M-J: сводка недели ── */
function v3weekSolo(p, w){ const wk = weekRow(w), k = p ? v3weeks(p, w) : null;
  return `<h3 class="disp">Итоги недели ${vis('me')}</h3><p class="big disp">${wk.done} ${plural(wk.done, 'шаг', 'шага', 'шагов')} из 7</p>
  ${k && !k.none ? `<p>Недель по плану: <span class="num">${k.n}</span>. Пропуск не обнуляет счёт.</p>` : ''}${wk.html}
  <button class="main press" data-act="shareWeek" style="margin-top:12px">Поделиться карточкой</button><button class="sec2 press" data-sheet="v3direct">Показать как есть</button>
  <p class="xs mut" style="margin-top:8px">В карточке нет сумм.</p>`; }
function v3weekGroup(p, w){ const ms = p.group.members, many = ms.length >= 3, wk = weekRow(w), k = v3weeks(p, w),
    on = ms.filter(m => v3stat(p, m) === 'по плану').length;
  return `<h3 class="disp">Итоги недели</h3><div class="sec" style="margin-top:8px"><h2>Ваш результат ${vis('me')}</h2>
  <p class="big disp">${wk.done} ${plural(wk.done, 'шаг', 'шага', 'шагов')} из 7</p>${k.none ? '' : `<p>Недель по плану: <span class="num">${k.n}</span>.</p>`}</div>
  <div class="sec"><h2>Общая цель ${visG()}</h2><p class="v3-wsum">${many ? `По плану <span class="num">${on}</span> из <span class="num">${ms.length}</span> участников.` : v3fits(p) ? 'К сроку сходится.' : 'Пока не сходится.'}</p>
  <p class="xs mut">Напоминаем мы — без имён и сумм.</p></div>
  <button class="main press" data-close>Закрыть</button><button class="sec2 press" data-sheet="v3direct">Показать как есть</button>`; }
SH.weeksum = () => { const w = S.who, p = v3goalOf(w); return p && p.group && p.share[w] != null ? v3weekGroup(p, w) : v3weekSolo(p, w); };
/* прямота — только по кнопке: свои цифры, без оценок характера */
SH.v3direct = () => { const w = S.who, p = v3goalOf(w); if (!p) return `<h3 class="disp">Как есть</h3><p>Целей пока нет.</p><button class="main press" data-close>Вернуться</button>`;
  const b = v3behind(p, w), c = v3slipCalc(p, w, Math.max(0, b));
  return `<h3 class="disp">Как есть, раз вы спросили ${vis('me')}</h3>
  ${b > 0 && c.plus > 0 ? `<p>До плана не хватает <b class="num">${rubT(b)}</b>. Догнать — это +${rubT(c.plus)} в день.</p><p class="sm mut">Или сдвинуть срок. Решать вам.</p><button class="main press" data-act="v3slipBehind">Перестроить план</button>`
    : `<p>Вы по плану${b < 0 ? `: отложено на <b class="num">${rubT(-b)}</b> больше нужного` : ''}.</p><p class="sm mut">Дальше — <span class="num">${rubT(perDay(p, w))}</span> в день.</p><button class="main press" data-close>Вернуться к цели</button>`}`; };

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
/* бот: фраза M-C — отдельным предложением. У ответов v2 «Останется 896 ₽», «Зарплата 10 октября» нет точки */
const v3mBotSay0 = botSay;
botSay = function(text){ const m = me(), n = m.chat.length; v3mBotSay0(text);
  const a = m.chat.slice(n).find(x => x.out === 'afford'), dp = a ? v3dayPrice(S.who, numIn(text.replace(/\d{1,2}\s*числ/g, '')), true) : '';
  if (dp) { const b = a.b.trim(); a.b = (/[.!?…]$/.test(b) ? b : b + '.') + ' ' + dp; } };
const v3mBot0 = scrBot;
scrBot = SCR.bot = function(){ const r = v3mBot0(); r.html = v3dom(r.html, f => { const s = f.querySelector('[data-out="bot-payday"]'); if (!s) return;
  const kb = s.closest('.bub').querySelector('.kb'); if (kb) kb.insertAdjacentHTML('beforeend', v3bankBtn('', true)); }); return r; };

const v3mPurchase0 = scrPurchase;
scrPurchase = SCR.purchase = function(){ const r = v3mPurchase0(), p = P(), w = S.who; if (!p || p.share[w] == null || !r.html) return r;
  r.html = v3dom(r.html, f => {
    const film = !!f.querySelector('.film'), wk = v3weeksHtml(p, w, film || p.state === 'done'), row = f.querySelector('.week'),
      shared = [...f.querySelectorAll('.sec')].find(s => /^Общая цель/.test(((s.querySelector('h2') || {}).textContent || '').trim()));
    if (wk) { if (row) row.insertAdjacentHTML('afterend', wk); else if (shared) shared.insertAdjacentHTML('beforebegin', wk); else f.append(document.createRange().createContextualFragment(wk)); }
    if (p.v3prop) { const ph = v3propHtml(p, w), hd = f.querySelector('.head'); if (ph) { if (hd) hd.insertAdjacentHTML('afterend', ph); else f.prepend(document.createRange().createContextualFragment(ph)); } }
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

/* общая цель: в показе участники без своего входа (Тимур, Света) соглашаются на следующий день */
const v3mSetDay0 = setDay;
setDay = function(off){ v3mSetDay0(off); let ch = false;
  for (const p of S.purchases) { const pr = p.v3prop; if (!pr || pr.st !== 'open') continue;
    for (const m of v3members(p)) if (!S.people[m] && !pr.ok.includes(m)) { pr.ok.push(m); ch = true; }
    if (v3propCheck(p)) ch = true; }
  if (ch) render(true); };

/* M-E: «Пришлось взять из отложенного» — вместо тоста экран с двумя дорогами. Захват раньше обработчика v2 */
document.addEventListener('submit', e => { const f = e.target; if (f.id !== 'inputf' || f.dataset.k !== 'took') return;
  e.preventDefault(); e.stopImmediatePropagation(); const p = P(), w = S.who, v = numIn($('#inputv').value); if (!p || !v) return;
  const took = Math.min(v, p.saved[w] || 0); if (!(took > 0)) { closeSheet(); return toast('Отложенного пока нет — план прежний'); }
  v3took(p, w, took); }, true);

Object.assign(ACT, {
  v3slipDate(){ const sl = S.v3.slip, p = P(sl.id), w = S.who, c = v3slipCalc(p, w, sl.amt), dl0 = p.dl; S.v3.slip = null;
    if (v3shared(p)) { p.v3prop = {by:w, dl:c.dl, ok:[w], st:'open'}; v3log('slip_propose'); const now1 = v3propCheck(p); go('purchase');
      return toast(now1 ? `Новый срок — ${v3dY(p.dl, dl0)}.` : 'Предложение отправлено. Срок сменится, когда согласятся все.'); }
    p.dl = c.dl; v3log('slip_date'); go('purchase'); toast(`Новый срок — ${v3dY(p.dl, dl0)}. ${rubT(perDay(p, w))} в день.`); },
  v3slipDay(){ const p = P(S.v3.slip.id); v3log('slip_day'); S.v3.slip = null; go('purchase'); toast(`Срок прежний. ${rubT(perDay(p, S.who))} в день.`); },
  v3slipBehind(){ const w = S.who, p = v3goalOf(w); S.cur = p.id; S.v3.slip = {id:p.id, amt:Math.max(1, v3behind(p, w)), why:'behind'}; v3log('slip_shown'); go('slip'); },
  v3propYes(){ const p = P(), pr = p && p.v3prop, w = S.who; if (!pr || pr.st !== 'open') return; if (!pr.ok.includes(w)) pr.ok.push(w); const dl0 = p.dl;
    const done = v3propCheck(p); render(true); toast(done ? `Все согласны. Новый срок — ${v3dY(p.dl, dl0)}.` : 'Ждём остальных участников.'); },
  v3propNo(){ const p = P(), pr = p && p.v3prop; if (!pr || pr.st !== 'open') return; pr.st = 'kept'; v3log('slip_kept'); render(true); toast('Срок прежний.'); },
  v3propSeen(){ const p = P(); if (p) p.v3prop = null; render(true); },
  v3next(){ v3log('next_goal_started'); S.v3.back = null; S.draftText = ''; go('phrase'); },
  v3bank(){ const p = v3goalOf(S.who), wh = p ? (p.where || {})[S.who] : null; v3log('bank_open');
    if (!V3_BANK[wh]) { if (p) S.cur = p.id; return openSheet('where'); }
    toast('Откроется приложение вашего банка. Деньги остаются у вас.'); }
});

/* ── коды состояний ── */
Object.assign(V3_SCEN, {
  dayprice(){ V3_SCEN.solo(); S.aff = 7000; go('today'); const el = $('#view .v3-dayprice'); if (el) $('#view').scrollTop = Math.max(0, el.offsetTop - 260); },
  /* доплата 164 ₽ ≥ V3_SLIP_MIN — две равные дороги; меньше порога — см. тест (одна кнопка + ссылка) */
  slip(){ V3_SCEN.solo(); const p = P(); p.saved.oleg = 50000; p.conf.oleg = 45000; v3took(p, 'oleg', 40000); },
  /* общая цель на четверых глазами Ани: Олег предложил новый срок, Тимур и Света согласились */
  slipPropose(){ V3_SCEN.group3(); const p = P(); p.v3prop = {by:'oleg', dl:p.dl + 30 * DAY, ok:['oleg', 'timur', 'sveta'], st:'open'}; S.who = 'anya'; go('purchase'); },
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
