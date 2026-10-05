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
    else { ok(name + ': две равные дороги', pb.length === 2 && pb[0].className === pb[1].className && !$('#bottom .main'), pb.length);
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
    slipCase('сдвиг: взяли 1 ₽', p => { p.saved.oleg = 50000; }, 1);
    for (const d of [1, 2, 3]) slipCase('сдвиг: срок через ' + d + ' дн., взяли 50 000', p => { p.cr = now() - 60 * DAY; p.dl = now() + d * DAY; p.saved.oleg = 100000; }, 50000);
    slipCase('сдвиг: цель создана сегодня, срок через 2 дня', p => { p.cr = now(); p.dl = now() + 2 * DAY; p.saved.oleg = 60000; }, 40000);
    slipCase('сдвиг: срок 20 декабря уходит в следующий год', p => { p.cr = Date.UTC(2026, 7, 1); p.dl = Date.UTC(2026, 11, 20); p.saved.oleg = 60000; }, 30000);
    V3_SCEN.solo(); const p = P(); p.saved.oleg = 50000; openSheet('input', 'took'); $('#inputv').value = '100'; $('#inputf').requestSubmit(); const dl0 = p.dl;
    budgetScreen('slip (продолжить)', true); $('#bottom .main').click(); ok('сдвиг 100 ₽: «Продолжить по плану» — срок прежний', S.scr === 'purchase' && p.dl === dl0 && S.v3.log.includes('slip_day')); }
  /* ── волна 5 · п.2: общая цель — сдвиг предложением (решение владельца 05.10, QA №12) ── */
  const propose = (who, took) => { const p = P(); S.who = who; p.saved[who] = (p.saved[who] || 0) + took; v3took(p, who, took); return p; };
  const propT = () => ($('#view .v3-prop') || {}).innerText || '';
  V3_SCEN.group2(); { const p = propose('oleg', 10000), dl0 = p.dl, c = v3slipCalc(p, 'oleg', 10000), pb = $$('#view .v3-pair button');
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
  V3_SCEN.group2(); { const p = propose('oleg', 10000), dl0 = p.dl; $('#view [data-act="v3slipDate"]').click(); demo.who('anya'); $('#view [data-act="v3propNo"]').click();
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
