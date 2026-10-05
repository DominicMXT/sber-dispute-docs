# -*- coding: utf-8 -*-
"""Модуль v3 «Тема»: переключатель в «Моих данных», поверхности тёмной темы, туман в тёмной теме, плавная смена.

Режим темы: system | light | dark, хранится в lsGet/lsSet под ключом 'fogp-theme-mode'.
Старый ключ v2 'fogp-theme' не читаем: v2 писал его при каждой загрузке, и по нему не отличить выбор человека
от того, что совпало с системой. Поэтому у всех по умолчанию — «Как в системе».
В v2 тёмная тема держится только на :root[data-theme="dark"], правил @media (prefers-color-scheme: dark) нет,
поэтому «Как в системе» ставит data-theme по matchMedia и обновляет его по событию change.

Значения цветов (обе темы, высокий контраст, --input) — в модуле palette: один токен — одно место.
Здесь — как тёмная тема раскладывает поверхности (design-review v3, раздел 5):
  - туман — вуаль из цвета карточки, а не белая: непроявленное темнее проявленного (fogCopy, кэш на обе темы);
  - лист .sheet на --card с верхней границей --line: поверхность выше страницы;
  - .go и выбранная .seg — на --film с контуром, тост — на --card с рамкой --line: не ярче главной .main;
  - «полароид» .cardp отделён от фона рамкой --line.
Проверка: python build_v3.py --only theme → v3/_test_theme.html#themeSet
"""

R = [
    # пульт: тот же режим «Как в системе», что и в «Моих данных»
    ('<button data-th="light">Светлая</button><button data-th="dark">Тёмная</button>',
     '<button data-th="system">Система</button><button data-th="light">Светлая</button><button data-th="dark">Тёмная</button>'),
    # запуск: режим из хранилища, без анимации и без объявления
    ("setTheme(lsGet('fogp-theme') || (matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'));",
     "themeInit();"),
]

CSS = r"""
/* фото цели в тёмной теме — темнее сама картинка */
:root[data-theme="dark"] .photo img.color,:root[data-theme="dark"] .mini img.color,:root[data-theme="dark"] .story .pic img.color{filter:brightness(.88)}
/* туман в тёмной теме: вуаль из цвета поверхности; запасной вариант (пока копия не готова) — тоже темнее, а не светлее */
:root[data-theme="dark"] .photo .fogfb{filter:blur(8px) saturate(.5) brightness(.55)}
:root[data-theme="dark"] .edge{background:linear-gradient(to top,color-mix(in srgb,var(--card) 80%,transparent),transparent)}
:root[data-theme="dark"] .rule{background:color-mix(in srgb,var(--ink) 70%,transparent)}
:root[data-theme="dark"] .thin{background-color:color-mix(in srgb,var(--card) 30%,transparent);background-image:repeating-linear-gradient(135deg,color-mix(in srgb,var(--card) 34%,transparent) 0 6px,transparent 6px 12px)}
@media (prefers-contrast:more){:root[data-theme="dark"] .thin{background-color:color-mix(in srgb,var(--card) 50%,transparent)}}
/* уровни поверхностей: страница → карточка/лист → рамка */
:root[data-theme="dark"] .sheet{background:var(--card);box-shadow:inset 0 1px 0 var(--line)}
:root[data-theme="dark"] .cardp{box-shadow:0 0 0 1px var(--line),0 14px 30px -16px rgba(0,0,0,.6)}
/* ярче всего на экране — только главная кнопка .main */
:root[data-theme="dark"] .go:not(.go2){background:var(--film);color:var(--ink);box-shadow:inset 0 0 0 1px var(--input)}
/* вторичная .go2 (distill) — тот же контур без заливки: белый контур 1,5 px был заметнее основной «Записать» */
:root[data-theme="dark"] .go2{box-shadow:inset 0 0 0 1px var(--input)}
:root[data-theme="dark"] .seg button[aria-pressed="true"]{background:var(--film);color:var(--ink);box-shadow:inset 0 0 0 2px var(--ink2)}
:root[data-theme="dark"] .toast{background:var(--card);color:var(--ink);box-shadow:0 0 0 1px var(--line),0 12px 28px -12px rgba(0,0,0,.6)}
/* плавная смена темы — только пока на <html> висит .theme-anim (ставит JS на 250 мс), при загрузке перехода нет */
@media (prefers-reduced-motion:no-preference){
  :root{--th-t:background-color 200ms var(--ease-out),color 200ms var(--ease-out),border-color 200ms var(--ease-out)}
  .theme-anim body,.theme-anim .app,.theme-anim .cardp,.theme-anim .bottom,.theme-anim .tabs,.theme-anim .tabs button,.theme-anim .panel,
  .theme-anim .seg,.theme-anim .seg button,.theme-anim .sec,.theme-anim .rowl,.theme-anim .mut,.theme-anim .chip,.theme-anim .bub,
  .theme-anim .go,.theme-anim .inp{transition:var(--th-t)}
  .theme-anim .sheet{transition:transform 380ms var(--ease-drawer),var(--th-t)}
  .theme-anim .press{transition:transform 160ms var(--ease-out),var(--th-t)}
  .theme-anim .toast{transition:opacity 200ms var(--ease-out),transform 200ms var(--ease-out),var(--th-t)}
}
.v3-theme .seg button{line-height:1.2;padding:4px 6px}
"""

JS = r"""
/* ── тема: «Как в системе» / «Светлая» / «Тёмная» ── */
const THEME_KEY = 'fogp-theme-mode', THEME_MQ = matchMedia('(prefers-color-scheme: dark)');
const THEME_SAY = {light:'Светлая тема', dark:'Тёмная тема'}, THEME_META = {light:'#F3F3F1', dark:'#121415'};
let themeMode = 'system', themeAnimT = null;
const themeOk = m => m === 'system' || m === 'light' || m === 'dark' ? m : 'system';
const themeNow = () => themeMode === 'system' ? (THEME_MQ.matches ? 'dark' : 'light') : themeMode;

/* туман: та же копия, что в v2 (40×40, приглушённая), но вуаль — цвет поверхности темы.
   Светлая — белая вуаль .42 (.5 у тёмных снимков), как в v2; тёмная — вуаль --card, копия темнее проявленного фото (.88).
   Копии кэшируются на обе темы, смена темы только переставляет готовую картинку — без мигания. */
const FOG_T = {};
function fogMake(img, t){
  const W = 40, H = 40, c = document.createElement('canvas'); c.width = W; c.height = H;
  const x = c.getContext('2d', {willReadFrequently:true}), k = Math.max(W / img.naturalWidth, H / img.naturalHeight), w = img.naturalWidth * k, h = img.naturalHeight * k;
  x.drawImage(img, (W - w) / 2, (H - h) / 2, w, h);
  const d = x.getImageData(0, 0, W, H).data; let L = 0; for (let i = 0; i < d.length; i += 4) L += (0.2126 * d[i] + 0.7152 * d[i+1] + 0.0722 * d[i+2]) / 255; L /= d.length / 4;
  const dim = L < 0.30, dark = t === 'dark'; x.clearRect(0, 0, W, H);
  if ('filter' in x) x.filter = `saturate(.5) brightness(${dark ? (dim ? .95 : .8) : (dim ? 1.28 : 1.1)})`;
  x.drawImage(img, (W - w) / 2, (H - h) / 2, w, h); x.filter = 'none';
  x.globalAlpha = dark ? (dim ? .35 : .45) : (dim ? .5 : .42);
  x.fillStyle = dark ? (getComputedStyle(document.documentElement).getPropertyValue('--card').trim() || '#1D2022') : '#FFFFFF';
  x.fillRect(0, 0, W, H); x.globalAlpha = 1;
  return c.toDataURL('image/jpeg', .8);
}
fogCopy = function(img){ const s = img.src, t = document.documentElement.dataset.theme === 'dark' ? 'dark' : 'light', m = FOG_T[s] || (FOG_T[s] = {});
  return m[t] || (m[t] = fogMake(img, t)); };
/* смена темы: готовые туманные копии пересобираются под новую поверхность; старая картинка висит, пока новая не готова */
function themeFogs(){ Object.keys(FOGS).forEach(k => { if (!FOGS[k]) return; const im = new Image();
  im.onload = () => { try { FOGS[k] = fogCopy(im); } catch(e) { return; } paintPhotos(); }; im.src = srcOf(k); }); }

function themeApply(animate){ const root = document.documentElement, t = themeNow(), was = root.dataset.theme;
  if (animate && was !== t && !reduce()) { root.classList.add('theme-anim'); clearTimeout(themeAnimT); themeAnimT = setTimeout(() => root.classList.remove('theme-anim'), 250); }
  root.dataset.theme = t;
  if (was && was !== t) themeFogs();
  let m = document.querySelector('meta[name="theme-color"]');
  if (!m) { m = document.createElement('meta'); m.name = 'theme-color'; document.head.appendChild(m); }
  m.content = THEME_META[t];
  $$('[data-th]').forEach(x => x.setAttribute('aria-pressed', x.dataset.th === themeMode)); }
/* один вход для «Моих данных», пульта и demo.theme; смена объявляется тостом (role="status") */
setTheme = function(m){ themeMode = themeOk(m); lsSet(THEME_KEY, themeMode); themeApply(true);
  toast(themeMode === 'system' ? 'Как в системе: ' + THEME_SAY[themeNow()].toLowerCase() : THEME_SAY[themeMode]); };
function themeInit(){ themeMode = themeOk(lsGet(THEME_KEY)); themeApply(false); }
const themeSys = () => { if (themeMode === 'system') themeApply(true); };
if (THEME_MQ.addEventListener) THEME_MQ.addEventListener('change', themeSys); else if (THEME_MQ.addListener) THEME_MQ.addListener(themeSys);
window.demo.theme = setTheme;

/* блок «Тема» в «Моих данных» — перед ссылками о данных; оборачиваем SCR.data, чтобы не стереть правки модулей до нас.
   Пояснение к «Как в системе» — в описании кнопки (title → accessible description), а не строкой на экране (QA №16). */
const themeBlock = () => `<div class="sec v3-theme" id="v3-theme"><h2 id="v3-theme-h">Тема</h2>
  <div class="seg" role="group" aria-labelledby="v3-theme-h">${[['system','Как в системе','Меняется вместе с настройкой телефона'],['light','Светлая',''],['dark','Тёмная','']].map(x => `<button data-th="${x[0]}" aria-pressed="${themeMode === x[0]}"${x[2] ? ` title="${x[2]}"` : ''}>${x[1]}</button>`).join('')}</div></div>`;
const _themeData = SCR.data;
SCR.data = function(){ const r = _themeData.apply(this, arguments), at = '<div class="sec"><button class="link" data-sheet="policy">';
  return Object.assign({}, r, {html: r.html.includes(at) ? r.html.replace(at, themeBlock() + at) : r.html + themeBlock()}); };

/* ?s=themeSet / #themeSet — «Мои данные», блок «Тема» в видимой части */
V3_SCEN.themeSet = () => { $('#panel').classList.remove('open'); if (!S.purchases.length) { S = seed('mid'); snap(); }
  me().consent = true; go('data');
  const v = $('#view'), el = $('#v3-theme'); if (el) v.scrollTop += el.getBoundingClientRect().top - v.getBoundingClientRect().top - 72; };
"""
