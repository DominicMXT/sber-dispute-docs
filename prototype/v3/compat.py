# -*- coding: utf-8 -*-
"""Совместимость с Safari (Mac, iPhone) — модуль интегратора, накладывается последним.

Проверка `v3/tests/mac/maccheck.mjs` в WebKit (движок Safari, Playwright) 05.10:
при открытии файлом (file://) Safari считает фото из photos/ чужим источником и запрещает getImageData —
fogCopy бросал ошибку, прототип её ловил и рисовал запасной туман (CSS-размытие), но WebKit писал ошибку в консоль.
Теперь на file:// для фото не из data: канвас не трогаем — сразу запасной туман, без ошибки.
По http(s) (сервер, ссылка артефакта) — как раньше.
"""
R = []
CSS = ""
JS = r"""const cpFog0 = fogCopy;
fogCopy = function(img){ if (location.protocol === 'file:' && !/^data:/.test(img.src)) throw new Error('file:// — запасной туман'); return cpFog0(img); };"""
