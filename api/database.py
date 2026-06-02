import os
from psycopg2.pool import ThreadedConnectionPool

dsn = f"host=localhost dbname={os.environ.get('POSTGRES_DB')} user={os.environ.get('POSTGRES_USER')} password={os.environ.get('POSTGRES_PASSWORD')}"
tcp = ThreadedConnectionPool(1, 10, dsn)

def get_db():
    conn = tcp.getconn()

    try:
        yield conn
    finally:
        tcp.putconn(conn)
