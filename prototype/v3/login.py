# -*- coding: utf-8 -*-
"""Вход через российские ID-сервисы вместо почты — решение владельца 05.10. Модуль интегратора, стоит после polish.

Решения владельца 05.10: вход через Сбер ID, VK ID, Яндекс ID и Max (Google и Telegram для входа запрещены: 149-ФЗ ст. 8 ч. 10,
КоАП ст. 13.55 с 07.07.2026 — review/2026-10-04_auth.md, 2.1); просить вход на «Сохранить цель» — после первого ответа,
до ежедневной работы (Baymard: обязательная регистрация до пользы теряет ≈19 %, поэтому не раньше ответа).
DAU считается по вошедшим, поэтому без входа цель не сохраняется; первый ответ по-прежнему без регистрации (ПК-01).

1. «Сохранить цель» без входа открывает лист «Войдите, чтобы цель не пропала»: Сбер ID, VK ID, Яндекс ID, Max. После входа цель
   сохраняется, путь дальше прежний. В мини-приложении Max вход идёт сам, листа нет (в прототипе не показан).
2. Лист почты после первой отметки и «Привязать почту» в «Моих данных» заменены входом: «Вход: VK ID» или «Войти».
3. Демо-состояния (пример, пара, группа) — уже с входом, чтобы лист не мешал другим сценариям.
"""
R = []
CSS = r"""
/* зелёный Сбера темнее фирменного #21A038 (3,41:1): белый текст 5,13:1 по WCAG AA; в продукте кнопку рисует SDK Сбер ID */
.l-sber{background:#107F2C !important;color:#fff !important}
:root[data-theme="dark"] /* зелёный Сбера темнее фирменного #21A038 (3,41:1): белый текст 5,13:1 по WCAG AA; в продукте кнопку рисует SDK Сбер ID */
.l-sber{background:#107F2C !important;color:#fff !important}
#sheet .l-btn{text-align:left;padding:0 16px}
"""
JS = r"""/* v3 · login — вход через Сбер ID, VK ID, Яндекс ID, Max */
const L_PROV = {sber:'Сбер ID', vk:'VK ID', ya:'Яндекс ID', max:'Max'};
const lAuthed = () => { const m = me(); return !m || S.mode !== 'fresh' || !!m.auth; };
SH.login = () => `<h3 class="disp">Войдите, чтобы цель не пропала</h3><p class="mut sm">Сохраним только номер входа, без имени и телефона.</p>
  <button class="main press l-sber" data-act="loginSber">Войти по Сбер ID</button>
  <button class="sec2 press l-btn" data-act="loginVk">Войти через VK ID</button>
  <button class="sec2 press l-btn" data-act="loginYa">Войти с Яндекс ID</button>
  <button class="sec2 press l-btn" data-act="loginMax">Войти через Max</button>
  <button class="link" data-close>Не сейчас</button>`;
let lAfter = null;
function lLogin(k){ const m = me(); m.auth = k; m.email = true; closeSheet();
  try { v3log('login_linked'); } catch(e) {}
  const next = lAfter; lAfter = null;
  if (next) next(); else render(true);
  setTimeout(() => toast('Вход через ' + L_PROV[k] + '. ' + (next ? 'Цель сохранена.' : 'Данные не пропадут.')), 60); }
ACT.loginSber = () => lLogin('sber'); ACT.loginVk = () => lLogin('vk'); ACT.loginYa = () => lLogin('ya'); ACT.loginMax = () => lLogin('max');
/* 1. «Сохранить цель» — только после входа */
const lSave0 = ACT.v3save;
ACT.v3save = function(){ if (lAuthed()) return lSave0.apply(this, arguments);
  const args = arguments, self = this; lAfter = () => lSave0.apply(self, args);
  $$('[aria-busy="true"]').forEach(b => { b.disabled = false; b.removeAttribute('aria-busy'); if (b.dataset.hLabel) b.textContent = b.dataset.hLabel; });
  openSheet('login'); };
/* 2. лист почты → вход; «Мои данные» — строка входа */
const lOpen0 = openSheet;
openSheet = function(k, arg){ if (k === 'email') { if (me() && me().auth) return; k = 'login'; } return lOpen0.call(this, k, arg); };
const lData0 = SCR.data;
SCR.data = function(){ const r = lData0.apply(this, arguments), m = me(); if (!r || !r.html || !m) return r;
  r.html = r.html.replace(/<span>(?:Почта привязана|Только на этом телефоне)<\/span>(?:<button class="chip press sm" data-sheet="email">Привязать почту<\/button>)?/,
    m.auth ? '<span>Вход: ' + L_PROV[m.auth] + '</span>' : S.mode !== 'fresh' ? '<span>Вход: Сбер ID</span>' : '<span>Только на этом телефоне</span><button class="chip press sm" data-sheet="login">Войти</button>');
  return r; };
"""
JS += r"""
/* коды доски и карты: ?s=email и ?s=login — лист входа на «Моих данных» */
V3_SCEN.email = V3_SCEN.login = () => { go('data'); lOpen0('login'); };
"""
