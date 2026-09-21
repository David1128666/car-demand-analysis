import pymysql
from pymysql.cursors import DictCursor
from config import MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE

def get_connection():
    return pymysql.connect(
        host=MYSQL_HOST, port=MYSQL_PORT,
        user=MYSQL_USER, password=MYSQL_PASSWORD,
        database=MYSQL_DATABASE,
        charset="utf8mb4",
        use_unicode=True,
        cursorclass=DictCursor,
        autocommit=True,
        connect_timeout=5,
        read_timeout=10,
        write_timeout=10,
    )

def query(sql: str, params=None):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql, params)
            return cursor.fetchall()
    finally:
        conn.close()

def query_one(sql: str, params=None):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql, params)
            return cursor.fetchone()
    finally:
        conn.close()

def get_system_config(key: str, default: str = None) -> str:
    """Read a config value from system_config table. Returns default if not found."""
    row = query_one("SELECT config_value FROM system_config WHERE config_key = %s", (key,))
    return row["config_value"] if row else default


def get_system_config_int(key: str, default: int = 0) -> int:
    """Read a config value and convert to int. Returns default on missing or invalid."""
    val = get_system_config(key, str(default))
    try:
        return int(val)
    except (ValueError, TypeError):
        return default


def execute(sql: str, params=None):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql, params)
            conn.commit()
            return cursor.lastrowid
    finally:
        conn.close()
