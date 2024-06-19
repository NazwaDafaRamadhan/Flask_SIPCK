from flask_login import UserMixin
from app import mysql, login_manager, bcrypt
import logging
import uuid

logging.basicConfig(level=logging.DEBUG)

class User(UserMixin):
    def __init__(self, id, username, email, password, last_login, is_active):
        self.id = id
        self.username = username
        self.email = email
        self.password = password
        self.last_login = last_login
        self.is_active = is_active

    @staticmethod
    def get_by_email(email):
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cur.fetchone()
        if user:
            return User(user[0], user[1], user[2], user[3], user[6], user[7])
        return None

    @staticmethod
    def create(username, email, password, role):
        try:
            password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO users (username, email, password, role) VALUES (%s, %s, %s, %s)", (username, email, password_hash, role))
            mysql.connection.commit()
            cur.close()
            logging.debug("User created successfully")
        except Exception as e:
            logging.error(f"Error: {e}")
            mysql.connection.rollback()

    @property
    def is_active(self):
        return self._is_active

    @is_active.setter
    def is_active(self, value):
        self._is_active = value

@login_manager.user_loader
def load_user(user_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cur.fetchone()
    if user:
        return User(user[0], user[1], user[2], user[3], user[6], user[7])
    return None

class Candidate():
    def __init__(self, id, nama_akun, kode, status, uuid):
        self.id = id
        self.nama_akun = nama_akun
        self.kode = kode
        self.status = status
        self.uuid = uuid

    @staticmethod
    def create(nama_akun, kode, status, uuid):
        try:
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO candidate (nama_akun, kode, status, uuid) VALUES (%s, %s, %s, %s)", (nama_akun, kode, status, uuid))
            mysql.connection.commit()
            cur.close()
            logging.debug("Candidate created successfully")
        except Exception as e:
            logging.error(f"Error: {e}")
            mysql.connection.rollback()

    @staticmethod
    def get_by_username(username):
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE nama_akun = %s", (username,))
        username = cur.fetchone()
        if username:
            return Candidate(username[0], username[1], username[2], username[3], username[13])
        return None

class Question():
    def __init__(self, id, fitur, pertanyaan):
        self.id = id
        self.fitur = fitur
        self.pertanyaan = pertanyaan

    @staticmethod
    def create(fitur, pertanyaan):
        try:
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO question (fitur, pertanyaan) VALUES (%s, %s)", (fitur, pertanyaan))
            mysql.connection.commit()
            cur.close()
            logging.debug("Question created successfully")
        except Exception as e:
            logging.error(f"Error: {e}")
            mysql.connection.rollback()

    def get_question(page, per_page):
        cur = mysql.connection.cursor()
        cur.execute("SELECT COUNT(*) FROM question")
        total_rows = cur.fetchone()[0]
        
        cur.execute("SELECT * FROM question LIMIT %s OFFSET %s", (per_page, (page - 1) * per_page))
        question = cur.fetchall()
        
        cur.close()
        return question, total_rows