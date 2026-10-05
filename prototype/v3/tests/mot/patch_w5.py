# -*- coding: utf-8 -*-
# Волна 5: дополняет mottest.js (из mottest.wave4.js) и runmt.py. Запуск повторяемый: всегда от копии волны 4.
import io, os
here = os.path.dirname(os.path.abspath(__file__))
s = io.open(os.path.join(here, 'mottest.wave4.js'), encoding='utf-8').read()


def rep(a, b):
    global s
    assert s.count(a) == 1, (s.count(a), a[:90])
    s = s.replace(a, b)


# 1. превышение 45 на своих экранах — FAIL, не WARN; в имени — размер окна
rep("""  if (whole || base + mine <= 45) ok(name + ': первый экран ≤45 слов' + (whole ? ' (весь экран — экран модуля)' : ''), W(t) <= 45, W(t));
  else out.push('WARN ' + name + ': первый экран ' + (base + mine) + ' слов > 45 — база экрана v2 ' + base + ' (была выше бюджета до модуля), добавка модуля ' + mine); ok(""",
    """  ok(name + ': первый экран ≤45 слов' + (whole ? ' (весь экран — экран модуля)' : '') + ' [' + innerWidth + '×' + innerHeight + ']', W(t) <= 45, W(t) + (whole ? '' : ' — база экрана ' + base + ', добавка модуля ' + mine)); ok(""")
# новый код состояния
rep("""weeks:() => S.scr === 'purchase' && !!$('#view .v3-weeks'),""",
    """weeks:() => S.scr === 'purchase' && !!$('#view .v3-weeks'), slipPropose:() => S.scr === 'purchase' && S.who === 'anya' && !!$('#view .v3-prop [data-act="v3propYes"]') && !!$('#view .v3-prop [data-act="v3propNo"]'),""")
# прямота: новое имя кнопки и заголовок листа
rep("""ok('weeksum одного: недели по плану, «Сказать прямо»', /Недель по плану/.test(st()) && /Пропуск не обнуляет/.test(st()) && !!$('#sheet [data-sheet="v3direct"]'), st().replace(/\\n/g, ' | '));""",
    """ok('weeksum одного: недели по плану, «Показать как есть»', /Недель по плану/.test(st()) && /Пропуск не обнуляет/.test(st()) && !!$('#sheet [data-sheet="v3direct"]') && $('#sheet [data-sheet="v3direct"]').textContent === 'Показать как есть' && !/Сказать прямо/.test(st()), st().replace(/\\n/g, ' | '));""")
rep("""ok('weeksum одного: без прямоты до кнопки', !/Прямо/.test(st()));""",
    """ok('weeksum одного: без прямоты до кнопки', !/Как есть,/.test(st()));""")
rep("""ok('v3direct открывается по кнопке', S.sheet === 'v3direct' && /Прямо, раз вы спросили/.test(st()));""",
    """ok('v3direct открывается по кнопке', S.sheet === 'v3direct' && /Как есть, раз вы спросили/.test(st()));""")
# M-F: на экране с v2-плёнкой — строка без третьей полоски; сетка проверяется на общей цели (ниже)
rep("""  ok('weeks: сетка недель от старта до срока', cells().length === k0.total && k0.ci === 4, cells().length + ' / ' + k0.total + ' / ci ' + k0.ci);
  ok('weeks: 3 недели по плану, пропуск не закрашен и не обнуляет', /3 недели по плану/.test($('#view .v3-weeks').innerText) && onIx().join() === '0,1,3', onIx().join());
  ok('weeks: текущая неделя отмечена .v3-now, будущие — .v3-fut', cells()[4].classList.contains('v3-now') && $$('#view .v3-day.v3-fut').length === k0.total - 5);""",
    """  ok('weeks: история 1,1,0,1 + текущая → 3 по плану, пропуск не обнуляет', k0.ci === 4 && k0.cells.map(Number).join() === '1,1,0,1,0' && k0.n === 3, k0.cells.join() + ' / ci ' + k0.ci);
  ok('weeks: на экране с v2-плёнкой — строка «3 недели по плану», третьей полоски нет', !!$('#view .film') && /3 недели по плану/.test($('#view .v3-weeks').innerText) && cells().length === 0, cells().length + ' :: ' + $('#view .v3-weeks').innerText);""")
rep("""  ok('weeks: после «отложил» текущая неделя закрашена (.on), прошлые не изменились', onIx().join() === '0,1,3,4' && /4 недели по плану/.test($('#view .v3-weeks').innerText), onIx().join());""",
    """  ok('weeks: после «отложил» текущая неделя засчитана, прошлые не изменились', v3weeks(pw, 'oleg').cells.map(Number).join() === '1,1,0,1,1' && /4 недели по плану/.test($('#view .v3-weeks').innerText), v3weeks(pw, 'oleg').cells.join());""")
rep("""  if (ANIM) ok('anim: ячейка недели заполняется (.v3-fill)', !!$('#view .v3-day.on.v3-fill')); else info('anim не подключён — проверка заливки пропущена');
""", "")

NEW = io.open(os.path.join(here, 'mottest_w5_block.js'), encoding='utf-8').read()
rep("""  /* ── v2 не сломан ── */""", NEW + """  /* ── v2 не сломан ── */""")
io.open(os.path.join(here, 'mottest.js'), 'w', encoding='utf-8').write(s)

r = io.open(os.path.join(here, 'runmt.py'), encoding='utf-8').read()
if 'SIZES' not in r:
    r = r.replace("CODES = ['', 'dayprice', 'slip', 'weeks', 'weeksum3', 'nextgoal']",
                  "CODES = ['', 'dayprice', 'slip', 'slipPropose', 'weeks', 'weeksum3', 'nextgoal']\nSIZES = ['1200,900', '420,860']   # десктоп и телефон")
    lines, out, inb = r.split('\n'), [], False
    for l in lines:
        if l.startswith('        for c in CODES:'):
            out.append('        for size in SIZES:'); out.append('  ' + l); inb = True; continue
        if inb and l.startswith('    finally:'):
            inb = False
        if inb and l.startswith('            '):
            out.append('  ' + l); continue
        out.append(l)
    r = '\n'.join(out)
    r = r.replace("'--window-size=1200,900'", "'--window-size=' + size")
    r = r.replace("out = f'=== {f} #{c or \"(полный прогон)\"}", "out = f'=== {f} [{size}] #{c or \"(полный прогон)\"}")
    io.open(os.path.join(here, 'runmt.py'), 'w', encoding='utf-8').write(r)
print('patched')
