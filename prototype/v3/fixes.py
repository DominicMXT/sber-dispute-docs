# -*- coding: utf-8 -*-
"""Мелкие правки вёрстки по отчётам агентов — модуль интегратора, после motivation.

1. Собранная цель: в шапке было «к 1 октября · через 1 день» → «к 1 октября · собрано» (своя и общая цель).
2. Собранная цель: счёт недели «Неделя: 2 из 7 · ещё 1 неделя» и плёнка недели скрыты — копить больше нечего.
0. Срок в шапке своей и общей цели и в списке покупок — с годом, если он не в текущем году (fxDl; после сдвига срока).
"""
R = [
    ('к ${dStr(p.dl)} · <span class="num" data-out="days">через ${daysW(daysTo(p))}</span></p></div>',
     'к ${fxDl(p.dl)} · ${p.state === \'done\' ? \'собрано\' : `<span class="num" data-out="days">через ${daysW(daysTo(p))}</span>`}</p></div>'),
    ('к ${dStr(p.dl)} · <span class="num" data-out="days">через ${daysW(daysTo(p))}</span> · ${n} ',
     'к ${fxDl(p.dl)} · ${p.state === \'done\' ? \'собрано\' : `<span class="num" data-out="days">через ${daysW(daysTo(p))}</span>`} · ${n} '),
    ('<br><span class="mut sm">к ${dStr(p.dl)} · ${p.state', '<br><span class="mut sm">к ${fxDl(p.dl)} · ${p.state'),
    # год в шапке +1 слово: экран своей цели был ровно 45 — «Вам» снимаем только тут (своё и так помечено замком;
    # в общей цели «Вам» отличает свою часть от общей и остаётся)
    ('<small>Вам осталось отложить ${vis(\'me\')}</small><span class="num" data-out="my-left">',
     '<small>Осталось отложить ${vis(\'me\')}</small><span class="num" data-out="my-left">'),
    ("  <div class=\"filmlab\"><span>Неделя: ${steps} из 7</span><span>ещё ${Math.ceil(daysTo(p) / 7)} ${plural(Math.ceil(daysTo(p) / 7), 'неделя', 'недели', 'недель')}</span></div>\n"
     "  <div class=\"film\">${'<div class=\"fr\"></div>'.repeat(13).replace('<div class=\"fr\">', `<div class=\"fr\" style=\"--r:${(100 - steps / 7 * 100).toFixed(1)}%\">`)}</div>\n"
     "  ${wk.html}",
     "  ${p.state === 'done' ? '' : `<div class=\"filmlab\"><span>Неделя: ${steps} из 7</span><span>ещё ${Math.ceil(daysTo(p) / 7)} ${plural(Math.ceil(daysTo(p) / 7), 'неделя', 'недели', 'недель')}</span></div>\n"
     "  <div class=\"film\">${'<div class=\"fr\"></div>'.repeat(13).replace('<div class=\"fr\">', `<div class=\"fr\" style=\"--r:${(100 - steps / 7 * 100).toFixed(1)}%\">`)}</div>\n"
     "  ${wk.html}`}"),
]
# 3. Текст 200 % (WCAG 1.4.4, ТЗ 9.x): на slip, themeSet, recon (label.tip), example строки вылезали за правый край.
#    Перенос включается только когда не влезает — на обычном размере вид не меняется.
# 4. Ссылки с min-height:0 («Изменить», «Что-то лишнее?», «вписать самому») были 20–23 px — WCAG 2.5.8 требует цель ≥ 24 px.
CSS = """.v3-pair{grid-template-columns:repeat(auto-fit,minmax(min(100%,9.5rem),1fr))}
.v3-theme .seg{flex-wrap:wrap}.v3-theme .seg button{flex:1 1 6rem}
.rowl,.cap,label.tip{flex-wrap:wrap}
.chip{max-width:100%;overflow-wrap:anywhere}
button.link[style*="min-height:0"]{min-height:24px!important;padding-block:2px}
.vis{width:26px;height:26px;border-radius:13px}.vis svg{transform:scale(1.15)}
.fx-leg{display:inline-flex;align-items:center;gap:6px;margin-top:4px}.fx-leg .vis{margin-left:0}"""
# 5. Закрытый лист (QA №5): уезжает за край, но оставался в дереве доступности и в фокусе, со старым текстом другого человека.
#    Теперь при закрытии — inert + aria-hidden, после анимации содержимое очищается; при открытии снимается.
# 6. Значки видимости (решение владельца 05.10): серые, но расшифрованы словами на экране согласия и чуть крупнее.
JS = r"""/* 0. срок с годом, если он не в текущем году */
const fxDl = t => { const y = new Date(t).getUTCFullYear(); return dStr(t) + (y !== new Date(now()).getUTCFullYear() ? NB + y : ''); };
const fxOpen0 = openSheet, fxClose0 = closeSheet;
function fxSheetIdle(on){ const sw = $('#sheetwrap'); if (!sw) return; sw.inert = on; if (on) sw.setAttribute('aria-hidden', 'true'); else sw.removeAttribute('aria-hidden'); }
openSheet = function(k, arg){ fxSheetIdle(false); return fxOpen0(k, arg); };
closeSheet = function(){ fxClose0(); fxSheetIdle(true); clearTimeout(closeSheet.t); closeSheet.t = setTimeout(() => { if (!S.sheet) $('#sheet').innerHTML = ''; }, 450); };
fxSheetIdle(true);
const fxConsent0 = scrConsent;
scrConsent = SCR.consent = function(){ const r = fxConsent0(); const g = typeof visG === 'function' ? visG() : vis('all');
  r.html = v3sub(r.html, 'Ваши деньги видите только вы.', `Ваши деньги видите только вы ${vis('me')}<br><span class="fx-leg">${g} — видят участники</span>`, 'fixes:consent');
  r.html = v3sub(r.html, 'Регистрация не нужна.', 'Без регистрации.', 'fixes:consent-reg'); return r; };"""
