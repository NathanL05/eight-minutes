import os
from psycopg2.pool import SimpleConnectionPool

dsn = (
    f"host={os.environ.get('POSTGRES_HOST', 'localhost')} "
    f"dbname={os.environ.get('POSTGRES_DB')} "
    f"user={os.environ.get('POSTGRES_USER')} "
    f"password={os.environ.get('POSTGRES_PASSWORD')} "
)
tcp = None


def get_db():
    global tcp

    if tcp is None:
        tcp = SimpleConnectionPool(1, 10, dsn)

    conn = tcp.getconn()
    try:
        yield conn
    finally:
        tcp.putconn(conn)
