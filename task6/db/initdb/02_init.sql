CREATE DATABASE demo_db
  TEMPLATE template0
  ENCODING 'UTF8'
  LC_COLLATE 'ru_RU.UTF-8'
  LC_CTYPE   'ru_RU.UTF-8';

DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'app_user') THEN
    CREATE ROLE app_user LOGIN PASSWORD 'app_pass';
  END IF;
END$$;

GRANT CONNECT ON DATABASE demo_db TO app_user;
\connect demo_db
REVOKE CREATE ON SCHEMA public FROM PUBLIC;
GRANT USAGE ON SCHEMA public TO app_user;

ALTER SYSTEM SET password_encryption = 'scram-sha-256';
SELECT pg_reload_conf();

