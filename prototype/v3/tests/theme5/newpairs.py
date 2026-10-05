# Новые пары волны 5 (тема): тот же способ, что design/color_audit.py — WCAG coloraide, APCA apca-w3 через node.
import sys, os, json, subprocess
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "..", "design")))
import color_audit as ca
from coloraide import Color
P = ca.palettes()           # читает сборку v3 (без блока высокого контраста)
HC = {"light": {"line": "#6E6E69", "ink2": "#1A1A19", "input": "#6E6E69"}, "dark": {"line": "#B9BCBA", "ink2": "#F1F0EC", "input": "#B9BCBA"}}
L, D = P["light"], P["dark"]
rows = [
 # (тема, режим, передний, фон, вид, где)
 ("light", "", "input", "card", "ui", "рамка поля .inp на карточке"),
 ("light", "", "input", "bg", "ui", "рамка поля .inp на фоне / в листе"),
 ("light", "", "input", "film", "ui", "рамка поля на плашке"),
 ("dark", "", "input", "card", "ui", "рамка поля .inp на карточке / в листе"),
 ("dark", "", "input", "bg", "ui", "рамка поля .inp на фоне"),
 ("dark", "", "input", "film", "ui", "рамка поля на плашке"),
 ("light", "HC", "input", "card", "ui", "рамка поля, больше контраста"),
 ("light", "HC", "input", "bg", "ui", "рамка поля, больше контраста"),
 ("dark", "HC", "input", "card", "ui", "рамка поля, больше контраста"),
 ("dark", "HC", "input", "bg", "ui", "рамка поля, больше контраста"),
 ("dark", "", "ink", "card", "body", "текст в листе .sheet и в тосте"),
 ("dark", "", "ink2", "card", "body", "вторичный текст в листе"),
 ("dark", "", "accent", "card", "label", "ссылка / кнопка-ссылка в листе"),
 ("dark", "", "line", "bg", "faint", "верхняя граница листа, рамка тоста и полароида на фоне"),
 ("dark", "", "ink", "film", "label", "надпись .go и выбранной .seg на --film"),
 ("dark", "", "input", "card", "ui", "контур .go на карточке"),
 ("dark", "", "input", "bg", "ui", "контур .go на фоне"),
 ("dark", "", "ink2", "film", "ui", "контур выбранной .seg против заливки"),
 ("dark", "", "ink2", "card", "ui", "контур выбранной .seg против невыбранной"),
 ("dark", "HC", "ink2", "card", "ui", "контур выбранной .seg, больше контраста"),
 ("dark", "", "fill", "film", "ui", "заливка прогресса на дорожке (и в больше контраста)"),
 ("dark", "", "fill", "card", "ui", "заливка прогресса на карточке (и в больше контраста)"),
]
def val(theme, mode, k):
    v = P[theme]
    if mode == "HC" and k in HC[theme]: return HC[theme][k]
    return v[k]
flat = [(val(t, m, f), val(t, m, b)) for t, m, f, b, _, _ in rows]
lc = ca.apca_many(flat)
bad = 0
print("| Тема | Режим | Пара | Цвета | Где | Вид | WCAG | порог | APCA Lc | порог | Итог |\n|---|---|---|---|---|---|---|---|---|---|---|")
for (t, m, f, b, kind, where), (cf, cb), l in zip(rows, flat, lc):
    w = Color(cf).contrast(cb, method="wcag21"); tw, ta = ca.TH[kind]
    ok = (tw is None or w >= tw) and abs(l) >= ta; bad += not ok
    print(f"| {t} | {m or 'обычный'} | `{f}` на `{b}` | {cf} / {cb} | {where} | {kind} | {w:.2f} | {tw or '—'} | {abs(l):.1f} | {ta} | {'✅' if ok else '❌'} |")
de = lambda a, b: Color(a).delta_e(b, method="2000")
print(f"\nΔE2000 accent–fill, тёмная, обычный и больше контраста: {de(D['accent'], D['fill']):.1f} ({D['accent']} / {D['fill']}); светлая: {de(L['accent'], L['fill']):.1f}")
print(f"Старое значение в больше контраста, тёмная: accent–#72B7CA ΔE {de(D['accent'], '#72B7CA'):.1f}")
print(f"\nНе прошли: {bad}")
