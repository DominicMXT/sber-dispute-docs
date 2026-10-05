# -*- coding: utf-8 -*-
# Волна 5b (решение владельца 05.10): доплата < V3_SLIP_MIN = 150 ₽ в день — одна кнопка «Догнать» + ссылка «или сдвинуть срок».
# Накладывается на mottest.js после patch_w5.py. Повторный запуск ничего не меняет (метка W5B).
import io, os
here = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(here, 'mottest.js')
s = io.open(p, encoding='utf-8').read()
if '/* W5B */' in s:
    print('already patched'); raise SystemExit


def rep(a, b):
    global s
    assert s.count(a) == 1, (s.count(a), a[:90])
    s = s.replace(a, b)


# сценарий #slip теперь берёт 40 000 (доплата 164 ₽ ≥ порога — две равные дороги)
rep("V3_SCEN.slip(); const ps = P(), dl0 = ps.dl, c0 = v3slipCalc(ps, 'oleg', 20000);",
    "/* W5B */ V3_SCEN.slip(); const ps = P(), dl0 = ps.dl, c0 = v3slipCalc(ps, 'oleg', 40000);")
rep("ok('slip: экран после крупной траты, отложенное уменьшилось, но не обнулилось', S.scr === 'slip' && ps.saved.oleg === 30000);",
    "ok('slip: экран после крупной траты, отложенное уменьшилось, но не обнулилось', S.scr === 'slip' && ps.saved.oleg === 10000);\n"
    "  ok('slip: сценарий — доплата ≥ V3_SLIP_MIN (150), значит две дороги', V3_SLIP_MIN === 150 && c0.plus >= V3_SLIP_MIN && !c0.small, c0.plus);")
rep("$('#inputv').value = '20 000'; $('#inputf').requestSubmit();\n  ok('slip: путь «Изменить цель → Пришлось взять из отложенного» ведёт на slip', S.scr === 'slip' && pt.saved.oleg === 30000",
    "$('#inputv').value = '40 000'; $('#inputf').requestSubmit();\n  ok('slip: путь «Изменить цель → Пришлось взять из отложенного» ведёт на slip', S.scr === 'slip' && pt.saved.oleg === 10000")

# slipCase: третья ветка — доплата меньше порога
rep("""    else { ok(name + ': две равные дороги', pb.length === 2 && pb[0].className === pb[1].className && !$('#bottom .main'), pb.length);""",
    """    else if (c.plus < V3_SLIP_MIN) { const ln = $('#view .v3-sliplink'), mb = $('#bottom .main'), y = new Date(c.dl).getUTCFullYear(), y0 = new Date(dl0).getUTCFullYear();
      ok(name + ': доплата ' + c.plus + ' < ' + V3_SLIP_MIN + ' — одна главная кнопка «Догнать: +N ₽ в день», равных кнопок нет', !pb.length && bt() === 'Догнать: +' + rubT(c.plus) + ' в день', pb.length + ' / ' + bt());
      ok(name + ': сдвиг — вторичная ссылка «или сдвинуть срок», мельче главной кнопки', !!ln && ln.textContent === 'или сдвинуть срок' && ln.classList.contains('link') && !ln.classList.contains('sec2') && !!mb
        && parseFloat(getComputedStyle(ln).fontSize) < parseFloat(getComputedStyle(mb).fontSize) && ln.getBoundingClientRect().height >= 24, ln && ln.className + ' ' + getComputedStyle(ln).fontSize);
      ln.click(); ok(name + ': ссылка сдвигает срок — срок и темп как в расчёте', Math.round((p.dl - dl0) / DAY) === c.shift && perDay(p, 'oleg') === c.base, Math.round((p.dl - dl0) / DAY) + ' / ' + perDay(p, 'oleg') + ' vs ' + c.base);
      ok(name + ': тост с годом, если год сменился', (y !== y0) === new RegExp('\\\\s' + y + '\\\\D').test($('#toast').textContent), $('#toast').textContent); }
    else { ok(name + ': доплата ≥ ' + V3_SLIP_MIN + ' — две равные дороги', c.plus >= V3_SLIP_MIN && pb.length === 2 && pb[0].className === pb[1].className && !$('#bottom .main') && !$('#view .v3-sliplink'), c.plus + ' / ' + pb.length);""")

# границы порога: доплата 82, 149, 150 и большая
rep("""    slipCase('сдвиг: взяли 100 ₽', p => { p.saved.oleg = 50000; }, 100);""",
    """    slipCase('сдвиг: взяли 100 ₽', p => { p.saved.oleg = 50000; }, 100);
    const c82 = slipCase('порог: взяли 20 000 из 50 000 (доплата 82 ₽)', p => { p.saved.oleg = 50000; }, 20000);
    ok('порог: доплата 82 ₽ — режим «одна кнопка + ссылка»', c82.plus === 82 && c82.small, c82.plus);
    V3_SCEN.solo(); const dN = daysTo(P());   /* у solo stepped = false: доплата ровно N при отложенном share − 100·d и взятых N·d */
    for (const N of [149, 150]) { const cN = slipCase('порог: доплата ровно ' + N + ' ₽', p => { p.saved.oleg = p.share.oleg - 100 * dN; }, N * dN);
      ok('порог: доплата ' + N + ' ₽ — ' + (N < 150 ? 'одна кнопка + ссылка' : 'две равные кнопки'), cN.plus === N && cN.small === (N < 150), cN.plus + ' / small ' + cN.small); }
    const cBig = slipCase('порог: большая доплата (взяли 90 000 из 100 000)', p => { p.saved.oleg = 100000; }, 90000);
    ok('порог: большая доплата — две равные кнопки', cBig.plus >= 150 && !cBig.small, cBig.plus);""")

# общая цель: основной случай — доплата выше порога; ниже порога — ссылка ведёт к предложению
rep("V3_SCEN.group2(); { const p = propose('oleg', 10000), dl0 = p.dl, c = v3slipCalc(p, 'oleg', 10000), pb = $$('#view .v3-pair button');",
    "V3_SCEN.group2(); { const p = propose('oleg', 30000), dl0 = p.dl, c = v3slipCalc(p, 'oleg', 30000), pb = $$('#view .v3-pair button');\n"
    "    ok('группа: доплата ≥ 150 — две равные кнопки', c.plus >= V3_SLIP_MIN && !c.small, c.plus);")
rep("""  V3_SCEN.group2(); { const p = propose('oleg', 10000), dl0 = p.dl; $('#view [data-act="v3slipDate"]').click();""",
    """  V3_SCEN.group2(); { const p = propose('oleg', 10000), dl0 = p.dl, c = v3slipCalc(p, 'oleg', 10000), ln = $('#view .v3-sliplink');
    ok('группа: доплата ' + c.plus + ' < 150 — «Догнать: +N ₽ в день» и ссылка «или сдвинуть срок»', c.small && bt() === 'Догнать: +' + rubT(c.plus) + ' в день' && !!ln && ln.textContent === 'или сдвинуть срок' && !$$('#view .v3-pair button').length && /согласятся все/.test(vt()), bt() + ' / ' + (ln && ln.textContent));
    budgetScreen('slip (общая цель, доплата < 150)', true);
    $('#view [data-act="v3slipDate"]').click();
    ok('группа: ссылка ведёт к предложению, срок не меняется', p.dl === dl0 && !!p.v3prop && p.v3prop.st === 'open', JSON.stringify(p.v3prop));""")
io.open(p, 'w', encoding='utf-8').write(s)
print('patched')
