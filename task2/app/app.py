import os, sys, time, logging, signal
from datetime import datetime
from psycopg import connect

INTERVAL = int(os.getenv("PING_INTERVAL_SECONDS", os.getenv("PING_INTERVAL_MINUTES", "0")) or 0)
if INTERVAL == 0:
    INTERVAL = 300

ms = int(os.getenv("DB_STATEMENT_TIMEOUT_MS", "3000"))
DB_PARAMS = {
    "host": os.getenv("DB_HOST", "db"),
    "port": int(os.getenv("DB_PORT", "5432")),
    "dbname": os.getenv("DB_NAME", "appdb"),
    "user": os.getenv("DB_USER", ""),
    "password": os.getenv("DB_PASSWORD", ""),
    "sslmode": os.getenv("DB_SSLMODE", "disable"),
    "connect_timeout": int(os.getenv("DB_CONNECT_TIMEOUT", "5")),
    "options": f"-c statement_timeout={ms}",
}

LOG_FILE = os.getenv("LOG_FILE_PATH")

logger = logging.getLogger("pinger")
logger.setLevel(logging.INFO)

class StdoutFilter(logging.Filter):
    def filter(self, record):
        return record.levelno < logging.ERROR

sh = logging.StreamHandler(stream=sys.stdout)
sh.setLevel(logging.INFO)
sh.addFilter(StdoutFilter())
logger.addHandler(sh)

eh = logging.StreamHandler(stream=sys.stderr)
eh.setLevel(logging.ERROR)
logger.addHandler(eh)

if LOG_FILE:
    fh = logging.FileHandler(LOG_FILE, encoding="utf-8")
    fh.setLevel(logging.INFO)
    logger.addHandler(fh)

stop = False
def handle_term(signum, frame):
    global stop
    stop = True
    logger.info("Выходим аккуратно...")

for sig in (signal.SIGINT, signal.SIGTERM):
    signal.signal(sig, handle_term)

def ping_once():
    try:
        with connect(**DB_PARAMS) as conn, conn.cursor() as cur:
            cur.execute("SELECT version();")
            row = cur.fetchone()
            if not row:
                logger.info("Ответ на запрос версии пустой (атипично).")
                return

            (ver,) = row
            if not isinstance(ver, str):
                logger.info("Нетипичный ответ версии (тип %s): %r", type(ver).__name__, ver)
            else:
                logger.info("Успешное подключение. Версия PostgreSQL: %s", ver)
    except Exception as e:
        logger.error("Ошибка подключения или запроса: %s", e)

def main():
    logger.info("Pinger стартовал. Интервал: %s сек. Хост: %s:%s БД: %s",
                INTERVAL, DB_PARAMS["host"], DB_PARAMS["port"], DB_PARAMS["dbname"])
    while not stop:
        started = datetime.now().isoformat(timespec="seconds")
        logger.info("Проверка соединения (%s)...", started)
        ping_once()
        slept = 0
        while not stop and slept < INTERVAL:
            time.sleep(min(1, INTERVAL - slept))
            slept += 1
    logger.info("Завершено.")

if __name__ == "__main__":
    main()
