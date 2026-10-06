# -*- coding: utf-8 -*-
"""Прототип «Туман» v3 = v2 + модули правок из prototype/v3/*.py.

Запуск:
  python build_v3.py                 — все модули по порядку → 2026-10-04_fog-prototype-v3.html
  python build_v3.py --only theme    — только ядро + один модуль → v3/_test_theme.html (для агента-владельца)

Модуль — файл v3/<имя>.py с тремя необязательными переменными:
  R   — список пар (старое, новое): каждое «старое» обязано встретиться в тексте ровно один раз, иначе сборка падает;
  CSS — строка, дописывается в конец <style>;
  JS  — строка, вставляется перед блоком «/* ── запуск ── */» (функции уже объявлены, состояние ещё не создано).
Точки расширения ядра (для JS модулей):
  V3_SCEN[код] = () => {...}   — свой сценарий для ?s=<код> и #<код>;
  SCR.<экран> = () => ({html, main, extra, notabs}) — свой экран (SCR — обычный объект, можно дописывать);
  SH.<лист> = arg => '<html>' — свой лист снизу.
Проверка: после сборки скрипт страницы прогоняется `node --check`.
"""
import importlib.util, io, os, re, subprocess, sys, tempfile

sys.stdout.reconfigure(encoding="utf-8")   # консоль Windows cp1251 не печатает «→»

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "2026-10-04_fog-prototype-v2.html")
OUT = os.path.join(HERE, "2026-10-04_fog-prototype-v3.html")
ORDER = ["flow_group", "motivation", "distill", "fixes", "theme", "anim", "palette", "pult", "edge", "harden", "polish", "login", "polish2", "decisions", "mentor1006", "compat"]   # порядок наложения; distill, fixes, palette, pult, edge, harden, polish, login, polish2, decisions, mentor1006, compat — интегратор
DEPS = {"motivation": ["flow_group"]}                    # --only <модуль> подключает и то, на чём он стоит

CORE = [
    # #код работает так же, как ?s=код (для доски и ссылок из артефактов)
    ("const q = new URLSearchParams(location.search).get('s'); if (!q) return;",
     "const q = new URLSearchParams(location.search).get('s') || decodeURIComponent(location.hash.slice(1)); if (!q) return;"),
    # свои сценарии модулей — раньше встроенных
    ("if (SC.includes(k)) scenario(k);",
     "if (V3_SCEN[k]) V3_SCEN[k](); else if (SC.includes(k)) scenario(k);"),
    ("<title>v2 · ", "<title>v3 · "),
]
CORE_JS = "const V3_SCEN = {};\n"


def apply(s, pairs, where):
    for a, b in pairs:
        n = s.count(a)
        if n != 1:
            sys.exit(f"[{where}] «старое» встречается {n} раз (нужно 1): {a[:100]!r}")
        s = s.replace(a, b)
    return s


def load(name):
    p = os.path.join(HERE, "v3", name + ".py")
    if not os.path.exists(p):
        return None
    spec = importlib.util.spec_from_file_location("v3_" + name, p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def build(names, out):
    s = io.open(SRC, encoding="utf-8").read()
    s = apply(s, CORE, "ядро")
    marker = "/* ── запуск ── */"
    s = s.replace(marker, CORE_JS + marker, 1)
    stats = []
    for name in names:
        m = load(name)
        if m is None:
            stats.append(f"{name}: нет файла — пропущен")
            continue
        R, CSS, JS = getattr(m, "R", []), getattr(m, "CSS", ""), getattr(m, "JS", "")
        s = apply(s, R, name)
        if CSS:
            s = s.replace("</style>", f"/* v3 · {name} */\n{CSS}\n</style>", 1)
        if JS:
            s = s.replace(marker, f"/* v3 · {name} */\n{JS}\n{marker}", 1)
        stats.append(f"{name}: замен {len(R)}, CSS {len(CSS)} знаков, JS {len(JS)} знаков")
    io.open(out, "w", encoding="utf-8").write(s)
    # синтаксис скрипта страницы
    js = s[s.index("<script>") + 8: s.rindex("</script>")]
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False, encoding="utf-8") as f:
        f.write(js); tmp = f.name
    r = subprocess.run(["node", "--check", tmp], capture_output=True, text=True)
    os.unlink(tmp)
    print("\n".join(stats))
    print("→", os.path.relpath(out, HERE), "|", len(s), "знаков |", "node --check: OK" if r.returncode == 0 else "node --check: ОШИБКА\n" + r.stderr[-1500:])
    if r.returncode != 0:
        sys.exit(1)


if __name__ == "__main__":
    if "--only" in sys.argv:
        name = sys.argv[sys.argv.index("--only") + 1]
        build(DEPS.get(name, []) + [name], os.path.join(HERE, "v3", f"_test_{name}.html"))
    else:
        build(ORDER, OUT)
