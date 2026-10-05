<script>
(() => { const out = [], ok = (n, c, x) => out.push((c ? 'PASS ' : 'FAIL ') + n + (x !== undefined && !c ? ' :: ' + x : ''));
const vt = () => $('#view').innerText, bt = () => $('#bottom').innerText.trim(), words = s => (s.match(/[A-Za-zА-Яа-яЁё0-9]+/g) || []).length;
const longSent = s => s.split(/[.!?\n]+/).map(x => x.trim()).filter(x => words(x) > 15);
const budget = (name) => { const t = vt().replace('Что не так?', ''); ok(name + ': ≤45 слов', words(t) <= 45, words(t)); ok(name + ': предложения ≤15 слов', !longSent(t).length, longSent(t).join(' / ')); };
try {
  /* сторис вернулись (решение владельца 05.10): fresh → сторис → согласие → пример */
  const storyOn = () => $('#story').classList.contains('on'), PAIR = /(^|[^а-яё])пар(а|е|у|ы|ой)([^а-яё]|$)|партн|вдво[её]м|супруг/i;
  scenario('fresh'); ok('fresh → сторис поверх согласия', storyOn() && S.scr === 'consent' && /Пропустить/.test($('#story').innerText), S.scr + ' ' + storyOn());
  ok('сторис: от 3 до 5 карточек', SLIDES.length >= 3 && SLIDES.length <= 5, SLIDES.length);
  ok('пульт: «Первый вход: знакомство, согласие и пример»', /Первый вход: знакомство, согласие и пример/.test($('#panel [data-sc="fresh"]').textContent));
  for (let i = 0; i < SLIDES.length; i++) { story(i); const t = $('#stxt').innerText;
    ok('карточка ' + (i + 1) + ': без «пара/партнёр»', !PAIR.test(t), t);
    ok('карточка ' + (i + 1) + ': ≤30 слов, предложения ≤15', words(t) <= 30 && !longSent(t).length, words(t) + ' :: ' + longSent(t).join(' / ')); }
  ok('карточки про пивот: «на себя», цель на фото, вместе — по желанию, чужих денег не видно', /на себя/i.test(SLIDES[0].h + SLIDES[0].t) && SLIDES.some(s => /фото/.test(s.t)) && /по желанию/.test(SLIDES[SLIDES.length - 1].h) && /Чужих денег не видит никто/.test(SLIDES[SLIDES.length - 1].t));
  ok('последняя карточка — кнопка «Начать»', !!$('#start'));
  $('#start').click(); ok('«Начать» → согласие, событие onboarding_done', !storyOn() && S.scr === 'consent' && S.v3.log.includes('onboarding_done'), S.v3.log.join());
  scenario('fresh'); story(1); $('#skip').click();
  ok('«Пропустить» → согласие, событие onboarding_skipped', !storyOn() && S.scr === 'consent' && S.v3.log.includes('onboarding_skipped') && !S.v3.log.includes('onboarding_done'), S.v3.log.join());
  ok('согласие: без «Партнёр»', !/Партнёр/.test(vt()), vt().slice(0, 120)); budget('согласие');
  ACT.consentOk(); ok('согласие → пример', S.scr === 'example' && !!$('#view .v3-example'));
  ok('пример: плашка и кнопка', /Пример/.test(vt()) && bt() === 'Создать свою цель', bt()); budget('пример');
  ACT.v3exStep(); ok('«Отложить» в примере: туман проясняется, ничего не сохранено', S.v3.ex === 73000 && S.purchases.length === 0 && +$('#view .photo').dataset.pct > 0.6);
  openSheet('how'); ok('how в примере без ссылки на пример', !/Посмотреть пример/.test($('#sheet').innerText)); closeSheet();
  ACT.v3own(); ok('«Создать свою цель» → фраза Э-02', S.scr === 'phrase' && /Что хотите купить и к какому сроку\?/.test(vt()));
  $('#phrase').value = 'Ноутбук 90 тысяч к 1 марта'; ACT.phraseGo();
  ok('уточнение без партнёра', S.scr === 'clarify' && /Какую часть цены отложите вы/.test(vt()) && /всю сумму/.test(vt()) && !/партн/i.test(vt()), vt().slice(0, 160));
  ok('имя разобрано (фикс парсера)', S.draft.name === 'Ноутбук', S.draft.name);
  $('#clar').value = 'плачу сам'; $('#clarf').requestSubmit();
  ok('ответ: «Сохранить цель», блочные строки ответа', S.scr === 'answer' && bt() === 'Сохранить цель' && $$('#view .v3-answer-line').length >= 3 && $$('#view .v3-answer-line').every(x => getComputedStyle(x).display === 'block'), $$('#view .v3-answer-line').length);
  ACT.v3save(); ok('сохранить без входа → лист входа: VK ID и Яндекс ID (Сбер ID и Max — позже)', S.sheet === 'login' && ['VK ID','Яндекс ID'].every(t => $('#sheet').textContent.includes(t)) && !/почт/i.test($('#sheet').textContent)); ACT.loginVk(); ok('сохранить → «Копить вместе?»', S.scr === 'together' && $$('#view .v3-pair .sec2').length === 2); budget('вместе?');
  const pb = $$('#view .v3-pair button'); ok('кнопки одного веса', pb[0].className === pb[1].className && pb[0].offsetWidth === pb[1].offsetWidth, pb.map(b => b.className + ':' + b.offsetWidth).join(' '));
  ACT.v3alone(); ok('«Пока сам» → своя цель без партнёра', S.scr === 'purchase' && /своя цель/.test(vt()) && !/Аня|партн/i.test(vt()), (vt().match(/.*(Аня|партн).*/i) || [''])[0]);
  ok('«Пока сам»: без листа поверх, строка «Где лежат деньги — указать»', !S.sheet && /Где лежат деньги — указать/.test(vt()), S.sheet);
  $('#view .v3-where').click(); ok('лист «где» без «Партнёр»', S.sheet === 'where' && !/Партнёр/.test($('#sheet').innerText)); closeSheet();
  ok('журнал событий', ['example_shown','example_action','own_goal_started','goal_saved','together_solo'].every(e => S.v3.log.includes(e)), S.v3.log.join(','));
  openSheet('how'); ok('how с экрана цели: «Посмотреть пример»', /Посмотреть пример/.test($('#sheet').innerText));
  ACT.v3showEx(); ok('пример повторно, с «Назад»', S.scr === 'example' && /Назад/.test(vt())); go(S.v3.back);
  ok('пример только один раз', (() => { const s0 = S; S = seed('fresh'); me().exSeen = true; ACT.consentOk(); const r = S.scr === 'phrase'; S = s0; go('purchase'); return r; })());
  ACT.v3call(); ok('«Позвать» → отправка ссылки', S.scr === 'groupShare' && /до 6 человек/i.test(vt())); budget('позвать');
  ok('текст ссылки без моих сумм', !/в день|отложен|отложил/i.test($('#v3sharetxt').innerText), $('#v3sharetxt').innerText);
  ACT.v3send(); const p = P(); ok('после отправки — общая цель на одного', !!p.group && p.group.members.length === 1 && S.scr === 'purchase' && /Ссылка отправлена/.test(vt()));
  ACT.v3asGuest(); ok('глазами приглашённого', S.who === 'anya' && /зовёт копить вместе/.test(vt()) && /Без регистрации/.test(vt()));
  $('#v3accept').value = 'беру 15'; $('#v3acceptf').requestSubmit();
  ok('№6: цена уже покрыта — предупреждение, не вступила молча', p.group.members.join() === 'oleg' && /больше/.test($('#v3accnote').textContent), $('#v3accnote').textContent);
  $('#v3acceptf').requestSubmit();
  ok('вступила: пара, без процентов', p.group.members.join() === 'oleg,anya' && p.share.anya === 15000 && !/%/.test($('#view .sec').innerText) && $$('#view [data-v3-member]').length === 2, $('#view .sec').innerText.replace(/\n/g, ' ').slice(0, 200));
  closeSheet();
  V3_SCEN.group3(); const g = P(), t3 = vt();
  ok('group3: «Вместе ≈ 30 %», снимок 0.3', /Вместе ≈ 30/.test(t3) && g.group.snap === 0.3);
  const stOf = () => $$('#view .v3-member').map(x => x.dataset.v3Member + ':' + ((x.querySelector('.v3-st') || {}).textContent || '—')).join();
  ok('group3: статусы в порядке входа, у отстающей — без плашки', stOf() === 'oleg:по плану,anya:по плану,timur:по плану,sveta:—', stOf());
  ok('group3: чужих отложенных сумм нет', !/11\s500|9\s000|3\s000|14\s000/.test(t3), (t3.match(/.*(11\s500|9\s000|3\s000|14\s000).*/) || [''])[0]);
  ok('group3: значок «видят участники»', !!$('#view [aria-label="видят участники"]'));
  ok('без красного', !$$('#view *').some(x => { const m = getComputedStyle(x).color.match(/\d+/g).map(Number); return m[0] > 150 && m[1] < 90 && m[2] < 90; }));
  step(9000); ok('своя отметка не двигает общий % в тот же день', P().group.snap === 0.3 && /Вместе ≈ 30/.test(vt()));
  setDay(1); ok('назавтра — новый снимок', P().group.snap === 0.3 || P().group.snap === 0.4, P().group.snap); setDay(0);
  V3_SCEN.group2(); const t2 = vt(); ok('group2: «к сроку сходится», без %', /К сроку сходится/.test(t2) && !/%/.test(t2.replace('Что не так?', '')), t2.slice(0, 200));
  ok('group2: отложенного Ани нет', !/21\s000/.test(t2));
  demo.who('anya'); ok('group2 глазами Ани', /беру 70/.test(vt()) && !/24\s000/.test(vt()), vt().slice(0, 300));
  V3_SCEN.groupInvite(); ok('groupInvite: что увидит / не увидит', S.who === 'anya' && /Все увидят/.test(vt()) && /Только вам/.test(vt()) && /Организатор их не видит/.test(vt()) && !!$('#view [aria-label="видят участники"]') && !!$('#view [aria-label="видно только вам"]'));
  V3_SCEN.empty(); ok('пустые «Покупки»: пример и кнопка', S.scr === 'list' && /Пример/.test(vt()) && bt() === 'Создать свою цель');
  go('data'); $('#tabs [data-tab="buy"]').click(); ok('вкладка «Покупки» без целей → пустой список', S.scr === 'list');
  scenario('partner'); ok('v2 partner работает', S.scr === 'purchase' && /Аня: по плану/.test(vt()) && /сделала шаг/.test(vt()), vt().slice(0, 300));
  scenario('mid'); demo.who('anya'); ok('v2 anya-purchase работает', /Олег/.test(vt()) && !/своя цель/.test(vt()));
  /* ── волна 5: правки по QA и дизайн-ревью 04.10 ── */
  const stRow = m => { const el = $(`#view [data-v3-member="${m}"] .v3-st`); return el ? el.textContent : null; };
  const cssOf = (prop, v) => { const d = document.createElement('div'); d.style[prop] = v; document.body.append(d); const c = getComputedStyle(d)[prop]; d.remove(); return c; };
  const W = s => (s.match(/[A-Za-zА-Яа-яЁё0-9]+/g) || []).length;
  /* №1, №7: чужие статусы — из суточного снимка, только «по плану»; порог — от даты входа */
  S.who = 'oleg'; V3_SCEN.group3(); let G5 = P();
  ok('№1: на 3+ ни у кого из чужих нет «отстаёт» / «только начали»', ['anya','timur','sveta'].every(m => !/отстаёт|только начали/.test(($(`#view [data-v3-member="${m}"]`) || {}).textContent || '')));
  G5.saved.sveta += 3000; render(); ok('№1: чужая отметка в тот же день не меняет ни статус, ни %', stRow('sveta') === null && /Вместе ≈ 30/.test(vt()), stRow('sveta'));
  setDay(1); ok('№1: назавтра снимок обновил статус', stRow('sveta') === 'по плану', stRow('sveta')); setDay(0);
  V3_SCEN.group3(); G5 = P(); G5.saved.timur = 0; render(); ok('№1: «только начали» (= 0 ₽) чужим не виден', stRow('timur') === 'по плану' || stRow('timur') === null, stRow('timur'));
  setDay(1); ok('№1: и после снимка ноль не виден как «только начали»', stRow('timur') === null, stRow('timur')); setDay(0);
  V3_SCEN.group3(); G5 = P(); G5.saved.oleg = 0; render(); ok('№1: свой статус видит сам — «только начали» с замком', stRow('oleg') === 'только начали' && !!$('#view [data-v3-member="oleg"] [aria-label="видно только вам"]'), stRow('oleg'));
  V3_SCEN.group2(); G5 = P(); G5.join = {anya: now()}; G5.saved.anya = 0; v3snap(G5); render();
  ok('№7: вошедшая сегодня — по плану от даты входа, цель сходится', onPlan(G5, 'anya') && /К сроку сходится/.test(vt()), onPlan(G5, 'anya') + ' ' + (vt().match(/(К сроку сходится|Пока не сходится)/) || [''])[0]);
  demo.who('anya'); ok('№7: у вошедшей своя строка — «только начали», видна только ей', stRow('anya') === 'только начали'); demo.who('oleg');
  /* №2: «Собрано» на 3–6, когда собраны все части */
  V3_SCEN.group3(); G5 = P(); ok('№2: gapOf считает всех участников', gapOf(G5) === v3gap(G5) && gapOf(G5) === 0, gapOf(G5) + ' / ' + v3gap(G5));
  for (const m of G5.group.members) G5.saved[m] = G5.share[m]; G5.saved.timur -= 500; G5.saved.oleg -= 100; render(); step(100);
  ok('№2: пока у одного не собрано — цель активна', G5.state === 'active');
  G5.saved.timur = G5.share.timur; G5.saved.oleg -= 100; render(); step(100);
  ok('№2: все части собраны → «Собрано», без «Я отложил(а)»', G5.state === 'done' && /Собрано/.test(vt()) && bt() !== 'Я отложил(а)', G5.state + ' / ' + bt());
  /* №4: участник выходит, организатор отменяет у всех с предупреждением */
  V3_SCEN.group3(); G5 = P(); demo.who('anya'); openSheet('change');
  ok('№4: у участника — «Выйти из цели», без «Отменить цель»', /Выйти из цели/.test($('#sheet').innerText) && !/Отменить (?:покупк|цель)у/.test($('#sheet').innerText), $('#sheet').innerText.replace(/\n/g, ' | '));
  ACT.cancelBuy(); ok('№4: «отмена» участником = выход, цель у остальных осталась', S.purchases.includes(G5) && G5.state === 'active' && G5.group.members.join() === 'oleg,timur,sveta' && G5.group.gone.includes('anya'), G5.group.members.join());
  ok('№4: вышедшая цель у себя не видит', S.scr === 'list' && !/Дом у моря/.test(vt()), S.scr);
  demo.who('oleg'); S.cur = G5.id; go('purchase'); ok('№11: у остальных — «Аня вышла из цели», без «берёт 0»', /Аня\s+вышла из цели/.test(vt()) && !/берёт 0/.test(vt()), vt().slice(0, 400));
  openSheet('change'); ok('№4: у организатора — «Отменить цель»', /Отменить цель/.test($('#sheet').innerText));
  openSheet('cancelAsk'); ok('№4: предупреждение «у всех участников»', /у всех участников/.test($('#sheet').innerText) && !/партн/i.test($('#sheet').innerText), $('#sheet').innerText); closeSheet();
  /* №11: удалила данные */
  V3_SCEN.group2(); G5 = P(); demo.who('anya'); ACT.delAll(); S.who = 'oleg'; me().consent = true; go('purchase');
  ok('№11: удалила данные — у Олега «Аня вышла», её часть не висит', S.purchases.includes(G5) && /Аня\s+вышла из цели/.test(vt()) && !/берёт 0/.test(vt()) && G5.share.anya == null, vt().slice(0, 300));
  /* №10: в свою цель никто не звал — у другого человека нет «зовёт» */
  V3_SCEN.solo(); demo.who('anya'); ok('№10: своя цель Олега, взгляд Ани — без «Олег зовёт»', !/зовёт/.test(vt()) && S.scr === 'list', vt().slice(0, 160)); demo.who('oleg');
  /* №6: части больше цены — видно и есть действие */
  V3_SCEN.group3(); G5 = P(); G5.share.oleg = 60000; render(); ok('№6: части больше цены — строка с суммой и «Уменьшить»', /Части больше цены на 20\s000/.test(vt()) && !!$('#view [data-input="share"]') && !/покрывают цену/.test(vt()), vt().match(/.*цен.*/g).join(' | '));
  /* №13: своя цель — ни слова о партнёре в листах; сценарий partner не ложится на свою цель */
  V3_SCEN.solo(); const bad = ['how','cancelAsk','photo','change','save','where'].filter(k => { openSheet(k); const t = $('#sheet').innerText; closeSheet(); return /партн/i.test(t); });
  ok('№13: листы своей цели без партнёра', !bad.length, bad.join());
  S = seed('fresh'); me().consent = true; me().exSeen = true; S.draft = parsePhrase('Кофемашина 30 тысяч к 1 марта, плачу сам'); commitDraft(); go('purchase');
  scenario('partner'); ok('№13: сценарий partner на своей цели → данные пары', S.purchases[0].id === 'sofa' && /Аня/.test(vt()));
  /* нераспознанная цель — нейтральный туман */
  S = seed('fresh'); me().consent = true; me().exSeen = true; S.draft = parsePhrase('Кофемашина 30 тысяч к 1 марта, плачу сам'); commitDraft(); go('purchase');
  ok('нераспознанная цель — нейтральный туман и «Добавить фото»', P().photo === 'v3fog' && /Добавить фото/.test(vt()), P().photo);
  ok('новая цель: неделя с нуля, мостик в «Сегодня»', /Неделя: 0 из 7/.test(vt()) && !/1 неделя по плану/.test(vt()) && bt().startsWith('Посмотреть, сколько можно на себя'), (vt().match(/Неделя: \d из 7/) || [''])[0] + ' / ' + bt());
  $('#bottom .main').click(); ok('мостик ведёт в «Сегодня»', S.scr === 'today' || S.scr === 'source', S.scr);
  /* пример ≠ мои данные; №17 */
  V3_SCEN.example(); ok('пример: без замка «видно только вам»', !$('#view [aria-label="видно только вам"]'));
  const exNote = $('#view .v3-exnote'), exBtn = $('#view [data-act="v3exStep"]');
  ok('пример: «Это пример, не ваши деньги» до «Отложить»', !!exNote && /Это пример, не ваши деньги/.test(exNote.textContent) && !!(exNote.compareDocumentPosition(exBtn) & Node.DOCUMENT_POSITION_FOLLOWING));
  ok('пример: пунктирная рамка карточки, плашка крупнее', getComputedStyle($('#view .cardp')).outlineStyle === 'dashed' && parseFloat(getComputedStyle($('#view .v3-exbadge')).fontSize) > 13, getComputedStyle($('#view .cardp')).outlineStyle);
  openSheet('how'); ok('лист how в примере ≤30 слов', W($('#sheet').innerText) <= 30, W($('#sheet').innerText)); closeSheet();
  for (let i = 0; i < 6; i++) ACT.v3exStep(); ok('пример можно «собрать»', /собрано/.test(vt()));
  V3_SCEN.group2(); ok('№17: тост примера не переживает переход', !$('#toast').classList.contains('on'));
  V3_SCEN.solo(); ACT.v3showEx(); ok('№17: повторный пример — с исходных данных, не «собрано, 0 ₽»', S.v3.ex === V3_EX.saved && !/собрано/.test(vt()) && /59\s000/.test(vt()), vt().slice(0, 200));
  /* общая цель на двоих: объяснение и нейтральная шкала */
  V3_SCEN.group2(); G5 = P();
  ok('group2: объяснение, почему без процента', /Вдвоём процент раскрыл бы/.test(vt()));
  const tr = $('#view .v3-time'), tick = $('#view .v3-time i'), fr = (now() - G5.cr) / (G5.dl - G5.cr);
  ok('group2: шкала — нейтральная дорожка (--film), засечка не цвета денег (--fill)', getComputedStyle(tr).backgroundColor === cssOf('backgroundColor', 'var(--film)') && getComputedStyle(tick).backgroundColor !== cssOf('backgroundColor', 'var(--fill)') && !$('#view .v3-time [style*="scaleX"]'), getComputedStyle(tr).backgroundColor + ' / ' + getComputedStyle(tick).backgroundColor);
  const tx = tick.getBoundingClientRect(), rr = tr.getBoundingClientRect();
  ok('group2: засечка там, где сегодня', Math.abs((tx.left + tx.width / 2 - rr.left) / rr.width - fr) < 0.02 && /сегодня/.test($('#view .v3-tnow').textContent), ((tx.left - rr.left) / rr.width).toFixed(3) + ' vs ' + fr.toFixed(3));
  /* значки: расшифровка в how, «видят участники» у «вместе N %» */
  for (const c of ['solo','group2','group3']) { V3_SCEN[c](); openSheet('how'); const t = $('#sheet').innerText;
    ok('how ' + c + ': ≤30 слов, предложения ≤15', W(t) <= 30 && !longSent(t).length, W(t) + ' :: ' + t.replace(/\n/g, ' | '));
    ok('how ' + c + ': значки расшифрованы словами', /видите только вы/.test(t) && (c === 'solo' || /видят участники/.test(t)) && !(c === 'solo' && /партн|участник/i.test(t)), t.replace(/\n/g, ' | ')); closeSheet(); }
  V3_SCEN.group3(); ok('3+: значок «видят участники» у «вместе N %»', !!$('#view .cap [aria-label="видят участники"]') && /вместе 30/.test($('#view .cap').textContent));
  ok('3+: «4 участника» с неразрывным пробелом', /4 участника/.test($('#view .head').textContent));
  /* приглашение: «Присоединиться», бюджет */
  V3_SCEN.groupInvite(); ok('groupInvite: «Присоединиться», без «Войти»', /Присоединиться/.test(vt()) && !/Войти/.test(vt())); ok('groupInvite: предложения ≤15 слов', !longSent(vt()).length, longSent(vt()).join(' / '));
  /* мелкое */
  V3_SCEN.solo(); const stp = $('#view .stamp'); ok('«своя цель» — нейтральная плашка, не зелёная', /своя цель/.test(stp.textContent) && getComputedStyle(stp).color !== cssOf('color', 'var(--ok)') && getComputedStyle(stp).borderTopColor !== cssOf('color', 'var(--ok)'), getComputedStyle(stp).color);
  V3_SCEN.together(); ok('Э-06: подтверждение не курсивом ответа GigaChat', !$('#view .ai'));
  S = seed('fresh'); me().consent = true; me().exSeen = true; go('phrase'); ok('Э-02: примеры одного — без «я могу»', !/я могу/.test(vt()));
  $('#phrase').value = 'Ноутбук 90 тысяч к 1 марта'; ACT.phraseGo(); ok('Э-03: без «половину», есть «часть — впишу»', !/половину/.test(vt()) && /часть — впишу/.test(vt()), vt().slice(0, 200));
  ok('Э-02: «откладываю 90» разбирается как своя часть', parsePhrase('Диван 180 тысяч к 31 декабря, откладываю 90').share === 90000);

  /* ── ТЗ 1.4, ФТ-91/92: шаг другого, «Подбодрить», точка «день у обоих» — на двоих есть, на 3–6 нет ── */
  const stepNote = () => /сегодня сделала? шаг/.test(vt()), cheerBtn = () => !!$('#view [data-act="cheer"]'), both = () => !!$('#view .wd.both');
  S.who = 'oleg'; V3_SCEN.group2(); ok('group2: точка «день у обоих» в неделе', both());
  scenario('partner'); ok('group2 + пульт «Партнёр отложил»: цель та же, «Аня сегодня сделала шаг» и «Подбодрить»', P().id === 'g2' && /Аня сегодня сделала шаг/.test(vt()) && cheerBtn(), P().id + ' :: ' + vt().slice(0, 200));
  $('#view [data-act="cheer"]').click(); ok('«Подбодрить» — без сумм', /без сумм/.test($('#toast').textContent), $('#toast').textContent);
  V3_SCEN.group2step(); ok('код group2step: шаг другого на двоих', stepNote() && cheerBtn() && both());
  openSheet('how'); ok('how на двоих объясняет точку и ≤30 слов', /Точка — день у обоих/.test($('#sheet').innerText) && W($('#sheet').innerText) <= 30, W($('#sheet').innerText)); closeSheet();
  demo.who('anya'); go('purchase'); ok('group2step глазами Ани: «Олег сегодня сделал шаг»', /Олег сегодня сделал шаг/.test(vt()) && cheerBtn()); demo.who('oleg');
  for (const who of ['oleg', 'anya']) { S.who = who; V3_SCEN.group3(); S.flags.partnerStep = true; render();
    ok('group3 (' + who + '): нет шага другого, «Подбодрить» и точки у обоих', !stepNote() && !cheerBtn() && !both() && !/сделала? шаг/.test(vt())); }
  S.who = 'oleg'; V3_SCEN.group3(); scenario('partner'); ok('пульт «Партнёр отложил» не кладёт шаг на цель 3–6', !(P() && P().group && /сделала? шаг/.test(vt())));
  /* ── одна ссылка на всю цель; «Новая ссылка» у организатора; вход закрыт при 6 ── */
  const linkTxt = () => ($('#view [data-v3-link]') || {}).textContent;
  V3_SCEN.groupShare(); const l0 = linkTxt(); ACT.v3send(); go('groupShare'); const l1 = linkTxt();
  ok('ссылка одна на цель: до и после отправки та же', !!l0 && l0 === l1, l0 + ' / ' + l1);
  ok('«Позвать»: «Одна ссылка для всех», «Новая ссылка» у организатора', /Одна ссылка для всех/.test(vt()) && !!$('#view [data-act="v3newLink"]')); budget('позвать (после отправки)');
  $('#view [data-act="v3asGuest"]').click(); $('#v3accept').value = 'беру 10'; $('#v3acceptf').requestSubmit(); if (!P().group.members.includes('anya')) $('#v3acceptf').requestSubmit();
  ok('Аня вошла по ссылке цели', P().group.members.includes('anya'));
  go('groupShare'); ok('у участника нет «Новая ссылка», ссылка та же', !$('#view [data-act="v3newLink"]') && linkTxt() === l0, linkTxt());
  V3_SCEN.groupInvite(); const gi = P(); S.who = 'oleg'; go('groupShare'); const oldL = linkTxt(); $('#view [data-act="v3newLink"]').click();
  ok('«Новая ссылка»: ссылка сменилась, тост «Старая больше не работает»', linkTxt() !== oldL && /Старая больше не работает/.test($('#toast').textContent), oldL + ' → ' + linkTxt());
  S.who = 'anya'; go('purchase'); ok('по старой ссылке — «Ссылка больше не работает», без поля', /Ссылка больше не работает/.test(vt()) && !$('#v3acceptf'), vt().slice(0, 120));
  S.v3.via = v3link(gi); render(); ok('по новой ссылке — приглашение с полем', !!$('#v3acceptf'));
  Object.assign(NAME, {k1:'Ира', k2:'Лев', k3:'Яна'}); for (const m of ['k1','k2','k3']) { gi.share[m] = 1000; gi.saved[m] = 0; gi.group.members.push(m); } render();
  ok('6 участников: вход закрыт — без поля, «максимум»', !$('#v3acceptf') && /максимум/.test(vt()), vt().slice(0, 200));
  S.who = 'oleg'; go('groupShare'); ok('6 участников: у организатора нет «Отправить ссылку»', !/Отправить ссылку/.test(bt()) && /В цели уже 6 человек/.test(vt()), bt());
  ok('все подмены текста сработали', demo.v3.warn().length === 0, demo.v3.warn().join());
} catch (e) { ok('ИСКЛЮЧЕНИЕ', false, e.stack); }
const pre = document.createElement('pre'); pre.id = 'T'; pre.textContent = out.join('\n'); document.body.append(pre); })();
</script>
