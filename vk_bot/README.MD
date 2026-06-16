# Документация по переменным окружения EXAMPEL PROJECT

## Необходимые переменные окружения

Перед запуском проекта необходимо получить и заполнить следующие переменные окружения:

### Telegram

- `API_TOKEN` — токен Telegram-бота
- `WEBHOOK_URL` — URL для webhook Telegram-бота
- `FRONTEND_URL` — URL фронтенд части проекта

---

# Пример `.env` файла

```env
# =========================
# Telegram
# =========================
API_TOKEN=
WEBHOOK_URL=
FRONTEND_URL=


# =========================
# PostgreSQL
# =========================
PG_PORT=5432
POSTGRES_USER=
POSTGRES_PASSWORD=
POSTGRES_DB=music-findef-db
PG_HOST=db

DB_POSTGRE=postgresql+asyncpg://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${PG_HOST}:${PG_PORT}/${POSTGRES_DB}

# =========================
# Backend
# =========================
WEBAPP_PORT=8080

# =========================
# Docker
# =========================
PG_CONTAINER_NAME=
BACKEND_CONTAINER_NAME=


| Переменная     | Назначение               | Пример                        |
| -------------- | ------------------------ | ----------------------------- |
| `API_TOKEN`    | Токен Telegram-бота      | `65828fe911:AAG...`           |
| `WEBHOOK_URL`  | URL для webhook Telegram | `https://example.com/webhook` |
| `FRONTEND_URL` | URL фронтенда проекта    | `https://music-findef.app`    |


| Переменная          | Назначение                    | Пример                     |
| ------------------- | ----------------------------- | -------------------------- |
| `PG_PORT`           | Порт PostgreSQL               | `5432`                     |
| `POSTGRES_USER`     | Пользователь БД               | `postgres`                 |
| `POSTGRES_PASSWORD` | Пароль БД                     | `password`                 |
| `POSTGRES_DB`       | Название базы данных          | `music-findef-db`          |
| `PG_HOST`           | Хост PostgreSQL               | `db`                       |
| `DB_POSTGRE`        | Строка подключения SQLAlchemy | `postgresql+asyncpg://...` |


| Переменная               | Назначение                | Пример                  |
| ------------------------ | ------------------------- | ----------------------- |
| `WEBAPP_PORT`            | Порт backend приложения   | `8080`                  |
| `PG_CONTAINER_NAME`      | Имя PostgreSQL контейнера | `music-findef-postgres` |
| `BACKEND_CONTAINER_NAME` | Имя backend контейнера    | `music-findef-backend`  |


# Запуск проекта

## Docker Compose

Для запуска проекта выполните команду:

```bash
docker compose up --build