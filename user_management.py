import sqlite3
from flask_login import UserMixin
from werkzeug.security import check_password_hash
from db_utils import get_db_connection

class User(UserMixin):
    def __init__(self, id, email, password, username, birth_year=None, country=None):
        self.id = id
        self.email = email
        self.password = password
        self.username = username
        self.birth_year = birth_year
        self.country = country

    @staticmethod
    def get(user_id):
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
        conn.close()
        if user:
            return User(id=user['id'], email=user['email'], password=user['password'], username=user['username'],
                        birth_year=user['birth_year'], country=user['country'])
        return None

    @staticmethod
    def authenticate(email, password):
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
        conn.close()
        if user and check_password_hash(user['password'], password):
            return User(id=user['id'], email=user['email'], password=user['password'], username=user['username'],
                        birth_year=user['birth_year'], country=user['country'])
        return None
