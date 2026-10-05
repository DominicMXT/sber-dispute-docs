import os
# Подбор тёмного --input: только светлота OKLCH от #70777A, оттенок и насыщенность держатся; цель — WCAG ≥3 и APCA Lc ≥30 на bg, card, film
import sys; sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "..", "design")))
import color_audit as ca
from coloraide import Color
base = Color("#70777A").convert("oklch"); L0, C0, H0 = base["lightness"], base["chroma"], base["hue"]
BG = {"bg": "#121415", "card": "#1D2022", "film": "#2A2E31"}
cands = []
for i in range(0, 13):
    L = round(L0 + i * 0.01, 3); hx = Color("oklch", [L, C0, H0]).convert("srgb").fit("srgb").to_string(hex=True).upper()
    cands.append((L, hx))
flat = [(hx, b) for _, hx in cands for b in BG.values()]
lc = ca.apca_many(flat); k = 0
print(f"основа #70777A: L{L0:.3f} C{C0:.4f} H{H0:.0f}")
for L, hx in cands:
    cells = []; ok = True
    for name, b in BG.items():
        w = Color(hx).contrast(b, method="wcag21"); l = abs(lc[k]); k += 1; ok &= w >= 3 and l >= 30
        cells.append(f"{name} {w:.2f}/Lc{l:.1f}")
    o = Color(hx).convert("oklch")
    print(f"L{L:.3f} {hx} (C{o['chroma']:.4f} H{o['hue']:.0f}): " + " · ".join(cells) + ("  ✅" if ok else ""))
