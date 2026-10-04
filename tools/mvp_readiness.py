"""Готовность MVP, % — для недельного отчёта «Метрики» на платформе программы.

Определение (решение владельца 04.10.2026): сделанные ФТ релиза Р1 ÷ все ФТ Р1, вниз до целого.
Состав Р1 берётся из ТЗ, раздел 10.1, строка «| Р1 |» — не переписывать руками.
«Сделано» — ФТ, которые команда разработки отметила как принятые на стенде.

Запуск:
  python tools/mvp_readiness.py                  # только состав Р1
  python tools/mvp_readiness.py --done 1-5,7,20  # с отметками команды
"""
import argparse
import re
import sys
from pathlib import Path

TZ = Path(__file__).resolve().parent.parent / "tz" / "TZ_finance-assistant.md"


def expand(spec: str) -> list[int]:
    out = []
    for part in re.split(r"[,\s]+", spec.replace("ФТ-", "").replace("–", "-")):
        if not part:
            continue
        if "-" in part:
            a, b = part.split("-")
            out.extend(range(int(a), int(b) + 1))
        else:
            out.append(int(part))
    return sorted(set(out))


def r1_list() -> list[int]:
    for line in TZ.read_text(encoding="utf-8").splitlines():
        if line.startswith("| Р1 |"):
            cell = line.split("|")[3]
            return expand(cell)
    sys.exit("Строка Р1 в ТЗ 10.1 не найдена")


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser()
    p.add_argument("--done", default="", help="сделанные ФТ: 1-5,7,20")
    args = p.parse_args()
    r1 = r1_list()
    done = [n for n in expand(args.done) if n in r1]
    extra = [n for n in expand(args.done) if n not in r1]
    print(f"ФТ в Р1: {len(r1)}")
    if not args.done:
        print("Отметок команды нет — поле «Готовность MVP, %» оставить пустым (пустое ≠ 0).")
        return
    pct = len(done) * 100 // len(r1)
    print(f"Сделано из Р1: {len(done)}")
    print(f"Готовность MVP, %: {pct}")
    if extra:
        print("Не из Р1, в расчёт не идут: " + ", ".join(f"ФТ-{n:02d}" for n in extra))


if __name__ == "__main__":
    main()
