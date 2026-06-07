import os
import threading
from psycopg2.pool import ThreadedConnectionPool

dsn = (
    f"host={os.environ.get('POSTGRES_HOST', 'localhost')} "
    f"dbname={os.environ.get('POSTGRES_DB')} "
    f"user={os.environ.get('POSTGRES_USER')} "
    f"password={os.environ.get('POSTGRES_PASSWORD')} "
)
tcp = None
_tcp_lock = threading.Lock()


def _get_pool():
    global tcp

    if tcp is None:
        with _tcp_lock:
            if tcp is None:
                tcp = ThreadedConnectionPool(1, 10, dsn)

    return tcp


def get_db():
    conn = _get_pool().getconn()
    try:
        yield conn
    finally:
        tcp.putconn(conn)
