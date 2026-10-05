# -*- coding: utf-8 -*-
"""Третья волна правок под номинацию №3 — модуль интегратора, 05.10. Стоит после login.

Основание: независимые переоценки 43/60 и 46/60 (review/2026-10-05_n3-rescore3-rater1.md, -rater2.md, заметки там же).

1. Деньги в листах: «Пришлось взять» — пусто, буквы, минус, больше отложенного — ошибка под полем (раньше перехват мотивации
   молча обрезал сумму и писал «не сгорело: осталось 0 ₽»); копейки («9,5» без «тысяч») — вопрос, а не 10 ₽; номер карты в поле — ошибка;
   цена больше 50 млн ₽ в форме полей — переспрос; отметку «Я отложил(а)» можно отменить в тот же день.
2. Фраза: «хочу», «купить» и подобное не попадают в название; «откладываю 10 тысяч в месяц» — темп, а не доля цены
   (на ответе — сколько соберётся к сроку); «уже есть N» и очень большой план в день — с пояснением; длинное название переносится.
3. Тексты: «Подтверждено 0 ₽ из N» → понятная строка; согласие без строки-обрывка «— видят участники»; «Пока сам» → «Пока только я»;
   отзыв пустым не отправляется, нет обещания про контакт без поля для него; подсказки прихода называют кнопку «Посчитать «Сегодня»».
4. Вёрстка: «плёнка» — 7 кадров по дням недели вместо 13 (подпись «Неделя: N из 7»); значки видимости — только когда есть
   общие цели; тост — над нижней зоной, не на заголовке; в альбомной нижняя зона уходит в поток раньше; «Отменить покупку» —
   как опасное действие; панель вкладок не просвечивает.
"""
R = [
    # плёнка: 7 кадров — по одному на день, как в подписи «Неделя: N из 7» (было 13 кадров и заливка первого)
    ('<div class="film">${\'<div class="fr"></div>\'.repeat(13).replace(\'<div class="fr">\', `<div class="fr" style="--r:${(100 - steps / 7 * 100).toFixed(1)}%">`)}</div>',
     '<div class="film" role="img" aria-label="Дней с отметкой на этой неделе: ${steps} из 7">${Array.from({length:7}, (_, i) => `<div class="fr" style="--r:${i < steps ? 0 : 100}%"></div>`).join(\'\')}</div>'),
    ('<button class="main press" data-act="cancelBuy">Отменить покупку</button>', '<button class="main press p-danger" data-act="cancelBuy">Отменить покупку</button>'),
    ('<p>Читаем каждый отзыв. Ответим в течение суток, если оставите контакт.</p>', '<p>Читаем каждый отзыв и исправляем.</p>'),
    ('<button class="sec2 press" data-act="v3alone">Пока сам</button>', '<button class="sec2 press" data-act="v3alone">Пока только я</button>'),
]
CSS = r"""
/* плёнка — 7 кадров по дням недели, той же высоты, что прежние 13 */
.film{grid-template-columns:repeat(7,1fr)}
.film .fr{aspect-ratio:7/4}
.fr:last-child{outline:none}
/* значки видимости без общих целей ничего не различают */
.p-solo #view .vis:not(.p-keep){display:none}
/* тост — над нижней зоной */
.toast{top:auto !important;bottom:var(--p-tb,146px) !important;transform:translateY(8px)}
.toast.on{transform:none}
/* длинное название цели переносится, а не уходит за край */
.ai,.head h1,.cap .hand{overflow-wrap:anywhere}
/* панель вкладок не просвечивает (WebKit) */
.tabs{background:var(--card) !important}
"""
JS = r"""/* v3 · polish2 — третья волна правок под №3 */
/* 1. «Пришлось взять»: проверка раньше перехвата мотивации (window, фаза захвата) */
window.addEventListener('submit', e => { const f = e.target; if (!f || f.id !== 'inputf' || f.dataset.k !== 'took') return;
  const inp = $('#inputv'), p = P(), w = S.who, r = hSum(inp.value, '3 000'), stop = m => { e.preventDefault(); e.stopImmediatePropagation(); hErr(inp, m); };
  if (r.err) return stop(r.err);
  if (p && r.n > (p.saved[w] || 0)) return stop((p.saved[w] || 0) > 0 ? 'Отложено ' + rubT(p.saved[w] || 0) + ' — больше взять нельзя.' : 'Отложенного пока нет — взять нечего.');
  inp.value = String(r.n); }, true);
/* копейки и номер карты в полях сумм */
const p2Sum0 = hSum;
hSum = function(v, ex){ const s = String(v || '').trim(); P_CARD.lastIndex = 0;
  if (P_CARD.test(s)) { P_CARD.lastIndex = 0; return {err:'Номер карты не нужен — впишите только сумму.'}; } P_CARD.lastIndex = 0;
  const m = parseMoney(s)[0]; if (m && !m.unit && /\d[.,]\d/.test(m.raw) && m.v < 1000) return {err:'Сумма в рублях, без копеек — например, ' + ex + '.'};
  return p2Sum0.apply(this, arguments); };
/* цена больше 50 млн ₽ в форме полей — переспрос */
let p2BigF = null;
const p2ValF0 = HVAL.fieldsGo;
const p2ValFields = () => { const fp = $('#f-price'); if (fp) { const n = hMoney(fp.value); if (n > 5e7 && p2BigF !== n) { p2BigF = n; pErrAt(fp, 'Цена ' + rubT(n) + ' — верно? Нажмите «Посчитать» ещё раз.'); fp.focus(); return false; } }
  return p2ValF0(); };
HVAL.fieldsGo = p2ValFields;
ACT.fieldsGo = function(){ if (!p2ValFields()) return; return hFields0.apply(this, arguments); };
/* приход: номер карты; подсказки называют кнопку как на экране */
const p2Inc0 = HVAL.incomeGo;
HVAL.incomeGo = function(){ const inp = $('#income'); P_CARD.lastIndex = 0; if (inp && P_CARD.test(inp.value || '')) { P_CARD.lastIndex = 0; hErr(inp, 'Номер карты не нужен — уберите его из фразы.'); return false; } P_CARD.lastIndex = 0;
  const ok = p2Inc0(); const e = document.getElementById('income-err'); if (e) e.textContent = e.textContent.replace('нажмите «Посчитать» ещё раз', 'нажмите «Посчитать «Сегодня»» ещё раз'); return ok; };
ACT.incomeGo = function(){ if (!HVAL.incomeGo()) return; return hIncome0.apply(this, arguments); };
/* отзыв пустым не отправляется */
document.addEventListener('submit', e => { if (e.target.id !== 'fbf') return; const t = e.target.querySelector('textarea');
  if (t && !t.value.trim()) { e.preventDefault(); e.stopImmediatePropagation(); if (!t.id) t.id = 'fbtext'; hErr(t, 'Напишите, что не так — хватит пары слов.'); } }, true);
/* отметку «Я отложил(а)» можно отменить в тот же день */
let p2Last = null;
const p2Step0 = step;
step = function(a){ const p = P(), w = S.who, before = p && p.share[w] != null ? (p.saved[w] || 0) : null; const r = p2Step0.apply(this, arguments);
  const q = p && P(p.id); if (q && before != null && (q.saved[w] || 0) > before) p2Last = {id:q.id, w, v:(q.saved[w] || 0) - before, day:S.off}; return r; };
ACT.p2Undo = function(){ const l = p2Last; if (!l) return; const p = P(l.id); if (!p) return; p.saved[l.w] = Math.max(0, (p.saved[l.w] || 0) - l.v);
  const m = S.people[l.w]; m.stepAmt = Math.max(0, (m.stepAmt || 0) - l.v); if (!m.stepAmt) m.stepped = false; if (p.state === 'done') p.state = 'active';
  p2Last = null; render(true); toast('Отметка отменена.'); };
/* 2. фраза: название без «хочу», темп «в месяц», пояснения */
const p2Parse0 = parsePhrase;
parsePhrase = function(t){ const r = p2Parse0(t), s = String(t || '');
  if (r && r.name) { r.name = r.name.replace(/^(?:я\s+)?(?:хочу|хотим|хотелось бы|мечтаю о|нужен|нужна|нужно|нужны|надо|куплю|купить|накопить на|коплю на|копим на)\s+/i, '').trim(); if (r.name) r.name = r.name[0].toUpperCase() + r.name.slice(1); }
  if (r && r.link && r.linkFail && r.name && !/[а-яё]/i.test(r.name)) r.name = 'Товар по ссылке';
  const rm = s.match(/(?:откладываю|отложу|могу откладывать|буду откладывать|откладываем)\s+([\d\s .,]+\s*(?:тыс[а-яё]*|к(?![а-яё])|k\b)?)\s*(?:₽|руб[а-яё.]*)?\s*(?:в|за|каждый|каждую)\s+(месяц|мес\.?|неделю|день)/i);
  if (r && rm) { const v = (parseMoney(rm[1])[0] || {}).v || 0; if (v > 0) { const unit = /^нед/i.test(rm[2]) ? 'неделю' : /^д/i.test(rm[2]) ? 'день' : 'месяц'; r.rate = {v, unit}; if (r.price) r.share = r.price; } }
  return r; };
const p2Ans0 = SCR.answer;
scrAnswer = SCR.answer = function(){ const r = p2Ans0.apply(this, arguments), d = S.draft; if (!d || !r || !r.html || !d.dl) return r;
  const days = Math.max(1, Math.round((d.dl - now()) / DAY)), per = Math.ceil((d.share || 0) / days), echo = /(<p class="ai sm[^"]*">Я понял так:[\s\S]*?<\/p>)/, add = [];
  if (d.rate) { const k = d.rate.unit === 'день' ? 1 : d.rate.unit === 'неделю' ? 7 : 30.4, got = Math.floor(d.rate.v * days / k), need = Math.ceil((d.share || 0) * k / days);
    add.push(got >= (d.share || 0) ? 'Если откладывать ' + rubT(d.rate.v) + ' в ' + d.rate.unit + ', к сроку соберётся ' + rubT(got) + ' — хватит.'
      : 'Если откладывать ' + rubT(d.rate.v) + ' в ' + d.rate.unit + ', к сроку будет ' + rubT(got) + '. Нужно ≈ ' + rubT(need) + ' в ' + d.rate.unit + '.'); }
  if (/(уже\s+(?:есть|отложен[а-яё]*|накоплен[а-яё]*|скопил[а-яё]*)|отложено|накоплено)\s*\d/i.test(d.text || '') && !/Уже отложенное отметьте/.test(r.html)) add.push('Уже отложенное отметьте после сохранения — «Я отложил(а)».');
  if (per > 30000) add.push('Это ≈ ' + rubT(per * 30) + ' в месяц. Можно сдвинуть срок или цену — «Поправить».');
  if (add.length) r.html = r.html.replace(echo, '$1' + add.map(t => '<p class="xs mut">' + t + '</p>').join(''));
  return r; };
/* 3. экран цели: строка о выписке, отмена отметки */
const p2Pur0 = SCR.purchase;
scrPurchase = SCR.purchase = function(){ const r = p2Pur0.apply(this, arguments), p = P(), w = S.who; if (!p || !r || !r.html || p.share[w] == null) return r;
  r.html = r.html.replace(/Подтверждено 0(?:\s|&nbsp;)₽ из ([^<]*?)(\s*<button)/, 'Отмечено $1 — сверю с выпиской, когда загрузите её.$2');
  if (p2Last && p2Last.id === p.id && p2Last.w === w && p2Last.day === S.off)
    r.html = r.html.replace(/(<p class="mut"[^>]*>[^]*?data-out="perday"[^]*?<\/p>)/, '$1<p class="xs mut">Отмечено сегодня ' + rubT(p2Last.v) + ' · <button class="link sm" data-act="p2Undo">Отменить</button></p>');
  return r; };
/* согласие: одна строка видимости, без обрывка */
const p2Cons0 = SCR.consent;
scrConsent = SCR.consent = function(){ const r = p2Cons0.apply(this, arguments); if (!r || !r.html) return r;
  r.html = r.html.replace(/<span class="p-leg">([\s\S]*?) Ваши деньги видите только вы<\/span><span class="p-leg">[\s\S]*?— видят участники<\/span>/, '<span class="p-leg">Ваши деньги видите только вы $1</span>')
    .replace(/<span class="vis/g, '<span class="p-keep vis');
  return r; };
/* 4. значки видимости — только при общих целях; тост — над нижней зоной; альбомная — поток раньше */
const p2Shared = () => (S.purchases || []).some(p => p.state !== 'archived' && (p.group || Object.keys(p.share || {}).filter(k => p.share[k] != null).length > 1 || p.invited));
const p2Render0 = render;
render = function(){ const r = p2Render0.apply(this, arguments);
  try { const app = $('#app'); if (app) app.classList.toggle('p-solo', !p2Shared());
    const bar = $('#bottom .bottom'), tabs = $('#tabs'), H = (app && app.clientHeight) || innerHeight, th = tabs && getComputedStyle(tabs).display !== 'none' ? tabs.offsetHeight : 0;
    if (bar && H < 500 && bar.offsetHeight + th > H * 0.25) { bar.classList.add('p-flow'); bar.style.bottom = ''; $('#view').appendChild(bar); $('#view').style.paddingBottom = (th + 16) + 'px'; }
    const live = $('#bottom .bottom'); if (app) app.style.setProperty('--p-tb', ((live ? live.offsetHeight : 0) + th + 10) + 'px');
  } catch(e) { console.warn('polish2:', e); }
  return r; };
"""
