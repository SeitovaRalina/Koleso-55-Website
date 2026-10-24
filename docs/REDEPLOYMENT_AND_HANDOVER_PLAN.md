# Redeployment and handover plan

> Current runtime state, resource limit, verified routes, and unresolved
> follow-up work are recorded in `docs/AGENT_HANDOVER.md` (updated 2026-10-24).

Цель: восстановить production сайта «Колесо путешествий 55» на новом Timeweb VPS, подключить новую PostgreSQL DBaaS и подготовить передачу администрирования заказчику.

Ограничение: работающий `candidate-screening-bot.service` нельзя останавливать, перезапускать или изменять.

## 1. Безопасный аудит VPS

- [x] Проверить SSH-доступ, ОС, RAM, диск и private network.
- [x] Инвентаризировать systemd services и открытые порты.
- [x] Подтвердить, что Telegram-бот работает отдельно от сайта.
- [x] Проверить DNS домена.
- [ ] Зафиксировать базовые метрики бота до и после деплоя.

## 2. Базовая инфраструктура

- [x] Добавить swap без перезагрузки VPS.
- [x] Установить Docker Engine, Compose plugin, Certbot и PostgreSQL client.
- [x] Настроить Docker registry mirror и log rotation при необходимости.
- [ ] Настроить firewall без блокировки SSH и Timeweb monitoring.

## 3. PostgreSQL DBaaS

- [x] Проверить TCP-доступ к DBaaS через private network.
- [x] Проверить имя БД и application user.
- [x] Проверить/включить расширение `vector`.
- [x] Применить Django и Alembic migrations.
- [x] Проверить доступ каждого backend-сервиса к БД.

## 4. Production deployment

- [x] Разместить текущую ветку в `/opt/koleso` отдельным Docker Compose project.
- [x] Установить `backend/.env.production` с правами `600`.
- [x] Собрать production images.
- [x] Запустить сервисы без вмешательства в Telegram-бот.
- [x] Проверить health checks, logs, restart counts, RAM и swap.

## 5. Домен, HTTPS и почта

- [x] Перенаправить `koleso-travel55.ru` и `www` на новый public IPv4.
- [ ] Выпустить Let's Encrypt certificate и проверить auto-renewal.
- [x] Проверить SMTP авторизацию и доставку письма.
- [ ] Проверить MX, SPF, DKIM и DMARC корпоративной почты.

## 6. Endpoint audit

- [ ] Получить список Django endpoint'ов из OpenAPI schema.
- [ ] Получить список recommender endpoint'ов из FastAPI OpenAPI.
- [ ] Проверить public read endpoints.
- [ ] Проверить регистрацию, вход, refresh/logout, email verification и password reset.
- [ ] Проверить authenticated profile, wishlist, reviews и orders на тестовых данных.
- [ ] Проверить analytics, recommender и assistant flows.
- [ ] Проверить Django Admin и права staff user.
- [ ] Исправить найденные ошибки, добавить regression tests и повторить smoke.

## 7. Передача заказчику

- [x] Подготовить руководство по Django Admin.
- [x] Создать отдельную staff-группу с минимальными правами (`Content managers`).
- [ ] Описать создание/редактирование экскурсий, слотов, заказов и модерацию отзывов.
- [x] Описать резервное копирование, обновление, rollback и аварийные контакты.
- [ ] Удалить тестовые данные и временные credentials.

## Definition of Done

- Telegram-бот продолжает работать без перезапуска.
- Все production-контейнеры healthy.
- Сайт и API доступны только через HTTPS.
- DBaaS, SMTP и обязательные пользовательские flows проверены.
- Заказчик получает отдельный staff account и актуальную документацию.
