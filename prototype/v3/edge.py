# -*- coding: utf-8 -*-
"""Пограничные случаи разбора фразы — модуль интегратора, 05.10.

Карта покрытия v3 (`prototype/2026-10-05_coverage-v3.md`, прогон `tests/cov/covcheck.mjs`) нашла три провала нажатиями:
- случай 5 БТ «Срок в прошлом или сегодня» → «Срок уже прошёл — на какую дату переносим?».
  Было: год в фразе игнорировался («к 1 сентября 2026» → 2027), сегодняшняя дата уезжала на год вперёд.
  Стало: явный год берётся как есть; дата с годом в прошлом и дата «сегодня» без года — вопрос.
  Дата без года раньше сегодня по-прежнему значит следующий год («к 1 сентября» в октябре — следующий сентябрь).
- случай 6 «Доли вместе больше суммы» → «вносите на N больше — уменьшить?». Было: своя цель «Сходится» и план от суммы больше цены.
- случай 22 «Сумма в валюте» → только рубли, вопрос «сколько в рублях?». Было: «1000 долларов» молча становились 1 000 ₽.
Вопросы задаются тем же экраном уточнения (форма `clarf`, ответ обрабатывает ядро v2).
Экран ответа: срок другого года — с годом (`fxDl` из fixes), как в шапке цели и в списке.
Год в фразе убирается до разбора суммы: ядро v2 считало «2026» ценой (находка critique N3, 05.10).
"""
R = []
CSS = ""
JS = r"""const edgeMI = s => ['январ','феврал','март','апрел','ма','июн','июл','август','сентябр','октябр','ноябр','декабр'].findIndex(x => s.toLowerCase().startsWith(x));
const edgeMON = '(январ|феврал|март|апрел|ма[йя]|июн|июл|август|сентябр|октябр|ноябр|декабр)[а-я]*';
const edgeParse0 = parsePhrase;
parsePhrase = function(txt){ const yRe = new RegExp('(к\\s+\\d{1,2}\\s+' + edgeMON + ')\\s+(20\\d\\d)', 'i'), yM = String(txt).match(yRe);
  const r = edgeParse0(yM ? String(txt).replace(yRe, '$1') : txt), s = String(txt);   /* год в фразе — только срок, не сумма (иначе «к 1 сентября 2026» давало цену 2 026 ₽) */
  if (!r.link) {
    const cur = s.match(/\d[\d\s]*(?:[.,]\d+)?\s*(?:тыс\S*\s*)?(?:долл\S*|\$|usd|евро|€|eur|юан\S*|¥|cny)/i) || s.match(/[$€¥]\s*\d[\d\s]*/);
    if (cur) { r.cur = /евро|€|eur/i.test(cur[0]) ? 'евро' : /юан|¥|cny/i.test(cur[0]) ? 'юанях' : 'долларах'; r.curRaw = cur[0].trim(); r.price = null; }
  }
  const today = Math.floor(now() / DAY) * DAY;
  const y = s.match(new RegExp('к\\s+(\\d{1,2})\\s+' + edgeMON + '\\s+(20\\d\\d)', 'i'));
  if (y) { const t = Date.UTC(+y[3], edgeMI(y[2]), +y[1]); if (t <= today) { r.pastDl = t; r.dl = null; } else r.dl = t; }
  else { const m = s.match(new RegExp('к\\s+(\\d{1,2})\\s+' + edgeMON, 'i'));
    if (m) { const t = Date.UTC(new Date(today).getUTCFullYear(), edgeMI(m[2]), +m[1]); if (t === today) { r.pastDl = t; r.dl = null; } } }
  return r; };
const edgeNext0 = draftNext;
draftNext = function(){ const d = S.draft;
  if (d && d.price && d.share != null && d.share > d.price) return go('clarify');
  return edgeNext0(); };
const edgeClar0 = SCR.clarify;
const edgeAsk = (said, q, f, chips, note) => ({notabs:true, html:`${backBtn('phrase')}<p class="ai sm">Я понял так: ${said}</p>
  <h1 class="h1 disp">${q}</h1>${note ? `<p class="mut">${note}</p>` : ''}<form id="clarf" class="field"><input class="inp" id="clar" data-f="${f}" inputmode="${f === 'dl' ? 'text' : 'numeric'}" aria-label="${q}"><button class="go press">Дальше</button></form>
  <div class="chips">${chips.map(c => `<button class="chip press" data-clar="${c}">${c}</button>`).join('')}</div>`});
scrClarify = SCR.clarify = function(){ const d = S.draft;
  if (!d) { S.draft = parsePhrase('Ноутбук к 1 марта'); /* ?s=clarify без черновика — образец вопроса «Сколько стоит?» */ return SCR.clarify(); }
  const nm = esc(d.name || 'покупка');
  if (d.cur && d.price == null)
    return edgeAsk(`${nm} · ${esc(d.curRaw)}`, 'Сколько это в рублях?', 'price', [], 'Считаю только в рублях.');
  if (d.pastDl && d.dl == null) { const yr = new Date(d.pastDl).getUTCFullYear();
    return edgeAsk(`${nm} · к ${dStr(d.pastDl)}${yr !== new Date(now()).getUTCFullYear() ? NB + yr : ''}`, 'Срок уже прошёл — на какую дату переносим?', 'dl', ['к 15 ноября','к 31 декабря','к 1 июня']); }
  if (d.price && d.share != null && d.share > d.price)
    return edgeAsk(`${nm} · ${rubT(d.price)} · ваша часть ${rubT(d.share)}`, `Откладываете на ${rubT(d.share - d.price)} больше цены — уменьшить?`, 'share', [`до ${rubT(d.price)}`]);
  return edgeClar0(); };
const edgeAns0 = SCR.answer;
scrAnswer = SCR.answer = function(){ const r = edgeAns0(), d = S.draft;
  if (d && d.dl && fxDl(d.dl) !== dStr(d.dl)) for (const sp of [NB, '&nbsp;'])   // разметка после v3dom хранит неразрывный пробел как &nbsp;
    r.html = r.html.split('к ' + dStr(d.dl).split(NB).join(sp)).join('к ' + fxDl(d.dl).split(NB).join(sp));
  return r; };"""
