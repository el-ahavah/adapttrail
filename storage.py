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
    connection.execute('PRAGMA foreign_keys = ON')
    connection.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT NOT NULL UNIQUE, password_hash TEXT NOT NULL)')
    connection.execute('''CREATE TABLE IF NOT EXISTS drafts (
        id INTEGER PRIMARY KEY, title TEXT NOT NULL, country TEXT NOT NULL,
        problem TEXT NOT NULL, approach TEXT NOT NULL, conditions TEXT NOT NULL,
        source_id TEXT NOT NULL, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        user_id INTEGER REFERENCES users(id))''')
    if 'user_id' not in {row['name'] for row in connection.execute('PRAGMA table_info(drafts)')}:
        connection.execute('ALTER TABLE drafts ADD COLUMN user_id INTEGER REFERENCES users(id)')
    if 'status' not in {row['name'] for row in connection.execute('PRAGMA table_info(drafts)')}:
        connection.execute("ALTER TABLE drafts ADD COLUMN status TEXT NOT NULL DEFAULT 'planned'")
    connection.execute("""CREATE TABLE IF NOT EXISTS progress_entries (
        id INTEGER PRIMARY KEY, project_id INTEGER NOT NULL REFERENCES drafts(id) ON DELETE CASCADE,
        entry_date TEXT NOT NULL, observation TEXT NOT NULL, measurement TEXT,
        unit TEXT NOT NULL, metric TEXT NOT NULL, period TEXT NOT NULL,
        entry_type TEXT NOT NULL, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    )""")
    connection.execute("""CREATE TABLE IF NOT EXISTS project_tasks (
        id INTEGER PRIMARY KEY, project_id INTEGER NOT NULL REFERENCES drafts(id) ON DELETE CASCADE,
        title TEXT NOT NULL CHECK(length(trim(title)) BETWEEN 1 AND 240),
        completed INTEGER NOT NULL DEFAULT 0 CHECK(completed IN (0,1)),
        archived INTEGER NOT NULL DEFAULT 0 CHECK(archived IN (0,1)),
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    )""")
    connection.execute('CREATE INDEX IF NOT EXISTS tasks_project ON project_tasks(project_id,archived,id)')
    connection.execute("""CREATE TABLE IF NOT EXISTS assessments (
        id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL REFERENCES users(id),
        project_id INTEGER REFERENCES drafts(id) ON DELETE CASCADE,
        approach TEXT NOT NULL, inputs TEXT NOT NULL, result TEXT NOT NULL,
        rule_version TEXT NOT NULL, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    )""")
    connection.execute("""CREATE TABLE IF NOT EXISTS publications (
        id INTEGER PRIMARY KEY, project_id INTEGER NOT NULL UNIQUE REFERENCES drafts(id) ON DELETE CASCADE,
        title TEXT NOT NULL, country TEXT NOT NULL, problem TEXT NOT NULL,
        action TEXT NOT NULL, outcome TEXT NOT NULL, lessons TEXT NOT NULL,
        published INTEGER NOT NULL DEFAULT 1, hidden INTEGER NOT NULL DEFAULT 0,
        updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    )""")
    connection.execute("""CREATE TABLE IF NOT EXISTS story_reports (
        id INTEGER PRIMARY KEY, publication_id INTEGER NOT NULL REFERENCES publications(id) ON DELETE CASCADE,
        reason TEXT NOT NULL, resolved INTEGER NOT NULL DEFAULT 0,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    )""")
    connection.execute("""CREATE TABLE IF NOT EXISTS adaptations (
        project_id INTEGER PRIMARY KEY REFERENCES drafts(id) ON DELETE CASCADE,
        publication_id INTEGER REFERENCES publications(id) ON DELETE SET NULL,
        source_title TEXT NOT NULL, changes TEXT NOT NULL, reason TEXT NOT NULL
    )""")
    connection.commit()
    return connection
