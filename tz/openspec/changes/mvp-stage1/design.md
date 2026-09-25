# Технический подход

Это рекомендация, а не приказ: разработчик может выбрать иначе, если сохранит инварианты
из `openspec/project.md` и сценарии спецификаций. Интерфейс — как в прототипе
`prototype/2026-09-24_mvp-prototype.html`, токены и компоненты — `prototype/DESIGN.md`.

## Схема

```
Телефон (PWA, React)  ──HTTPS──►  FastAPI  ──►  PostgreSQL
      │  расчёт советов на клиенте      │
      │  для мгновенного пересчёта      ├──►  GigaChat API (SDK gigachat)
      │                                 ├──►  страница магазина (httpx + extruct)
      └─ Web Share API                  ├──►  разбор выписки в памяти (csv / Sberbank2Excel)
                                        └──►  фоновая задача раз в сутки: цены по ссылкам (Р3)
```

Расчётные функции (`calc`, `daily`, `analyze`, `tips`, `auto_pick`) живут на сервере в модуле
`money/` и покрыты тестами по `tz/fixtures/`. Клиент повторяет только `tips` и пересчёт суммы
к сроку при переключении советов — тем же тестам на TypeScript.

## Модель данных

| Таблица | Поля | Заметки |
|---|---|---|
| `users` | `id uuid`, `created_at`, `device_hash`, `consent_at`, `consent_version`, `source_tag`, `is_test`, `is_related`, `tz` | никаких имён, телефонов, почт до Т16 |
| `purchases` | `id`, `owner_id`, `title`, `sum`, `date`, `created_at`, `status` (`active`/`done`/`cancelled`), `link_url`, `link_store`, `link_title`, `link_price`, `link_card_price`, `link_price_date`, `link_new_price` | `link_url` — уже без меток |
| `participants` | `purchase_id`, `user_id`, `role` (`owner`/`partner`), `share`, `saved`, `joined_at`, `left_at` | `share` и `saved` отдаются только самому участнику |
| `invites` | `token` (случайные 128 бит), `purchase_id`, `created_at`, `opened_at`, `accepted_by`, `revoked_at` | одно принятие на токен |
| `savings_events` | `id`, `purchase_id`, `user_id`, `amount` (+/−), `kind` (`saved`/`took`), `at` | |
| `money_profiles` | `user_id`, `income_month`, `mandatory_month`, `pay_days int[]`, `source` (`manual`/`statement`), `updated_at` | |
| `spends` | `id`, `user_id`, `amount`, `label`, `local_day date`, `created_at` | `local_day` — по поясу устройства |
| `statement_summaries` | `user_id`, `period_from`, `period_to`, `ops_count`, `income_month`, `pay_days`, `recurring jsonb`, `categories jsonb`, `tips jsonb`, `tips_on jsonb`, `created_at` | только сводка, имена и номера уже скрыты |
| `feedback` | `id`, `user_id`, `screen`, `text`, `at` | удаляется с пользователем |
| `events` | см. `specs/telemetry` | без сумм и текстов, не удаляется |

Деньги — `integer` рублей: копейки в расчётах не нужны, выписка округляется до рубля при разборе.

## API

| Метод | Путь | Требование |
|---|---|---|
| POST | `/api/session` | Т1 |
| POST | `/api/consent` | Т2 |
| POST | `/api/purchases/parse` `{text}` → `{fields, missing, masked}` | Т3 |
| POST | `/api/purchases/link` `{url, text}` → `{ok, store, title, price, card_price, currency, fields}` | Т3а |
| POST | `/api/purchases` `{fields}` → `{purchase, calc, coach_text}` | Т4, Т5 |
| GET | `/api/purchases`, `/api/purchases/{id}` | Т4, Т9 |
| POST | `/api/purchases/{id}/actions` `{text}` — «отложил», «взял», «моя часть», «перенести», «отменить» | Т9, случаи 10, 14, 37 |
| POST/DELETE | `/api/purchases/{id}/invite` | Т6, Т7, случай 9 |
| GET | `/api/invites/{token}` — предпросмотр | Т7 |
| POST | `/api/invites/{token}/accept` `{text}` | Т8 |
| POST | `/api/money` `{text}` или `{fields}` | Т10 |
| POST | `/api/spends` `{text}` · GET `/api/today` | Т11 |
| POST | `/api/statement` (multipart, ≤ 5 МБ) · DELETE `/api/statement` · PUT `/api/statement/tips` · PUT `/api/statement/recurring` | Т19, Т20 |
| POST | `/api/segment`, `/api/feedback` | Т13, Т18 |
| DELETE | `/api/me` | Т12 |

Ответы для партнёра собираются отдельной схемой Pydantic `PartnerPurchaseView` — в ней физически нет полей чужих денег (инвариант 3).

## Контракты GigaChat

Все вызовы — через один модуль `llm/` с общей функцией маскирования на входе, таймаутом 5 с,
`temperature=0` для разбора, записью `model_call` в журнал. Структурный ответ — через function calling.

**1. `parse_purchase`** — вход: маскированная фраза, сегодняшняя дата, пояс. Выход:
```json
{"title": "string", "sum_rub": "integer|null", "date": "YYYY-MM-DD|null",
 "share_rub": "integer|null", "pays_alone": "boolean", "currency": "RUB|EUR|USD|OTHER",
 "date_has_year": "boolean"}
```
Код после ответа: `pays_alone → share = sum`; «25» при сумме от 1 000 → 25 000; `missing` считает код, не модель.
Приёмка — `fixtures/phrases.json`, 18 из 20.

**2. `parse_action`** — короткие фразы на экранах покупки, «Сегодня», «Деньги в месяц». Выход:
```json
{"intent": "spend|saved|took|share_change|date_change|cancel|money_profile|partner_share|unknown",
 "amount_rub": "integer|null", "label": "string|null", "date": "YYYY-MM-DD|null",
 "income_month": "integer|null", "pay_days": "integer[]", "mandatory_month": "integer|null"}
```
Сначала пробуются правила (число + ключевое слово: «отложил», «взял», «кофе 300»); модель — только если правила не узнали фразу.

**3. `coach_answer`** — вход: JSON с посчитанными кодом числами и 1–2 вариантами. Выход — текст до 280 знаков.
Сверка: все числа из текста (нормализация «15 000», «15000», «15 тыс») должны быть в множестве входных чисел и дат, иначе шаблон (случай 3).

**4. `categorize`** — вход: до 50 маскированных описаний операций. Выход — массив категорий из фиксированного списка:
Продукты, Доставка еды, Кафе и кофе, Такси, Маркетплейсы, Подписки, Связь и интернет, ЖКУ, Переводы, Другое.

**5. `read_screenshot`** (Р3, Т15) — изображение уведомления → `{amount_rub, label}`; человек подтверждает перед записью.

Одна фраза даёт честно 2–3 вызова: разбор, расчёт как вызов инструмента, формулировка ответа. Вызовы вне сценария не засчитываются.

## Ссылка на товар

`httpx` с таймаутом 5 с, лимит 2 МБ, не больше 3 переадресаций; перед каждым запросом — разрешить
DNS и отказать частным и локальным адресам. Разбор: `extruct` — JSON-LD и microdata `Product/Offer`
(`price`, `priceCurrency`, `name`), затем Open Graph (`og:title`, `product:price:amount`). Больше одной цены
в предложениях — вопрос «Какую цену берём?». Метки срезаются по списку из `fixtures/links.json`.

## Выписка

1. Файл читается в память (`SpooledTemporaryFile`, `finally` — удаление), на диск не пишется. В логи сервера имя файла и содержимое не пишутся.
2. CSV: определение кодировки (UTF-8, затем cp1251), разделителя по первой строке, колонок по заголовкам. PDF: если это выписка Сбербанка — `Sberbank2Excel` в операции; иначе — случай 29.
3. Операции → маскирование описаний → дедупликация → `analyze` (как в прототипе, вектор — `statement-demo.expected.json`) → категории по правилам → `categorize` для оставшихся → советы → `auto_pick`.
4. В базу — только `statement_summaries`.

Перед подключением `Sberbank2Excel` проверить: ставится ли пакетом, какие у него зависимости и их лицензии; если пакета нет — положить модуль в `vendor/` с файлом лицензии MIT.

## Безопасность и секреты

- Ключ GigaChat, соль для хэшей, строка подключения к базе — только в хранилище секретов облака или переменных окружения стенда. Не в репозитории, не в `.env` в git. Перед каждым пушем — проверка на секреты.
- Хэш IP и устройства — HMAC-SHA256 с солью из секретов.
- Ограничение частоты: 20 вызовов модели в час и 60 запросов API в минуту на идентификатор.
- CORS — только свой домен. Заголовки: CSP без внешних скриптов, кроме шрифтов.

## Тесты

| Что | Чем | Порог |
|---|---|---|
| Расчёт, «сегодня», выписка, советы, ссылки | юнит-тесты по `tz/fixtures/*.json` с подменой «сегодня» и пояса | 100% векторов |
| Разбор фраз GigaChat | прогон 20 фраз против настоящего API, отдельная команда, не в каждом CI | 18 из 20 |
| Партнёр не видит чужого | тест схемы ответа `PartnerPurchaseView` | 0 лишних полей |
| Маскирование | перехват всех вызовов клиента GigaChat | 0 номеров |
| Файл выписки удалён | каталог временных файлов пуст после запроса, включая запрос с ошибкой | 0 файлов |
| Сквозной сценарий | Playwright на ширине 375 px: фраза → ответ → выписка → «сходится» | проходит |

## Окружения

`dev` (локально), `stage` (`is_test=true` для всех событий), `prod`. Переменные: `GIGACHAT_CREDENTIALS`,
`GIGACHAT_SCOPE`, `DATABASE_URL`, `HASH_SALT`, `TEAM_DEVICE_IDS`, `RELATED_DEVICE_IDS`, `APP_ENV`.
