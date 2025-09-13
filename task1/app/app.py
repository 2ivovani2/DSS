import yaml, getpass, sys
from psycopg import connect

ALLOWED_CFG_KEYS = {"host", "port", "dbname", "sslmode"}

def load_cfg(path="config.yaml"):
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return {k: v for k, v in data.items() if k in ALLOWED_CFG_KEYS}

def main():
    cfg = load_cfg()
    user = input("DB user: ").strip()
    password = getpass.getpass("DB password: ")
    params = {**cfg, "user": user, "password": password}

    with connect(**params) as conn, conn.cursor() as cur:
        cur.execute("SELECT version();")
        ver, = cur.fetchone()
        print("Версия постгри:", ver)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("Ошибка:", e, file=sys.stderr)
        sys.exit(1)

