# 🚀 Postgres 17 (ru\_RU.UTF-8) + SCRAM + Python client — Docker Compose Boilerplate

![PostgreSQL](https://img.shields.io/badge/PostgreSQL-17-blue)
![Python](https://img.shields.io/badge/Python-3.12-informational)
![Docker Compose](https://img.shields.io/badge/Docker-Compose-green)
![Auth](https://img.shields.io/badge/Auth-SCRAM--SHA--256-purple)

---

## ⚡️ Быстрый старт

```bash
# 1) Первый запуск/пересборка
docker compose down -v && docker compose up --build -d

# 2) Проверить БД
docker compose ps
# или
docker compose logs -f db

# 3) Запустить клиент (спросит логин/пароль)
docker compose run --rm app
# Введите:
#   DB user: app_user
#   DB password: app_pass
```

Убедиться, что БД отвечает с хоста:

```bash
psql -h 127.0.0.1 -U app_user -d demo_db -c "select version();"
```

---

## 🧱 Что внутри

```
.
├─ app/
│  ├─ app.py                # CLI: спрашивает логин/пароль, шлёт SELECT version()
│  ├─ config.yaml           # Безопасные параметры подключения (host/port/db/sslmode)
│  ├─ requirements.txt      # Зависимости Python (psycopg, PyYAML)
│  └─ Dockerfile            # Образ клиента (python:3.12-slim)
├─ db/
│  ├─ Dockerfile            # Образ БД (postgres:17 + локаль ru_RU.UTF-8)
│  └─ initdb/
│     ├─ 00_config.sh       # listen_addresses='*', password_encryption='scram-sha-256'
│     ├─ 02_init.sql        # БД demo_db, роль app_user, права CONNECT/USAGE
│     └─ 90_pg_hba.sh       # Требуем SCRAM для всех подключений
└─ docker-compose.yml       # Два сервиса: db и app, healthcheck и depends_on
```

### 🧩 Сервисы

* **db**: PostgreSQL 17, локаль `ru_RU.UTF-8`, шифрование паролей `scram-sha-256`, healthcheck (`pg_isready`), автоматический рестарт.
* **app**: Python‑клиент. Берёт `host/port/dbname/sslmode` из `app/config.yaml`, логин/пароль спрашивает интерактивно, мержит по белому списку — никакого инъектируемого DSN.

--- 

## 🔐 Безопасность: SCRAM коротко

**SCRAM‑SHA‑256** хранит пароль как «соль + многократный SHA‑256». Клиент доказывает знание секрета без передачи самого пароля, что защищает от перехвата и упрощает ротацию. Мы включили его и для хранения (`password_encryption`) и для аутентификации (`pg_hba.conf`).

---

## 🛠️ Типовые операции

Создать новую роль приложению:

```bash
docker compose exec db psql -U postgres -d postgres \
  -c "CREATE ROLE app_login LOGIN PASSWORD 'new_pass'; GRANT CONNECT ON DATABASE demo_db TO app_login;"

docker compose exec db psql -U postgres -d demo_db \
  -c "GRANT USAGE ON SCHEMA public TO app_login;"
```

Подключиться psql внутри контейнера:

```bash
docker compose exec -it db psql -U postgres -d demo_db
```

Сбросить кластер (полная переинициализация):

```bash
docker compose down -v && docker compose up --build -d
```

---

## 📜 Лицензия

MIT

