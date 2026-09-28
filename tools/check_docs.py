# -*- coding: utf-8 -*-
"""Сверка БТ и ТЗ между собой, с покрытием прототипа и с контрольными расчётами. Запуск: python tools/check_docs.py"""
import io, json, os, re, subprocess, sys
sys.stdout.reconfigure(encoding="utf-8")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rd = lambda p: io.open(os.path.join(ROOT, p), encoding="utf-8").read()
bt, tz = rd("prd/BT_finance-assistant.md"), rd("tz/TZ_finance-assistant.md")
COV = os.path.join(ROOT, "prototype", "2026-09-24_coverage.md")  # покрытие прототипа живёт вне git; если его нет — сверка БТ ↔ ТЗ без него
cov = io.open(COV, encoding="utf-8").read() if os.path.exists(COV) else None
fails = []
def check(name, ok, detail=""):
    print(("OK  " if ok else "FAIL"), name, ("— " + str(detail) if detail and not ok else ""))
    if not ok: fails.append(name)

# 1. номера требований и случаев: БТ — основа; покрытие прототипа — если есть на диске
req_bt = re.findall(r"^\| Т-(\d+а?) \|", bt, re.M)
case_bt = sorted(int(x) for x in re.findall(r"^\| (\d+) \|", bt.split("## 7. Пограничные случаи")[1].split("## 8.")[0], re.M))
check(f"БТ: случаи 1–{len(case_bt)} подряд", case_bt == list(range(1, len(case_bt) + 1)), case_bt)
if cov:
    req_cov = re.findall(r"^\| (\d+а?) \|", cov.split("## Требования")[1].split("## Пограничные")[0], re.M)
    case_cov = [int(x) for x in re.findall(r"^\| (\d+) \|", cov.split("## Пограничные случаи")[1].split("## Решения")[0], re.M)]
    check(f"БТ: требования = покрытию прототипа ({len(req_cov)})", sorted(req_bt) == sorted(req_cov), set(req_cov) ^ set(req_bt))
    check(f"БТ: случаи = покрытию прототипа ({len(case_cov)})", case_bt == sorted(case_cov), set(case_cov) ^ set(case_bt))
else:
    print("—   покрытие прототипа не найдено на диске — сверка только БТ ↔ ТЗ")

# 2. ТЗ: все Т и случаи упомянуты
req_tz = set(re.findall(r"(?<!Ф)Т-(\d+а?)\b", tz))
check("ТЗ: упомянуты все требования БТ", set(req_bt) <= req_tz, set(req_bt) - req_tz)
cases_tz = set()
for m in re.finditer(r"случа[йия]\w*\s+((?:\d+(?:[–-]\d+)?(?:,\s*|\s+и\s+)?)+)", tz):
    for part in re.findall(r"\d+(?:[–-]\d+)?", m.group(1)):
        a, _, b = part.replace("–", "-").partition("-"); cases_tz.update(range(int(a), int(b or a) + 1))
check("ТЗ: упомянуты все случаи", set(case_bt) <= cases_tz, sorted(set(case_bt) - cases_tz))

# 3. ФТ: подряд, EARS, ровно в одном релизе, релиз Т в БТ = самый ранний релиз его ФТ
ft = re.findall(r"^- \*\*ФТ-(\d+)\.\*\* (.+)$", tz, re.M)
nums = [int(x) for x, _ in ft]
check(f"ТЗ: ФТ-01…ФТ-{max(nums):02d} подряд, без повторов", nums == list(range(1, max(nums) + 1)))
bad = [x for x, t in ft if not re.match(r"(Система должна|Когда .+?, система должна|Пока .+?, система должна|Если .+?, то система должна|Где .+?, система должна)", t)]
check("ТЗ: все ФТ по шаблонам EARS", not bad, bad)
rel = {}
for r, cell in re.findall(r"^\| (Р\d) \| [^|]+ \| ([^|]+) \|", tz.split("### 10.1.")[1].split("### 10.2.")[0], re.M):
    for part in re.findall(r"\d+(?:–\d+)?", cell.replace("ФТ-", "")):
        a, _, b = part.partition("–")
        for k in range(int(a), int(b or a) + 1): rel.setdefault(k, []).append(r)
dup = {k: v for k, v in rel.items() if len(v) > 1}; miss = [k for k in nums if k not in rel]
check("ТЗ: каждое ФТ ровно в одном релизе (10.1)", not dup and not miss, f"повторы {dup}, без релиза {miss}")
inline = {int(x): r for x, r in re.findall(r"^- \*\*ФТ-(\d+)\.\*\* .*· (Р\d)$", tz, re.M)}
diff = [k for k in nums if inline.get(k) != (rel.get(k) or [None])[0]]
check("ТЗ: релиз в строке ФТ = таблице 10.1", not diff, diff)
bt_rel = dict(re.findall(r"^\| Т-(\d+а?) \|[^|]*\|[^|]*\| (Р\d) \|", bt, re.M))
t_ft = {}
for x, t in ft:
    for tt in re.findall(r"(?<!Ф)Т-(\d+а?)", t): t_ft.setdefault(tt, []).append(inline[int(x)])
diff = {t: (bt_rel.get(t), min(r)) for t, r in t_ft.items() if bt_rel.get(t) != min(r)}
check("релиз Т в БТ = самому раннему релизу его ФТ в ТЗ", not diff, diff)

# 4. ПК ссылаются на существующие ФТ
pk = re.findall(r"^\| ПК-(\d+) \| [^|]+ \| ([^|]+) \|", tz, re.M)
badpk = [p for p, refs in pk for x in re.findall(r"\d+", refs) if refs.strip() != "Р1" and int(x) not in nums]
check(f"ТЗ: {len(pk)} ПК ссылаются на существующие ФТ", not badpk, badpk)

# 5. числа в тексте = контрольным расчётам
v = json.loads(subprocess.run(["node", os.path.join(ROOT, "tools", "vectors.js")], capture_output=True, check=True).stdout.decode("utf-8"))
f = lambda x: f"{x:,}".replace(",", " ")
c0, d0, p0, s = v["calc"][0], v["daily"][0], v["push"][0], v["statement"]
need = [f"{c0['days']} дня", f(c0["gap"]), f"{d0['per']:,}".replace(",", " "), f(p0["sum"]), f"не хватает {s['goal43']['left']} ₽", f"{len(s['goal52']['picked'])} совета"]
body = tz.split("## Приложение Б")[0]
missing = [x for x in need if x not in body]
check("ТЗ: числа разделов 1–10 совпадают с расчётом", not missing, missing)
bnums = [f(s["operations"]), f(s["mandatory"]), f(s["goal52"]["covered"]), f(p0["sum"])]
check("ТЗ: приложение Б свежее (совпадает с пересчётом)", all(x in tz.split("## Приложение Б")[1] for x in bnums), bnums)
check("БТ: пример напоминания = расчёту", f(p0["sum"]) in bt)

# 6. секреты, почты, коды участников интервью
files = ["prd/BT_finance-assistant.md", "tz/TZ_finance-assistant.md", "tz/AGENTS.md", "tz/statement-demo.csv", "tools/build_docs.py", "tools/vectors.js"]
pat = re.compile(r"(api[_-]?key|secret|token|password)\s*[:=]\s*['\"]?[A-Za-z0-9_\-]{12,}|-----BEGIN|[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.(?:ru|com)\b|P0\d-[AB]", re.I)
hits = [(p, m.group(0)) for p in files if os.path.exists(os.path.join(ROOT, p)) for m in pat.finditer(rd(p))]
check(f"секреты и персональные данные: {len(files)} файлов", not hits, hits)

# 7. PDF
try:
    import pypdf
    for name in sorted(x for x in os.listdir(os.path.join(ROOT, "pdf")) if x.endswith(".pdf")):
        r = pypdf.PdfReader(os.path.join(ROOT, "pdf", name)); t = r.pages[0].extract_text()
        check(f"PDF {name}: {len(r.pages)} стр., кириллица читается", len(r.pages) > 3 and ("задание" in t or "требования" in t), t[:80])
except ImportError:
    print("—   PDF не проверен: нет pypdf")
print("\nИТОГ:", "ПРОБЛЕМ НЕТ" if not fails else f"ПРОВАЛЕНО {len(fails)}: " + "; ".join(fails))
