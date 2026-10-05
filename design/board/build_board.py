# -*- coding: utf-8 -*-
"""Доска «Туман» v3: все состояния прототипа в рамках телефона + токены DESIGN.md.
Пишет board/index.html и board/proto.html (копия сборки v3; #код она понимает сама — ядро build_v3.py)."""
import html, io, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
PROTO = r"C:\Users\a.motovilov\Desktop\Работа\Клод\Продукты\Sber500xDisrupt\prototype"

src = io.open(os.path.join(PROTO, "2026-10-04_fog-prototype-v3.html"), encoding="utf-8").read()
assert "decodeURIComponent(location.hash.slice(1))" in src, "сборка v3 без #код — пересобрать build_v3.py"
io.open(os.path.join(HERE, "proto.html"), "w", encoding="utf-8").write(src)

design = io.open(os.path.join(PROTO, "DESIGN.md"), encoding="utf-8").read()
colors = dict(re.findall(r'^  ([a-z-]+): "(#[0-9A-Fa-f]{6})"', design, re.M))

GROUPS = [
    ("Первый вход", "Знакомство, согласие и первая фраза — до регистрации и до партнёра.", [
        ("fresh", "Знакомство, Э-01"), ("consent", "Согласие, Э-01"), ("phrase", "Фраза о покупке, Э-02"),
        ("answer", "Ответ: сходится или нет, Э-05"), ("share", "Отправить партнёру, Э-06"), ("list", "Мои покупки, Э-07")]),
    ("Покупка и фото цели", "Туман на фото проясняется по мере того, как пара откладывает.", [
        ("mid", "Покупка на полпути, Э-08"), ("payday", "День зарплаты"), ("week", "Кадр недели"),
        ("price", "Цена изменилась"), ("done", "Собрано"), ("how", "Лист «Как это работает?», Л-14"),
        ("askq", "Вопрос о прошлой покупке, Л-15"), ("photo", "Фото цели, Л-16"), ("save", "Сколько отложили, Л-02"),
        ("change", "Изменить покупку, Л-03"), ("where", "Где лежат деньги, Л-12"), ("weeksum", "Итоги недели, Л-13")]),
    ("Глазами партнёра", "Партнёр видит покупку и свою часть — без сумм второго.", [
        ("partner", "Партнёр отложил"), ("anya-purchase", "Покупка у партнёра, Э-11"),
        ("anya-where", "Где деньги — у партнёра"), ("used", "Ссылка уже использована, Э-10")]),
    ("Сегодня на себя", "Частая работа: сколько можно потратить сегодня и влезет ли трата.", [
        ("today", "Сегодня, Э-14"), ("income", "Приходы и обязательные, Э-13"), ("source", "Источник денег, Э-12"),
        ("remind", "Напоминать в день зарплаты, Л-06"), ("shot", "Трата скриншотом, Л-09")]),
    ("Выписка", "Выписка вместо подключения к банку: разбор, советы и сверка отметок.", [
        ("stmtIntro", "Что возьму, Э-15"), ("stmtResult", "Разбор и советы, Э-16"), ("recon", "Сверка отметок"),
        ("format", "Чужой формат файла")]),
    ("Бот и мои данные", "Бот в мессенджере без сумм; данные удаляются одной кнопкой.", [
        ("bot", "Чат с ботом, Э-19"), ("botoff", "Бот выключен"), ("data", "Мои данные, Э-17"),
        ("policy", "Как мы обращаемся с данными, Л-01"), ("install", "На главный экран, Л-07"),
        ("email", "Вход: Сбер ID, VK ID, Яндекс ID, Max · Л-08"), ("feedback", "Что не так?, Л-10"), ("deleted", "Данные удалены, Э-18")]),
    ("Р2 · вход и своя цель", "После согласия — пример чужой цели, потом своя; копить можно одному.", [
        ("example", "Пример цели, Э-08"), ("solo", "Своя цель одного"), ("together", "Копить вместе?, Э-06"),
        ("empty", "Пусто: пример и кнопка")]),
    ("Р2 · общая цель", "Вдвоём — только «сходится / нет»; на 3–6 — общий прогресс шагом 10 %. Чужих сумм нет.", [
        ("groupInvite", "Приглашение в общую цель"), ("groupShare", "Позвать: ссылка"), ("group2", "Цель на двоих"),
        ("anya-group2", "На двоих глазами Ани"), ("group2step", "На двоих: второй сделал шаг"), ("group3", "Цель на четверых"), ("anya-group3", "На четверых глазами Ани")]),
    ("Р2 · мотивация", "Поддержка без давления: цена траты в днях цели, срыв без обнуления, счёт недель.", [
        ("dayprice", "«Влезет ли» с ценой в днях"), ("slip", "Взяли из отложенного"), ("slipPropose", "Предложение сдвинуть срок"),
        ("weeks", "Счёт недель по плану"), ("weeksum3", "Итоги недели в группе"), ("nextgoal", "Собрано — следующая цель")]),
    ("Р2 · тема", "«Как в системе», светлая и тёмная — в «Моих данных».", [
        ("themeSet", "Выбор темы")]),
    ("Ссылки и сбои", "Что видит человек, когда что-то пошло не так.", [
        ("linkTwo", "Две цены по ссылке"), ("linkFail", "Страница не открылась"), ("linkNot", "Ссылка не на товар"),
        ("offline", "Нет сети"), ("limit", "Лимит вызовов модели")]),
]
n_states = sum(len(g[2]) for g in GROUPS)

SW = [("background", "Фон"), ("card", "Карточка"), ("foreground", "Текст"), ("muted-foreground", "Второстепенный"),
      ("primary", "Главная кнопка"), ("secondary", "Видят участники"), ("film", "Плёнка фото"), ("stage", "Подложка полосы"),
      ("progress", "Прогресс"), ("positive", "Сходится"), ("warm", "Тёплый"), ("input", "Рамка поля")]

def plural(n, one, few, many):
    n10, n100 = n % 10, n % 100
    return one if n10 == 1 and n100 != 11 else few if 2 <= n10 <= 4 and not 12 <= n100 <= 14 else many

def esc(t): return html.escape(t, quote=True)

def swatches(prefix):
    out = []
    for key, label in SW:
        k = (prefix + key) if prefix else key
        if k not in colors and prefix: k = prefix + key.replace("-foreground", "-foreground")
        val = colors.get(k) or colors.get(key)
        out.append(f'<li><span class="chip" style="background:{val}"></span><b>{esc(label)}</b><code>{val.upper()}</code></li>')
    return "\n".join(out)

cards = []
for title, lead, items in GROUPS:
    tiles = "\n".join(
        f'''<figure class="tile">
  <div class="phone"><iframe title="{esc(name)}" loading="lazy" src="proto.html?clean#{code}" tabindex="-1"></iframe></div>
  <figcaption><span>{esc(name)}</span><a href="proto.html#{code}" target="_blank" rel="noopener">{esc(code)} ↗</a></figcaption>
</figure>''' for code, name in items)
    cards.append(f'''<section class="group" id="g-{len(cards)+1}">
  <header><h2>{esc(title)}</h2><p>{esc(lead)}</p><span class="count">{len(items)}</span></header>
  <div class="tiles">{tiles}</div>
</section>''')

page = f'''<meta charset="utf-8">
<title>Доска «Туман» v3</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Onest:wght@400;500;600&display=swap">
<style>
/* Доска макетов: полоса решений сверху, затем ряды телефонов по сценариям; токены — палитра «Туман» из prototype/DESIGN.md */
:root{{--bg:{colors["background"]};--card:{colors["card"]};--ink:{colors["foreground"]};--ink2:{colors["muted-foreground"]};--line:{colors["border"]};
  --accent:{colors["primary"]};--on-accent:{colors["primary-foreground"]};--soft:{colors["secondary"]};--film:{colors["film"]};--warm:{colors["warm"]};
  --f:'Onest',system-ui,-apple-system,'Segoe UI',sans-serif;--s:.5}}
@media (prefers-color-scheme: dark){{:root:not([data-theme="light"]){{--bg:{colors["dark-background"]};--card:{colors["dark-card"]};--ink:{colors["dark-foreground"]};
  --ink2:{colors["dark-muted-foreground"]};--line:{colors["dark-border"]};--accent:{colors["dark-primary"]};--on-accent:{colors["dark-primary-foreground"]};
  --soft:{colors["dark-secondary"]};--film:{colors["dark-film"]};--warm:{colors["dark-warm"]};color-scheme:dark}}}}
:root[data-theme="dark"]{{--bg:{colors["dark-background"]};--card:{colors["dark-card"]};--ink:{colors["dark-foreground"]};
  --ink2:{colors["dark-muted-foreground"]};--line:{colors["dark-border"]};--accent:{colors["dark-primary"]};--on-accent:{colors["dark-primary-foreground"]};
  --soft:{colors["dark-secondary"]};--film:{colors["dark-film"]};--warm:{colors["dark-warm"]};color-scheme:dark}}
*{{box-sizing:border-box}}
body{{background:var(--bg);color:var(--ink);font:400 1rem/1.45 var(--f);margin:0}}
.wrap{{max-width:1240px;margin:0 auto;padding-inline:clamp(16px,4vw,40px);padding-block:28px 64px;display:grid;gap:40px}}
a{{color:var(--accent)}}
a:focus-visible,button:focus-visible{{outline:2px solid var(--accent);outline-offset:2px;border-radius:6px}}
h1{{font-size:clamp(1.75rem,4vw,2.5rem);font-weight:600;letter-spacing:-.022em;line-height:1.05;margin:0;text-wrap:balance}}
h2{{font-size:1.25rem;font-weight:600;letter-spacing:-.015em;margin:0;text-wrap:balance}}
.eyebrow{{font-size:.8125rem;letter-spacing:.06em;text-transform:uppercase;color:var(--ink2);margin:0 0 8px}}
.lead{{color:var(--ink2);max-width:62ch;margin:10px 0 0}}
.top{{display:grid;gap:20px;grid-template-columns:minmax(0,1.3fr) minmax(0,1fr);align-items:start}}
@media (max-width:820px){{.top{{grid-template-columns:1fr}}}}
.facts{{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px;margin-top:20px}}
.fact{{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:12px 14px;min-width:0}}
.fact span{{display:block;font-size:.8125rem;color:var(--ink2)}}
.fact b{{display:block;font-weight:600;font-size:.9375rem;margin-top:2px}}
.panel{{background:var(--card);border:1px solid var(--line);border-radius:22px;padding:18px 20px;min-width:0}}
.panel h2{{font-size:1rem;margin-bottom:10px}}
.open{{list-style:none;margin:0;padding:0;display:grid;gap:8px}}
.open li{{display:grid;grid-template-columns:auto 1fr;gap:10px;font-size:.9375rem;align-items:baseline}}
.who{{font-size:.75rem;font-weight:600;letter-spacing:.03em;padding:2px 8px;border-radius:999px;background:var(--soft);color:var(--accent);white-space:nowrap}}
.who.w{{background:var(--film);color:var(--warm)}}
.palette{{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:16px}}
@media (max-width:620px){{.palette{{grid-template-columns:1fr}}}}
.sw{{list-style:none;margin:0;padding:0;display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:8px}}
.sw li{{display:grid;grid-template-columns:28px 1fr;grid-template-rows:auto auto;column-gap:10px;font-size:.8125rem;align-items:center}}
.sw .chip{{grid-row:span 2;width:28px;height:28px;border-radius:8px;border:1px solid var(--line)}}
.sw b{{font-weight:500}} .sw code{{font:500 .75rem/1.2 ui-monospace,Consolas,monospace;color:var(--ink2)}}
.theme{{border-radius:16px;padding:14px;border:1px solid var(--line)}}
.theme h3{{font-size:.875rem;font-weight:600;margin:0 0 10px}}
.theme.dark{{background:{colors["dark-background"]};color:{colors["dark-foreground"]};border-color:{colors["dark-border"]}}}
.theme.dark code{{color:{colors["dark-muted-foreground"]}}}
.theme.light{{background:{colors["background"]};color:{colors["foreground"]};border-color:{colors["border"]}}}
.theme.light code{{color:{colors["muted-foreground"]}}}
.group{{display:grid;gap:16px}}
.group header{{display:grid;grid-template-columns:1fr auto;gap:4px 16px;align-items:baseline;border-top:1px solid var(--line);padding-top:18px}}
.group header p{{grid-column:1;margin:0;color:var(--ink2);font-size:.9375rem;max-width:62ch}}
.count{{grid-row:1/span 2;grid-column:2;font-size:2rem;font-weight:600;color:var(--ink2);font-variant-numeric:tabular-nums}}
.tiles{{display:grid;grid-template-columns:repeat(auto-fill,minmax(calc(375px*var(--s) + 24px),1fr));gap:22px 18px}}
.tile{{margin:0;display:grid;gap:8px;justify-items:center;min-width:0}}
.phone{{width:calc(375px*var(--s));height:calc(812px*var(--s));border-radius:calc(44px*var(--s));overflow:hidden;
  background:var(--film);box-shadow:0 0 0 calc(8px*var(--s)) var(--ink),0 10px 24px rgba(0,0,0,.14);position:relative}}
.phone iframe{{width:375px;height:812px;border:0;transform:scale(var(--s));transform-origin:0 0;position:absolute;left:0;top:0;background:var(--card)}}
figcaption{{display:grid;gap:2px;text-align:center;font-size:.8125rem;max-width:calc(375px*var(--s) + 24px)}}
figcaption span{{font-weight:500}}
figcaption a{{font:500 .75rem/1.3 ui-monospace,Consolas,monospace;text-decoration:none}}
figcaption a:hover{{text-decoration:underline}}
.zoom{{display:flex;gap:6px;align-items:center;font-size:.8125rem;color:var(--ink2)}}
.zoom button{{font:inherit;font-weight:500;border:1px solid var(--line);background:var(--card);color:var(--ink);border-radius:999px;padding:6px 12px;min-height:36px;cursor:pointer}}
.zoom button[aria-pressed="true"]{{background:var(--accent);color:var(--on-accent);border-color:var(--accent)}}
.toc{{display:flex;flex-wrap:wrap;gap:8px}}
.toc a{{font-size:.875rem;padding:6px 12px;border-radius:999px;background:var(--soft);text-decoration:none;font-weight:500}}
footer{{color:var(--ink2);font-size:.8125rem;border-top:1px solid var(--line);padding-top:16px}}
</style>

<div class="wrap">
  <div class="top">
    <div>
      <p class="eyebrow">Finance Assistant · v3 после ревью · 05.10.2026</p>
      <h1>Доска «Туман» v3</h1>
      <p class="lead">Все {n_states} {plural(n_states, "состояние", "состояния", "состояний")} прототипа на одной странице. Каждый экран живой: его можно листать и нажимать. Ссылка под экраном открывает его во весь размер.</p>
      <div class="facts">
        <div class="fact"><span>Основа</span><b>shadcn/ui + Tailwind v4</b></div>
        <div class="fact"><span>Шрифт</span><b>Onest</b></div>
        <div class="fact"><span>Контраст</span><b>WCAG AA + APCA</b></div>
        <div class="fact"><span>Объём</span><b>Р1 + Р2: один и группа</b></div>
      </div>
    </div>
    <aside class="panel" aria-label="Открытые вопросы">
      <h2>Что ещё не решено</h2>
      <ul class="open">
        <li><span class="who">фронт</span>На какой библиотеке собран каркас — если не shadcn, переход стоит времени</li>
        <li><span class="who">разработка</span>Будут ли функции Р2 к открытию 08–10.10 и новые сроки Р1 и Р2 — таблица часов к 07.10</li>
        <li><span class="who w">владелец</span>Бот в Max в Р1: без него утреннего числа нет, в Telegram суммы не приходят</li>
        <li><span class="who">юрист</span>Виза на сокращённые листы о данных: Л-01 — 30 слов, полный текст по «Подробнее»</li>
        <li><span class="who w">владелец</span>4 интервью P10–P13 на прототипе: «дни копилки», значки видимости, пример</li>
      </ul>
    </aside>
  </div>

  <section class="panel" aria-labelledby="pal">
    <h2 id="pal">Палитра из DESIGN.md</h2>
    <div class="palette">
      <div class="theme light"><h3>Светлая тема</h3><ul class="sw">{swatches("")}</ul></div>
      <div class="theme dark"><h3>Тёмная тема</h3><ul class="sw">{swatches("dark-")}</ul></div>
    </div>
  </section>

  <nav class="toc" aria-label="Сценарии">{"".join(f'<a href="#g-{i+1}">{esc(g[0])} · {len(g[2])}</a>' for i, g in enumerate(GROUPS))}</nav>
  <div class="zoom" role="group" aria-label="Размер экранов">Размер экранов:
    <button type="button" data-s=".42" aria-pressed="false">мельче</button>
    <button type="button" data-s=".5" aria-pressed="true">обычный</button>
    <button type="button" data-s=".7" aria-pressed="false">крупнее</button>
  </div>

  {"".join(cards)}

  <footer>Эталон — prototype/2026-10-04_fog-prototype-v3.html (v2 + модули prototype/v3, сборка build_v3.py); токены — prototype/DESIGN.md, finance-assistant.tokens.json. Экраны входа Э-17, Э-20, Л-17 и новый Л-08 появятся перед Р2. Фото цели — CC0, Wikimedia Commons.</footer>
</div>
<script>
(function(){{
  var btns=document.querySelectorAll('.zoom button');
  function set(v){{document.documentElement.style.setProperty('--s',v);btns.forEach(function(b){{b.setAttribute('aria-pressed',String(b.dataset.s===v));}});
    try{{localStorage.setItem('board-s',v);}}catch(e){{}}}}
  btns.forEach(function(b){{b.addEventListener('click',function(){{set(b.dataset.s);}});}});
  try{{var v=localStorage.getItem('board-s');if(v)set(v);}}catch(e){{}}
}})();
</script>
'''
io.open(os.path.join(HERE, "index.html"), "w", encoding="utf-8").write(page)
print("состояний:", n_states, "| групп:", len(GROUPS), "| цветов из DESIGN.md:", len(colors))
