# -*- coding: utf-8 -*-
"""Модуль v3 «Вход и группы» (flow_group, волна 3a, правки волны 5 по ревью 04.10).

Что делает:
  1. Вход: сторис-знакомство → Э-01 согласие → Э-08 пример «Диван в гостиную» (плашка «Пример», .v3-example) → «Создать свою цель» → Э-02…Э-05
     → Э-06 «Копить вместе?». Пример показывается один раз (S.people[w].exSeen), повторно — «Посмотреть пример» в листе how,
     каждый раз с исходных данных. Пример не похож на свои данные: без замка, пунктирная рамка, «Это пример, не ваши деньги».
     Сторис (решение владельца 05.10) — механика v2: «Пропустить», пауза удержанием, без автолистания при reduced-motion;
     5 карточек о помощнике для одного, общая цель — по желанию; события onboarding_done / onboarding_skipped.
  2. Режим одного: своя цель без партнёра — «своя цель», значки «видно только вам», вместо «Отправить партнёру» —
     «Копить вместе с кем-то». Слов о партнёре нет ни на экране, ни в листах (how, cancelAsk, photo, change, save, where).
     После «Пока сам» — без листа поверх: строка «Где лежат деньги — указать» и мостик в «Сегодня»; неделя новой цели с нуля.
  3. Общая цель (p.group): одна функция на 1–6 участников. До двух — только «к сроку сходится / пока не сходится»
     и шкала времени, без процентов. От трёх — общий прогресс с шагом 10 %.
     Приватность (решение владельца 05.10): общий % и чужие статусы — из одного суточного снимка (v3snap, при смене дня);
     порог плана — от даты входа участника (p.join). Чужой статус виден только как «по плану»; «отстаёт» и «только начали»
     видит только сам человек. Обещанная часть видна всем. Порядок участников — порядок входа.
     «Собрано» — когда собраны все части (gapOf и условие в step — по участникам). Участник выходит из цели, отменить её
     у всех может только организатор (с предупреждением). Вышедший или удаливший данные — у остальных «вышел(ла)».

Коды: example, solo, together, group2, group2step, group3, groupInvite (+ служебные empty, groupShare).
«Партнёр отложил сегодня» (partner) на общей цели на двоих — шаг другого и «Подбодрить», как в паре Р1; на 3–6 этого нет. Приставка anya- работает
для group2 / group3 (взгляд Ани). Журнал событий — demo.v3.log(); несработавшие подмены текста — demo.v3.warn().
Проверка: python build_v3.py --only flow_group → v3/_test_flow_group.html#<код>
"""

R = [
    # разбор фразы: «к» на конце слова («Ноутбук 90 тысяч») съедалось как срок «к 90 тысяч» → имя «Ноутбу к».
    # Срок вырезаем, только если «к» — отдельное слово и дальше месяц, как в parseDate
    (r".replace(/к\s+\d{1,2}\s+[а-я]+/i, '')",
     r".replace(/(^|\s)к\s+\d{1,2}\s+(?:январ|феврал|март|апрел|ма[йя]|июн|июл|август|сентябр|октябр|ноябр|декабр)[а-я]*/i, '$1')"),
    # своя часть словами одного человека: «откладываю 90» и «отложу 90» — как «могу 90»
    ("const shareM = clean.match(/(могу|внесу|мои|с меня|беру на себя)",
     "const shareM = clean.match(/(могу|внесу|мои|с меня|беру на себя|откладываю|отложу)"),
    # пульт: «fresh» — знакомство (сторис), согласие и пример
    ('data-sc="fresh">Первый вход: знакомство и согласие</button>', 'data-sc="fresh">Первый вход: знакомство, согласие и пример</button>'),
    # вкладка «Покупки» без целей ведёт на пустой список с примером, а не сразу на фразу
    ("go(d.tab === 'buy' ? (S.purchases.length > 1 ? 'list' : S.purchases.length ? 'purchase' : 'phrase') : d.tab)",
     "go(d.tab === 'buy' ? (S.purchases.length > 1 ? 'list' : S.purchases.length ? 'purchase' : 'list') : d.tab)"),
    # QA №2: недостающее и переплата — по всем участникам цели, а не только по Олегу и Ане
    ("const gapOf = p => Math.max(0, p.price - (p.share.oleg || 0) - (p.share.anya || 0));",
     "const gapOf = p => Math.max(0, p.price - v3people(p).reduce((s, m) => s + (p.share[m] || 0), 0));"),
    ("const overOf = p => Math.max(0, (p.share.oleg || 0) + (p.share.anya || 0) - p.price);",
     "const overOf = p => Math.max(0, v3people(p).reduce((s, m) => s + (p.share[m] || 0), 0) - p.price);"),
    # QA №2: «Собрано» — когда собраны все части этой цели (было: только у Олега и Ани и только если собраны все цели сразу)
    ("if (S.purchases.every(q => q.state !== 'active' || (leftOf(q, 'oleg') === 0 && (q.share.anya == null || leftOf(q, 'anya') === 0))) && gapOf(p) === 0) p.state = 'done';",
     "if (v3collected(p)) p.state = 'done';"),
    # QA №7: порог плана — от даты входа участника (p.join), а не от создания цели
    ("const onPlan = (p, w) => { const tot = Math.max(1, Math.round((p.dl - p.cr) / DAY)), el = Math.round((now() - p.cr) / DAY);",
     "const onPlan = (p, w) => { const c0 = v3from(p, w), tot = Math.max(1, Math.round((p.dl - c0) / DAY)), el = Math.max(0, Math.round((now() - c0) / DAY));"),
]

CSS = r"""
.v3-tag{display:inline-block;font-size:.8125rem;font-weight:600;letter-spacing:.01em;color:var(--accent);background:var(--soft);border-radius:10px;padding:2px 9px;margin:0 0 6px}
.v3-tag.v3-exbadge{font-size:.9375rem;padding:4px 12px;border:1.5px dashed currentColor;border-radius:12px}
.v3-example .cardp{outline:1.5px dashed var(--ink2);outline-offset:4px;box-shadow:none}
.v3-exnote{margin:12px 0 0;font-weight:500}
.v3-row{display:flex;gap:14px;align-items:center;flex-wrap:wrap;margin-top:8px}
.v3-pair{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin:18px 0 10px}
.v3-pair .sec2{margin-top:0;min-height:54px;font-weight:600}
.v3-big{font-size:calc(1.5rem*var(--d-k));margin:0 0 8px}
.v3-tl{position:relative;padding-top:20px;margin-top:6px}
.v3-time{position:relative;height:6px;border-radius:3px;background:var(--film)}
.v3-time i{position:absolute;top:-4px;width:2px;height:14px;margin-left:-1px;border-radius:1px;background:var(--ink2)}
.v3-tnow{position:absolute;top:0;white-space:nowrap}
.v3-timelab{display:flex;justify-content:space-between;margin:4px 0 6px}
.v3-steps{display:grid;grid-template-columns:repeat(10,1fr);gap:3px;margin:2px 0 6px}
.v3-steps i{height:10px;border-radius:2px;background:var(--film)} .v3-steps i.on{background:var(--fill)}
.v3-members{margin:10px 0 4px}
.v3-member,.v3-gonerow{display:flex;align-items:center;gap:10px;min-height:52px;padding:6px 0;border-bottom:1px solid var(--line)}
.v3-member>span:nth-child(2),.v3-gonerow>span:nth-child(2){flex:1;min-width:0}
.v3-gonerow{color:var(--ink2)}
.v3-ava{width:32px;height:32px;flex:none;border-radius:50%;display:grid;place-items:center;background:var(--soft);color:var(--accent);font-weight:600}
.v3-st{font-size:.8125rem;letter-spacing:.01em;color:var(--ok);border:1px solid currentColor;border-radius:14px;padding:3px 9px;white-space:nowrap}
.v3-st.wait,.stamp.wait,.stamp.v3-plain{color:var(--ink2)}
.v3-stampw{display:inline-flex;align-items:center;white-space:nowrap}
.v3-legend .vis{margin-left:0}
.v3-invite .photo{aspect-ratio:2/1}
.v3-invite .sec p{margin:2px 0 10px}
.v3-invite .sec p .vis{margin-left:2px}
.v3-pad{height:60px}
"""

JS = r"""
/* ── v3 · flow_group: вход с примером, режим одного, «Копить вместе?», общая цель ── */
const V3_MAX = 6;
const V3_EX = {name:'Диван в гостиную', price:120000, dl:Date.UTC(2026, 11, 31), saved:61000, step:12000};
Object.assign(NAME, {timur:'Тимур', sveta:'Света'});
const V3_FEM = ['anya', 'sveta'];
/* нейтральный туман для цели, которую не узнали по названию (раньше — диван, как в примере) */
ART.v3fog = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 500" preserveAspectRatio="xMidYMid slice"><defs><linearGradient id="v3g" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#D5DCDE"/><stop offset="1" stop-color="#8E9FA4"/></linearGradient></defs><rect width="400" height="500" fill="url(#v3g)"/><ellipse cx="110" cy="380" rx="230" ry="80" fill="#7D9095" opacity=".45"/><ellipse cx="320" cy="440" rx="210" ry="70" fill="#6C8086" opacity=".4"/></svg>';
const v3warn = [];
/* подмена текста v2 на лету; если строки нет (её поменял другой модуль) — запись в demo.v3.warn(), экран не падает */
function v3sub(s, a, b, where){ if (!s.includes(a)) { if (!v3warn.includes(where)) v3warn.push(where); return s; } return s.replace(a, b); }
function v3dom(html, fn){ const t = document.createElement('template'); t.innerHTML = html; fn(t.content); return t.innerHTML; }
function v3log(ev){ (S.v3 = S.v3 || {log:[]}).log.push(ev); }
const visG = () => vis('all').replace(/видит партнёр/g, 'видят участники');
const v3solo = (p, w) => !!p && !p.group && p.owner === w && p.share[w] != null && p.share[OTHER[w]] == null && !p.invited;
const v3mode = () => { const p = P(); return !p ? 'pair' : p.group ? 'group' : v3solo(p, S.who) ? 'solo' : 'pair'; };

/* ── расчёт общей цели: всё из договорённостей и суточного снимка, чужие отложенные суммы на экран не попадают ── */
function v3people(p){ return p.group ? p.group.members : ['oleg', 'anya']; }          /* gapOf, overOf, «Собрано» */
function v3from(p, w){ return (p.join || {})[w] || p.cr; }                           /* план участника — от его входа */
function v3collected(p){ return gapOf(p) === 0 && v3people(p).every(m => p.share[m] == null || leftOf(p, m) === 0); }
const v3floor10 = x => Math.floor(Math.min(1, Math.max(0, x)) * 10 + 1e-9) / 10;
const v3promised = p => p.group.members.reduce((s, m) => s + (p.share[m] || 0), 0);
const v3gap = p => Math.max(0, p.price - v3promised(p));
/* снимок раз в сутки: общий % и статусы участников из одних и тех же данных одного момента */
function v3snap(p){ const g = p.group;
  g.snap = v3floor10(g.members.reduce((s, m) => s + (p.saved[m] || 0), 0) / p.price);
  g.stat = {}; for (const m of g.members) g.stat[m] = {plan:onPlan(p, m), started:(p.saved[m] || 0) > 0};
  if (p.state === 'active' && v3collected(p)) p.state = 'done'; }
/* свой статус — живой (это свои данные), чужой — только из снимка */
const v3planOf = (p, m) => m === S.who ? onPlan(p, m) : !!((p.group.stat || {})[m] || {}).plan;
const v3stat = (p, m) => { const st = m === S.who ? {plan:onPlan(p, m), started:(p.saved[m] || 0) > 0} : (p.group.stat || {})[m] || {plan:true, started:false};
  return !st.started ? 'только начали' : st.plan ? 'по плану' : 'отстаёт'; };
const v3fits = p => v3gap(p) === 0 && p.group.members.every(m => v3planOf(p, m));
/* что видно на строке участника: чужой — только «по плану» (решение владельца 05.10), свой — всё */
function v3word(p, m, many){ const s = v3stat(p, m);
  if (m !== S.who && s !== 'по плану') return '';
  if (many || s === 'только начали') return s;
  return s === 'по плану' ? 'к сроку сходится' : 'пока не сходится'; }
function v3makeGroup(p){ if (!p.group) { p.group = {members:[p.owner], sent:false, snap:0, gone:[]}; v3snap(p); } return p.group; }
/* выход из цели: часть освобождается, у остальных — «вышел(ла)»; организатор передаётся следующему по входу */
function v3leave(p, w){ const g = p.group; g.members = g.members.filter(m => m !== w); g.gone = (g.gone || []).filter(m => m !== w).concat([w]);
  p.share[w] = null; p.saved[w] = 0; if (p.conf) p.conf[w] = 0; if (p.where) delete p.where[w]; if (g.stat) delete g.stat[w];
  if (p.owner === w && g.members.length) p.owner = g.members[0]; }
/* видит ли человек цель: участник; приглашённый по отправленной ссылке; не вышедший */
const v3sees = (p, w) => p.share[w] != null || (!(p.group && (p.group.gone || []).includes(w)) && !!p.invited);

/* ── состояние ── */
const v3seed0 = seed;
seed = function(mode){ const s = v3seed0(mode); s.v3 = {ex:V3_EX.saved, log:[], back:null, fromEx:false};
  for (const w of ['oleg','anya']) s.people[w].exSeen = mode === 'mid'; return s; };
/* новая цель человека без других целей: неделя с нуля, фото — нейтральный туман, если цель не узнали по названию */
const v3commit0 = commitDraft;
commitDraft = function(){ const w = S.who, first = !active(w).length, name = (S.draft || {}).name || '';
  v3commit0(); const p = P();
  if (first) Object.assign(me(), {week:[0, 0, 0], stepped:false, stepAmt:0});
  if (p && p.photo === 'sofa' && !/диван|софа|кресл|мебел/i.test(name)) p.photo = 'v3fog'; };

/* ── сторис-знакомство: механика v2, тексты под пивот — помощник для одного, общая цель по желанию ── */
SLIDES.splice(0, SLIDES.length,
  {p:0,   h:'Сколько сегодня можно на себя', t:'Каждое утро — одна сумма. Обязательное и отложенное на цель уже вычтены.'},
  {p:.15, h:'Цель к дате — на фото', t:'Поставьте фото того, на что копите. Пока оно в тумане.'},
  {p:.5,  h:'Туман отступает, когда откладываете', t:'Чёткая часть — уже отложено. Пропустили день — ничего не сгорает.'},
  {p:.6,  h:'Влезет ли покупка?', t:'Спросите до траты — ответим, сдвинет ли она цель.'},
  {p:1,   h:'Вместе с кем-то — по желанию', t:'Каждый видит свою часть и общий ход. Чужих денег не видит никто.', last:true});
const v3storyOn = () => $('#story').classList.contains('on');
document.addEventListener('click', e => { const b = e.target.closest && e.target.closest('#skip, #start'); if (!b || !v3storyOn()) return;
  v3log(b.id === 'start' ? 'onboarding_done' : 'onboarding_skipped'); }, true);
document.addEventListener('keydown', e => { if (e.key === 'Escape' && v3storyOn()) v3log('onboarding_skipped'); }, true);

/* ── Э-01 согласие: без партнёра в обещаниях ── */
const v3consent0 = scrConsent;
scrConsent = SCR.consent = function(){ const r = v3consent0();
  r.html = v3sub(r.html, 'Посчитаем, сойдётся ли покупка к сроку', 'Посчитаем, сойдётся ли цель к сроку', 'consent:h1');
  r.html = v3sub(r.html, 'Партнёр не видит ваши деньги — только общую покупку.', 'Ваши деньги видите только вы.', 'consent:partner');
  r.main = ['Согласен, дальше', r.main[1]]; return r; };
const v3policy0 = SH.policy;
SH.policy = a => v3sub(v3policy0(a), 'Партнёр видит покупку и свою часть, но не ваши деньги.', 'Участники общей цели видят цель и части, но не ваши деньги.', 'policy');
const v3consentOk0 = ACT.consentOk;
ACT.consentOk = function(){ const w = S.who;
  if (!me().exSeen && !S.purchases.some(p => p.share[w] != null || p.invited)) { me().consent = true; S.v3.back = null; S.v3.ex = V3_EX.saved; v3log('example_shown'); return go('example'); }
  v3consentOk0(); };

/* ── Э-08 пример: тот же вид цели на демо-данных, но видно, что это не ваши деньги; «Отложить» ничего не сохраняет ── */
let v3exToast = false;
function v3exScr(){ const e = V3_EX, saved = Math.min(e.price, S.v3.ex), pc = saved / e.price, left = e.price - saved,
    days = Math.max(1, Math.round((e.dl - now()) / DAY)), per = Math.ceil(left / days), ml = mileOf(pc);
  me().exSeen = true;
  return {notabs:true, html:`<div class="v3-example" data-v3-example="root">${S.v3.back ? backBtn(S.v3.back) : ''}
  <div class="head"><div><span class="v3-tag v3-exbadge v3-example">Пример</span><h1 class="disp">${e.name}</h1><p class="mut" style="margin:2px 0 0">к ${dStr(e.dl)} · через ${daysW(days)}</p></div></div>
  <div class="cardp"><div class="photo" data-pic="sofa" data-pct="${pc}" data-conf="${pc}" data-step="${e.step / e.price}" role="img" aria-label="Фото цели в примере: чёткая часть — отложено, в тумане — впереди">
    <img class="fog" alt=""><img class="color" alt=""><div class="thin"></div><div class="edge"></div><div class="rule"></div><div class="band"></div><div class="bandlab num">отложено</div><span class="pctlab num">отложено ${Math.round(pc * 100)}${NB}%</span>
    ${ml ? `<span class="mile${S.flash ? ' pop' : ''}">${ml[1]}</span>` : ''}</div>
    <div class="cap"><span class="hand">Диван</span><span class="stamp">${left ? 'сходится к сроку' : 'собрано'}</span></div></div>
  <p class="left disp"><small>Осталось отложить</small><span class="num" data-v3-money>${rub(left)}</span></p>
  ${left ? `<p class="mut" style="margin:0">по плану: <span class="num">${rub(per)}</span> в день</p>` : ''}
  <p class="sm v3-exnote">Это пример, не ваши деньги.</p>
  <div class="v3-row">${left ? `<button class="chip press num" data-act="v3exStep">Отложить ${rubT(Math.min(e.step, left))}</button>` : ''}<button class="link sm" data-sheet="how" style="min-height:44px">Как это работает?</button></div>
  </div>`, main:['Создать свою цель','v3own']}; }
SCR.example = v3exScr;
/* тост примера не переживает уход с примера */
const v3go0 = go;
go = function(scr, keep){ if (v3exToast && scr !== 'example') { v3exToast = false; clearTimeout(toastT); $('#toast').classList.remove('on'); } return v3go0(scr, keep); };

/* «Как это работает?»: ≤30 слов; значки видимости расшифрованы словами; о партнёре — только в паре */
SH.how = () => { if (S.scr === 'example') return `<h3 class="disp">Как читать пример</h3><p class="sm">Чёткая часть фото — отложено, туман — ещё впереди.</p><p class="sm">«Отложить» проясняет туман. Это пример — ничего не сохраняется.</p><button class="sec2 press" data-act="closeS">Понятно</button>`;
  const m = v3mode(), p = P(), many = m === 'group' && p.group.members.length >= 3;
  const photo = many ? '<b>Чётко</b> — отложено вместе, шаг 10 %. <b>Туман</b> — впереди.' : '<b>Чётко</b> — подтверждено выпиской, <b>дымка</b> — по отметкам, <b>туман</b> — впереди.';
  const legend = vis('me') + ' — видите только вы' + (m === 'solo' ? '' : m === 'group' ? '; ' + visG() + ' — видят участники' : '; ' + vis('all') + ' — видит партнёр');
  return `<h3 class="disp">Как это работает</h3><p class="sm">${photo}</p><p class="sm">${m === 'group' ? (p.group.members.length === 2 ? 'Точка — день у обоих. ' : '') : 'Кадр недели — 5 дней из 7. '}Пропуск ничего не отнимает.</p>
  <p class="sm v3-legend">${legend}.</p><button class="link" data-act="v3showEx">Посмотреть пример</button><button class="sec2 press" data-act="closeS">Понятно</button>`; };

/* ── Э-02 фраза и Э-03 уточнение: без партнёра по умолчанию ── */
const v3phrase0 = scrPhrase;
scrPhrase = SCR.phrase = function(){ const r = v3phrase0();
  r.html = v3sub(r.html, '<h1 class="h1 disp">Что покупаете?</h1><p class="mut">Как написали бы партнёру. Или ссылка на товар.</p>',
    '<h1 class="h1 disp">Что хотите купить и к какому сроку?</h1><p class="mut">Одной фразой или ссылкой.</p>', 'phrase:h1');
  r.html = r.html.replace(/, я могу (\d)/g, ', откладываю $1'); return r; };
const v3clar0 = scrClarify;
scrClarify = SCR.clarify = function(){ const r = v3clar0(); if (!/Сколько вносите вы\?/.test(r.html)) return r;
  r.html = r.html.replace(/Сколько вносите вы\?/g, 'Сколько отложите сами к сроку?');
  r.html = v3dom(r.html, f => {
    f.querySelectorAll('[data-clar="плачу сам"]').forEach(b => { b.textContent = 'всю сумму сам'; });
    f.querySelectorAll('[data-clar="половину"]').forEach(b => { b.removeAttribute('data-clar'); b.setAttribute('data-act', 'v3clarPart'); b.textContent = 'часть — впишу'; }); });
  return r; };
const v3phraseGo0 = ACT.phraseGo;
ACT.phraseGo = function(){ if (S.v3.fromEx) { S.v3.fromEx = false; v3log('own_goal_started'); } return v3phraseGo0(); };

/* ── Э-05 ответ: «Сохранить цель» → Э-06; строки ответа — .v3-answer-line (блочные) ── */
const v3ans0 = scrAnswer;
scrAnswer = SCR.answer = function(){ const r = v3ans0();
  r.html = v3dom(r.html, f => {
    [...f.children].forEach(el => { if ((el.tagName === 'P' || el.tagName === 'DIV') && !el.classList.contains('backb')) el.classList.add('v3-answer-line'); });
    const big = f.querySelector('.big.num'); if (big) big.setAttribute('data-v3-money', '');
    f.querySelectorAll('.rowl > span').forEach(s => { if (/^Партнёр внесёт/.test(s.textContent)) s.textContent = 'Скинуться с кем-то — позовёте после сохранения'; });
  });
  r.main = ['Сохранить цель','v3save']; r.extra = ''; return r; };

/* ── Э-06 «Копить вместе?»: две кнопки одного веса; подтверждение — обычным шрифтом (курсив — только ответ GigaChat) ── */
function v3togetherScr(){ const p = P(); if (!p) return scrList();
  return {notabs:true, html:`<p class="sm mut">Цель сохранена: ${esc(p.name)} к ${dStr(p.dl)}</p>
  <h1 class="h1 disp">Копить вместе с кем-то?</h1>
  <p class="mut">Позовёте — люди увидят цель, срок и свои части, но не ваши деньги.</p>
  <div class="v3-pair"><button class="sec2 press" data-act="v3alone">Пока сам</button><button class="sec2 press" data-act="v3call">Позвать</button></div>
  <p class="xs mut">Позвать можно и позже — с экрана цели.</p>`}; }
SCR.together = v3togetherScr;

/* ── «Покупки»: только цели, которые человек видит; без целей — карточка примера ── */
const v3list0 = scrList;
scrList = SCR.list = function(){ const w = S.who, all = S.purchases, mine = all.filter(p => v3sees(p, w));
  if (!mine.length) return {html:`<div class="head"><h1 class="disp">Покупки</h1></div><p class="mut">Своих целей пока нет. Так выглядит цель, которая сходится.</p>
  <button class="pl press" data-act="v3showEx"><span class="mini" data-pic="sofa" data-pct="${V3_EX.saved / V3_EX.price}"><img class="fog" alt=""><img class="color" alt=""></span>
  <span><span class="v3-tag">Пример</span><br><b>${V3_EX.name}</b><br><span class="mut sm">к ${dStr(V3_EX.dl)} · сходится</span></span></button>`, main:['Создать свою цель','v3own']};
  S.purchases = mine; try { return v3list0(); } finally { S.purchases = all; } };

/* ── экран цели: своя / общая ── */
const v3whereRow = () => '<button class="rowl press v3-where" data-sheet="where"><span>Где лежат деньги — указать</span><span aria-hidden="true">›</span></button>';
function v3soloPost(html, p){ return v3dom(html, f => {
  const st = f.querySelector('.stamp'); if (st) { st.className = 'stamp v3-plain'; st.textContent = 'своя цель'; } else v3warn.push('solo:stamp');
  f.querySelectorAll('.wd.both').forEach(x => x.classList.remove('both'));
  f.querySelectorAll('.note').forEach(n => { if (n.querySelector('[data-act="cheer"]')) n.remove(); });   /* «Партнёр сделал шаг» — не про свою цель */
  if (p.photo === 'v3fog') { const sw = f.querySelector('.swap'); if (sw) sw.textContent = 'Добавить фото'; }
  const left = f.querySelector('[data-out="my-left"]'); if (left) left.setAttribute('data-v3-money', '');
  if (p.state !== 'done' && !(p.where || {})[p.owner]) { const pd = f.querySelector('[data-out="perday"]'), at = pd && pd.closest('p');
    const after = at && at.nextElementSibling && at.nextElementSibling.matches('p.xs') ? at.nextElementSibling : at;
    if (after) after.insertAdjacentHTML('afterend', v3whereRow()); else v3warn.push('solo:where'); }
  const sec = [...f.querySelectorAll('.sec')].find(s => /До полной суммы/.test((s.querySelector('h2') || {}).textContent || ''));
  if (!sec) return v3warn.push('solo:sec');
  sec.querySelector('h2').innerHTML = 'До полной суммы ' + vis('me');
  sec.querySelectorAll('.rowl').forEach(r => { const s = r.querySelector('span'), b = r.querySelector('b');
    if (s && /часть партнёра/.test(s.textContent)) { s.textContent = 'Ваша часть'; if (b) b.textContent = rubT(p.share[p.owner]); } });
  const sb = sec.querySelector('[data-go="share"]'); if (sb) sb.remove();
  if (p.state !== 'done') sec.insertAdjacentHTML('beforeend', '<button class="sec2 press" data-go="groupShare">Копить вместе с кем-то</button>');
}); }
function v3groupScr(p){ const w = S.who, g = p.group, ms = g.members, n = ms.length, many = n >= 3, done = p.state === 'done',
    left = leftOf(p, w), mine = perDay(p, w), plan = onPlan(p, w), gap = v3gap(p), over = Math.max(0, v3promised(p) - p.price), fits = v3fits(p),
    pc = done ? 1 : many ? g.snap : pctOf(p, w), pct = Math.round(pc * 100), more = n < V3_MAX && !done,
    tot = Math.max(1, Math.round((p.dl - p.cr) / DAY)), el = Math.min(tot, Math.max(0, Math.round((now() - p.cr) / DAY))), x = (el / tot * 100).toFixed(1),
    o2 = n === 2 ? ms.find(m => m !== w) : null, wk = o2 && !done ? weekRow(w) : null;   /* как в паре Р1 — только на двоих (ТЗ 1.4, ФТ-91/92) */
  const member = m => { const s = v3word(p, m, many), ok = s === 'по плану' || s === 'к сроку сходится';
    return `<div class="v3-member" data-v3-member="${m}"><span class="v3-ava" aria-hidden="true">${NAME[m][0]}</span>
    <span><b>${m === w ? 'Вы' : NAME[m]}</b><br><span class="mut sm">${m === w ? 'беру' : 'берёт'} <span class="num">${rubT(p.share[m] || 0)}</span></span></span>
    ${s ? `<span class="v3-st${ok ? '' : ' wait'}">${s}</span>${ok ? '' : vis('me')}` : ''}</div>`; };
  const gone = m => `<div class="v3-gonerow"><span class="v3-ava" aria-hidden="true">${NAME[m][0]}</span><span><b>${NAME[m]}</b><br><span class="sm">${V3_FEM.includes(m) ? 'вышла' : 'вышел'} из цели</span></span></div>`;
  const stamp = done ? '<span class="stamp">собрано</span>' : many ? `<span class="v3-stampw"><span class="stamp">вместе ${pct}${NB}%</span>${visG()}</span>`
    : `<span class="stamp${fits ? '' : ' wait'}">${fits ? 'к сроку сходится' : 'пока не сходится'}</span>`;
  const html = `<div class="head"><div>${S.purchases.length > 1 ? backBtn('list', 'Покупки') : ''}<h1 class="disp">${esc(p.name)}</h1><p class="mut" style="margin:2px 0 0">к ${dStr(p.dl)} · <span class="num" data-out="days">через ${daysW(daysTo(p))}</span> · ${n} ${plural(n, 'участник', 'участника', 'участников')}</p></div>
  <button class="icon press" data-sheet="change" aria-label="Изменить цель"><svg width="20" height="20" viewBox="0 0 20 20"><circle cx="4" cy="10" r="1.6" fill="currentColor"/><circle cx="10" cy="10" r="1.6" fill="currentColor"/><circle cx="16" cy="10" r="1.6" fill="currentColor"/></svg></button></div>
  ${o2 && S.flags.partnerStep && !done ? `<div class="note v3-step">${NAME[o2]} сегодня ${V3_FEM.includes(o2) ? 'сделала' : 'сделал'} шаг. ${me().stepped ? 'Сегодня точка у обоих.' : 'Отложите и вы — будет точка у обоих.'}<div class="kb"><button data-act="cheer">Подбодрить</button></div></div>` : ''}
  <div class="cardp"><div class="photo" data-pic="${p.photo}" data-pct="${pc}" data-conf="${many || done ? pc : confPct(p, w)}" role="img" aria-label="${many ? 'Фото цели: чёткая часть — отложено вместе, с шагом 10 %' : 'Фото цели: чёткая часть — ваше отложенное'}">
    <img class="fog" alt=""><img class="color" alt=""><div class="thin"></div><div class="edge"></div><div class="rule"></div><button class="swap press" data-sheet="photo">${p.photo === 'v3fog' ? 'Добавить фото' : 'Сменить фото'}</button></div>
    <div class="cap"><span class="hand">${esc(p.cap || p.name)}</span>${stamp}</div></div>
  <div class="v3-mine">${done ? '<p class="left disp">Собрано</p><div class="note">Деньги у каждого из вас — в своём банке. Мы деньги не храним.</div>'
    : `<p class="left disp"><small>Вам осталось отложить ${vis('me')}</small><span class="num" data-out="my-left" data-v3-money>${rub(left)}</span></p>
  <p class="mut" style="margin:0">${plan ? 'по плану' : 'догнать план'}: <span class="num" data-out="perday">${rub(mine)}</span> в день <button class="link sm" data-sheet="how" style="min-height:0">Как это работает?</button></p>
  ${(p.where || {})[w] ? '' : v3whereRow()}${wk ? wk.html : ''}`}</div>
  <div class="sec"><h2>Общая цель ${visG()}</h2>
  ${many ? `<p class="v3-big disp num">${done ? 'Собрано' : 'Вместе ≈ ' + pct + NB + '%'}</p><div class="v3-steps" aria-hidden="true">${Array.from({length:10}, (_, i) => `<i${i < Math.round(pc * 10) ? ' class="on"' : ''}></i>`).join('')}</div><p class="xs mut">Шаг 10 %, обновляется раз в сутки.</p>`
    : `<p class="v3-big disp">${done ? 'Собрано' : fits ? 'К сроку сходится' : 'Пока не сходится'}</p>${n === 2 ? '<p class="xs mut">Вдвоём процент раскрыл бы, сколько отложил партнёр. Поэтому — только «сходится».</p>' : ''}
    ${done ? '' : `<div class="v3-tl" role="img" aria-label="До срока прошло ${daysW(el)} из ${daysW(tot)}"><span class="v3-tnow xs mut" style="left:${x}%;transform:translateX(-${x}%)">сегодня</span><div class="v3-time"><i style="left:${x}%"></i></div></div><p class="xs mut v3-timelab"><span>${dStr(p.cr)}</span><span>${dStr(p.dl)}</span></p>`}`}
  <div class="v3-members">${ms.map(member).join('')}${(g.gone || []).map(gone).join('')}</div>
  ${n === 1 && g.sent ? '<p class="sm">Ссылка отправлена. Пока копите сами — план не меняется.</p>' : ''}
  ${over ? `<div class="rowl"><span>Части больше цены на <b class="num">${rubT(over)}</b></span><button class="chip press" data-input="share">Уменьшить свою часть</button></div>`
    : gap ? `<div class="rowl"><span>По договорённостям не хватает <b class="num">${rubT(gap)}</b></span></div>` : '<div class="rowl"><span>Договорённости покрывают цену</span></div>'}
  <p class="xs mut">Части — договорённость, их видят все. Отложенное каждого видит только он сам.</p>
  ${more ? `<button class="sec2 press" data-go="groupShare">${n > 1 || g.sent ? 'Позвать ещё' : 'Позвать людей'}</button>` : done ? '' : '<p class="xs mut">В цели 6 человек — это максимум.</p>'}</div>`;
  return {html:html.replace(/(\d) (участник)/, '$1' + NB + '$2'), main: done ? null : ['Я отложил(а)', 'saveSheet']}; }
/* приглашение глазами приглашённого: без аккаунта; что увидят все и что только вы — до договорённостей и поля (≤45 слов) */
function v3inviteScr(p){ const o = p.owner, ms = p.group.members, n = ms.length + 1, full = ms.length >= V3_MAX, many = n >= 3, need = v3gap(p);
  if (S.v3.via && S.v3.via !== v3link(p)) return {notabs:true, html:`<h1 class="h1 disp">Ссылка больше не работает</h1><p class="mut">${NAME[o]} ${V3_FEM.includes(o) ? 'сделала' : 'сделал'} новую. Попросите её — по ней можно присоединиться.</p>`};
  return {notabs:true, html:`<div class="v3-invite"><h1 class="h1 disp">${NAME[o]} зовёт копить вместе</h1>
  <div class="cardp"><div class="photo" data-pic="${p.photo}" data-pct="0"><img class="fog" alt=""><img class="color" alt=""><div class="edge"></div><div class="rule"></div></div><div class="cap"><span class="hand">${esc(p.cap || p.name)}</span><span class="stamp v3-plain">к ${dStr(p.dl)}</span></div></div>
  <div class="sec"><p>Все увидят ${visG()}: ${many ? 'части, общий прогресс шагом 10 % и «по плану»' : 'части и «сходится ли» к сроку'}.</p>
  <p>Только вам ${vis('me')}: отложенное, траты и доходы. Организатор их не видит.</p></div>
  <div class="sec"><h2>Договорённости</h2><div class="rowl"><span>${need ? `Свободно <b class="num">${rubT(need)}</b> из <span class="num">${rubT(p.price)}</span>` : `Цена <span class="num">${rubT(p.price)}</span> уже покрыта частями`}</span></div>
  <details><summary>Кто сколько берёт</summary><div class="v3-members">${ms.map(m => `<div class="v3-member" data-v3-member="${m}"><span class="v3-ava" aria-hidden="true">${NAME[m][0]}</span><span><b>${NAME[m]}</b><br><span class="mut sm">берёт <span class="num">${rubT(p.share[m] || 0)}</span></span></span></div>`).join('')}</div></details></div>
  ${full ? '<div class="note">В цели уже 6 человек — это максимум.</div>' : `<form id="v3acceptf"><input class="inp" id="v3accept" placeholder="беру ${fmt(need || 15000)}" aria-label="Сколько возьмёте на себя"><button class="main press" style="margin-top:8px">Присоединиться</button></form>
  <p class="xs mut" id="v3accnote" style="margin-top:6px">Без регистрации.</p>`}</div>`}; }
/* одна ссылка на всю цель (не своя на каждого); новая — старая перестаёт работать */
const v3link = p => p.v3link || (p.v3link = '4Rt9');
/* позвать: отправитель; в тексте ссылки нет ни моего «в день», ни отложенного */
function v3shareScr(){ const p = P(); if (!p) return scrList(); const n = p.group ? p.group.members.length : 1, free = V3_MAX - n, own = p.owner === S.who;
  const txt = `${esc(p.cap || p.name)} к ${dStr(p.dl)}, ${rubT(p.price)}. Каждый копит свою часть. Чужих денег никто не видит.`;
  return {notabs:true, html:`${backBtn('purchase')}<h1 class="h1 disp">Позвать в цель</h1><div class="note" id="v3sharetxt">${txt}<br><span class="mut" data-v3-link>fa.example/g/${v3link(p)}</span></div>
  <div class="sec"><p class="sm">Увидят цель, срок и части ${visG()}, но не ваши деньги ${vis('me')}</p></div>
  <p class="xs mut">Одна ссылка для всех, без регистрации. ${free <= 0 ? 'В цели уже 6 человек.' : n > 1 ? `Свободно мест: ${free} из 6.` : 'До 6 человек.'}</p>
  ${own && p.group && p.group.sent ? '<button class="sec2 press" data-act="v3newLink">Новая ссылка</button>' : ''}<button class="sec2 press" data-act="v3asGuest">Глазами приглашённого</button>`, main: free > 0 ? ['Отправить ссылку','v3send'] : null}; }
SCR.groupShare = v3shareScr;
const v3purchase0 = scrPurchase;
function v3purchase(){ const p = P(), w = S.who;
  /* QA №10, №11: чужая цель, куда не звали, и цель, из которой вышли, — не показываются */
  if (p && !v3sees(p, w)) { const q = S.purchases.find(x => v3sees(x, w)); if (q) { S.cur = q.id; return v3purchase(); } S.scr = 'list'; return scrList(); }
  if (p && p.group) return p.share[w] == null ? v3inviteScr(p) : v3groupScr(p);
  const r = v3purchase0(); if (!v3solo(p, w) || !r.html) return r;
  r.html = v3soloPost(r.html, p);
  /* только что созданная цель: следующий шаг — «Сегодня на себя», а не «Я отложил(а)» на пустой цели */
  if (p.state !== 'done' && !(p.saved[w] > 0) && !me().income) { r.main = ['Посмотреть, сколько можно на себя', 'v3today'];
    r.extra = '<button class="sec2 press" data-main="saveSheet">Я отложил(а)</button>'; r.html += '<div class="v3-pad" aria-hidden="true"></div>'; }
  return r; }
scrPurchase = SCR.purchase = v3purchase;

/* листы: подпись видимости по режиму цели */
for (const k of ['save','change','where','photo']) { const f = SH[k]; SH[k] = a => { let h = f(a); const m = v3mode();
  if (m === 'group') h = h.replace(/Партнёр увидит/g, 'Участники увидят').replace(/Партнёр этого не видит/g, 'Участники этого не видят').replace('в общей покупке', 'в общей цели');
  else if (m === 'solo') h = h.replace(/Партнёр (увидит|этого не видит)[^<.]*\./g, 'Это видно только вам.').replace(' Это видно только вам. Ниже', ' Ниже');
  return h; }; }
/* QA №4: участник выходит из цели; отменить её у всех может только организатор — с предупреждением */
const v3change1 = SH.change;
SH.change = a => { const h = v3change1(a), p = P();
  return p && p.group && p.owner !== S.who ? v3sub(h, '<button class="sec2 press" data-sheet="cancelAsk" style="color:var(--warm)">Отменить покупку</button>', '<button class="sec2 press" data-sheet="v3leaveAsk">Выйти из цели</button>', 'change:leave') : h; };
const v3cancelAsk0 = SH.cancelAsk;
SH.cancelAsk = a => { const m = v3mode(), p = P(), was = 'Покупка уйдёт в архив у вас и у партнёра. Отметки сохранятся.';
  if (m === 'group' && p.owner !== S.who) return SH.v3leaveAsk();
  return m === 'solo' ? v3sub(v3cancelAsk0(a), was, 'Покупка уйдёт в архив. Отметки сохранятся.', 'cancelAsk:solo')
    : m === 'group' ? v3sub(v3cancelAsk0(a), was, 'Покупка уйдёт в архив у всех участников. Все увидят, что вы её отменили.', 'cancelAsk:group') : v3cancelAsk0(a); };
SH.v3leaveAsk = () => `<h3 class="disp">Выйти из цели?</h3><p>Ваша часть освободится. Участники увидят «${V3_FEM.includes(S.who) ? 'вышла' : 'вышел'}», без ваших сумм.</p><p class="sm mut">Цель останется у них.</p>
  <button class="main press" data-act="v3leave">Выйти из цели</button><button class="sec2 press" data-close>Остаться</button>`;

/* ── действия ── */
Object.assign(ACT, {
  v3own(){ S.v3.back = null; S.v3.fromEx = true; S.draftText = ''; go('phrase'); },
  v3exStep(){ const before = mileOf(S.v3.ex / V3_EX.price); S.v3.ex = Math.min(V3_EX.price, S.v3.ex + V3_EX.step); S.flash = true; v3log('example_action'); render(true);
    const after = mileOf(S.v3.ex / V3_EX.price); toast((after && (!before || after[0] > before[0]) ? after[1] + '. ' : '') + 'Это пример — ничего не сохранилось.'); v3exToast = true; },
  v3showEx(){ if (S.scr !== 'example') S.v3.back = S.scr === 'list' || S.purchases.length ? S.scr : null; S.v3.ex = V3_EX.saved; v3log('example_shown'); go('example'); },
  v3clarPart(){ const i = $('#clar'); if (!i) return; i.placeholder = 'например, ' + fmt(Math.round((S.draft.price || 0) / 2000) * 1000); i.focus(); },
  v3save(){ commitDraft(); v3log('goal_saved'); go('together'); },
  v3alone(){ v3log('together_solo'); go('purchase'); },
  v3today(){ v3log('bridge_today'); go('today'); },
  v3call(){ v3log('together_invite'); go('groupShare'); },
  v3send(){ const p = P(), g = v3makeGroup(p), t = $('#v3sharetxt').innerText; g.sent = true; p.invited = true;
    if (navigator.share) navigator.share({text:t}).catch(() => {}); go('purchase'); toast('Ссылка отправлена'); },
  v3asGuest(){ const p = P(), g = v3makeGroup(p); g.sent = true; p.invited = true; const guest = ['anya','oleg'].find(x => !g.members.includes(x));
    if (!guest) return toast('В показе все уже в цели'); S.v3.via = v3link(p); S.who = guest; me().consent = true; me().exSeen = true; go('purchase'); },
  v3newLink(){ const p = P(), old = v3link(p); let t; do { t = Math.random().toString(36).slice(2, 6); } while (t === old || t.length < 4);
    p.v3link = t; v3log('link_renewed'); render(true); toast('Новая ссылка готова. Старая больше не работает.'); },
  v3leave(){ const p = P(), w = S.who; if (!p || !p.group || p.share[w] == null) return closeSheet();
    v3leave(p, w); v3log('group_left'); go('list'); toast('Вы вышли из цели. Ваши суммы никто не видел.'); }   /* S.cur не трогаем: у вышедшего цель скрывает v3sees */
});
const v3cancel0 = ACT.cancelBuy;
ACT.cancelBuy = function(){ const p = P(); if (p && p.group && p.owner !== S.who && p.share[S.who] != null) return ACT.v3leave();
  v3cancel0(); if (!S.purchases.length) go('list'); };
/* QA №11: удалил все данные — из общих целей человек выходит, цель остаётся у остальных с отметкой «вышел(ла)» */
const v3delAll0 = ACT.delAll;
ACT.delAll = function(){ const w = S.who, keep = S.purchases.filter(p => p.group && p.group.members.includes(w) && p.group.members.some(m => m !== w));
  keep.forEach(p => v3leave(p, w)); S.purchases = S.purchases.filter(p => !keep.includes(p)); v3delAll0(); S.purchases = S.purchases.concat(keep);
  if (!S.purchases.some(p => p.id === S.cur)) S.cur = S.purchases[0] ? S.purchases[0].id : null; };
/* вход в пару v2 — тоже с даты входа (QA №7 для всех общих целей) */
document.addEventListener('submit', e => { if (e.target.id !== 'acceptf') return; const p = P(); if (p) (p.join = p.join || {})[S.who] = now(); }, true);
document.addEventListener('submit', e => { const f = e.target; if (f.id !== 'v3acceptf') return; const p = P(), w = S.who; if (!p || !p.group) return;
  if (S.v3.via && S.v3.via !== v3link(p)) return go('purchase');
  let v = numIn($('#v3accept').value); if (!v) return; if (v < 1000) v *= 1000; const need = v3gap(p);
  if (v > need && need > 0) { $('#v3accnote').textContent = 'Вместе выйдет больше цены. Хватит ' + rubT(need) + ' — взять столько?'; $('#v3accept').value = fmt(need); return; }
  /* QA №6: цену уже покрыли — переплата только после явного согласия */
  if (v > need && +f.dataset.over !== v) { f.dataset.over = v; $('#v3accnote').textContent = 'Цену уже покрыли. С вашей частью выйдет на ' + rubT(v - need) + ' больше — присоединиться так?'; return; }
  if (p.group.members.length >= V3_MAX) return;
  p.share[w] = v; p.saved[w] = 0; (p.conf = p.conf || {})[w] = 0; (p.join = p.join || {})[w] = now();
  const g = p.group; g.members.push(w); g.gone = (g.gone || []).filter(m => m !== w); (g.stat = g.stat || {})[w] = {plan:true, started:false};
  v3log('group_joined'); go('purchase'); });

/* день сменился — новый снимок: общий прогресс и статусы (раз в сутки, без «+N % сегодня») */
const v3setDay0 = setDay;
setDay = function(off){ v3setDay0(off); let ch = false; for (const p of S.purchases) if (p.group) { v3snap(p); ch = true; } if (ch) render(true); };

/* «fresh» — как в v2: сторис поверх согласия. Сценарии v2 про пару — только на цели пары: на своей или общей цели они подменились бы словами о партнёре (QA №13) */
const v3scenario0 = scenario;
scenario = function(k){ const pc = P();
  if (k === 'partner' && pc && pc.group && pc.group.members.length === 2 && pc.share[S.who] != null) { $('#panel').classList.remove('open'); S.flags.partnerStep = true; return go('purchase'); }
  const p0 = S.purchases[0]; if (k !== 'mid' && k !== 'fresh' && p0 && (p0.v3 || p0.group || v3solo(p0, p0.owner))) { S = seed('mid'); snap(); }
  return v3scenario0(k); };
demo.scenario = scenario;
demo.v3 = {log: () => S.v3.log.slice(), warn: () => v3warn.slice()};

/* ── коды состояний ── */
function v3reset(keepWho){ const who = S && S.who; S = seed('fresh'); snap();
  Object.assign(S.people.oleg, {consent:true, exSeen:true, income:{m:80000, mand:30000, pay:[10,25], src:'manual'}});
  Object.assign(S.people.anya, {consent:true, exSeen:true, income:{m:72000, mand:29500, pay:[10,25], src:'manual'}});
  if (keepWho && who) S.who = who; }
function v3goal(o){ const p = Object.assign({link:null, owner:'oleg', conf:{}, where:{}, invited:false, state:'active', v3:true}, o); p.cap = p.cap || p.name; S.purchases.push(p); S.cur = p.id; return p; }
function v3groupSeed(members, keepWho){ v3reset(keepWho);
  const sh = {oleg:40000, anya:30000, timur:30000, sveta:20000}, sv = {oleg:14000, anya:11500, timur:9000, sveta:3000}, two = members.length === 2;
  const p = v3goal(two ? {id:'g2', name:'Ремонт кухни', photo:'flat-light', price:150000, cr:Date.UTC(2026, 7, 1), dl:Date.UTC(2027, 2, 1), share:{oleg:80000, anya:70000}, saved:{oleg:24000, anya:21000}, conf:{oleg:20000, anya:21000}}
    : {id:'g3', name:'Дом у моря на неделю', cap:'Дом у моря', photo:'sea', price:120000, cr:Date.UTC(2026, 7, 1), dl:Date.UTC(2027, 2, 1), share:{}, saved:{}, conf:{}});
  if (!two) for (const m of members) { p.share[m] = sh[m]; p.saved[m] = sv[m]; p.conf[m] = Math.round(sv[m] * .8); }
  p.where = {oleg:'Копилка в банке', anya:'Вклад'}; p.invited = true; p.group = {members:members.slice(), sent:true, snap:0, gone:[]}; v3snap(p);
  if (!members.includes(S.who)) S.who = 'oleg'; return p; }
Object.assign(V3_SCEN, {
  example(){ S = seed('fresh'); snap(); me().consent = true; v3log('example_shown'); go('example'); },
  solo(){ v3reset(); v3goal({id:'p1', name:'Отпуск на море', cap:'Море', photo:'sea', price:120000, cr:Date.UTC(2026, 8, 1), dl:Date.UTC(2027, 5, 1),
    share:{oleg:120000, anya:null}, saved:{oleg:14000, anya:0}, conf:{oleg:9000, anya:0}, where:{oleg:'Копилка в банке'}}); go('purchase'); },
  together(){ v3reset(); const d = parsePhrase('Ноутбук 90 тысяч к 1 марта'); if (d.share == null) d.share = d.price; S.draft = d; commitDraft(); S.purchases[0].v3 = true; go('together'); },
  group2(){ v3groupSeed(['oleg','anya'], true); go('purchase'); },
  group3(){ v3groupSeed(['oleg','anya','timur','sveta'], true); go('purchase'); },
  groupInvite(){ const p = v3groupSeed(['oleg','timur','sveta']); S.who = 'anya'; p.share.anya = null; delete p.where.anya; S.v3.via = v3link(p); go('purchase'); },
  group2step(){ V3_SCEN.group2(); S.flags.partnerStep = true; render(true); },
  groupShare(){ V3_SCEN.solo(); go('groupShare'); },
  empty(){ v3reset(); go('list'); }
});
"""
