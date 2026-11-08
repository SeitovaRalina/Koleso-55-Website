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
