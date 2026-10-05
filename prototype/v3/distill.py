# -*- coding: utf-8 -*-
"""Бюджет текста ТЗ 5.1 на экранах «Сегодня» и своей цели — модуль интегратора, после motivation.

Скилл: impeccable distill (одна главная задача экрана, лишнее — убрать, спрятать или слить).
Главная задача «Сегодня» — «сколько сегодня на себя» и «влезет ли». Замер — тест mottest.js (слова #view до нижней панели).
  было: «Сегодня» с ответом «влезет ли» 79 слов, экран цели 47 — при бюджете 45.

1. Строка до зарплаты: «до зарплаты 10 октября на себя ≈ 9 864 ₽ · 9 дней» → «≈ 9 864 ₽ до зарплаты»
   (дата зарплаты — на экране цели и в уведомлении, срок в днях — в «Как я посчитал»).
2. Запас (M-B): «Запас 4 000 ₽ в месяц уже вычтен.» → «Запас уже вычтен.» Сумма — строкой в «Как я посчитал».
3. Цена траты в днях цели (M-C) на экране: «На «X» вы откладываете столько за 16 дней.» → «16 дней копилки «X».»
   В боте фраза остаётся полной: бюджет первого экрана к чату не относится.
4. «Напоминания» уходят с «Сегодня» в «Мои данные»: напоминание о зарплате и так приходит уведомлением (M-D),
   настройка — «Мои данные → Напоминания → Подключить». Вход в чат бота был только здесь — кнопка «Открыть» добавлена в «Мои данные».
5. Готовые суммы 450 / 7 000 / 15 000 → подсказка в поле: «например, 7 000 ₽».
6. «Закрыть день»: строка «Остаток — в покупку, день засчитается» убрана; кнопка «1 096 ₽ — в покупку» → «Остаток в покупку»
   (сумма — крупным числом над ней).
8. «или скриншот уведомления» → значок камеры в строке ввода (aria-label «Скриншот уведомления»); «Влезет ли покупка» → «Влезет ли?»;
   «Купил — записать» → «Купил» (пара с «Не буду»).
10. Решение владельца 05.10: «Мои данные» 60 → 45, лист «Где напоминать?» 45 → 30 (по счёту теста), лист о данных 49 → суть ≤ 30 + «Подробнее».
9. После design-review (05.10): «Можно ещё сегодня» → «Ещё можно на себя» (главная ценность словами); сумма вернулась в кнопку
   «1 096 ₽ в покупку»; «Это 16 дней копилки…» (глагол); «Запас вычтен.»; «Проверить» — вторичная (контур); главное число 2,5 rem (DESIGN hero).
7. Экран цели: «С зарплаты 10 октября ≈ 6 600 ₽» → «С зарплаты ≈ 6 600 ₽».
"""
NB = " "

R = [
    ("'до зарплаты ' + dStr(np) + ' на себя ≈" + NB + "' + rubT(untilPay(w)) + ' · ' + daysW(tp)",
     "'≈" + NB + "' + rubT(untilPay(w)) + ' до зарплаты'"),
    ("Запас ${rubT(v3buf(w))} в месяц уже вычтен.", "Запас вычтен."),
    ("'Можно ещё сегодня'} ${vis('me')}</p>", "'Ещё можно на себя'} ${vis('me')}</p>"),
    ("v3dayPrice(w, S.aff, true) : '';", "v3dayPriceShort(w, S.aff) : '';"),
    ('<div class="sec"><h2>Напоминания</h2>${m.bot && !m.botOff ? `<div class="rowl"><span>Пишем в ${m.bot === \'max\' ? \'Max\' : \'Telegram\'}: утром и в день зарплаты</span><button class="chip press" data-go="bot">Открыть чат</button></div>`\n   : `<div class="rowl"><span>${np ? \'Зарплата \' + dStr(np) + \' — напомнить отложить ≈' + NB + '\' + rubT(paydaySum(w)) + \'?\' : \'Напомнить отложить в день зарплаты?\'}</span><button class="chip press" data-sheet="remind">Напоминать</button></div>`}</div>',
     ""),
    ("'<button class=\"chip press sm\" data-act=\"botStop\">Отключить</button>'",
     "'<button class=\"chip press sm\" data-go=\"bot\">Открыть</button><button class=\"chip press sm\" data-act=\"botStop\">Отключить</button>'"),
    ('<form class="field" id="afff"><input class="inp" id="price" inputmode="numeric" placeholder="цена, ₽"',
     '<form class="field" id="afff"><input class="inp" id="price" inputmode="numeric" placeholder="например, 7' + NB + '000 ₽"'),
    ('<div class="chips"><button class="chip press num" data-price="450">450 ₽</button><button class="chip press num" data-price="7000">7 000 ₽</button><button class="chip press num" data-price="15000">15 000 ₽</button></div>',
     ""),
    ('<div class="rowl"><span>Остаток — в покупку, день засчитается</span><button class="chip press" data-act="rest">${rubT(l)} — в покупку</button></div>',
     '<button class="chip press" data-act="rest">${rubT(l)} в покупку</button>'),
    ('<button class="go press">Записать</button></form>\n  <button class="link sm" data-sheet="shot">или скриншот уведомления</button>',
     '<button type="button" class="ico press" data-sheet="shot" aria-label="Скриншот уведомления" title="Скриншот уведомления">${V3_CAM}</button><button class="go press">Записать</button></form>'),
    ("<h2>Влезет ли покупка ${vis('me')}</h2>", "<h2>Влезет ли? ${vis('me')}</h2>"),
    ('<button class="go press">Проверить</button>', '<button class="go go2 press">Проверить</button>'),
    ('data-act="affBuy">Купил — записать</button>', 'data-act="affBuy">Купил</button>'),
    ("'С зарплаты ' + dStr(nextPay(w, now())) + ' ≈" + NB + "<span class=\"num\">'",
     "'С зарплаты ≈" + NB + "<span class=\"num\">'"),
    # 10. Решение владельца 05.10: тексты v2 длиннее бюджета 5.1 — сократить, юртекст листа о данных — под «Подробнее».
    # «Мои данные» 60 → 45 слов
    ("Всё на этой странице ${vis('me')}", "Только для вас ${vis('me')}"),
    ('<span>Покупки, ваши части и отметки «отложил»</span>', '<span>Покупки, части, отметки</span>'),
    ('<span>Приходы и обязательные</span><span class="mut sm">${m.income', '<span>Приходы</span><span class="mut sm">${m.income'),
    ('<span>Сводка выписки (файла нет)</span>', '<span>Сводка выписки</span>'),
    ('<h2>Не потерять данные</h2>', '<h2>Доступ</h2>'),
    ("'Данные живут на этом телефоне'", "'Только на этом телефоне'"),
    ('<span>На главный экран телефона</span>', '<span>На главный экран</span>'),
    ('<div class="sec"><button class="link" data-sheet="policy">Как мы обращаемся с данными</button><br>', '<div class="sec"><button class="link" data-sheet="policy">Как храним данные</button><br>'),
    ('>Удалить все мои данные</button>', '>Удалить мои данные</button>'),
    # лист «Где напоминать?» 45 → 30 (по счёту теста) слов (галочки обе остаются)
    ('<span class="mut sm">траты и «влезет ли» прямо в чате</span>', '<span class="mut sm">траты и «влезет ли» в чате</span>'),
    ('<span>По утрам — сколько сегодня на себя</span>', '<span>Утром — сколько на себя</span>'),
    ('<span>Раз в месяц — обновить выписку</span>', '<span>Ежемесячно — выписка</span>'),
    ('Откроется мессенджер → «Старт». Ссылка одноразовая, действует сутки. Партнёр этот чат не видит.', 'Чат видите только вы.'),
    ('<summary>Без мессенджера — уведомлением на телефоне</summary>', '<summary>Или уведомлением на телефоне</summary>'),
]

CSS = """.ico{flex:none;width:48px;min-height:48px;display:grid;place-items:center;border:0;border-radius:12px;background:var(--film);color:var(--ink)}
.go2{background:transparent;color:var(--ink);box-shadow:inset 0 0 0 1.5px var(--ink)}
[data-out="left-today"]{font-size:calc(2.5rem*var(--d-k))}"""

JS = r"""/* M-C коротко для экрана: та же арифметика, что v3dayPrice */
function v3dayPriceShort(w, v){ const p = active(w).find(q => leftOf(q, w) > 0); if (!p || !(v > 0)) return '';
  const per = perDay(p, w); if (!(per > 0)) return ''; const n = Math.round(v / per);
  return n < 1 ? `Это меньше дневного плана на «${esc(p.name)}».` : `Это ${daysW(n)} копилки «${esc(p.name)}».`; }
/* 10. лист о данных: суть ≤ 30 слов, полный текст (как был) — под «Подробнее»; формулировки — на визу юриста */
const dsPolicy0 = SH.policy;
SH.policy = a => { const full = dsPolicy0(a), btn = (full.match(/<button[^>]*data-close[^>]*>[\s\S]*?<\/button>/) || [''])[0],
    body = full.replace(/<h3[^>]*>[\s\S]*?<\/h3>/, '').replace(btn, '');
  return `<h3 class="disp">Как мы обращаемся с данными</h3><p>GigaChat видит фразы без номеров карт и телефонов.</p><p>Файл выписки удаляется сразу.</p>
  <p>Чужих денег никто не видит. Хранение — в России.</p><details><summary>Подробнее</summary><div class="sm">${body}</div></details>${btn}`; };
const V3_CAM = '<svg width="22" height="22" viewBox="0 0 24 24" aria-hidden="true"><path d="M4 8h3l1.5-2h7L17 8h3v11H4z" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round"/><circle cx="12" cy="13.5" r="3.4" fill="none" stroke="currentColor" stroke-width="1.6"/></svg>';"""
