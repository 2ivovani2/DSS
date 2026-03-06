# task3 — CS:GO Skins Marketplace

## Быстрый старт (Docker Compose)
1) `docker compose up --build` — поднимет Postgres и CLI контейнер.
2) Применить SQL:
```
docker compose exec db psql -U $POSTGRES_USER -d $POSTGRES_DB -f docker-entrypoint-initdb.d/01_schema.sql
docker compose exec db psql -U $POSTGRES_USER -d $POSTGRES_DB -f docker-entrypoint-initdb.d/02_seed.sql
docker compose exec db psql -U $POSTGRES_USER -d $POSTGRES_DB -f docker-entrypoint-initdb.d/03_grants.sql
```
4) Запуск примеров:
```
docker compose exec app python /app/main.py view-all users
docker compose exec app python /app/main.py view-where items --col owner_id --val 1
docker compose exec app python /app/main.py view-where-many listings --json '{"status":"active","currency":"USD"}'
docker compose exec app python /app/main.py insert-one users --json '{"username":"sh1ro","email":"sh1ro@example.com"}'
docker compose exec app python /app/main.py update-one users --id 1 --json '{"email":"pro@example.com"}'
docker compose exec app python /app/main.py update-many-same listings --target-col status --new-value cancelled --in-col id --in-values '[1,2,3]'
docker compose exec app python /app/main.py insert-related
docker compose exec app python /app/main.py bulk-insert weapons --file /app/sample_bulk_weapons.json
```
Логи летят в stdout/stderr и (при наличии `LOG_PATH`) дублируются в файл.
