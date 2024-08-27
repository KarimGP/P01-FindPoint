import sqlite3

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def column_exists(conn, table_name, column_name):
    """ Verifica si una columna existe en la tabla """
    cursor = conn.execute(f"PRAGMA table_info({table_name})")
    for column in cursor.fetchall():
        if column_name == column[1]:
            return True
    return False

def create_users_table():
    conn = get_db_connection()

    cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
    if cursor.fetchone() is None:
        conn.execute('''
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                password TEXT NOT NULL,
                birth_year INTEGER,
                country TEXT,
                email TEXT UNIQUE
            )
        ''')
    else:
        if not column_exists(conn, 'users', 'birth_year'):
            conn.execute('ALTER TABLE users ADD COLUMN birth_year INTEGER')
        if not column_exists(conn, 'users', 'country'):
            conn.execute('ALTER TABLE users ADD COLUMN country TEXT')

        if not column_exists(conn, 'users', 'email'):
            conn.execute('ALTER TABLE users RENAME TO users_old')
            conn.execute('''
                CREATE TABLE users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    password TEXT NOT NULL,
                    birth_year INTEGER,
                    country TEXT,
                    email TEXT UNIQUE
                )
            ''')
            conn.execute('''
                INSERT INTO users (id, username, password, birth_year, country)
                SELECT id, username, password, birth_year, country FROM users_old
            ''')
            conn.execute('DROP TABLE users_old')

    conn.commit()
    conn.close()
