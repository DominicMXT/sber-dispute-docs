# -*- coding: utf-8 -*-
"""Сборка БТ и ТЗ: пересчёт контрольных примеров из прототипа, реестр экранов, PDF.

Запуск из корня репозитория документов:
    python tools/build_docs.py            — обновить блоки АВТО в ТЗ и tz/statement-demo.csv
    python tools/build_docs.py --pdf      — то же + собрать pdf/ (нужны пакет markdown и Edge или Chrome)

Руками в ТЗ правится всё, кроме блоков между <!-- АВТО:… начало --> и <!-- АВТО:… конец -->.
"""
import io, json, os, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TZ = os.path.join(ROOT, "tz", "TZ_finance-assistant.md")
BT = os.path.join(ROOT, "prd", "BT_finance-assistant.md")
PROTO = os.path.join(ROOT, "prototype", "2026-09-24_mvp-prototype.html")
CSV = os.path.join(ROOT, "tz", "statement-demo.csv")

def n(x):
    return "—" if x is None else f"{x:,}".replace(",", " ")

def dt(s):
    if not s: return "—"
    y, m, d = s.split("-"); return f"{d}.{m}.{y}"

def vectors():
    out = subprocess.run(["node", os.path.join(ROOT, "tools", "vectors.js"), CSV], capture_output=True, check=True)
    return json.loads(out.stdout.decode("utf-8"))

# ---------- реестр экранов из карты состояний прототипа ----------
SCREENS = [("consent", "Э-01", "Согласие и обещание о данных"), ("phrase", "Э-02", "Фраза о покупке"), ("clarify", "Э-03", "Уточнение: один вопрос"),
    ("fields", "Э-04", "Поля разбора и запасная форма"), ("answer", "Э-05", "Ответ: сходится или не хватает"), ("share", "Э-06", "Отправить партнёру"),
    ("purchases", "Э-07", "Мои покупки"), ("purchase", "Э-08", "Покупка"), ("pInvite", "Э-09", "Партнёр: приглашение"), ("pUsed", "Э-10", "Партнёр: ссылка уже использована"),
    ("pHome", "Э-11", "Покупка глазами партнёра"), ("source", "Э-12", "Источник денег"), ("income", "Э-13", "Приходы и обязательные траты"), ("today", "Э-14", "Сегодня на себя"),
    ("stmtIntro", "Э-15", "Выписка: что возьму и загрузка"), ("stmtResult", "Э-16", "Разбор выписки и советы"), ("data", "Э-17", "Мои данные"), ("deleted", "Э-18", "Данные удалены")]
SHEETS = [("sh-policy", "Л-01", "Как мы обращаемся с данными"), ("sh-save", "Л-02", "Сколько отложили"), ("sh-change", "Л-03", "Изменить покупку"),
    ("sh-ask", "Л-04", "Ввод: взял из отложенного, моя часть, срок"), ("sh-confirm", "Л-05", "Подтверждение"), ("sh-push", "Л-06", "Напоминать в день зарплаты"),
    ("sh-install", "Л-07", "На главный экран"), ("sh-email", "Л-08", "Сохранить по почте"), ("sh-shot", "Л-09", "Трата скриншотом уведомления"),
    ("sh-fb", "Л-10", "Что не так?"), ("sh-fbok", "Л-11", "Отзыв отправлен")]

def registry():
    h = io.open(PROTO, encoding="utf-8").read()
    blk = h[h.index("const STATES=["):h.index("window.__STATES=")]
    st = []
    for line in blk.split("\n"):
        m = re.match(r" \['(\w+)','([^']*)',\[([^\]]*)\],\[([^\]]*)\]", line)
        if not m: continue
        scr = re.search(r"\},\s*'(\w+)'", line)
        scr = scr.group(1) if scr else ("consent" if m.group(1) == "consent" else "?")
        if "loadStatement" in line: scr = "stmtResult"
        st.append((m.group(1), m.group(2), m.group(3).replace("'", ""), m.group(4), scr, re.findall(r"sheet\('(sh-[\w-]+)'\)", line), "showPush" in line))
    L = ["| Код | Экран | Состояния прототипа (`?s=`) | Т в БТ |", "|---|---|---|---|"]
    used = set()
    for key, code, name in SCREENS:
        rows = [s for s in st if s[4] == key and not s[5]]
        used.update(r[0] for r in rows)
        reqs = sorted({x.strip() for r in rows for x in r[2].split(",") if x.strip()}, key=lambda x: (int(x.rstrip("а")), x))
        L.append(f"| {code} | {name} | " + ", ".join(f"`{r[0]}`" for r in rows) + f" | {', '.join('Т-' + x for x in reqs)} |")
    L += ["", "| Код | Лист | Состояния прототипа (`?s=`) |", "|---|---|---|"]
    for key, code, name in SHEETS:
        rows = [s for s in st if key in s[5]]
        used.update(r[0] for r in rows)
        L.append(f"| {code} | {name} | " + (", ".join(f"`{r[0]}`" for r in rows) or "открывается из экрана") + " |")
    push = [s for s in st if s[6]]; used.update(r[0] for r in push)
    L += ["", "| Код | Уведомление | Состояния прототипа (`?s=`) |", "|---|---|---|",
          "| У-01 | В день зарплаты: «Зарплата пришла — отложите ≈ N ₽» | " + ", ".join(f"`{r[0]}`" for r in push) + " |"]
    left = [s[0] for s in st if s[0] not in used]
    L += ["", f"Всего состояний в прототипе: {len(st)}; в реестре: {len(st) - len(left)}." + (f" Не разнесены: {', '.join(left)}." if left else "")]
    return "\n".join(L), len(st), left

def appendix_b(v):
    L = [f"Все расчёты — на дату **{dt(v['today'])}**, код прототипа, скрипт `tools/vectors.js`. Автотесты подменяют «сегодня» на эту дату.", ""]
    L += ["### Б.1. Разбор фраз", "", "Ожидаемые поля — это спецификация для GigaChat (ПК-03: 18 из 20). В модель уходит уже маскированная фраза.", "",
          "| № | Фраза | Название | Сумма | Срок | Моя часть | Что должно быть |", "|---|---|---|---|---|---|---|"]
    for i, p in enumerate(v["phrases"], 1):
        t = p["t"] if p["t"] == p["masked"] else f"{p['t']}<br>→ в модель: {p['masked']}"
        L.append(f"| {i} | {t} | {p['title']} | {n(p['sum'])} | {dt(p['date'])} | {n(p['share'])} | {p['note'] or 'ответ сразу'} |")
    same = sum(1 for p in v["phrases"] if p["rules_same"])
    L += ["", f"Правила прототипа совпадают с ожидаемым в {same} из {len(v['phrases'])} фраз — это нижняя планка, GigaChat должен дать не меньше 18.", ""]
    L += ["### Б.2. План покупки", "", "Котёл 40 000 ₽ к 15.11.2026, создан 03.10.2026, если не сказано иначе.", "",
          "| Вариант | Моя часть | Партнёр | Отложено | Срок | Дней | Недостача | Перебор | В день | Собрано | По плану |", "|---|---|---|---|---|---|---|---|---|---|---|"]
    for c in v["calc"]:
        L.append(f"| {c['name']} | {n(c['share'])} | {n(c['partner'])} | {n(c['saved'])} | {dt(c['date'])} | {c['days']} | {n(c['gap'])} | {n(c['over'])} | {n(c['per_day'])} | {n(c['collected'])} | {'да' if c['on_plan'] else 'нет'} |")
    d1, d2 = v["daily"]
    L += ["", "### Б.3. «Сегодня на себя»", "", "Приход 80 000 ₽, обязательные 30 000 ₽, дни выплат 10 и 25.", "",
          "| Вариант | Резерв в день | На себя в день | Потрачено сегодня | Осталось сегодня | Ближайшая выплата | Дней до неё |", "|---|---|---|---|---|---|---|",
          f"| Котёл; траты 300 и 450 | {n(d1['reserve'])} | {n(d1['per'])} | {n(d1['spent'])} | {n(d1['left'])} | {dt(d1['next_pay'])} | {d1['to_pay']} |",
          f"| Котёл + диван 30 000 к 31.12 (моя часть 15 000); трата 1 900 — перерасход | {n(d2['reserve'])} | {n(d2['per'])} | {n(d2['spent'])} | {n(d2['left'])} | {dt(d2['next_pay'])} | {d2['to_pay']} |", ""]
    L += ["### Б.4. Сумма напоминания в день зарплаты", "", "| Вариант | Резерв в день | Выплата | Следующая | Дней | Сумма в уведомлении |", "|---|---|---|---|---|---|"]
    for name, p in zip(["Котёл", "Котёл + диван"], v["push"]):
        L.append(f"| {name} | {n(p['reserve'])} | {dt(p['pay'])} | {dt(p['next'])} | {p['days']} | {n(p['sum'])} |")
    s = v["statement"]
    L += ["", "### Б.5. Разбор выписки `tz/statement-demo.csv`", "",
          "Синтетика в формате CSV-выгрузки Т-Банка, реальных данных нет; имя и телефон в переводе вымышлены.", "",
          "| Показатель | Ожидается |", "|---|---|",
          f"| Строк операций в файле | {s['rows_in_file']} |", f"| Учтено операций | {s['operations']} |", f"| Пропущено: отклонённых / дублей | {s['failed']} / {s['dups']} |",
          f"| Скрыто персональных данных | {s['masked']} |", f"| Период | {dt(s['from'])} – {dt(s['to'])}, {s['days']} дней |",
          f"| Приход в месяц, дни выплат | {n(s['income'])}, {' и '.join(str(x) for x in s['pay_days'])} |",
          f"| Обязательные в месяц | {n(s['mandatory'])} ({len(s['recurring'])} регулярных) |",
          f"| Свои переводы | {s['own']['count']} на {n(s['own']['sum'])} |", f"| Возвраты | {s['refunds']['count']} на {n(s['refunds']['sum'])} |",
          f"| Операции в валюте | {s['fx']} |", f"| Пиковый день | {s['peak']['day']}, в {str(s['peak']['ratio']).replace('.', ',')} раза больше среднего |",
          f"| Маскирование | «Перевод по номеру +7 916 000-00-00 Иван И.» → «{s['masked_example']}» |", "",
          "| Регулярный платёж | В месяц | Число |", "|---|---|---|"]
    for r in s["recurring"]: L.append(f"| {r['name']} | {n(r['amount'])} | {r['day']} |")
    L += ["", "Подписки: " + ", ".join(f"{x['name']} {n(x['amount'])}" for x in s["subs"]) + f" — всего {n(sum(x['amount'] for x in s['subs']))} в месяц.", "",
          "Советы для котла к 15.11.2026 (43 дня):", "", "| Совет | В месяц | К сроку |", "|---|---|---|"]
    for t in s["tips"]: L.append(f"| {t['title']} | {n(t['monthly'])} | {n(t['to_deadline'])} |")
    g43, g52 = s["goal43"], s["goal52"]
    L += ["", "| Срок котла | Дней | Недостача | Автоподбор | Наберётся к сроку | Остаток | Главное число |", "|---|---|---|---|---|---|---|",
          f"| {dt(g52['date'])} | {g52['days']} | {n(g52['gap'])} | {len(g52['picked'])} совета | {n(g52['covered'])} | {n(g52['left'])} | «сходится» |",
          f"| {dt(g43['date'])} | {g43['days']} | {n(g43['gap'])} | все {len(g43['picked'])} | {n(g43['covered'])} | {n(g43['left'])} | «не хватает {n(g43['left'])} ₽» + сдвинуть срок |", ""]
    L += ["### Б.6. Ссылки на товар: метки срезаны", "", "| Вход | Сохраняется |", "|---|---|"]
    for l in v["links"]: L.append(f"| `{l['in']}` | `{l['out']}` |")
    t, pr = v["took"], v["price"]
    L += ["", "### Б.7. «Взял из отложенного» и рост цены", "",
          "| Вариант | Было | Стало |", "|---|---|---|",
          f"| Котёл, отложено 9 000, взял 3 000 — в день | {n(t['before'])} | {n(t['after'])} |",
          f"| То же — срок, чтобы остаться на {n(t['before'])} в день | 15.11.2026 | {dt(t['alt'])} |",
          f"| «Плачу сам», цена по ссылке 41 990 → 43 990 — в день | {n(pr['before'])} | {n(pr['after'])} |"]
    return "\n".join(L)

def fill(text, name, body):
    a, b = f"<!-- АВТО:{name} начало -->", f"<!-- АВТО:{name} конец -->"
    i, j = text.index(a) + len(a), text.index(b)
    return text[:i] + "\n" + body + "\n" + text[j:]

CSS = """@page{size:A4;margin:18mm 16mm 18mm 16mm}
body{font-family:"Segoe UI",Arial,sans-serif;font-size:10.5pt;line-height:1.45;color:#111}
h1{font-size:20pt;margin:0 0 6pt}h2{font-size:14pt;margin:16pt 0 6pt;page-break-after:avoid;border-bottom:1px solid #ccc;padding-bottom:2pt}
h3{font-size:11.5pt;margin:12pt 0 4pt;page-break-after:avoid}
table{border-collapse:collapse;width:100%;margin:6pt 0 10pt;font-size:9pt;page-break-inside:auto}tr{page-break-inside:avoid}
th,td{border:1px solid #bbb;padding:3pt 5pt;vertical-align:top;text-align:left}th{background:#f1f3f6}
code{font-family:Consolas,monospace;font-size:8.8pt;background:#f4f4f4;padding:0 2pt;word-break:break-all}
pre{background:#f6f6f6;padding:6pt;font-size:8.8pt;white-space:pre-wrap}hr{border:0;border-top:1px solid #ccc}"""

def pdf(md_path, out_pdf, title):
    import markdown
    body = markdown.markdown(io.open(md_path, encoding="utf-8").read(), extensions=["tables", "fenced_code"])
    html = f"<!doctype html><html lang='ru'><head><meta charset='utf-8'><title>{title}</title><style>{CSS}</style></head><body>{body}</body></html>"
    tmp = out_pdf[:-4] + ".html"
    io.open(tmp, "w", encoding="utf-8").write(html)
    for exe in [r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe", r"C:\Program Files\Google\Chrome\Application\chrome.exe"]:
        if os.path.exists(exe):
            subprocess.run([exe, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", f"--print-to-pdf={out_pdf}", "file:///" + tmp.replace("\\", "/")],
                           capture_output=True, timeout=120)
            break
    os.remove(tmp)
    return os.path.exists(out_pdf)

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    v = vectors()
    reg, nst, left = registry()
    t = io.open(TZ, encoding="utf-8").read()
    t = fill(t, "РЕЕСТР", reg)
    t = fill(t, "Б", appendix_b(v))
    io.open(TZ, "w", encoding="utf-8", newline="\n").write(t)
    print(f"ТЗ: реестр — {nst} состояний, не разнесены: {left or 'нет'}; приложение Б обновлено; {os.path.relpath(CSV, ROOT)} записан")
    if "--pdf" in sys.argv:
        os.makedirs(os.path.join(ROOT, "pdf"), exist_ok=True)
        ver = lambda p: re.search(r"\| Версия документа \| ([\d.]+) \|", io.open(p, encoding="utf-8").read()).group(1)
        for src, name, title in [(TZ, "TZ_finance-assistant", "ТЗ Finance Assistant"), (BT, "BT_finance-assistant", "БТ Finance Assistant")]:
            out = os.path.join(ROOT, "pdf", f"{name}_v{ver(src)}.pdf")
            print(("PDF: " if pdf(src, out, title) else "PDF НЕ СОБРАН: ") + os.path.relpath(out, ROOT))
