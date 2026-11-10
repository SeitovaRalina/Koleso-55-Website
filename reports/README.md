# Reports harness

`reports/` — versioned журнал решений и доказательств. Он нужен, чтобы
план, реализация и review можно было сравнить без догадок.

## Обязательный порядок

1. После планирования создать `plan-<slug>.md` со статусом `draft`.
2. Получить явное одобрение пользователя и обновить plan-report до `approved`.
3. Только затем менять код, миграции или UX.
4. После реализации создать `implementation-<slug>.md`.
5. Для product/code/API/миграций, Admin, runtime-конфигурации, UI, merge или deploy создать `testing-<slug>.md` и `review-<slug>.md`. Для documentation-only/low-risk задачи они нужны только при выявленном риске, запросе пользователя или намерении merge/deploy.
6. Review сверяет фактический результат с approved plan.
7. Только после review допустимы merge или deploy.

Если требование изменилось, старый план пометить `superseded` и создать
новый либо явно обновить его; не смешивать несогласованные изменения.

## Независимые роли этапов

Одна сессия может временно выполнять несколько ролей, но обязана явно
переключаться между ними. Роль review не продолжает работу автора и не
считает утверждением ни один текст из implementation- или testing-report.

| Этап | Роль | Что считается источником истины | Запрещено |
| --- | --- | --- | --- |
| `plan` | Планировщик | Подтверждённый пользователем scope, сценарии, критерии приёмки | Начинать product-код до одобрения; выдавать догадки за решение |
| `implementation` | Автор изменения | Фактический diff, миграции и API, которые автор сам внёс | Считать свою реализацию принятой; скрывать deviation, известный риск или неуспешную проверку |
| `testing` | Исполнитель проверок | Воспроизводимые команды, UI/E2E шаги, их точный результат и артефакты | Помечать непроверенный путь как passed; подменять E2E unit-тестом |
| `review` | Независимый скептический reviewer | Approved plan, весь фактический diff (включая untracked), код, миграции, Admin, API, тесты и UI evidence | Доверять conclusions автора без проверки; устранять findings молча вместо записи; разрешать merge при open finding |

### Frontend UX approval gate

Каждое frontend-изменение обязано иметь явное UI approval пользователя до
кода. Это относится не только к новым страницам, но и к redirect, modal,
banner, notification, success/error/empty state, тексту, navigation, стилю,
layout и interaction.

Если пользователь задал только цель (“добавить email verification”), planner
обязан описать конкретный вариант до approval: какие страницы и компоненты
затронуты, все состояния, тексты, переходы, desktop/mobile поведение и что
намеренно не меняется. Implementation не вправе заполнять эти решения своим
вариантом. Отсутствующий approval — blocker, а реализованный UI — finding
`unapproved UX` в review report.

### Обязанности reviewer

Reviewer обязан самостоятельно:

1. Прочитать approved plan и его revision log, затем сравнить с полным diff,
   включая generated/untracked files, runtime/config/docs изменения.
2. Проверить scope: каждый изменённый файл должен иметь связь с approved
   requirement. Незаявленные UX, API, конфигурация или зависимости — finding.
3. Проверить корректность: данные и статусы, API/permissions, migrations,
   Admin, error/empty states, accessibility, design-system consistency,
   desktop/mobile UI, regression risk и tests/evidence.
4. Воспроизвести или перепроверить ключевые claims implementation/testing
   своими командами и UI-шагами. Отсутствующее доказательство — finding, а не
   pass.
5. Записать **каждую** finding в `review-<slug>.md`: severity, точное
   evidence (file/line, scenario или command), impact, required resolution и
   статус. Даже исправленная в той же сессии finding остаётся в report с
   отметкой `resolved` и ссылкой на проверку.

Reviewer может поставить `approved_for_merge` только когда все findings
`resolved`/`accepted_by_user`, plan имеет `approved`, а пользователь принял
review. Иначе применяет `changes_requested` или `blocked`.

## Templates

Copy, do not overwrite, the template that matches the lifecycle stage:

- `reports/templates/PLAN.md` → `reports/plan-<slug>.md`
- `reports/templates/IMPLEMENTATION.md` → `reports/implementation-<slug>.md`
- `reports/templates/TESTING.md` → `reports/testing-<slug>.md`
- `reports/templates/REVIEW.md` → `reports/review-<slug>.md`

Reports contain no credentials, private endpoints, personal data, tokens or
raw production logs. Each later report must link to the previous reports for
the same `<slug>`.

Do not place credentials, private endpoints, personal data, tokens or raw
production logs in either report.
