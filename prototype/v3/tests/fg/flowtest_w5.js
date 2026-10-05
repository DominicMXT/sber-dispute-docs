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
