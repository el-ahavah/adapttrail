"""SQLite for local work; PostgreSQL for a configured hosted installation."""
import sqlite3
import psycopg
from psycopg.rows import dict_row

IntegrityErrors = (sqlite3.IntegrityError, psycopg.IntegrityError)


class PostgresConnection:
    def __init__(self, url):
        self.connection = psycopg.connect(url, sslmode='require', row_factory=dict_row,
                                         prepare_threshold=None, connect_timeout=10)
        self.connection.execute('SET search_path TO adapttrail_private')

    def execute(self, query, parameters=()):
        return self.connection.execute(query.replace('?', '%s'), parameters)

    def __enter__(self):
        return self

    def __exit__(self, kind, value, traceback):
        if kind:
            self.connection.rollback()
        else:
            self.connection.commit()

    def close(self):
        self.connection.close()


def connect(config):
    if config.get('DATABASE_URL'):
        return PostgresConnection(config['DATABASE_URL'])
    connection = sqlite3.connect(config['DATABASE'])
    connection.row_factory = sqlite3.Row
    connection.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT NOT NULL UNIQUE, password_hash TEXT NOT NULL)')
    connection.execute('''CREATE TABLE IF NOT EXISTS drafts (
        id INTEGER PRIMARY KEY, title TEXT NOT NULL, country TEXT NOT NULL,
        problem TEXT NOT NULL, approach TEXT NOT NULL, conditions TEXT NOT NULL,
        source_id TEXT NOT NULL, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        user_id INTEGER REFERENCES users(id))''')
    if 'user_id' not in {row['name'] for row in connection.execute('PRAGMA table_info(drafts)')}:
        connection.execute('ALTER TABLE drafts ADD COLUMN user_id INTEGER REFERENCES users(id)')
    connection.commit()
    return connection
