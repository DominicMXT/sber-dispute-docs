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
  if (whole || base + mine <= 45) ok(name + ': первый экран ≤45 слов' + (whole ? ' (весь экран — экран модуля)' : ''), W(t) <= 45, W(t));
  else out.push('WARN ' + name + ': первый экран ' + (base + mine) + ' слов > 45 — база экрана v2 ' + base + ' (была выше бюджета до модуля), добавка модуля ' + mine); ok(name + ': предложения ≤15 слов', !longSent(vt()).length, longSent(vt()).join(' / ')); info(name + ': первый экран ' + W(fold()) + ' слов (из них модуль ' + W(fold(true)) + '), весь экран ' + W(vt()) + ' слов'); };
const budgetSheet = name => { ok(name + ': лист ≤30 слов', W(st()) <= 30, W(st()) + ' :: ' + st().replace(/\n/g, ' | ')); ok(name + ': предложения листа ≤15', !longSent(st()).length, longSent(st()).join(' / ')); };
const noReproach = (name, s) => ok(name + ': без «всё сначала» и упрёков', !/сначала|сгорел[аио]?\b(?!о)|отстаёте|вы отстаёте|срочно|провал|увы/i.test(s.replace('не сгорело', '').replace('Ничего не сгорело', '')), s.slice(0, 160));
const lock = (name, root) => ok(name + ': значок «видно только вам» с aria-label', !!$(root + ' [aria-label="видно только вам"]'));
const EXP = {dayprice:() => S.scr === 'today' && !!$('#view .v3-dayprice'), slip:() => S.scr === 'slip', weeks:() => S.scr === 'purchase' && !!$('#view .v3-weeks'),
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
  V3_SCEN.slip(); const ps = P(), dl0 = ps.dl, c0 = v3slipCalc(ps, 'oleg', 20000);
  ok('slip: экран после крупной траты, отложенное уменьшилось, но не обнулилось', S.scr === 'slip' && ps.saved.oleg === 30000);
  const pb = $$('#view .v3-pair button');
  ok('slip: две равные кнопки', pb.length === 2 && pb[0].className === pb[1].className && pb[0].offsetWidth === pb[1].offsetWidth && !$('#bottom .main'), pb.map(b => b.className + ':' + b.offsetWidth).join(' '));
  ok('slip: «сдвинем на N дней» и «+M ₽ в день»', new RegExp('Сдвинуть срок на ' + c0.shift + '\\s').test(pb[0].innerText) && /^Откладывать \+/.test(pb[1].innerText) && c0.plus > 0, pb.map(b => b.innerText.replace(/\n/g, ' ')).join(' | '));
  noReproach('slip', vt()); budgetScreen('slip', true); noRed('slip'); lock('slip', '#view');
  pb[0].click(); ok('slip: журнал slip_shown → slip_date', S.v3.log.join().endsWith('slip_shown,slip_date'), S.v3.log.join()); ok('slip: «Сдвинуть срок» — срок +N дней, план в день прежний', S.scr === 'purchase' && Math.round((ps.dl - dl0) / DAY) === c0.shift && perDay(ps, 'oleg') <= c0.base + 1, Math.round((ps.dl - dl0) / DAY) + ' / ' + perDay(ps, 'oleg') + ' vs ' + c0.base);
  V3_SCEN.solo(); const pt = P(); pt.saved.oleg = 50000; openSheet('input', 'took'); $('#inputv').value = '20 000'; $('#inputf').requestSubmit();
  ok('slip: путь «Изменить цель → Пришлось взять из отложенного» ведёт на slip', S.scr === 'slip' && pt.saved.oleg === 30000 && !S.sheet, S.scr + ' ' + pt.saved.oleg);
  const dl1 = pt.dl; $('#view [data-act="v3slipDay"]').click(); ok('slip: «+M ₽ в день» — срок прежний', S.scr === 'purchase' && pt.dl === dl1);
  ok('slip: журнал событий', ['slip_shown', 'slip_day'].every(e => S.v3.log.includes(e)), S.v3.log.join());
  /* ── M-F weeks ── */
  V3_SCEN.weeks(); const pw = P(), cells = () => $$('#view .v3-day'), onIx = () => cells().map((x, i) => x.classList.contains('on') ? i : -1).filter(i => i >= 0);
  const k0 = v3weeks(pw, 'oleg');
  ok('weeks: сетка недель от старта до срока', cells().length === k0.total && k0.ci === 4, cells().length + ' / ' + k0.total + ' / ci ' + k0.ci);
  ok('weeks: 3 недели по плану, пропуск не закрашен и не обнуляет', /3 недели по плану/.test($('#view .v3-weeks').innerText) && onIx().join() === '0,1,3', onIx().join());
  ok('weeks: текущая неделя отмечена .v3-now, будущие — .v3-fut', cells()[4].classList.contains('v3-now') && $$('#view .v3-day.v3-fut').length === k0.total - 5);
  budgetScreen('weeks'); noRed('weeks'); lock('weeks', '#view .v3-weeks');
  ok('weeks: текст недель — предложения ≤15', !longSent($('#view .v3-weeks').innerText).length);
  ACT.saveSheet(); $('#saveamt').value = '500'; $('#savef').requestSubmit();
  ok('weeks: после «отложил» текущая неделя закрашена (.on), прошлые не изменились', onIx().join() === '0,1,3,4' && /4 недели по плану/.test($('#view .v3-weeks').innerText), onIx().join());
  ok('M-J: похвала за факт — тост «Неделя засчитана»', /Неделя засчитана — уже 4 недели/.test($('#toast').textContent), $('#toast').textContent);
  if (ANIM) ok('anim: ячейка недели заполняется (.v3-fill)', !!$('#view .v3-day.on.v3-fill')); else info('anim не подключён — проверка заливки пропущена');
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
  V3_SCEN.solo(); openSheet('weeksum'); ok('weeksum одного: недели по плану, «Сказать прямо»', /Недель по плану/.test(st()) && /Пропуск не обнуляет/.test(st()) && !!$('#sheet [data-sheet="v3direct"]'), st().replace(/\n/g, ' | '));
  budgetSheet('weeksum одного'); ok('weeksum одного: без прямоты до кнопки', !/Прямо/.test(st()));
  $('#sheet [data-sheet="v3direct"]').click(); ok('v3direct открывается по кнопке', S.sheet === 'v3direct' && /Прямо, раз вы спросили/.test(st())); budgetSheet('v3direct'); noReproach('v3direct', st());
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
  /* ── v2 не сломан ── */
  scenario('partner'); ok('v2 partner работает', S.scr === 'purchase' && /Аня: по плану/.test(vt()));
  scenario('mid'); demo.who('anya'); ok('v2 anya-purchase: недели Ани, чужих сумм нет', !!$('#view .v3-weeks') && !/46\s000/.test(vt()));
  scenario('week'); ok('v2 «итоги недели» (пара) открываются', S.sheet === 'weeksum' && /Недель по плану/.test(st()));
} catch (e) { ok('ИСКЛЮЧЕНИЕ', false, e.stack); }
finish(); })();
</script>
