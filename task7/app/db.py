import os, sys, json, getpass, logging
import psycopg2
import psycopg2.extras
from psycopg2 import sql

def get_logger():
    logger = logging.getLogger('csgo_cli')
    logger.setLevel(logging.INFO)
    fmt = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
    sh = logging.StreamHandler(sys.stdout); sh.setLevel(logging.INFO); sh.setFormatter(fmt)
    eh = logging.StreamHandler(sys.stderr); eh.setLevel(logging.ERROR); eh.setFormatter(fmt)
    if not logger.handlers:
        logger.addHandler(sh); logger.addHandler(eh)
        log_path = os.getenv('LOG_PATH')
        if log_path:
            fh = logging.FileHandler(log_path); fh.setLevel(logging.INFO); fh.setFormatter(fmt); logger.addHandler(fh)
    return logger

LOGGER = get_logger()

def friendly_error(e: Exception) -> str:
    return 'Ошибка при выполнении операции. Проверьте ввод и попробуйте снова.'

def prompt_conn():
    host = os.getenv('DB_HOST', 'db')
    port = int(os.getenv('DB_PORT', '5432'))
    dbname = os.getenv('DB_NAME', 'postgres')
    user = input(f"DB user [{os.getenv('DB_USER','app_user')}] : ") or os.getenv('DB_USER','app_user')
    password = getpass.getpass('DB password (не видно при вводе): ')
    return dict(host=host, port=port, dbname=dbname, user=user, password=password)

def connect(params=None):
    if params is None:
        try:
            params = prompt_conn()
        except Exception:
            LOGGER.error("Не удалось получить параметры подключения."); return None
    if not params.get("password"):
        env_pwd = os.getenv("DB_PASSWORD")
        if env_pwd:
            params["password"] = env_pwd
    try:
        conn = psycopg2.connect(**params)
        conn.autocommit = False
        LOGGER.info("Подключение к БД успешно.")
        return conn
    except Exception as e:
        LOGGER.error(friendly_error(e))
        return None


def validate_table_column(table, column, tables):
    if table not in tables: raise ValueError('Неверная таблица.')
    if column not in tables[table]: raise ValueError('Неверная колонка.')
    return True

def select_all(conn, table, tables):
    try:
        if table not in tables: raise ValueError('Неверная таблица.')
        q = sql.SQL('SELECT * FROM {}').format(sql.Identifier(table))
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(q); rows = cur.fetchall(); LOGGER.info('Запрос выполнен успешно.'); return rows
    except Exception as e:
        conn.rollback(); LOGGER.error(friendly_error(e)); return []

def select_filter_one(conn, table, column, value, tables):
    try:
        validate_table_column(table, column, tables)
        q = sql.SQL('SELECT * FROM {} WHERE {} = %s').format(sql.Identifier(table), sql.Identifier(column))
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(q, (value,)); rows = cur.fetchall(); LOGGER.info('Запрос выполнен успешно.'); return rows
    except Exception as e:
        conn.rollback(); LOGGER.error(friendly_error(e)); return []

def select_filter_many(conn, table, conditions, tables):
    try:
        if table not in tables: raise ValueError('Неверная таблица.')
        parts = []; vals = []
        for col, val in conditions.items():
            if col not in tables[table]: raise ValueError(f'Неверная колонка: {col}')
            parts.append(sql.SQL('{} = %s').format(sql.Identifier(col))); vals.append(val)
        where_clause = sql.SQL(' AND ').join(parts) if parts else sql.SQL('TRUE')
        q = sql.SQL('SELECT * FROM {} WHERE ').format(sql.Identifier(table)) + where_clause
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(q, vals); rows = cur.fetchall(); LOGGER.info('Запрос выполнен успешно.'); return rows
    except Exception as e:
        conn.rollback(); LOGGER.error(friendly_error(e)); return []

def update_one(conn, table, row_id, updates, tables):
    try:
        if table not in tables: raise ValueError('Неверная таблица.')
        updates.pop('id', None)
        parts = []; vals = []
        for col, val in updates.items():
            if col not in tables[table]: raise ValueError(f'Неверная колонка: {col}')
            parts.append(sql.SQL('{} = %s').format(sql.Identifier(col))); vals.append(val)
        if not parts: raise ValueError('Нет полей для обновления.')
        vals.append(row_id)
        q = sql.SQL('UPDATE {} SET ').format(sql.Identifier(table)) + sql.SQL(', ').join(parts) + sql.SQL(' WHERE id = %s RETURNING *')
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(q, vals); row = cur.fetchone(); conn.commit(); LOGGER.info('Обновление успешно.'); return row
    except Exception as e:
        conn.rollback(); LOGGER.error(friendly_error(e)); return None

def update_many_same(conn, table, target_column, new_value, in_column, in_values, tables):
    try:
        validate_table_column(table, target_column, tables); validate_table_column(table, in_column, tables)
        if not in_values: raise ValueError('Пустой список значений.')
        q = sql.SQL('UPDATE {} SET {} = %s WHERE {} = ANY(%s) RETURNING id').format(sql.Identifier(table), sql.Identifier(target_column), sql.Identifier(in_column))
        with conn.cursor() as cur:
            cur.execute(q, (new_value, in_values)); ids = [r[0] for r in cur.fetchall()]; conn.commit(); LOGGER.info('Групповое обновление успешно.'); return ids
    except Exception as e:
        conn.rollback(); LOGGER.error(friendly_error(e)); return []

def insert_one(conn, table, values, tables):
    try:
        if table not in tables: raise ValueError('Неверная таблица.')
        cols = []; params = []; vals = []
        for col, val in values.items():
            if col not in tables[table]: raise ValueError(f'Неверная колонка: {col}')
            cols.append(sql.Identifier(col)); params.append(sql.Placeholder()); vals.append(val)
        q = sql.SQL('INSERT INTO {} ({}) VALUES ({}) RETURNING *').format(sql.Identifier(table), sql.SQL(', ').join(cols), sql.SQL(', ').join(params))
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(q, vals); row = cur.fetchone(); conn.commit(); LOGGER.info('Вставка успешна.'); return row
    except Exception as e:
        conn.rollback(); LOGGER.error(friendly_error(e)); return None

def insert_related_example(conn):
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute('SELECT id, owner_id FROM csgo.items ORDER BY random() LIMIT 1')
            item = cur.fetchone()
            cur.execute('INSERT INTO csgo.listings(item_id, seller_id, price, currency, status) VALUES (%s,%s,%s,%s,\'active\') RETURNING id', (item['id'], item['owner_id'], 123.45, 'USD'))
            listing_id = cur.fetchone()['id']
            cur.execute('SELECT id FROM csgo.users WHERE id <> %s ORDER BY random() LIMIT 1', (item['owner_id'],))
            buyer_id = cur.fetchone()['id']
            cur.execute('INSERT INTO csgo.orders(listing_id, buyer_id, price) VALUES (%s,%s,%s) RETURNING id', (listing_id, buyer_id, 123.45))
            order_id = cur.fetchone()['id']
            cur.execute('UPDATE csgo.listings SET status = \'sold\' WHERE id = %s', (listing_id,))
            conn.commit(); return {'listing_id': listing_id, 'order_id': order_id}
    except Exception as e:
        conn.rollback(); LOGGER.error(friendly_error(e)); return None

def bulk_insert(conn, table, rows, tables):
    try:
        if table not in tables: raise ValueError('Неверная таблица.')
        if not rows: raise ValueError('Нет данных для вставки.')
        allowed = tables[table]; cols = [c for c in rows[0].keys() if c in allowed]
        if not cols: raise ValueError('Не найдены валидные колонки.')
        values_matrix = [[row.get(c) for c in cols] for row in rows]
        cols_ident = sql.SQL(', ').join([sql.Identifier(c) for c in cols])
        placeholders_row = sql.SQL(', ').join([sql.Placeholder()] * len(cols))
        values_sql = sql.SQL(', ').join([sql.SQL('({})').format(placeholders_row)] * len(values_matrix))
        q = sql.SQL('INSERT INTO {} ({}) VALUES ').format(sql.Identifier(table), cols_ident) + values_sql + sql.SQL(' RETURNING id')
        flat = [v for row in values_matrix for v in row]
        with conn.cursor() as cur:
            cur.execute(q, flat); ids = [r[0] for r in cur.fetchall()]; conn.commit(); return ids
    except Exception as e:
        conn.rollback(); LOGGER.error(friendly_error(e)); return []
