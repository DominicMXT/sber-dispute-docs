<script>
(() => { const out = [], errs = [], ok = (n, c, x) => out.push((c ? 'PASS ' : 'FAIL ') + n + (x !== undefined && !c ? ' :: ' + x : '')), info = s => out.push('INFO ' + s);
const ce = console.error, cw = console.warn; console.error = (...a) => { errs.push('error: ' + a.join(' ')); ce.apply(console, a); }; console.warn = (...a) => { errs.push('warn: ' + a.join(' ')); cw.apply(console, a); };
addEventListener('error', e => errs.push('onerror: ' + e.message));
const W = s => (s.match(/[A-Za-zА-Яа-яЁё0-9]+/g) || []).length;
const longSent = s => s.split(/[.!?\n]+/).map(x => x.trim()).filter(x => W(x) > 15);
const vt = () => $('#view').innerText.replace('Что не так?', ''), st = () => $('#sheet').innerText, bt = () => $('#bottom').innerText.trim();
/* первый экран — текст #view, который виден без прокрутки (выше нижней панели) */
const MINE = '.v3-buf,.v3-dayprice,.v3-weeks,.v3-shelfsec,.v3-remind';
const fold = (mineOnly) => { const v = $('#view'), top0 = v.scrollTop; v.scrollTop = 0; const r = v.getBoundingClientRect(), b = $('#bottom .bottom'), lim = b ? b.getBoundingClientRect().top : r.bottom, tw = document.createTreeWalker(v, NodeFilter.SHOW_TEXT); let s = '', n;
  while ((n = tw.nextNode())) { if (!n.textContent.trim() || n.parentElement.closest('[data-sheet="feedback"]') || (n.parentElement.closest('details:not([open])') && !n.parentElement.closest('summary')) || (mineOnly && !n.parentElement.closest(MINE))) continue; const rg = document.createRange(); rg.selectNodeContents(n); const q = rg.getBoundingClientRect();
    if (q.height && q.bottom > r.top && q.top < lim) s += ' ' + n.textContent; } v.scrollTop = top0; return s; };
const redIn = sel => $$(sel + ' *').concat($$(sel)).filter(x => ['color','backgroundColor','borderTopColor'].some(k => { const m = (getComputedStyle(x)[k].match(/[\d.]+/g) || []).map(Number);
  return m.length >= 3 && (m.length < 4 || m[3] > 0) && m[0] > 150 && m[1] < 90 && m[2] < 90; })).map(x => x.tagName + '.' + x.className);
const noRed = name => { for (const th of ['light', 'dark']) { const t0 = document.documentElement.dataset.theme; document.documentElement.dataset.theme = th;
  const r = redIn('#view').concat(redIn('#sheet'), redIn('#pushwrap')); document.documentElement.dataset.theme = t0; ok(name + ': без красного (' + th + ')', !r.length, r.slice(0, 3).join()); } };
const budgetScreen = (name, whole) => { const t = whole ? vt() : fold(), mine = W(fold(true)), base = W(fold()) - mine;
  ok(name + ': первый экран ≤45 слов' + (whole ? ' (весь экран — экран модуля)' : '') + ' [' + innerWidth + '×' + innerHeight + ']', W(t) <= 45, W(t) + (whole ? '' : ' — база экрана ' + base + ', добавка модуля ' + mine)); ok(name + ': предложения ≤15 слов', !longSent(vt()).length, longSent(vt()).join(' / ')); info(name + ': первый экран ' + W(fold()) + ' слов (из них модуль ' + W(fold(true)) + '), весь экран ' + W(vt()) + ' слов'); };
const budgetSheet = name => { ok(name + ': лист ≤30 слов', W(st()) <= 30, W(st()) + ' :: ' + st().replace(/\n/g, ' | ')); ok(name + ': предложения листа ≤15', !longSent(st()).length, longSent(st()).join(' / ')); };
const noReproach = (name, s) => ok(name + ': без «всё сначала» и упрёков', !/сначала|сгорел[аио]?\b(?!о)|отстаёте|вы отстаёте|срочно|провал|увы/i.test(s.replace('не сгорело', '').replace('Ничего не сгорело', '')), s.slice(0, 160));
const lock = (name, root) => ok(name + ': значок «видно только вам» с aria-label', !!$(root + ' [aria-label="видно только вам"]'));
const EXP = {dayprice:() => S.scr === 'today' && !!$('#view .v3-dayprice'), slip:() => S.scr === 'slip', weeks:() => S.scr === 'purchase' && !!$('#view .v3-weeks'), slipPropose:() => S.scr === 'purchase' && S.who === 'anya' && !!$('#view .v3-prop [data-act="v3propYes"]') && !!$('#view .v3-prop [data-act="v3propNo"]'),
  weeksum3:() => S.sheet === 'weeksum' && !!$('#sheet .v3-wsum'), nextgoal:() => S.scr === 'purchase' && P().state === 'done' && !!$('#view .v3-shelf')};
const ANIM = typeof V3_ANIM_VIEW_FADE !== 'undefined';
const finish = () => { ok('ошибок консоли нет', !errs.length, errs.slice(0, 3).join(' || ')); ok('demo.v3.warn() пуст', demo.v3.warn().length === 0, demo.v3.warn().join());
  const pre = document.createElement('pre'); pre.id = 'T'; pre.textContent = out.join('\n'); document.body.append(pre); };
const hash = decodeURIComponent(location.hash.slice(1));
try {
  if (hash) {   /* открытие кода по ссылке #код */
    ok('#' + hash + ' открывается', EXP[hash] && EXP[hash](), S.scr + '/' + S.sheet);
    ok('#' + hash + ': экран не пустой', W(vt()) > 5); noRed('#' + hash);
    if (hash === 'weeksum3') budgetSheet('#weeksum3'); else budgetScreen('#' + hash, hash === 'slip');
    return finish();
  }
  /* ── M-C dayprice ── */
  V3_SCEN.dayprice(); const dp = $('#view .v3-dayprice').innerText, p1 = P() || active('oleg')[0];
  ok('dayprice: экран «Сегодня», ответ «влезет ли»', S.scr === 'today' && /Влезет/.test($('[data-out="afford"]').innerText), $('[data-out="afford"]').innerText);
  const n1 = Math.round(7000 / perDay(p1, 'oleg'));
  ok('dayprice: цена траты в днях цели = 7000 / план в день', new RegExp('(^|\\s)' + n1 + '\\s(день|дня|дней)').test(dp) && /«Отпуск на море»/.test(dp), dp + ' :: ждали ' + n1);
  const kb = $$('#view .kb button'); ok('dayprice: решение за человеком — две равные кнопки «Купил»/«Не буду»', kb.length === 2 && kb[0].className === kb[1].className, kb.map(b => b.textContent).join());
  ok('dayprice: фраза ≤15 слов в предложении', !longSent(dp).length, dp); noReproach('dayprice', dp); budgetScreen('dayprice'); noRed('dayprice'); lock('dayprice', '#view');
  /* ── M-B запас прочности ── */
  const i = me().income, buf = v3buf('oleg');
  ok('M-B: запас 5 % дохода вычтен из «на себя»', buf === 4000 && selfDay('oleg') === Math.floor((i.m - i.mand - reserve('oleg') * 30 - buf) / 30), buf + ' / ' + selfDay('oleg'));
  ok('M-B: одна строка о запасе под числом, сумма — в «Как я посчитал»', $$('#view .v3-buf').length === 1 && /Запас/.test($('#view .v3-buf').innerText) && /Запас на непредвиденное[\s\S]*4\s000/.test(($('#view details') || {}).textContent || '') && !longSent($('#view .v3-buf').innerText).length);
  ok('M-B: строка запаса в «Как я посчитал»', /Запас на непредвиденное/.test($('#view details').textContent));
  ok('M-B: главное число «Сегодня» с data-v3-money', !!$('#view [data-out="left-today"][data-v3-money]'));
  me().bot = 'max'; botSay('влезет ли ужин за 3000?'); const last = me().chat[me().chat.length - 1].b;
  ok('dayprice в боте', /откладываете столько за \d+/.test(last), last);
  /* ── M-E slip ── */
  /* W5B */ V3_SCEN.slip(); const ps = P(), dl0 = ps.dl, c0 = v3slipCalc(ps, 'oleg', 40000);
  ok('slip: экран после крупной траты, отложенное уменьшилось, но не обнулилось', S.scr === 'slip' && ps.saved.oleg === 10000);
  ok('slip: сценарий — доплата ≥ V3_SLIP_MIN (150), значит две дороги', V3_SLIP_MIN === 150 && c0.plus >= V3_SLIP_MIN && !c0.small, c0.plus);
  const pb = $$('#view .v3-pair button');
  ok('slip: две равные кнопки', pb.length === 2 && pb[0].className === pb[1].className && pb[0].offsetWidth === pb[1].offsetWidth && !$('#bottom .main'), pb.map(b => b.className + ':' + b.offsetWidth).join(' '));
  ok('slip: «сдвинем на N дней» и «+M ₽ в день»', new RegExp('Сдвинуть срок на ' + c0.shift + '\\s').test(pb[0].innerText) && /^Откладывать \+/.test(pb[1].innerText) && c0.plus > 0, pb.map(b => b.innerText.replace(/\n/g, ' ')).join(' | '));
  noReproach('slip', vt()); budgetScreen('slip', true); noRed('slip'); lock('slip', '#view');
  pb[0].click(); ok('slip: журнал slip_shown → slip_date', S.v3.log.join().endsWith('slip_shown,slip_date'), S.v3.log.join()); ok('slip: «Сдвинуть срок» — срок +N дней, план в день прежний', S.scr === 'purchase' && Math.round((ps.dl - dl0) / DAY) === c0.shift && perDay(ps, 'oleg') <= c0.base + 1, Math.round((ps.dl - dl0) / DAY) + ' / ' + perDay(ps, 'oleg') + ' vs ' + c0.base);
  V3_SCEN.solo(); const pt = P(); pt.saved.oleg = 50000; openSheet('input', 'took'); $('#inputv').value = '40 000'; $('#inputf').requestSubmit();
  ok('slip: путь «Изменить цель → Пришлось взять из отложенного» ведёт на slip', S.scr === 'slip' && pt.saved.oleg === 10000 && !S.sheet, S.scr + ' ' + pt.saved.oleg);
  const dl1 = pt.dl; $('#view [data-act="v3slipDay"]').click(); ok('slip: «+M ₽ в день» — срок прежний', S.scr === 'purchase' && pt.dl === dl1);
  ok('slip: журнал событий', ['slip_shown', 'slip_day'].every(e => S.v3.log.includes(e)), S.v3.log.join());
  /* ── M-F weeks ── */
  V3_SCEN.weeks(); const pw = P(), cells = () => $$('#view .v3-day'), onIx = () => cells().map((x, i) => x.classList.contains('on') ? i : -1).filter(i => i >= 0);
  const k0 = v3weeks(pw, 'oleg');
  ok('weeks: история 1,1,0,1 + текущая → 3 по плану, пропуск не обнуляет', k0.ci === 4 && k0.cells.map(Number).join() === '1,1,0,1,0' && k0.n === 3, k0.cells.join() + ' / ci ' + k0.ci);
  ok('weeks: на экране с v2-плёнкой — строка «3 недели по плану», третьей полоски нет', !!$('#view .film') && /3 недели по плану/.test($('#view .v3-weeks').innerText) && cells().length === 0, cells().length + ' :: ' + $('#view .v3-weeks').innerText);
  budgetScreen('weeks'); noRed('weeks'); lock('weeks', '#view .v3-weeks');
  ok('weeks: текст недель — предложения ≤15', !longSent($('#view .v3-weeks').innerText).length);
  ACT.saveSheet(); $('#saveamt').value = '500'; $('#savef').requestSubmit();
  ok('weeks: после «отложил» текущая неделя засчитана, прошлые не изменились', v3weeks(pw, 'oleg').cells.map(Number).join() === '1,1,0,1,1' && /4 недели по плану/.test($('#view .v3-weeks').innerText), v3weeks(pw, 'oleg').cells.join());
  ok('M-J: похвала за факт — тост «Неделя засчитана»', /Неделя засчитана — уже 4 недели/.test($('#toast').textContent), $('#toast').textContent);
  setDay(1); setDay(0); ok('weeks: смена дня не сжигает счёт', /4 недели по плану/.test($('#view .v3-weeks').innerText) || /3 недели по плану/.test($('#view .v3-weeks').innerText));
  /* ── M-G weeksum3 ── */
  V3_SCEN.weeksum3(); const g = P(), sh = st();
  ok('weeksum3: «ваш результат» и «по плану N из M участников»', /Ваш результат/.test(sh) && /По плану 3 из 4 участников/.test(sh), sh.replace(/\n/g, ' | '));
  ok('weeksum3: без имён в сводке', !/Аня|Тимур|Света|Олег/.test(sh), sh);
  ok('weeksum3: без сумм в сводке', !/₽|\d\s\d{3}/.test(sh), sh);
  ok('weeksum3: напоминает продукт', /Напоминаем мы/.test(sh));
  ok('weeksum3: значки «видно только вам» и «видят участники»', !!$('#sheet [aria-label="видно только вам"]') && !!$('#sheet [aria-label="видят участники"]'));
  budgetSheet('weeksum3'); noRed('weeksum3');
  closeSheet(); const gv = vt();
  ok('M-I: в группе напоминает продукт', /Напоминаем участникам мы/.test(gv));
  ok('группа: чужих отложенных сумм нет на экране', !/11\s500|9\s000|3\s000/.test(gv), (gv.match(/.*(11\s500|9\s000|3\s000).*/) || [''])[0]);
  ok('группа: недели — свои, со значком замка', !!$('#view .v3-weeks [aria-label="видно только вам"]'));
  V3_SCEN.group2(); openSheet('weeksum'); ok('weeksum на двоих: только «сходится / нет», без «N из 2»', /(К сроку сходится|Пока не сходится)/.test(st()) && !/из 2/.test(st()) && !/Аня/.test(st()), st().replace(/\n/g, ' | '));
  /* ── M-J прямота по кнопке ── */
  V3_SCEN.solo(); openSheet('weeksum'); ok('weeksum одного: недели по плану, «Показать как есть»', /Недель по плану/.test(st()) && /Пропуск не обнуляет/.test(st()) && !!$('#sheet [data-sheet="v3direct"]') && $('#sheet [data-sheet="v3direct"]').textContent === 'Показать как есть' && !/Сказать прямо/.test(st()), st().replace(/\n/g, ' | '));
  budgetSheet('weeksum одного'); ok('weeksum одного: без прямоты до кнопки', !/Как есть,/.test(st()));
  $('#sheet [data-sheet="v3direct"]').click(); ok('v3direct открывается по кнопке', S.sheet === 'v3direct' && /Как есть, раз вы спросили/.test(st())); budgetSheet('v3direct'); noReproach('v3direct', st());
  const pd = P(); pd.saved.oleg = 2000; openSheet('v3direct'); ok('v3direct при отставании: сумма и «Перестроить план»', /До плана не хватает/.test(st()) && !!$('#sheet [data-act="v3slipBehind"]'), st());
  budgetSheet('v3direct (отстаёт)'); $('#sheet [data-act="v3slipBehind"]').click(); ok('«Перестроить план» → slip «Как догнать план?»', S.scr === 'slip' && /Как догнать план/.test(vt())); budgetScreen('slip (догнать)', true);
  /* ── M-K nextgoal ── */
  V3_SCEN.nextgoal(); const nv = vt();
  ok('nextgoal: «Собрано» и полка из 2 целей', /Собрано/.test(nv) && $$('#view .v3-shelf figure').length === 2 && /Вы собрали 2 цели/.test(nv), nv.slice(0, 200));
  ok('nextgoal: кнопка называет действие', bt() === 'Создать следующую цель', bt());
  budgetScreen('nextgoal'); noRed('nextgoal'); lock('nextgoal', '#view .v3-shelfsec');
  $('#bottom .main').click(); ok('nextgoal → Э-02 создания цели', S.scr === 'phrase' && S.v3.log.includes('next_goal_started'));
  /* ── M-D день зарплаты ── */
  scenario('payday'); const bk = $('#pushwrap [data-act="v3bank"]');
  ok('M-D: в уведомлении зарплаты — копилка своего банка', !!bk && /Открыть копилку в своём банке/.test(bk.textContent), bk && bk.textContent);
  bk.click(); ok('M-D: ссылка не держит деньги — тост', /Деньги остаются у вас/.test($('#toast').textContent) && S.v3.log.includes('bank_open'));
  noRed('payday');
  V3_SCEN.solo(); S.flags.push = true; render(); ok('M-D: уведомление одного без «Партнёр»', !/Партнёр/.test($('#pushwrap').innerText) && /Это видно только вам/.test($('#pushwrap').innerText), $('#pushwrap').innerText);
  P().where = {}; render(); ok('M-D: места нет — «Завести копилку»', /Завести копилку/.test($('#pushwrap').innerText));
  $('#pushwrap [data-act="v3bank"]').click(); ok('«Завести копилку» открывает лист «где»', S.sheet === 'where');
  /* ── M-L лист «где лежат деньги» ── */
  ok('M-L: отдельная копилка под эту цель', /Отдельная копилка под эту цель/.test(st()) && /Копилка в банке/.test(st())); budgetSheet('where');
  closeSheet(); scenario('mid'); me().bot = 'max'; S.off = 0; S.flags.push = true; go('bot');
  ok('M-D: в боте в день зарплаты — «Открыть копилку»', !!$('#view .bub [data-act="v3bank"]'), $$('#view .bub').length);
  /* ── волна 5 · п.5: сетка недель на общей цели — прошедшие и текущая, ≤13, будущее строкой ── */
  const cssVar = (prop, v) => { const k = document.createElement('i'); k.style[prop] = v; document.body.append(k); const c = getComputedStyle(k)[prop]; k.remove(); return c; };
  const lum = c => { const v = (c.match(/[\d.]+/g) || []).map(Number); return .2126 * v[0] + .7152 * v[1] + .0722 * v[2]; };
  V3_SCEN.group3(); { const p = P(), k = v3weeks(p, 'oleg'), cs = cells(), fut = k.total - k.ci - 1;
    ok('сетка: на общей цели (без v2-плёнки) — клетки прошедших недель и текущей', !$('#view .film') && cs.length === k.ci + 1 && cs.length <= 13, cs.length + ' / ci ' + k.ci);
    ok('сетка: будущих клеток нет, будущее — строкой «Впереди ещё N недель»', !$('#view .v3-fut') && new RegExp('Впереди ещё ' + fut + '\\s').test($('#view .v3-weeks').innerText), $('#view .v3-weeks').innerText);
    ok('сетка: текущая неделя — последняя клетка, .v3-now', cs.length > 0 && cs[cs.length - 1].classList.contains('v3-now'));
    ok('сетка: личные блоки подряд — недели до «Общей цели»', (() => { const a = $('#view .v3-weeks'), b = $$('#view .sec').find(s => /^Общая цель/.test(s.querySelector('h2') ? s.querySelector('h2').textContent.trim() : '')); return !!(a && b && (a.compareDocumentPosition(b) & 4)); })());
    const miss = cs.find(x => !x.classList.contains('on')), fill = cs.find(x => x.classList.contains('on')), t0 = document.documentElement.getAttribute('data-theme');
    info('сетка: закрашено ' + cs.filter(x => x.classList.contains('on')).length + ' из ' + cs.length + (miss ? '' : ' — пропусков нет, вид пропуска проверен на длинной цели'));
    const missLook = (m, f, tag) => { for (const th of ['light', 'dark']) { document.documentElement.setAttribute('data-theme', th);
      const ms = getComputedStyle(m), bg = lum(cssVar('backgroundColor', 'var(--bg)'));
      ok('сетка: пропуск — сплошная заливка, не пустой контур (' + th + tag + ')', !/rgba\(0, 0, 0, 0\)/.test(ms.backgroundColor) && ms.boxShadow === 'none', ms.backgroundColor + ' / ' + ms.boxShadow);
      ok('сетка: пропуск мягче закрашенной (' + th + tag + ')', Math.abs(lum(ms.backgroundColor) - bg) < Math.abs(lum(getComputedStyle(f).backgroundColor) - bg), ms.backgroundColor + ' vs ' + getComputedStyle(f).backgroundColor); }
      if (t0 == null) document.documentElement.removeAttribute('data-theme'); else document.documentElement.setAttribute('data-theme', t0); };
    if (miss && fill) missLook(miss, fill, '');
    Object.assign(S.people.oleg, {week:[0, 0, 0], stepped:false}); render(); const last = () => { const c = cells(); return c.length > 0 && c[c.length - 1].classList.contains('on'); }, b0 = v3weeks(p, 'oleg').n;
    ok('сетка: без отметок на этой неделе текущая клетка не закрашена', !last(), cells().map(x => +x.classList.contains('on')).join());
    ACT.saveSheet(); $('#saveamt').value = '500'; $('#savef').requestSubmit();
    ok('сетка: после «отложил» на общей цели текущая клетка закрашена, счёт +1', last() && v3weeks(p, 'oleg').n === b0 + 1, cells().map(x => +x.classList.contains('on')).join() + ' / ' + b0 + ' → ' + v3weeks(p, 'oleg').n);
    if (ANIM) ok('anim: ячейка недели заполняется (.v3-fill)', !!$('#view .v3-day.on.v3-fill')); else info('anim не подключён — проверка заливки пропущена');
    p.cr = Date.UTC(2025, 9, 1); p.v3wk = {oleg:Array.from({length:60}, (_, i) => i % 3 !== 2)}; render(); const k2 = v3weeks(p, 'oleg');
    ok('сетка: длинная цель (' + (k2.ci + 1) + ' недель позади) — ровно 13 клеток', k2.ci + 1 > 13 && cells().length === 13 && /Впереди ещё/.test($('#view .v3-weeks').innerText), cells().length);
    ok('сетка: aria-label считает все недели, не только видимые', new RegExp('из ' + (k2.ci + 1) + '$').test($('#view .v3-wk').getAttribute('aria-label')), $('#view .v3-wk').getAttribute('aria-label'));
    const c2 = cells(), m2 = c2.find(x => !x.classList.contains('on')), f2 = c2.find(x => x.classList.contains('on'));
    ok('сетка: на длинной цели есть пропуски для проверки вида', !!(m2 && f2)); if (m2 && f2) missLook(m2, f2, ', длинная цель'); }
  /* ── волна 5 · п.4: новая цель — без ложного счёта недель (QA №14) ── */
  V3_SCEN.together(); go('purchase'); { const p = P();
    ok('новая цель: создана сегодня, отметок нет', Math.round((now() - p.cr) / DAY) === 0 && !(p.saved.oleg > 0));
    ok('новая цель: блока «Недели по плану» нет до первой отметки', !$('#view .v3-weeks') && !/недел[яиь]\s+по плану/i.test(vt()), vt().slice(0, 300));
    openSheet('weeksum'); ok('новая цель: в итогах недели нет «Недель по плану»', !/Недель по плану/.test(st()), st().replace(/\n/g, ' | ')); closeSheet();
    ok('новая цель: 0 недель, отметки до дня создания цели не считаются', v3weeks(p, 'oleg').n === 0 && v3wkMarks(p, 'oleg') === 0, v3weeks(p, 'oleg').n + ' / ' + v3wkMarks(p, 'oleg'));
    ACT.saveSheet(); $('#saveamt').value = '500'; $('#savef').requestSubmit();
    ok('новая цель: после первой отметки — «1 неделя по плану»', /1 неделя по плану/.test(($('#view .v3-weeks') || {}).innerText || ''), ($('#view .v3-weeks') || {}).innerText); }
  /* ── волна 5 · п.1: крайние случаи сдвига (QA №3) ── */
  const slipCase = (name, setup, took) => { V3_SCEN.solo(); const p = P(); setup(p); render(); const dl0 = p.dl, span = Math.round((p.dl - p.cr) / DAY);
    openSheet('input', 'took'); $('#inputv').value = String(took); $('#inputf').requestSubmit(); const c = v3slipCalc(p, 'oleg', took), v = vt();
    ok(name + ': экран slip', S.scr === 'slip', S.scr);
    ok(name + ': без «+0 ₽», NaN, Infinity', !/\+0\s₽|NaN|Infinity|undefined/.test(v), v.replace(/\n/g, ' | '));
    ok(name + ': сдвиг ≤ исходного срока цели и ≤ 365 дней', c.shift >= 1 && c.shift <= Math.min(365, Math.max(1, span)), c.shift + ' / срок цели ' + span);
    ok(name + ': предложения ≤15 слов, экран ≤45', !longSent(v).length && W(v) <= 45, W(v) + ' :: ' + longSent(v).join(' / '));
    const pb = $$('#view .v3-pair button');
    if (c.keep) ok(name + ': догонять нечего — одна кнопка «Продолжить по плану»', !pb.length && bt() === 'Продолжить по плану', pb.length + ' / ' + bt());
    else if (c.plus < V3_SLIP_MIN) { const ln = $('#view .v3-sliplink'), mb = $('#bottom .main'), y = new Date(c.dl).getUTCFullYear(), y0 = new Date(dl0).getUTCFullYear();
      ok(name + ': доплата ' + c.plus + ' < ' + V3_SLIP_MIN + ' — одна главная кнопка «Догнать: +N ₽ в день», равных кнопок нет', !pb.length && bt() === 'Догнать: +' + rubT(c.plus) + ' в день', pb.length + ' / ' + bt());
      ok(name + ': сдвиг — вторичная ссылка «или сдвинуть срок», мельче главной кнопки', !!ln && ln.textContent === 'или сдвинуть срок' && ln.classList.contains('link') && !ln.classList.contains('sec2') && !!mb
        && parseFloat(getComputedStyle(ln).fontSize) < parseFloat(getComputedStyle(mb).fontSize) && ln.getBoundingClientRect().height >= 24, ln && ln.className + ' ' + getComputedStyle(ln).fontSize);
      ln.click(); ok(name + ': ссылка сдвигает срок — срок и темп как в расчёте', Math.round((p.dl - dl0) / DAY) === c.shift && perDay(p, 'oleg') === c.base, Math.round((p.dl - dl0) / DAY) + ' / ' + perDay(p, 'oleg') + ' vs ' + c.base);
      ok(name + ': тост с годом, если год сменился', (y !== y0) === new RegExp('\\s' + y + '\\D').test($('#toast').textContent), $('#toast').textContent); }
    else { ok(name + ': доплата ≥ ' + V3_SLIP_MIN + ' — две равные дороги', c.plus >= V3_SLIP_MIN && pb.length === 2 && pb[0].className === pb[1].className && !$('#bottom .main') && !$('#view .v3-sliplink'), c.plus + ' / ' + pb.length);
      const y = new Date(c.dl).getUTCFullYear(), y0 = new Date(dl0).getUTCFullYear();
      ok(name + ': год в дате — только если срок уходит в следующий год', (y !== y0) === new RegExp('\\s' + y + '(\\D|$)').test(pb[0].innerText), y + ' / ' + y0 + ' :: ' + pb[0].innerText.replace(/\n/g, ' '));
      ok(name + ': решающие числа в подстроке — 14 px, цвет --ink', (() => { const sm = $('#view .v3-pair small'), n = sm && sm.querySelector('.num');
        return !!sm && getComputedStyle(sm).fontSize === '14px' && !!n && getComputedStyle(n).color === cssVar('color', 'var(--ink)'); })());
      pb[0].click(); ok(name + ': «Сдвинуть» — срок и темп ровно как в подписи', Math.round((p.dl - dl0) / DAY) === c.shift && perDay(p, 'oleg') === c.base, Math.round((p.dl - dl0) / DAY) + ' / ' + perDay(p, 'oleg') + ' vs ' + c.base);
      ok(name + ': тост с годом, если год сменился', (y !== y0) === new RegExp('\\s' + y + '\\D').test($('#toast').textContent), $('#toast').textContent); }
    return c; };
  { const c1 = slipCase('сдвиг: отложено почти всё (119 900), взяли 20 000', p => { p.saved.oleg = 119900; p.conf.oleg = 0; }, 20000);
    info('сдвиг «почти всё»: на ' + c1.shift + ' дн. (предел ' + c1.cap + '), ' + c1.base + ' ₽ в день против ' + c1.rate + ' к прежнему сроку');
    slipCase('сдвиг: взяли 100 ₽', p => { p.saved.oleg = 50000; }, 100);
    const c82 = slipCase('порог: взяли 20 000 из 50 000 (доплата 82 ₽)', p => { p.saved.oleg = 50000; }, 20000);
    ok('порог: доплата 82 ₽ — режим «одна кнопка + ссылка»', c82.plus === 82 && c82.small, c82.plus);
    V3_SCEN.solo(); const dN = daysTo(P());   /* у solo stepped = false: доплата ровно N при отложенном share − 100·d и взятых N·d */
    for (const N of [149, 150]) { const cN = slipCase('порог: доплата ровно ' + N + ' ₽', p => { p.saved.oleg = p.share.oleg - 100 * dN; }, N * dN);
      ok('порог: доплата ' + N + ' ₽ — ' + (N < 150 ? 'одна кнопка + ссылка' : 'две равные кнопки'), cN.plus === N && cN.small === (N < 150), cN.plus + ' / small ' + cN.small); }
    const cBig = slipCase('порог: большая доплата (взяли 90 000 из 100 000)', p => { p.saved.oleg = 100000; }, 90000);
    ok('порог: большая доплата — две равные кнопки', cBig.plus >= 150 && !cBig.small, cBig.plus);
    slipCase('сдвиг: взяли 1 ₽', p => { p.saved.oleg = 50000; }, 1);
    for (const d of [1, 2, 3]) slipCase('сдвиг: срок через ' + d + ' дн., взяли 50 000', p => { p.cr = now() - 60 * DAY; p.dl = now() + d * DAY; p.saved.oleg = 100000; }, 50000);
    slipCase('сдвиг: цель создана сегодня, срок через 2 дня', p => { p.cr = now(); p.dl = now() + 2 * DAY; p.saved.oleg = 60000; }, 40000);
    slipCase('сдвиг: срок 20 декабря уходит в следующий год', p => { p.cr = Date.UTC(2026, 7, 1); p.dl = Date.UTC(2026, 11, 20); p.saved.oleg = 60000; }, 30000);
    V3_SCEN.solo(); const p = P(); p.saved.oleg = 50000; openSheet('input', 'took'); $('#inputv').value = '100'; $('#inputf').requestSubmit(); const dl0 = p.dl;
    budgetScreen('slip (продолжить)', true); $('#bottom .main').click(); ok('сдвиг 100 ₽: «Продолжить по плану» — срок прежний', S.scr === 'purchase' && p.dl === dl0 && S.v3.log.includes('slip_day')); }
  /* ── волна 5 · п.2: общая цель — сдвиг предложением (решение владельца 05.10, QA №12) ── */
  const propose = (who, took) => { const p = P(); S.who = who; p.saved[who] = (p.saved[who] || 0) + took; v3took(p, who, took); return p; };
  const propT = () => ($('#view .v3-prop') || {}).innerText || '';
  V3_SCEN.group2(); { const p = propose('oleg', 30000), dl0 = p.dl, c = v3slipCalc(p, 'oleg', 30000), pb = $$('#view .v3-pair button');
    ok('группа: доплата ≥ 150 — две равные кнопки', c.plus >= V3_SLIP_MIN && !c.small, c.plus);
    ok('группа: на slip — «Предложить новый срок» и «Откладывать +M»', pb.length === 2 && /^Предложить новый срок/.test(pb[0].innerText) && /^Откладывать \+/.test(pb[1].innerText) && /согласятся все/.test(vt()), pb.map(b => b.innerText.replace(/\n/g, ' ')).join(' | '));
    budgetScreen('slip (общая цель)', true); noReproach('slip (общая цель)', vt());
    pb[0].click(); const pr = p.v3prop;
    ok('группа: предложение не меняет срок', p.dl === dl0 && !!pr && pr.st === 'open' && pr.dl === c.dl && S.v3.log.includes('slip_propose'), JSON.stringify(pr));
    ok('группа: у предложившего — «согласны 1 из 2» и «догнать свою часть: +N ₽ в день»', /Согласны 1 из 2/.test(propT()) && /догнать свою часть: \+\d[\d\s]*₽ в день/.test(propT()) && !/\+0\s₽/.test(propT()), propT());
    demo.who('anya'); const other = propT();
    ok('группа: Аня видит «Предложено перенести срок на …» и «Согласна / Оставить срок»', /^Предложено перенести срок на \d+\s\S+/.test(other) && !!$('#view .v3-prop [data-act="v3propYes"]') && $('#view .v3-prop [data-act="v3propYes"]').textContent === 'Согласна' && $('#view .v3-prop [data-act="v3propNo"]').textContent === 'Оставить срок', other);
    ok('группа: в предложении нет причин, сумм и автора', !/₽|\d\s\d{3}|взял|Олег|не хватает/.test(other), other);
    ok('группа: срок у Ани прежний до согласия', p.dl === dl0);
    budgetScreen('предложение глазами Ани'); noRed('предложение'); noReproach('предложение', other);
    $('#view [data-act="v3propYes"]').click();
    ok('группа: все согласны — срок сменился у всех', p.dl === c.dl && !p.v3prop && S.v3.log.includes('slip_agreed') && /Все согласны/.test($('#toast').textContent), new Date(p.dl).toISOString() + ' ' + $('#toast').textContent);
    demo.who('oleg'); ok('группа: у Олега новый срок, блока предложения нет', !$('#view .v3-prop') && $('#view .head').innerText.includes(dStr(c.dl)), $('#view .head').innerText); }
  V3_SCEN.group2(); { const p = propose('oleg', 10000), dl0 = p.dl, c = v3slipCalc(p, 'oleg', 10000), ln = $('#view .v3-sliplink');
    ok('группа: доплата ' + c.plus + ' < 150 — «Догнать: +N ₽ в день» и ссылка «или сдвинуть срок»', c.small && bt() === 'Догнать: +' + rubT(c.plus) + ' в день' && !!ln && ln.textContent === 'или сдвинуть срок' && !$$('#view .v3-pair button').length && /согласятся все/.test(vt()), bt() + ' / ' + (ln && ln.textContent));
    budgetScreen('slip (общая цель, доплата < 150)', true);
    $('#view [data-act="v3slipDate"]').click();
    ok('группа: ссылка ведёт к предложению, срок не меняется', p.dl === dl0 && !!p.v3prop && p.v3prop.st === 'open', JSON.stringify(p.v3prop)); demo.who('anya'); $('#view [data-act="v3propNo"]').click();
    ok('группа: «Оставить срок» — срок прежний, у Ани блока нет', p.dl === dl0 && !!p.v3prop && p.v3prop.st === 'kept' && S.v3.log.includes('slip_kept') && !$('#view .v3-prop'), JSON.stringify(p.v3prop));
    demo.who('oleg'); const t = propT();
    ok('группа: предложивший видит «Срок оставили прежним» и как догнать', /Срок оставили прежним/.test(t) && /Догнать свою часть: \+/.test(t), t);
    $('#view [data-act="v3propSeen"]').click(); ok('группа: «Понятно» убирает блок', !p.v3prop && !$('#view .v3-prop')); }
  V3_SCEN.group3(); { const p = propose('oleg', 8000), dl0 = p.dl, c = v3slipCalc(p, 'oleg', 8000); $('#view [data-act="v3slipDate"]').click();
    demo.who('anya'); $('#view [data-act="v3propYes"]').click();
    ok('группа на 4: согласие Ани — ждём остальных, «согласны 2 из 4»', p.dl === dl0 && /Согласны 2 из 4/.test(propT()) && /Ждём остальных/.test($('#toast').textContent), propT() + ' / ' + $('#toast').textContent);
    setDay(1); ok('группа на 4: Тимур и Света согласились на следующий день — срок сменился', p.dl === c.dl && !p.v3prop, new Date(p.dl).toISOString()); setDay(0); }
  V3_SCEN.solo(); { const p = P(), dl0 = p.dl; p.saved.oleg = 50000; v3took(p, 'oleg', 20000); $('#view [data-act="v3slipDate"]').click();
    ok('своя цель: сдвиг сразу, без предложения', p.dl > dl0 && !p.v3prop && !$('#view .v3-prop')); }
  /* ── волна 5 · п.3: бот без склейки предложений (QA №8) ── */
  V3_SCEN.solo(); me().bot = 'max'; me().chat = []; for (const q of ['влезет ли ужин за 3000?', 'влезет ли телевизор за 90000?', 'влезет ли кофе за 200?']) botSay(q);
  { const bs = me().chat.filter(x => x.out === 'afford').map(x => x.b), glued = bs.filter(b => /[0-9a-zа-яё₽»]\s+[А-ЯЁ]/.test(b));
    ok('бот: три ответа «влезет ли» с ценой в днях', bs.length === 3 && bs.every(b => /(откладываете столько за|меньше дневного плана)/.test(b)), bs.join(' || '));
    ok('бот: предложения не склеены («октября На…», «₽ Это…»)', !glued.length, glued.join(' || '));
    ok('бот: предложения ≤15 слов', bs.every(b => !longSent(b).length), bs.map(b => longSent(b).join('/')).join(' || ')); }
  /* ── v2 не сломан ── */
  scenario('partner'); ok('v2 partner работает', S.scr === 'purchase' && /Аня: по плану/.test(vt()));
  scenario('mid'); demo.who('anya'); ok('v2 anya-purchase: недели Ани, чужих сумм нет', !!$('#view .v3-weeks') && !/46\s000/.test(vt()));
  scenario('week'); ok('v2 «итоги недели» (пара) открываются', S.sheet === 'weeksum' && /Недель по плану/.test(st()));
} catch (e) { ok('ИСКЛЮЧЕНИЕ', false, e.stack); }
finish(); })();
</script>
