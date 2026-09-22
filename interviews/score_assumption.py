# -*- coding: utf-8 -*-
"""Проверка допущения №1: пары обмениваются информацией о деньгах ежедневно.

Правила зафиксированы ДО интервью, чтобы результат нельзя было подогнать под ожидание:

  * день «денежный», если в переписке пары было хотя бы одно сообщение про деньги —
    сумму, трату, перевод или решение, тратить ли («купи хлеб» не считается);
  * пара «ежедневная», если денежных дней не меньше 5 из 7
    (не 7 из 7: в выходные пары вместе и говорят вслух, а не пишут);
  * если опрошены оба партнёра, берётся МЕНЬШЕЕ из двух чисел —
    консервативно, против самоподтверждения;
  * допущение живо, если ежедневных пар не меньше 60% при выборке от 10 пар;
  * досрочно можно только ОПРОВЕРГНУТЬ — когда порог уже недостижим;
    подтверждать досрочно нельзя;
  * разговоры вслух считаются отдельно и в прохождение НЕ засчитываются;
  * колонка relation (друг / родственник / знакомый / незнакомый) на вердикт не влияет:
    счёт сообщений — поведенческий факт. Но если больше половины пар близкие,
    «живо» помечается как ПРЕДВАРИТЕЛЬНОЕ: близкие скорее завысят частоту, чем занизят.
    «Опровергнуто» на близких не помечается — на них опровержение только сильнее.
    Продажа у близких показывается отдельно: «запишусь» от друга — поддержка, а не спрос.

Запуск:
    python score_assumption.py money-days-log.csv
"""
import csv
import io
import math
import sys

DAY_THRESHOLD = 5    # денежных дней из 7, чтобы пара считалась ежедневной
PAIR_SHARE = 0.6     # доля ежедневных пар, при которой допущение живо
MIN_PAIRS = 10       # плановая выборка; окончательный вердикт — только от неё
DAYS = ["d1", "d2", "d3", "d4", "d5", "d6", "d7"]
YES = {"да", "yes", "y", "1", "true", "+"}
CLOSE = {"друг", "подруга", "друзья", "родственник", "родственница", "родственники",
         "родня", "близкие", "близкий", "близкая"}


def is_yes(value):
    return str(value or "").strip().lower() in YES


def is_close(value):
    return str(value or "").strip().lower() in CLOSE


def load(path):
    raw = io.open(path, encoding="utf-8-sig").read()
    lines = raw.splitlines()
    if not lines:
        return []
    header = lines[0]
    delimiter = ";" if header.count(";") >= header.count(",") else ","
    reader = csv.DictReader(io.StringIO(raw), delimiter=delimiter)
    return [r for r in reader if (r.get("couple_id") or "").strip()]


def money_days(row):
    days = 0
    for d in DAYS:
        value = (row.get(d) or "").strip()
        who = "пара %s, партнёр %s" % (row.get("couple_id"), row.get("partner"))
        if value == "":
            raise ValueError("%s: не заполнен день %s (если сообщений не было — ставьте 0)" % (who, d))
        try:
            count = int(value)
        except ValueError:
            raise ValueError("%s: в дне %s должно быть целое число, а не %r" % (who, d, value))
        if count < 0:
            raise ValueError("%s: в дне %s отрицательное число" % (who, d))
        if count > 0:
            days += 1
    return days


def evaluate(rows):
    couples = {}
    for row in rows:
        cid = row["couple_id"].strip()
        partner = (row.get("partner") or "").strip().upper()
        if partner not in ("A", "B"):
            raise ValueError("пара %s: партнёр должен быть A или B, а не %r" % (cid, partner))
        couple = couples.setdefault(cid, {})
        if partner in couple:
            raise ValueError("пара %s: партнёр %s записан дважды" % (cid, partner))
        couple[partner] = row

    results = []
    for cid in sorted(couples):
        couple = couples[cid]
        counts = {p: money_days(r) for p, r in couple.items()}
        days = min(counts.values())
        daily = days >= DAY_THRESHOLD
        verbal = any(is_yes(r.get("verbal_yesterday")) and is_yes(r.get("verbal_day_before"))
                     for r in couple.values())
        close = any(is_close(r.get("relation")) for r in couple.values())
        flags = []
        if len(counts) < 2:
            flags.append("без кросс-чека")
        else:
            diff = abs(counts["A"] - counts["B"])
            if diff > 1:
                flags.append("расхождение %d дн." % diff)
        if daily:
            status = "ежедневная"
        elif verbal:
            status = "не ежедневная, говорят вслух"
        else:
            status = "не ежедневная"
        results.append(dict(couple=cid, counts=counts, days=days, daily=daily,
                            status=status, flags=flags, close=close))

    n = len(results)
    k = sum(1 for r in results if r["daily"])
    needed = math.ceil(PAIR_SHARE * MIN_PAIRS)
    early = False
    if n >= MIN_PAIRS:
        verdict = "ЖИВО" if k / n >= PAIR_SHARE else "ОПРОВЕРГНУТО"
    elif k + (MIN_PAIRS - n) < needed:
        verdict = "ОПРОВЕРГНУТО"
        early = True
    else:
        verdict = "НЕ ВЫНЕСЕН"

    close_n = sum(1 for r in results if r["close"])
    other = [r for r in results if not r["close"]]
    provisional = verdict == "ЖИВО" and close_n * 2 > n
    return dict(results=results, n=n, k=k, needed=needed, verdict=verdict, early=early,
                close_n=close_n, other_n=len(other), other_k=sum(1 for r in other if r["daily"]),
                provisional=provisional, rows=rows)


def tally(rows, field):
    out = {}
    for r in rows:
        value = (r.get(field) or "").strip().lower() or "не заполнено"
        out[value] = out.get(value, 0) + 1
    return ", ".join("%s — %d" % kv for kv in sorted(out.items())) or "нет записей"


def main(argv):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    if len(argv) < 2:
        print("Запуск: python score_assumption.py money-days-log.csv")
        return 2
    rows = load(argv[1])
    if not rows:
        print("Записей пока нет — заполните таблицу после первых интервью.")
        return 0
    try:
        r = evaluate(rows)
    except ValueError as e:
        print("ОШИБКА В ТАБЛИЦЕ: %s" % e)
        return 1

    line = "%-5s  %-2s %-2s  %-13s  %-8s  %-29s  %s"
    print(line % ("Пара", "A", "B", "Денежных дней", "Кто", "Статус", "Отметки"))
    for x in r["results"]:
        print(line % (x["couple"], x["counts"].get("A", "—"), x["counts"].get("B", "—"),
                      "%d из 7" % x["days"], "близкие" if x["close"] else "—",
                      x["status"], ", ".join(x["flags"])))

    print()
    print("Опрошено пар: %d из %d. Ежедневных: %d. Нужно для прохождения: %d из %d "
          "(порог — %d денежных дней из 7)." % (r["n"], MIN_PAIRS, r["k"], r["needed"],
                                               MIN_PAIRS, DAY_THRESHOLD))
    if r["close_n"]:
        print("Близких пар: %d из %d. Среди остальных ежедневных: %d из %d." % (
            r["close_n"], r["n"], r["other_k"], r["other_n"]))

    if r["verdict"] == "ЖИВО" and r["provisional"]:
        print("ВЕРДИКТ: ЖИВО, НО ПРЕДВАРИТЕЛЬНО — больше половины пар друзья и родственники. "
              "Проверить на незнакомых парах в неделях 2–3, прежде чем строить на этом продукт.")
    elif r["verdict"] == "ЖИВО":
        print("ВЕРДИКТ: ЖИВО. Пары обмениваются информацией о деньгах ежедневно — "
              "допущение выдержало проверку.")
    elif r["verdict"] == "ОПРОВЕРГНУТО":
        tail = (" досрочно: даже если все оставшиеся пары окажутся ежедневными, порога не набрать"
                if r["early"] else "")
        print("ВЕРДИКТ: ОПРОВЕРГНУТО%s. Менять сегмент до первой строки кода — "
              "запасной вариант из отчёта: люди с нерегулярным доходом." % tail)
    else:
        print("ВЕРДИКТ НЕ ВЫНЕСЕН: осталось опросить %d пар. Подтверждать досрочно нельзя, "
              "опровергнуть — можно." % (MIN_PAIRS - r["n"]))

    close_rows = [x for x in rows if is_close(x.get("relation"))]
    other_rows = [x for x in rows if not is_close(x.get("relation"))]
    waited = sum(1 for x in rows if is_yes(x.get("waited_for_reply")))
    print()
    print("Вторичные сигналы — на вердикт не влияют:")
    print("  ждали ответа партнёра перед покупкой: %d из %d опрошенных" % (waited, len(rows)))
    if close_rows:
        print("  продажа, близкие, не доказательство спроса: %s" % tally(close_rows, "sell_result"))
        print("  продажа, остальные: %s" % tally(other_rows, "sell_result"))
    else:
        print("  продажа: %s" % tally(rows, "sell_result"))
    print("  готовность позвать партнёра: %s" % tally(rows, "partner_invite"))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
