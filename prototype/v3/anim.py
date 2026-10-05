# -*- coding: utf-8 -*-
"""Модуль v3 «Анимации»: строки 1–7 из design/2026-10-04_animation-opportunities.md.

Разметку чужих модулей не правит: оборачивает render() и после отрисовки находит элементы
по селекторам v2 и по общим классам контракта (.v3-example, .v3-member, .v3-answer-line,
[data-v3-money], .v3-day). Классов ещё нет — ничего не делает.

Строки:
  1. Э-05, вход ответа: строки по очереди, opacity 0→1 + translateY(6px→0), 240 мс --ease-out,
     шаг 50 мс, не больше 4 шагов; «Сходится» — существующий pop 380 мс, только при «сходится».
  2. Главная сумма: старое значение вверх (opacity→0, translateY(-6px)) 160 мс, новое снизу 200 мс
     --ease-out. Без перебора цифр и перелёта. reduced-motion — только opacity 120 мс.
     Прерываемая (QA №15): нажатие во время смены не повторяет уход — новое число входит сразу,
     «старое» берётся из памяти модуля, а не из DOM. Проба: scratchpad/qa4 `node cdp.mjs "" p_mo.js`.
  3. Пример → своя цель: снимок примера уходит opacity→0 + scale(.98) 200 мс, новый экран
     входит из opacity 0 + translateY(12px) 280 мс --ease-out.
  4. Тема: делает модуль theme (.theme-anim). Здесь — ничего, цветовые свойства не трогаются.
  5. Новый участник .v3-member: scale(.96)+opacity 0 → норма, 240 мс --ease-out, один раз на участника.
  6. Ячейка дня .wd i и .v3-day: clip-path inset(100% 0 0 0) → inset(0), 320 мс --ease-out,
     только у ячейки, которая закрасилась на этом же экране. reduced-motion — сразу цвет.
  7. #view: opacity .6 → 1 за 120 мс при смене экрана, без сдвига. Выключатель — V3_ANIM_VIEW_FADE.

Только transform, opacity, clip-path; кривые — токены v2; нажатия не блокируются.
"""

R = []

CSS = r"""
/* строка 1 — ответ Э-05 */
.v3-line{animation:v3-line 240ms var(--ease-out) both;animation-delay:var(--v3-d,0ms)}
@keyframes v3-line{from{opacity:0;transform:translateY(6px)}}
.v3-pop,.v3-line.v3-pop{animation:pop 380ms var(--ease-out) both;animation-delay:var(--v3-d,0ms)}
/* строка 2 — смена суммы */
.v3-ib{display:inline-block}
.v3-mout{animation:v3-mout 160ms var(--ease-out) forwards}
@keyframes v3-mout{to{opacity:0;transform:translateY(-6px)}}
.v3-min{animation:v3-min 200ms var(--ease-out) both}
@keyframes v3-min{from{opacity:0;transform:translateY(6px)}}
/* строка 3 — пример → своя цель */
.view.v3-ghost{pointer-events:none;z-index:1;transform-origin:50% 30%;animation:v3-ghost 200ms var(--ease-out) forwards}
@keyframes v3-ghost{to{opacity:0;transform:scale(.98)}}
.view.v3-ex-in{animation:v3-ex-in 280ms var(--ease-out) both}
@keyframes v3-ex-in{from{opacity:0;transform:translateY(12px)}}
/* строка 5 — новый участник */
.v3-member.v3-join{animation:v3-join 240ms var(--ease-out) both}
@keyframes v3-join{from{opacity:0;transform:scale(.96)}}
/* строка 6 — ячейка дня */
.wd.on i.v3-filling{background:var(--film)}
.v3-fillbar{position:absolute;inset:0;border-radius:inherit;background:var(--fill);animation:v3-fill 320ms var(--ease-out) both}
.v3-day.v3-fill{animation:v3-fill 320ms var(--ease-out) both}
@keyframes v3-fill{from{clip-path:inset(100% 0 0 0)}to{clip-path:inset(0)}}
/* строка 7 — проявление экрана */
.view.v3-vin{animation:v3-vin 120ms var(--ease-out)}
@keyframes v3-vin{from{opacity:.6}}
@keyframes v3-fade{from{opacity:0}}
@keyframes v3-fade-out{to{opacity:0}}

@media (prefers-reduced-motion:reduce){
  .v3-line,.v3-pop,.v3-line.v3-pop,.v3-member.v3-join,.v3-min,.view.v3-ex-in{animation:v3-fade 120ms var(--ease-out) both;animation-delay:0ms}
  .v3-mout{animation:none}
  .view.v3-ghost{animation:v3-fade-out 120ms var(--ease-out) forwards}
  .v3-fillbar{display:none} .wd.on i.v3-filling{background:var(--fill)} .v3-day.v3-fill{animation:none}
  .view.v3-vin{animation:none}
}
"""

JS = r"""
const V3_ANIM_VIEW_FADE = true;   /* строка 7: false — выключить проявление #view при смене экрана */
(() => {
  let depth = 0, lastKey = null, lastScreen = null, ready = false;
  const seen = new Set();                       /* участники, которых уже показывали */
  setTimeout(() => { ready = true; }, 0);       /* отрисовки при запуске и по ?s= — без движения */
  const keyOf = () => [S.scr, S.cur, S.who, S.off ? 1 : 0].join('|');
  const screenOf = () => S.scr + '|' + S.cur;
  const play = (el, cls) => { el.classList.remove(cls); void el.offsetWidth; el.classList.add(cls); };
  const moneyEl = (scr, v) => $('[data-v3-money]', v) || (scr === 'purchase' ? $('[data-out="my-left"]', v) || $('.big', v) : null);
  const isOn = el => el.matches('.on, .done, .filled, [data-v3-on]');
  const memberKey = el => S.cur + ':' + (el.dataset.v3Member || el.dataset.who || el.dataset.id || el.getAttribute('aria-label') || el.textContent.trim().split(/\s+/)[0]);

  /* строка 3: снимок примера уходит, новый экран входит */
  function exitExample(ex, v){
    const g = ex.node; g.removeAttribute('id'); $$('[id]', g).forEach(x => x.removeAttribute('id'));
    g.classList.remove('v3-vin', 'v3-ex-in'); g.classList.add('v3-ghost'); g.setAttribute('aria-hidden', 'true'); g.inert = true;
    v.after(g); g.scrollTop = ex.top;
    const kill = () => g.remove(); g.addEventListener('animationend', e => { if (e.target === g) kill(); }); setTimeout(kill, 600);
    play(v, 'v3-ex-in');
  }
  /* строка 1: строки ответа по очереди, «Сходится» — поп */
  function answerIn(v){
    let ls = $$('.v3-answer-line', v);
    if (!ls.length) ls = [...v.children].filter(x => !x.matches('.backb') && !x.querySelector('[data-sheet="feedback"]'));
    ls.forEach((x, i) => {
      x.style.setProperty('--v3-d', Math.min(i, 3) * 50 + 'ms'); x.classList.add('v3-line');
      const big = x.matches('.big') ? x : $('.big', x);
      if (big && /^сходится/i.test(big.textContent.trim())) big.classList.add('v3-pop');
    });
  }
  /* строка 2: старое значение уходит вверх, новое входит снизу.
     Прерываемость (QA №15): пока идёт уход, в DOM лежит старое число — поэтому «что было» берётся из mSwap, а не из DOM;
     если прошлая смена ещё не доиграла (уход 160 + вход 200 мс), уход не повторяется: новое число входит сразу.
     Итог: последнее нажатие показывает верное число не позже 220 мс (обычно сразу или через 160 мс). */
  let mSwap = null;                              /* {n, txt, html, out, t}: элемент и настоящее (новое) значение */
  const MONEY_BUSY = 380;
  function moneyNow(n){
    if (!n) return null;
    if (mSwap && mSwap.n === n && mSwap.out) return {txt: mSwap.txt, html: mSwap.html};
    return {txt: n.textContent, html: n.innerHTML};
  }
  function moneySwap(m, v){
    if (!m) return; const n = moneyEl(S.scr, v); if (!n) return;
    const txt = n.textContent, html = n.innerHTML, t = performance.now();
    const busy = !!mSwap && t - mSwap.t < MONEY_BUSY;   /* прошлая смена ещё идёт (её уход прерван новой отрисовкой) */
    if (mSwap) mSwap.out = false;                         /* таймер прошлой смены больше ничего не подставит */
    if (txt === m.txt) { mSwap = busy ? {n, txt, html, out: false, t: mSwap.t} : null; return; }
    if (getComputedStyle(n).display === 'inline') n.classList.add('v3-ib');
    if (reduce() || busy) { mSwap = {n, txt, html, out: false, t}; return play(n, 'v3-min'); }
    const s = mSwap = {n, txt, html, out: true, t};
    const swap = () => { if (!s.out) return; s.out = false; if (!n.isConnected) return; n.innerHTML = html; n.classList.remove('v3-mout'); play(n, 'v3-min'); };
    n.innerHTML = m.html; n.classList.add('v3-mout');
    n.addEventListener('animationend', e => { if (e.target === n && e.animationName === 'v3-mout') swap(); }); setTimeout(swap, 220);
  }
  /* строка 6: закрасилась ячейка, которая на этом же экране была пустой */
  function daysFill(b, v){
    if (reduce()) return;
    $$('.wd', v).forEach((x, i) => { const c = $('i', x); if (!c || !x.classList.contains('on') || b.wd[i] !== false) return;
      const bar = document.createElement('span'); bar.className = 'v3-fillbar'; bar.setAttribute('aria-hidden', 'true');
      c.classList.add('v3-filling'); c.prepend(bar);
      const end = () => { bar.remove(); c.classList.remove('v3-filling'); }; bar.addEventListener('animationend', end, {once:true}); setTimeout(end, 500); });
    $$('.v3-day', v).forEach((x, i) => { if (isOn(x) && b.vd[i] === false) play(x, 'v3-fill'); });
  }
  /* строка 5: участник входит один раз — при первом появлении */
  function members(v, animate){
    $$('.v3-member', v).forEach(x => { const k = memberKey(x); if (seen.has(k)) return; seen.add(k); if (animate) x.classList.add('v3-join'); });
  }

  const _render = render;
  render = function(...a){
    if (depth) return _render.apply(this, a);
    const v = $('#view'), prevKey = lastKey, prevScreen = lastScreen;
    const m0 = prevKey ? moneyEl(prevKey.split('|')[0], v) : null;
    const b = {
      money: moneyNow(m0),
      wd: $$('.wd', v).map(x => x.classList.contains('on')),
      vd: $$('.v3-day', v).map(isOn),
      ex: $('.v3-example', v) ? {node: v.cloneNode(true), top: v.scrollTop} : null };
    depth++; let r;
    try { r = _render.apply(this, a); } finally { depth--; }
    lastKey = keyOf(); lastScreen = screenOf();
    try {
      if (!ready) { members(v, false); return r; }
      const changed = prevScreen !== lastScreen; let viewDone = false;
      if (b.ex && !$('.v3-example', v)) { exitExample(b.ex, v); viewDone = true; }
      else if (S.scr === 'answer' && changed) { answerIn(v); viewDone = true; }
      if (!viewDone && changed && V3_ANIM_VIEW_FADE && !reduce()) play(v, 'v3-vin');
      if (prevKey === lastKey) { moneySwap(b.money, v); daysFill(b, v); }
      members(v, true);
    } catch (e) { console.warn('v3 anim:', e); }
    return r;
  };
})();
"""
