# Лабораторная работа №6
## Хранение и доступ к секретам (HashiCorp Vault)

## Описание

В рамках лабораторной работы реализовано безопасное хранение секретов с использованием HashiCorp Vault.
Логин и пароль для подключения к базе данных PostgreSQL хранятся в Vault и получаются сервисом динамически.

Для доступа к секретам используется метод аутентификации AppRole.

---

# Архитектура

Используются следующие сервисы:

- pinger — сервис, выполняющий запросы к базе данных
- postgres — база данных PostgreSQL
- vault — система хранения секретов HashiCorp Vault

Сервис pinger перед запросом к базе данных:

1. Аутентифицируется в Vault через AppRole
2. Получает секрет с логином и паролем
3. Использует полученные данные для подключения к PostgreSQL

---

# Запуск проекта

Запуск контейнеров:

docker compose up -d

Проверка контейнеров:

docker compose ps

---

# Настройка Vault

Войти в контейнер:

docker exec -it vault sh

Указать адрес Vault:

export VAULT_ADDR=http://127.0.0.1:8200

Авторизация:

vault login root

---

# Настройка доступа

Включить AppRole:

vault auth enable approle

Создать секрет для БД:

vault kv put secret/db username=dbuser password=dbpassword

Создать политику:

vault policy write db-policy /vault/policy.hcl

Создать AppRole:

vault write auth/approle/role/pinger token_policies="db-policy"

Получить role-id:

vault read auth/approle/role/pinger/role-id

Получить secret-id:

vault write -f auth/approle/role/pinger/secret-id

---

# Проверка работы

Проверить секрет:

vault kv get secret/db

Посмотреть логи сервиса:

docker compose logs pinger

При корректной работе в логах отображается информация о подключении к PostgreSQL.

---

# Тестирование

Изменить пароль в Vault:

vault kv put secret/db username=dbuser password=wrong

После изменения секрета сервис перестанет подключаться к базе данных.
Это подтверждает, что сервис получает секрет непосредственно из Vault.
