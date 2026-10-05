"""Прототип «Туман» v2: меньше текста на экране (impeccable distill, 04.10.2026).

Бюджет — из открытых норм: первый экран ≤ 45 слов (NN/g: читают 20–28 % слов, 57 % времени — первый экран),
предложение ≤ 15 слов (GOV.UK: 25 — предел, 14 — понимание > 90 %), лист ≤ 30 слов, кнопка — глагол + объект
(Material 3, Apple HIG). Смысл не удаляется: правила и подробности уходят в листы и «Подробнее».
Вход: 2026-10-03_fog-prototype.html · выход: 2026-10-04_fog-prototype-v2.html. Каждая замена обязана сработать.
"""
from pathlib import Path

HERE = Path(__file__).parent
SRC, OUT = HERE / "2026-10-03_fog-prototype.html", HERE / "2026-10-04_fog-prototype-v2.html"
s = SRC.read_text(encoding="utf-8")

LOCK = '<svg width="13" height="13" viewBox="0 0 16 16" aria-hidden="true"><rect x="3" y="7" width="10" height="7" rx="1.5" fill="none" stroke="currentColor" stroke-width="1.5"/><path d="M5.5 7V5a2.5 2.5 0 0 1 5 0v2" fill="none" stroke="currentColor" stroke-width="1.5"/></svg>'
TWO = '<svg width="15" height="13" viewBox="0 0 18 16" aria-hidden="true"><circle cx="6" cy="5" r="2.5" fill="none" stroke="currentColor" stroke-width="1.5"/><circle cx="12.5" cy="5.5" r="2" fill="none" stroke="currentColor" stroke-width="1.5"/><path d="M1.5 14c.6-2.8 2.4-4 4.5-4s3.9 1.2 4.5 4M10.5 10.3c.6-.2 1.3-.3 2-.3 1.8 0 3.3 1 3.8 3.5" fill="none" stroke="currentColor" stroke-width="1.5"/></svg>'

R = [
 # пометки видимости — значком с подписью для экранного чтеца
 ("const vis = k => k === 'all' ? '<span class=\"vis all\">видит партнёр</span>' : '<span class=\"vis me\">видно только вам</span>';",
  "const vis = k => k === 'all' ? '<span class=\"vis all\" role=\"img\" aria-label=\"видит партнёр\" title=\"видит партнёр\">" + TWO + "</span>' : '<span class=\"vis me\" role=\"img\" aria-label=\"видно только вам\" title=\"видно только вам\">" + LOCK + "</span>';"),
 (".vis{display:inline-block;font-size:0.8125rem;border-radius:10px;padding:1px 8px;margin-left:6px;vertical-align:middle;white-space:nowrap}",
  ".vis{display:inline-flex;align-items:center;justify-content:center;width:24px;height:24px;border-radius:12px;margin-left:6px;vertical-align:middle}"),
 # экран покупки
 ("<p class=\"mut\" style=\"margin:0\">${paydaySum(w) ? 'С зарплаты ' + dStr(nextPay(w, now())) + ' — отложить ≈ <span class=\"num\">' + rub(paydaySum(w)) + '</span>. ' : ''}${plan ? 'Вы по плану' : 'Чтобы догнать план'}: это <span class=\"num\" data-out=\"perday\">${rub(mine)}</span> в день</p>",
  "<p class=\"mut\" style=\"margin:0\">${paydaySum(w) ? 'С зарплаты ' + dStr(nextPay(w, now())) + ' ≈ <span class=\"num\">' + rub(paydaySum(w)) + '</span> · ' : ''}${plan ? 'по плану' : 'догнать план'}: <span class=\"num\" data-out=\"perday\">${rub(mine)}</span> в день</p>"),
 ("<p class=\"xs mut\" style=\"margin:6px 0 0\">${(p.saved[w] || 0) === 0 ? 'Отметок пока нет.' : ((p.conf || {})[w] || 0) >= p.saved[w] ? 'Все отметки подтверждены выпиской.' : ((p.conf || {})[w] || 0) > 0 ? 'Чётко — подтверждено выпиской: ' + rubT(p.conf[w]) + '. В лёгкой дымке — по вашим отметкам: ' + rubT(p.saved[w] - p.conf[w]) + '.' : 'Пока по вашим отметкам — в лёгкой дымке. Подтвердится, когда загрузите выписку.'}</p>`}",
  "<p class=\"xs mut\" style=\"margin:6px 0 0\">${(p.saved[w] || 0) === 0 ? 'Отметок пока нет' : ((p.conf || {})[w] || 0) >= p.saved[w] ? 'Всё подтверждено выпиской' : 'Подтверждено ' + rubT((p.conf || {})[w] || 0) + ' из ' + rubT(p.saved[w])} <button class=\"link sm\" data-sheet=\"how\" style=\"min-height:0\" aria-label=\"Как читать фото и неделю\">Как это работает?</button></p>`}"),
 ("<div class=\"filmlab\"><span>${Math.ceil(daysTo(p) / 7)} ${plural(Math.ceil(daysTo(p) / 7), 'неделя', 'недели', 'недель')} до покупки</span><span>эта неделя: ${steps} из 7</span></div>",
  "<div class=\"filmlab\"><span>Неделя: ${steps} из 7</span><span>ещё ${Math.ceil(daysTo(p) / 7)} ${plural(Math.ceil(daysTo(p) / 7), 'неделя', 'недели', 'недель')}</span></div>"),
 ("${wk.html}<p class=\"xs mut\" style=\"margin-top:6px\">День засчитан, когда вы отложили с зарплаты или отправили в покупку остаток дня. Кадр недели проявится при 5 днях из 7. Пропуск ничего не отнимает. Точка — день, который засчитан у обоих.</p>",
  "${wk.html}"),
 ("<details><summary>Подробнее: цена, части, где лежат деньги</summary>", "<details><summary>Цена, части, где деньги</summary>"),
 ("${ask ? `<div class=\"sec\"><h2>Один вопрос, один раз</h2><p>Как вы решали последнюю крупную покупку?</p><div class=\"chips\">${['Обсудили и скинулись','Купил(а) сам(а)','Взяли в рассрочку','Долго откладывали','Спорили'].map(a => `<button class=\"chip press sm\" data-act=\"asked\">${a}</button>`).join('')}<button class=\"chip press sm\" data-act=\"asked\">Пропустить</button></div></div>` : ''}`,",
  "${ask ? `<button class=\"rowl press askrow\" data-sheet=\"askq\"><span>Один вопрос о вашей прошлой покупке</span><span aria-hidden=\"true\">›</span></button>` : ''}`,"),
 # «Сегодня»
 ("<button class=\"link sm\" data-sheet=\"shot\">Или пришлите скриншот уведомления банка</button>",
  "<button class=\"link sm\" data-sheet=\"shot\">или скриншот уведомления</button>"),
 ("<div class=\"rowl\"><span>Вечером остаток дня можно отправить в покупку — туман отступит сверх плана, день засчитается.</span><button class=\"chip press\" data-act=\"rest\">${rubT(l)} — в покупку</button></div>",
  "<div class=\"rowl\"><span>Остаток — в покупку, день засчитается</span><button class=\"chip press\" data-act=\"rest\">${rubT(l)} — в покупку</button></div>"),
 # ввод фразы
 ("<h1 class=\"h1 disp\">Что покупаете?</h1><p class=\"mut\">Обычными словами, как написали бы партнёру, — или вставьте ссылку на товар.</p>",
  "<h1 class=\"h1 disp\">Что покупаете?</h1><p class=\"mut\">Как написали бы партнёру. Или ссылка на товар.</p>"),
 ("<p class=\"xs mut\" style=\"margin-top:6px\">Хватит суммы и срока — номера карт и имена не нужны. Можно надиктовать: микрофон на клавиатуре.</p>",
  "<p class=\"xs mut\" style=\"margin-top:6px\">Хватит суммы и срока. Номера карт не нужны.</p>"),
 ("<p class=\"lbl\" style=\"margin-top:14px\">Примеры</p><div class=\"chips\">\n  ${['Диван 180 тысяч к 31 декабря, я могу 90','Отпуск 120 тысяч к 1 июня, я могу 70','Котёл 40 тысяч, я могу 25','https://divan.example/oslo к 31 декабря, я могу 90','https://shop.example/tv-two к 1 марта, я могу 30','https://shop.example/fail/Робот-пылесос к 1 декабря, я могу 20','https://blog.example/notproduct к 1 декабря'].map(e => `<button class=\"chip press sm\" data-ex=\"${esc(e)}\">${esc(e)}</button>`).join('')}</div>`,",
  "<p class=\"lbl\" style=\"margin-top:14px\">Примеры</p><div class=\"chips\">\n  ${['Диван 180 тысяч к 31 декабря, я могу 90','Отпуск 120 тысяч к 1 июня, я могу 70','Котёл 40 тысяч, я могу 25'].map(e => `<button class=\"chip press sm\" data-ex=\"${esc(e)}\">${esc(e)}</button>`).join('')}</div>\n  <details><summary>Примеры со ссылкой</summary><div class=\"chips\">${['https://divan.example/oslo к 31 декабря, я могу 90','https://shop.example/tv-two к 1 марта, я могу 30','https://shop.example/fail/Робот-пылесос к 1 декабря, я могу 20','https://blog.example/notproduct к 1 декабря'].map(e => `<button class=\"chip press sm\" data-ex=\"${esc(e)}\">${esc(e)}</button>`).join('')}</div></details>`,"),
 # ответ на фразу
 ("<div class=\"sec\"><div class=\"rowl\"><span>Стоит</span><b class=\"num\">${rubT(d.price)}</b></div><div class=\"rowl\"><span>Вносите вы</span><b class=\"num\">${rubT(d.share)}</b></div>\n  <div class=\"rowl\"><span>Ваши ${rubT(d.share)} будут к сроку, если откладывать</span><b class=\"num\"><span data-out=\"new-perday\">${rubT(per)}</span> в день</b></div>\n  <div class=\"rowl\"><span>Это в месяц</span><b class=\"num\">≈ ${rubT(per * 30)}</b></div>",
  "<div class=\"sec\"><div class=\"rowl\"><span>Откладывать</span><b class=\"num\"><span data-out=\"new-perday\">${rubT(per)}</span> в день · ≈ ${rubT(per * 30)} в месяц</b></div>"),
 ("<div class=\"rowl\"><span>Если партнёр внесёт ${rubT(gap)} — сходится</span></div>\n  <div class=\"rowl\"><span>Закрыть самим: ещё ${rubT(Math.ceil(gap / days))} в день</span></div>\n  <div class=\"rowl\"><span>Сдвинуть срок на 30 дней: ${rubT(Math.ceil(d.price / d2))} в день</span></div></div>",
  "<div class=\"rowl\"><span>Партнёр внесёт ${rubT(gap)} — сходится</span></div>\n  <details><summary>Ещё варианты</summary><div class=\"rowl\"><span>Самим: ещё ${rubT(Math.ceil(gap / days))} в день</span></div>\n  <div class=\"rowl\"><span>Срок +30 дней: ${rubT(Math.ceil(d.price / d2))} в день</span></div></details></div>"),
 # результат выписки
 ("${backBtn('today', 'Сегодня')}<p class=\"xs mut\">по выписке с 1 июля по 30 сентября · обновить после зарплаты 10 октября ${vis('me')}</p>",
  "${backBtn('today', 'Сегодня')}<p class=\"xs mut\">Выписка 1 июля – 30 сентября ${vis('me')}</p>"),
 ("<div class=\"sec\"><h2>Подписки</h2>", "<div class=\"sec\"><h2>Нужен ваш ответ</h2><div class=\"rowl\" style=\"flex-wrap:wrap\"><span>От [человек]: 12 000 ₽ — ${S.petr ? S.petr : 'это доход?'}</span>${S.petr ? '' : '<span class=\"kb\" style=\"margin:0\"><button data-petr=\"вернули долг\">Вернули долг</button><button data-petr=\"партнёр скинулся\">Партнёр скинулся</button><button data-petr=\"это доход\">Это доход</button></span>'}</div></div>\n  <details><summary>Подробности выписки</summary><div class=\"sec\"><h2>Подписки</h2>"),
 ("   <div class=\"rowl\" style=\"flex-wrap:wrap\"><span>От [человек]: 12 000 ₽ — ${S.petr ? S.petr : 'это доход?'}</span>${S.petr ? '' : '<span class=\"kb\" style=\"margin:0\"><button data-petr=\"вернули долг\">Вернули долг</button><button data-petr=\"партнёр скинулся\">Партнёр скинулся</button><button data-petr=\"это доход\">Это доход</button></span>'}</div>\n   <p class=\"xs mut\" style=\"margin-top:6px\">Скрыто номеров карт, телефонов и имён: 14. Возвратов: 2. Дублей: 1.</p></div>`, main:['Считать «Сегодня» по выписке','stmtUse']}; }",
  "   <p class=\"xs mut\" style=\"margin-top:6px\">Скрыто номеров карт, телефонов и имён: 14. Возвратов: 2. Дублей: 1. Обновить — после зарплаты 10 октября.</p></div></details>`, main:['Считать «Сегодня» по выписке','stmtUse']}; }"),
 # новые листы: «Как это работает» и вопрос о прошлой покупке; действие закрытия
 ("const SH = {", "const SH = {\n  how: () => `<h3 class=\"disp\">Как читать фото</h3><p class=\"sm\"><b>Чётко</b> — подтверждено выпиской. <b>Дымка</b> — по вашим отметкам. <b>Туман</b> — ещё впереди.</p><p class=\"sm\">День засчитан, если отложили с зарплаты или отправили остаток дня. Кадр недели — 5 дней из 7. Пропуск ничего не отнимает. Точка — день у обоих.</p><button class=\"sec2 press\" data-act=\"closeS\">Понятно</button>`,\n  askq: () => `<h3 class=\"disp\">Как вы решали последнюю крупную покупку?</h3><div class=\"chips\">${['Обсудили и скинулись','Купил(а) сам(а)','Взяли в рассрочку','Долго откладывали','Спорили'].map(a => `<button class=\"chip press sm\" data-act=\"askedS\">${a}</button>`).join('')}<button class=\"chip press sm\" data-act=\"askedS\">Пропустить</button></div>`,"),
 ("  asked(){ me().asked = true; render(true); },", "  asked(){ me().asked = true; render(true); }, askedS(){ me().asked = true; closeSheet(); render(true); }, closeS(){ closeSheet(); },"),
 # второй проход: вход в выписку, бот, политика, «Собрано», ответ
 ("<div class=\"sec\"><h2>Что возьму</h2><p>Дату, сумму, описание и категорию каждой операции.</p><h2>Что скрою</h2><p>Номера карт, телефоны, имена в переводах.</p><h2>Что не храню</h2><p>Сам файл и снимки: удаляю сразу после разбора. Партнёр не увидит ничего.</p></div>",
  "<div class=\"sec\"><div class=\"rowl\"><span>Возьму</span><b>дату, сумму, описание</b></div><div class=\"rowl\"><span>Скрою</span><b>карты, телефоны, имена</b></div><div class=\"rowl\"><span>Файл</span><b>удалю сразу</b></div></div>"),
 ("<div class=\"note sm\"><b>Какую выписку:</b> свою, за 2–3 месяца. Выписку партнёра не загружайте: это его данные.</div>\n  <div class=\"note sm\"><b>Про снимки экрана:</b> снимок распознаю на своём сервере в России; имена, номера карт и телефонов скрываю до GigaChat; сам снимок удаляю сразу после распознавания.</div>",
  "<div class=\"note sm\">Свою, за 2–3 месяца. Выписку партнёра не загружайте: это его данные.</div>\n  <details><summary>Про снимки экрана</summary><p class=\"sm\">Распознаю на своём сервере в России. Карты, телефоны и имена скрываю до GigaChat. Снимок удаляю сразу.</p></details>"),
 ("[{b:'Подключено. Утром пишу, сколько сегодня на себя, в день зарплаты — сколько отложить. Траты пишите прямо сюда: «кофе 300». Партнёр этот чат не видит.'},",
  "[{b:'Подключено. Утром — сколько на себя, в день зарплаты — сколько отложить. Траты пишите сюда: «кофе 300». Партнёр чат не видит.'},"),
 ("<p>Аккаунт привязан к этому устройству: без телефона и почты.</p><p>Фразы разбирает GigaChat. До отправки номера карт и телефонов заменяются на метки.</p><p>Файл выписки и снимки удаляются сразу после разбора; хранится только сводка.</p><p>Партнёр видит покупку, срок, цену и свою часть. Ваши остатки, траты и доходы — нет.</p><p>Данные хранятся в России 12 месяцев с последнего входа. Удалить всё можно в «Моих данных».</p>",
  "<p>Аккаунт — на этом устройстве, без телефона и почты.</p><p>GigaChat видит фразы без номеров карт и телефонов.</p><p>Файл выписки удаляется сразу, остаётся сводка.</p><p>Партнёр видит покупку и свою часть, но не ваши деньги.</p><p>Хранение — в России, 12 месяцев. Удалить всё — в «Моих данных».</p>"),
 ("<div class=\"note\">Деньги лежат у вас. Собрать их в одном месте можно копилкой или сбором в своём банке — мы деньги не храним и не переводим.</div>",
  "<div class=\"note\">Деньги у вас. Собрать их можно копилкой или сбором в своём банке. Мы деньги не храним.</div>"),
 ("<p class=\"lbl\">Чтобы «${esc(d.name)}» сошлось к ${dStr(d.dl)}, найти ещё</p>", "<p class=\"lbl\">Не хватает к ${dStr(d.dl)}</p>"),
 # шрифт по DESIGN.md (решение владельца 04.10): Onest по умолчанию, SB Sans — после подтверждения лицензии
 ('<link rel="stylesheet" href="https://cdn-app.sberdevices.ru/shared-static/0.0.0/styles/SBSansText.0.2.0.css">', ''),
 ('<link rel="stylesheet" href="https://cdn-app.sberdevices.ru/shared-static/0.0.0/styles/SBSansDisplay.0.2.0.css">', ''),
 ("--f-text:'SB Sans Text',system-ui,-apple-system,'Segoe UI',sans-serif", "--f-text:'Onest',system-ui,-apple-system,'Segoe UI',sans-serif"),
 ("--f-disp:'SB Sans Display','SB Sans Text',system-ui,sans-serif", "--f-disp:'Onest',system-ui,sans-serif"),
 ('data-font="sber">Сбер</button>', 'data-font="sber">Onest</button>'),
 # служебные строки
 ("<title>", "<title>v2 · "),
]
NBSP = " "
for a, b in R:
    if a not in s and a.replace("≈ ", "≈" + NBSP) in s:
        a, b = a.replace("≈ ", "≈" + NBSP), b.replace("≈ ", "≈" + NBSP)
    if a not in s:
        raise SystemExit("не найдено: " + a[:90])
    s = s.replace(a, b, 1)
css = ".askrow{width:100%;justify-content:space-between;background:none;border:0;border-top:1px solid var(--line);padding:14px 0;font:inherit;color:inherit;text-align:left;cursor:pointer}\n"
s = s.replace("</style>", css + "</style>", 1)
OUT.write_text(s, encoding="utf-8")
print("замен:", len(R), "→", OUT.name)
