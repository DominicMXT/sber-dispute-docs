---
version: alpha
name: Finance Assistant — крупная покупка к дате
description: "Мобильная PWA для пар с раздельными деньгами. Основа — дизайн-система Plasma Giga (Сбер, MIT); поверх — продуктовый слой видимости «видит партнёр / видно только вам» и спокойное пружинное движение. Эталон вёрстки — prototype/2026-09-24_mvp-prototype.html."
colors:
  background: "#FAFCFF"
  card: "#FFFFFF"
  surface: "#F2F2F2"
  outline: "#E0E0E0"
  text-primary: "rgba(8,8,8,.96)"
  text-paragraph: "rgba(8,8,8,.80)"
  text-secondary: "rgba(8,8,8,.56)"
  accent: "#122654"
  on-accent: "#FFFFFF"
  shared-soft: "#E3E5EB"
  hatch: "#DADADA"
  positive: "#13742A"
  positive-fill: "#1A9E32"
  positive-soft: "#E4F5E8"
  warning: "#A6400A"
  warning-soft: "#FEE2D2"
  calm: "rgba(8,8,8,.80)"
  calm-soft: "#F2F2F2"
  focus: "#2463EB"
  dark-background: "#171717"
  dark-card: "#262626"
  dark-surface: "#0D0D0D"
  dark-text-primary: "rgba(255,255,255,.96)"
  dark-accent: "#FFFFFF"
  dark-on-accent: "#080808"
  dark-positive: "#5FD17A"
  dark-positive-soft: "#0A2B10"
  dark-warning: "#FF9A5C"
  dark-warning-soft: "#3D1D0A"
typography:
  hero:
    fontFamily: SB Sans Display
    fontSize: 40px
    fontWeight: 600
    lineHeight: 1.05
    letterSpacing: -0.02em
    fontFeature: "tnum"
  h1:
    fontFamily: SB Sans Display
    fontSize: 26px
    fontWeight: 600
    lineHeight: 1.15
    letterSpacing: -0.015em
  h3:
    fontFamily: SB Sans Text
    fontSize: 18px
    fontWeight: 600
    lineHeight: 1.3
  body:
    fontFamily: SB Sans Text
    fontSize: 16px
    fontWeight: 400
    lineHeight: 1.4
  small:
    fontFamily: SB Sans Text
    fontSize: 14px
    fontWeight: 400
    lineHeight: 1.4
  caption:
    fontFamily: SB Sans Text
    fontSize: 13px
    fontWeight: 400
    lineHeight: 1.35
  money:
    fontFamily: SB Sans Text
    fontSize: 15px
    fontWeight: 600
    lineHeight: 1.4
    fontFeature: "tnum"
spacing:
  s1: 4px
  s2: 8px
  s3: 12px
  s4: 16px
  s5: 20px
  s6: 24px
  s8: 32px
  hit: 44px
rounded:
  sm: 8px
  md: 12px
  card: 16px
  lg: 20px
  pill: 999px
components:
  button-primary:
    backgroundColor: "{colors.accent}"
    textColor: "{colors.on-accent}"
    height: 52px
    rounded: "{rounded.md}"
  button-outline:
    backgroundColor: transparent
    textColor: "{colors.accent}"
    border: "1.5px {colors.accent}"
    height: 52px
    rounded: "{rounded.md}"
  card-shared:
    backgroundColor: "{colors.card}"
    rounded: "{rounded.card}"
    shadow: "0 0 0 1px rgba(8,8,8,.05), 0 1px 2px -1px rgba(8,8,8,.06), 0 4px 14px rgba(18,38,84,.06)"
  card-private:
    backgroundColor: transparent
    border: "1px {colors.outline}"
    rounded: "{rounded.card}"
  status-ok:
    backgroundColor: "{colors.positive-soft}"
    textColor: "{colors.positive}"
    rounded: "{rounded.card}"
  status-gap:
    backgroundColor: "{colors.warning-soft}"
    textColor: "{colors.warning}"
    rounded: "{rounded.card}"
  status-calm:
    backgroundColor: "{colors.calm-soft}"
    textColor: "{colors.calm}"
    rounded: "{rounded.card}"
  input:
    backgroundColor: "{colors.surface}"
    border: "1.5px {colors.outline}"
    height: 52px
    rounded: "{rounded.md}"
  product-card:
    backgroundColor: "{colors.card}"
    rounded: "{rounded.card}"
    padding: "{spacing.s3}"
  sheet:
    backgroundColor: "{colors.card}"
    rounded: "{rounded.lg} {rounded.lg} 0 0"
---

# Finance Assistant — дизайн-система продукта

## Overview

Человек открывает приложение, когда впереди крупная общая покупка и хочется понять: сойдётся ли к сроку и сколько можно потратить на себя сегодня. Ощущение — **спокойная уверенность**, а не восторг: деньги, пара, приватность.

Основа — **Plasma Giga** (`@salutejs/plasma-giga`, `@salutejs/plasma-themes` 0.64.0, лицензия MIT): компоненты, токены, шрифты SB Sans с CDN Сбера. Мы на конкурсе Сбера и строим на GigaChat — интерфейс говорит на языке экосистемы. **Но это не официальное приложение Сбера:** логотипа и фирменного зелёного Сбера нет, название своё.

Фирменный элемент продукта — **метка видимости** на каждом блоке: квадрат цвета акцента — «видит партнёр», штриховка — «видно только вам». Главное обещание продукта (партнёр не видит чужих денег) читается на каждом экране.

## Colors

- Все цвета — токены Plasma Giga, кроме **продуктового слоя** `positive`, `warning`, `calm`.
- Причина слоя — контраст. Зелёный Plasma `#1A9E32` на белом даёт 3,51:1, оранжевый `#FA5F05` — 3,13:1: для мелкого текста это ниже WCAG AA (4,5:1). Текст статусов берёт более тёмные оттенки (5,2:1 и 5,07:1). Цвета Plasma остаются для заливок и точек.
- `text-secondary` (56%) проходит впритык (4,62:1) — только для подписей от 13 px. Третичный текст Plasma (28%, 1,93:1) не используем для смысла.
- Перерасход «на себя» — **`calm`, не красный и не оранжевый**: человек и так расстроен, упрёк цветом уводит из продукта.
- Тёмная тема — токены `plasma_giga__dark`: акцент белый, главная кнопка белая с чёрным текстом.

## Typography

- SB Sans Display — для главного числа экрана (`hero`) и заголовка `h1`. SB Sans Text — всё остальное.
- Шрифты — с CDN Сбера по инструкции Plasma. Google Fonts не подключаем: хостинг и запросы — в России.
- Все денежные значения — табличные цифры (`tnum`), чтобы при изменении суммы строка не прыгала.
- Одна главная точка на экран: `hero` 40 px/600. Остальная иерархия — весом и цветом, а не размером.

## Layout

- Мобильный экран от 360 px. Шапка 56 px, середина прокручивается, **кнопки действий и вкладки закреплены внизу** — никогда не уезжают за длинный экран.
- Три вкладки словами: «Покупки», «Сегодня», «Мои данные». Без иконок: слова короче и понятнее.
- Все области касания — не меньше 44 × 44 px, включая ссылки. Ссылку-действие внутри абзаца не делаем — выносим отдельной кнопкой.
- Сетка отступов — кратно 4 px.

## Elevation & Depth

- Общие блоки (`card-shared`) — белая карточка с мягкой многослойной тенью.
- Личные блоки (`card-private`) — прозрачные с тонкой обводкой: визуально «тише», чем общие.
- Нижние листы — поверх затемнения; у листа есть ручка, его можно смахнуть вниз.

## Motion

Пружины из исходников Material 3 (androidx `ExpressiveMotionTokens`, `StandardMotionTokens`), переведены в CSS `linear()`; в React — те же параметры в Motion (`type: "spring"`, `damping`/`stiffness`).

| Токен | Пружина (затухание / жёсткость) | Длительность | Где |
|---|---|---|---|
| `--m-fast` | standard 0,9 / 1400 | 175 мс | мелкие перемещения |
| `--m-spatial` | standard 0,9 / 700 | 240 мс | переход между экранами |
| `--m-slow` | standard 0,9 / 300 | 355 мс | лист снизу, рост полоски прогресса |
| `--m-effects` | effects 1,0 / 1600 | 230 мс | цвет, прозрачность, **смена денежных сумм** |
| `--m-effects-fast` | effects 1,0 / 3800 | 160 мс | отклик на нажатие |
| `--m-joy` | expressive 0,6 / 800 | 370 мс | только «Сходится» и «Отложил» |

Правила:
- **Деньги — только пружиной без перелёта.** Сумма «15 000 ₽» не должна на миг показать «15 225 ₽».
- Радость (`--m-joy`, лёгкий «пружинный» масштаб) — только в двух моментах: сумма сошлась и человек отложил деньги.
- Живая точка (пульс) — только у ожидания: «партнёр ещё не открыл», «GigaChat разбирает фразу».
- При `prefers-reduced-motion` движение отключается, суммы ставятся сразу. В скрытой вкладке — тоже.

## Shapes

Скругления: поле и кнопка 12 px, карточка и статус 16 px, лист 20 px сверху, плашки статуса — полностью скруглённые. Фигур и морфинга Material 3 не берём: на iPhone выглядит как Android.

## Components

Компоненты — из `@salutejs/plasma-giga` (Button, TextField, Sheet/Modal, Tabs, Progress, Cell). Свои — только продуктовый слой:
- **метка видимости** `vis` (варианты `shared` / `private`);
- **статус покупки** с главным числом (варианты `ok` / `gap` / `calm`);
- **строка «Я понял так: … Поправить»** — объяснимый разбор фразы GigaChat;
- **карточка участника** с плашкой «по плану / отстаёт» без сумм второго;
- **карточка товара по ссылке** (`product-card`): магазин, название, цена с датой «цена на …— может измениться», метка «видит партнёр»; у партнёра — «Открыть товар в магазине». Картинку товара с чужого сервера не грузим — буква магазина на подложке акцента. Две цены (обычная и по карте банка) — показываем обе, пока человек не выбрал.

Все экраны и состояния — в прототипе, открываются ссылкой `?s=<код>`; перечень — `prototype/2026-09-24_coverage.md`.

## Do's and Don'ts

- ✅ Одна главная цифра на экран; объяснение — ниже или по запросу.
- ✅ Метка видимости на каждом блоке с деньгами.
- ✅ Кнопка называет действие: «Отправить партнёру», «Я отложил(а)».
- ✅ Главное число экрана — выше карточки товара: карточка поясняет, а не спорит.
- ❌ Красный цвет и упрёки при перерасходе.
- ❌ Суммы второго участника на экране партнёра — только «по плану / отстаёт».
- ❌ Эффекты ради эффекта: бегущие строки, лучи, конфетти — это для лендинга, не для денег.
- ❌ Логотип, фирменный зелёный и название Сбера — мы не официальное приложение банка.
