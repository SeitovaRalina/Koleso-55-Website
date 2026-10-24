# Production operations

> Current production exception: read `docs/AGENT_HANDOVER.md` before using
> this runbook. The VPS has 2 GiB RAM, so the documented blanket Compose start
> command is unsafe: it can start ML workers and trigger OOM. Use selective
> service commands from the handover until the VPS RAM is increased.

Инструкция для технического владельца сайта «Колесо путешествий 55».

## Доступ и границы

- Production project: `/opt/koleso` на Timeweb VPS.
- Команда Compose всегда использует `backend/.env.production` и `backend/compose.production.yml`.
- Не останавливайте, не перезапускайте и не изменяйте `candidate-screening-bot.service`: это отдельный Telegram-бот.
- Секреты не помещают в Git, документацию, тикеты и скриншоты.

## Проверка состояния

```bash
cd /opt/koleso
docker compose --env-file backend/.env.production -f backend/compose.production.yml ps
docker compose --env-file backend/.env.production -f backend/compose.production.yml logs --tail=100 main_service nginx
curl -fsS https://koleso-travel55.ru/health/
curl -fsS https://koleso-travel55.ru/api/v1/health
curl -fsS https://koleso-travel55.ru/api/assistant/health/
systemctl is-active candidate-screening-bot.service
```

Все контейнеры должны быть `healthy`; Telegram-бот — `active`.

## Резервные копии

1. В Timeweb включите ежедневные backup/snapshot для PostgreSQL DBaaS и сохраните период хранения, согласованный с заказчиком.
2. Перед миграцией или обновлением создайте manual snapshot DBaaS в панели Timeweb.
3. Скопируйте media из Docker volume в защищённое хранилище:

```bash
docker run --rm \
  -v koleso-production_django_media:/source:ro \
  -v /opt/koleso/backups:/backup \
  alpine tar czf /backup/media-$(date +%F).tar.gz -C /source .
```

4. Проверяйте восстановление в отдельной тестовой БД. Не восстанавливайте snapshot поверх рабочей production БД без согласованного окна работ.

## Обновление

1. Сделайте backup DBaaS и media.
2. На локальной машине проверьте код, затем передайте проверенную ветку в `main`.
3. На VPS обновите исходники выбранным штатным способом (Git/CI), проверьте, что `backend/.env.production` не заменён.
4. Соберите и примените только сайт:

```bash
cd /opt/koleso
docker compose --env-file backend/.env.production -f backend/compose.production.yml up -d --build --wait
```

5. Запустите проверки из раздела «Проверка состояния», затем smoke ключевых экранов: каталог, login, admin, password reset.
6. Отдельно проверьте `systemctl is-active candidate-screening-bot.service`.

## Rollback

1. Зафиксируйте ошибку: время, URL, container logs, версия commit/image.
2. Верните предыдущую проверенную версию исходников/images.
3. Запустите `docker compose ... up -d --wait` с тем же production env.
4. Если проблема вызвана миграцией, сначала восстановите DBaaS snapshot в отдельный кластер и проверьте целостность. Обратные миграции production БД выполняйте только после backup и технического согласования.
5. Проверьте сайт, API и Telegram-бот.

## Секреты и инциденты

- При утечке пароля/ключа: сразу замените его у поставщика, обновите `.env.production` с правами `600`, пересоздайте затронутые контейнеры и отзовите старый credential.
- `GOOGLE_CLIENT_SECRET`, SMTP password, DB password, JWT/`SECRET_KEY` не сообщают заказчику и не публикуют.
- Контакты: технический владелец проекта, поддержка Timeweb, владелец домена. В финальной передаче заполните имена, email и телефон из актуального договора.
