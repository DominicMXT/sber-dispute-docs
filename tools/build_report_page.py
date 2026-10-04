"""Собирает страницу для копирования отчётов на платформу программы.

Источники — два файла plan/, тексты не переписываются руками:
  plan/2026-10-01_bootcamp-results.md  — карточки 1–12 (поля «- Поле: значение»)
  plan/2026-10-04_weekly-metrics.md    — М-1, М-2, 16, 17 (поля «- **Поле:** значение»)
Выход: plan/2026-10-04_reports-copy.html

Запуск: python tools/build_report_page.py
"""
import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BOOT = ROOT / "plan" / "2026-10-01_bootcamp-results.md"
WEEK = ROOT / "plan" / "2026-10-04_weekly-metrics.md"
OUT = ROOT / "plan" / "2026-10-04_reports-copy.html"

WEEK1 = ("21.09–27.09", "2026-09-21", "2026-09-27")
WEEK2 = ("28.09–04.10", "2026-09-28", "2026-10-04")


def sections(text: str, level: str) -> list[tuple[str, str]]:
    parts = re.split(rf"^{level} (.+)$", text, flags=re.M)
    return [(parts[i].strip(), parts[i + 1]) for i in range(1, len(parts), 2)]


def fields(body: str) -> dict[str, str]:
    out = {}
    for line in body.splitlines():
        m = re.match(r"^- (?:\*\*)?([^:*]+?):(?:\*\*)? (.*)$", line)
        if m:
            out[m.group(1).strip()] = m.group(2).strip()
    return out


def iso(d: str) -> str:
    dd, mm, yy = d.split(".")
    return f"{yy}-{mm}-{dd}"


def link_parts(v: str) -> tuple[str, str]:
    url = re.findall(r"https?://\S+", v)
    if not url:
        return "", v
    note = v.replace(url[0], "").strip(" —;").strip()
    return url[0].rstrip(".,;)"), note


def boot_cards() -> list[dict]:
    text = BOOT.read_text(encoding="utf-8")
    cards = []
    for head, body in sections(text, "###"):
        m = re.match(r"^(\d+)\. (.+)$", head)
        if not m or int(m.group(1)) > 12:
            continue
        f = fields(body)
        url, note = link_parts(f.get("Ссылки", ""))
        cards.append({
            "no": m.group(1), "name": m.group(2), "type": f["Тип"],
            "desc": f["Описание"], "due": f["Согласованный срок"],
            "url": url, "url_note": note if url else f.get("Ссылки", ""),
        })
    return cards


def week_cards() -> list[dict]:
    text = WEEK.read_text(encoding="utf-8")
    cards = []
    for head, body in sections(text, "##") + sections(text, "###"):
        m = re.match(r"^(М-\d|\d+)\.", head)
        f = fields(body)
        if not m or "Название" not in f:
            continue
        no = m.group(1)
        url, note = link_parts(f.get("Ссылка", ""))
        c = {"no": no, "name": f["Название"], "type": f["Тип"], "desc": f["Описание"],
             "due": f["Согласованный срок"], "url": url, "url_note": note}
        if f["Тип"] == "Метрики":
            c["week"] = f["Отчётная неделя"]
            c["weekly"] = [(k, f[k]) for k in ("Активные пользователи", "Вернувшиеся пользователи", "Всего запросов к LLM")]
            c["total"] = [(k, f[k]) for k in ("Всего пользователей", "Проведено кастдевов", "Готовность MVP, %")]
        cards.append(c)
    return cards


def week_of(due: str, w) -> bool:
    return w[1] <= iso(due) <= w[2]


def check(cards, bc, wc):
    errs = []
    for c in cards:
        for k in ("name", "type", "desc", "due"):
            if not c.get(k):
                errs.append(f"{c['no']}: пусто поле {k}")
        if c["type"] == "Метрики":
            nums = [v for _, v in c["weekly"] + c["total"] if v.isdigit()]
            if not nums:
                errs.append(f"{c['no']}: нет ни одного числа")
            a, r = c["weekly"][0][1], c["weekly"][1][1]
            if a.isdigit() and r.isdigit() and int(r) > int(a):
                errs.append(f"{c['no']}: вернувшихся больше активных")
    if len(bc) != 12:
        errs.append(f"карточек 1–12 найдено {len(bc)}")
    return errs


E = html.escape


def field_row(label, value, copy=True, hint=""):
    v = E(value)
    btn = (f'<button class="cp" type="button" data-v="{E(value, quote=True)}" aria-label="Копировать: {E(label)}">Копировать</button>'
           if copy and value else "")
    h = f'<p class="hint">{E(hint)}</p>' if hint else ""
    val = f'<div class="val">{v}</div>' if value else '<div class="val empty">оставить пустым</div>'
    return f'<div class="row"><div class="lab">{E(label)}</div><div class="cell">{val}{h}</div><div class="act">{btn}</div></div>'


def card_html(c):
    rows = [field_row("Название", c["name"]), field_row("Тип", c["type"], hint="выбрать кнопкой в форме"),
            field_row("Описание", c["desc"])]
    alltext = [f"Название: {c['name']}", f"Тип: {c['type']}", f"Описание: {c['desc']}"]
    if c["type"] == "Метрики":
        rows.append(field_row("Отчётная неделя", c["week"], hint="выбрать в списке"))
        alltext.append(f"Отчётная неделя: {c['week']}")
        rows.append('<div class="grp">За неделю</div>')
        for k, v in c["weekly"]:
            rows.append(field_row(k, v))
            alltext.append(f"{k}: {v}")
        rows.append('<div class="grp">Всего — если блок есть в форме</div>')
        for k, v in c["total"]:
            if v.isdigit():
                rows.append(field_row(k, v))
                alltext.append(f"{k}: {v}")
            else:
                rows.append(field_row(k, "", copy=False, hint=v))
                alltext.append(f"{k}: —")
    rows.append(field_row("Согласованный срок", c["due"], hint="выбрать дату в календаре"))
    alltext.append(f"Согласованный срок: {c['due']}")
    if c["url"]:
        rows.append(field_row("Ссылка", c["url"], hint=c["url_note"]))
        alltext.append(f"Ссылка: {c['url']}")
    elif c["url_note"]:
        rows.append(field_row("Ссылка", "", copy=False, hint=c["url_note"]))
    t = "metric" if c["type"] == "Метрики" else "res"
    cid = f"c-{c['no']}"
    return f'''<article class="card {t}" id="{cid}">
<header><span class="no">{E(c["no"])}</span><span class="chip">{E(c["type"])}</span>
<label class="done"><input type="checkbox" id="d-{cid}" data-k="{cid}"> перенесено</label></header>
<h3>{E(c["name"])}</h3>
<div class="rows">{"".join(rows)}</div>
<footer><button class="cp all" type="button" data-v="{E(chr(10).join(alltext), quote=True)}">Копировать карточку целиком</button></footer>
</article>'''


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    bc, wc = boot_cards(), week_cards()
    cards = bc + wc
    errs = check(cards, bc, wc)
    if errs:
        sys.exit("Ошибки:\n" + "\n".join(errs))
    weeks = []
    for w, label in ((WEEK1, "Прошлая неделя"), (WEEK2, "Текущая неделя")):
        metric = [c for c in wc if c["type"] == "Метрики" and c["week"] == w[0]]
        res = [c for c in cards if c["type"] != "Метрики" and week_of(c["due"], w)]
        weeks.append((w, label, metric, res))
    tpl = (Path(__file__).resolve().parent / "report_page_template.html").read_text(encoding="utf-8")
    body = []
    nav = []
    for w, label, metric, res in weeks:
        wid = "w" + w[1].replace("-", "")
        nav.append(f'<a href="#{wid}">{E(w[0])}<small>{1 + len(res)} карточек</small></a>')
        body.append(f'<section class="week" id="{wid}"><div class="wh"><h2>{E(w[0])}</h2><p>{label} · 1 отчёт «Метрики» и {len(res)} результатов</p></div>')
        body.append('<h4 class="sub">Метрики — один отчёт на неделю</h4>' + "".join(card_html(c) for c in metric))
        body.append('<h4 class="sub">Результаты других типов</h4>' + "".join(card_html(c) for c in res))
        body.append("</section>")
    page = tpl.replace("{{NAV}}", "".join(nav)).replace("{{BODY}}", "\n".join(body))
    OUT.write_text(page, encoding="utf-8")
    for w, label, metric, res in weeks:
        print(f"{w[0]}: метрики {len(metric)}, результаты {len(res)} — " + ", ".join(c["no"] for c in res))
    print("Записано:", OUT.relative_to(ROOT))


if __name__ == "__main__":
    main()
