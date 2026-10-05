# -*- coding: utf-8 -*-
"""Пульт прототипа: кнопки для состояний v3 — модуль интегратора, накладывается последним.

Обработчик пульта в v2 вызывает scenario(код) напрямую — мимо V3_SCEN, поэтому сначала ищем код в V3_SCEN
(и закрываем пульт, как это делает scenario() — QA №9). Перед сценарием лист закрывается и очищается сразу —
иначе в нём оставался текст другого человека (QA №5, проба p_stale).
Новая группа «Р2» — 11 кодов агентов (flow_group, motivation) и themeSet (theme).
"""
R = [
    ("  else if (d.sc) scenario(d.sc);",
     "  else if (d.sc) { closeSheet(); $('#sheet').innerHTML = ''; if (V3_SCEN[d.sc]) { $('#panel').classList.remove('open'); V3_SCEN[d.sc](); } else scenario(d.sc); }"),
    ('<button class="pbtn" data-sc="used">Приглашение уже использовано</button></div>',
     '<button class="pbtn" data-sc="used">Приглашение уже использовано</button></div>\n'
     '    <div class="grp"><span>Р2: вход и общая цель</span>\n'
     '      <button class="pbtn" data-sc="example">Пример цели после согласия</button>\n'
     '      <button class="pbtn" data-sc="solo">Своя цель одного человека</button>\n'
     '      <button class="pbtn" data-sc="together">«Копить вместе с кем-то?»</button>\n'
     '      <button class="pbtn" data-sc="groupInvite">Приглашение в общую цель</button>\n'
     '      <button class="pbtn" data-sc="group2">Общая цель на двоих</button>\n'
     '      <button class="pbtn" data-sc="group2step">На двоих: второй сделал шаг</button>\n'
     '      <button class="pbtn" data-sc="group3">Общая цель на четверых</button></div>\n'
     '    <div class="grp"><span>Р2: мотивация</span>\n'
     '      <button class="pbtn" data-sc="dayprice">«Влезет ли» с ценой в днях цели</button>\n'
     '      <button class="pbtn" data-sc="slip">Взяли из отложенного</button>\n'
     '      <button class="pbtn" data-sc="slipPropose">Предложение нового срока (глазами Ани)</button>\n'
     '      <button class="pbtn" data-sc="weeks">Счёт недель по плану</button>\n'
     '      <button class="pbtn" data-sc="weeksum3">Итоги недели в общей цели</button>\n'
     '      <button class="pbtn" data-sc="nextgoal">Собрано — следующая цель</button>\n'
     '      <button class="pbtn" data-sc="themeSet">Выбор темы в «Моих данных»</button></div>'),
]
# ?clean (например ?s=group3&clean или ?clean#group3) — показ людям и скриншоты: пульт и его кнопка скрыты (в продукт пульт не идёт; QA №9, design §6.6).
CSS = """html.v3-clean #fab,html.v3-clean #panel{display:none!important}"""
JS = r"""if (/[?&#]clean\b/.test(location.search + location.hash) || new URLSearchParams(location.search).has('clean')) document.documentElement.classList.add('v3-clean');"""
