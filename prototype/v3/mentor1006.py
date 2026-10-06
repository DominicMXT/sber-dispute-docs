# -*- coding: utf-8 -*-
"""Решения владельца после встречи с ментором 06.10 — модуль интегратора, стоит после decisions.

Основание: review/2026-10-06_mentor-falsification-table.md — на этапе 1 нужны 50 уникальных пользователей накопительно,
анонимные засчитываются, регистрация — шаг воронки, а не условие (E1); ограничений по входу от программы нет,
у других команд — код на почту или Яндекс (E8).

1. Вход по желанию: «Сохранить без входа» сохраняет цель на этом телефоне; вход предлагается для переноса и не блокирует.
2. Все законные способы входа на одном листе — разработчик выбирает, какие подключить первыми:
   VK ID, Яндекс ID, Сбер ID, Max и код на почту. Google и Telegram — нет (149-ФЗ ст. 8 ч. 10, КоАП ст. 13.55).
3. Код на почту: адрес → код из 6 цифр; ошибки — под полем.
"""
R = []
CSS = r"""
#sheet .l-grid{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin:10px 0 8px}
#sheet .l-grid .sec2{margin-top:0;min-height:48px}
#sheet .l-grid .l-wide{grid-column:1 / -1}
"""
JS = r"""/* v3 · mentor1006 — вход по желанию, все законные способы */
L_PROV.mail = 'почту';
SH.login = () => `<h3 class="disp">Войдите, чтобы цель не пропала</h3><p class="mut sm">Сохраним только номер входа, без имени и телефона.</p>
  <div class="l-grid"><button class="sec2 press" data-act="loginVk">VK ID</button><button class="sec2 press" data-act="loginYa">Яндекс ID</button>
  <button class="sec2 press" data-act="loginSber">Сбер ID</button><button class="sec2 press" data-act="loginMax">Max</button>
  <button class="sec2 press l-wide" data-act="mLoginMail">Код на почту</button></div>
  <button class="link" data-act="mSkip">Сохранить без входа</button>`;
/* «Сохранить без входа»: цель сохраняется, вход больше не навязывается в этом сеансе */
ACT.mSkip = function(){ const next = lAfter; lAfter = null; me().authSkip = true; closeSheet(); try { v3log('login_skipped'); } catch(e) {}
  if (next) { next(); setTimeout(() => toast('Цель сохранена на этом телефоне. Войти можно в «Мои данные».'), 60); } };
const mAuthed0 = lAuthed;
const mSave0 = ACT.v3save;
ACT.v3save = function(){ const m = me(); if (m && m.authSkip) return lSave0.apply(this, arguments); return mSave0.apply(this, arguments); };
/* код на почту */
SH.mMail = () => S.mMailStep ? `<h3 class="disp">Код из письма</h3><p class="mut sm">Отправили 6 цифр на ${esc(S.mMailTo || 'почту')}.</p><form id="mcodef" class="field"><input class="inp" id="mcode" inputmode="numeric" maxlength="6" autocomplete="one-time-code" aria-label="Код из письма"><button class="go press">Войти</button></form><button class="link" data-act="mMailBack">Другая почта</button>`
  : `<h3 class="disp">Вход по коду на почту</h3><form id="mmailf" class="field" novalidate><input class="inp" id="mmail" type="email" inputmode="email" autocomplete="email" placeholder="почта" aria-label="Почта"><button class="go press">Код</button></form><p class="xs mut">Храним только отпечаток адреса.</p>`;
ACT.mLoginMail = () => { S.mMailStep = false; lOpen0('mMail'); };
ACT.mMailBack = () => { S.mMailStep = false; lOpen0('mMail'); };
document.addEventListener('submit', e => { const id = e.target.id; if (id !== 'mmailf' && id !== 'mcodef') return; e.preventDefault(); e.stopImmediatePropagation();
  if (id === 'mmailf') { const inp = $('#mmail'), v = (inp.value || '').trim();
    if (!v) return hErr(inp, 'Напишите адрес почты — с @ и точкой.');
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(v)) return hErr(inp, 'Похоже, в адресе ошибка — проверьте @ и точку.');
    S.mMailStep = true; S.mMailTo = v; lOpen0('mMail'); return; }
  const inp = $('#mcode'), v = (inp.value || '').replace(/\s/g, '');
  if (!/^\d{6}$/.test(v)) return hErr(inp, 'Код — 6 цифр из письма.');
  S.mMailStep = false; lLogin('mail'); }, true);
/* «Мои данные»: войти можно в любой момент */
const mData0 = SCR.data;
SCR.data = function(){ const r = mData0.apply(this, arguments), m = me(); if (!r || !r.html || !m) return r;
  if (m.auth === 'mail') r.html = r.html.replace('Вход: почту', 'Вход: код на почту');
  return r; };
"""
