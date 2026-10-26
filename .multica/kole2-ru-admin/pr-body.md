## Результат

- Гостевая заявка на сертификат сохраняется через `POST /api/bookings/certificate-requests/` без онлайн оплаты.
- Django Admin показывает покупателя, получателя, номинал, формат и статус; менеджер меняет статус.
- Форма показывает успех только после `201`, сохраняет ошибку при неуспешном запросе. Необоснованные обещания отправки и условий сертификата удалены.
- Diff PR проверен: только 10 файлов KOLE-2, без временных файлов и чужих изменений. Работа в `feature/KOLE-2-certificate-requests`.

## Проверки — 26.10.2026, локально

Изолированная PostgreSQL `kole2-admin-db-1025` без общего тома; Django `kole2-admin-web-1026` с текущим checkout на `127.0.0.1:18183`. Production и чужие контейнеры не менялись.

- `docker exec kole2-admin-web-1026 python manage.py check` — `System check identified no issues`.
- `docker exec kole2-admin-web-1026 python manage.py makemigrations bookings --check --dry-run` — `No changes detected in app 'bookings'`.
- `docker exec kole2-admin-web-1026 python manage.py test bookings.test_certificates --noinput` — 7 тестов, `OK`, PostgreSQL test DB. Проверены создание, валидация, запрет публичного списка, запрет клиентской смены статуса, повторная подача как отдельная заявка, права Admin, смена статуса и отказ неверному статусу.
- `npm run lint` — успешно. `npm run build` — успешно; предупреждение Vite о чанке свыше 500 kB.
- Chrome E2E: `http://127.0.0.1:5173/certificates` → реальный `POST` дал `201`, заявка `#2` появилась в `http://127.0.0.1:18183/admin/bookings/giftcertificaterequest/`. В деталях совпали покупатель, получатель, 3000 ₽ и электронный формат. Смена `new` → `in_progress` сохранилась и видна в списке и деталях. Desktop 1440×900, mobile 390×844: горизонтального переполнения нет. Скриншоты ниже сделаны в браузере с вымышленными данными.

CI: на ветке нет зарегистрированных checks (`gh pr checks 8`: `no checks reported`).

## Ручная проверка

В тестовом окружении применить миграции, открыть `/certificates`, отправить гостевую заявку. В `/admin/bookings/giftcertificaterequest/` проверить список, детали, фильтр по статусу и смену статуса. Недопустимый номинал должен вернуть `400`; ошибка API не должна показывать успех.

Оплата, выпуск и отправка сертификата остаются ручной обработкой менеджера. Деплоя и merge не было.

![Форма сертификата — desktop 1440x900](https://github.com/user-attachments/assets/b96067b5-a6db-4656-ae77-b12f4157513b)

![Форма сертификата — mobile 390x844](https://github.com/user-attachments/assets/54fc24e8-9c1c-4aa1-a2c5-10ca1a31fd0a)

![Успех после реального HTTP 201](https://github.com/user-attachments/assets/54d1ead2-c56a-4e46-a9fa-36ea371aad41)

![Django Admin — список и сохранённый статус](https://github.com/user-attachments/assets/be671df6-42a7-4229-bdca-f2c4924ced5e)

![Django Admin — детали заявки](https://github.com/user-attachments/assets/2487a285-e40a-482f-a64a-10929f26fec4)

## Дополнение: русификация Django Admin — 26.10.2026

- Русские подписи всех полей, подсказки, заголовки и хлебные крошки списка, создания и редактирования. Стандартные сообщения после сохранения согласованы с женским родом слова «заявка».
- Поля покупателя и получателя доступны при создании и редактировании в Admin; даты остаются только для чтения. API-поля и значения статусов не изменены.
- Миграции `bookings.0004` и `bookings.0005` меняют только отображаемые подписи, подсказки и имя модели.
- Изолированные локальные PostgreSQL и Django, порт `127.0.0.1:18184`: `python manage.py check` — 0 ошибок; `python manage.py makemigrations bookings --check --dry-run` — изменений нет; `python manage.py test bookings.test_certificates --noinput` — 8/8 на PostgreSQL. Реальные миграции применены при запуске Django.
- Chrome E2E: в Admin создана заявка #2 с вымышленными данными, затем статус изменён `Новая` → `В работе` → `Обработана`; список показывает сохранённый статус. Проверены русские форма, список, фильтры и сообщения. Desktop 1440×900, mobile 390×844; на mobile страница без горизонтального переполнения.
- Diff PR содержит только файлы KOLE-2. Два посторонних gitlink из task branch удалены добавочным коммитом. Production, чужие контейнеры и общие тома не затронуты. Деплоя и merge не было.

Ручная проверка: открыть `/admin/bookings/giftcertificaterequest/`, создать заявку, заполнить контакты, номинал и формат, сохранить; открыть карточку, изменить статус, проверить его в списке и фильтре. Скриншоты реального Admin приложены ниже.

![Django Admin: создание заявки, 1440x900](https://github.com/user-attachments/assets/c466550c-f952-42ef-baf0-53da1a6adadd)

![Django Admin: редактирование заявки, 1440x900](https://github.com/user-attachments/assets/8869c055-f6a2-4801-bf09-036fb3549020)

![Django Admin: форма создания, 390x844](https://github.com/user-attachments/assets/a670ff4f-5326-48c4-b0fb-ee7aebd9e782)
