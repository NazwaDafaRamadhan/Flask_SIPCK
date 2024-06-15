from flask import render_template, request, redirect, url_for, Blueprint, flash, session
from datetime import datetime
from flask_login import login_user, current_user, logout_user, login_required
from app import mysql, bcrypt
from app.forms import RegistrationForm, LoginForm, AddCandidateForm
from app.models import User, Candidate
import uuid
import pytz

main = Blueprint('main', __name__)

@main.route("/", methods=['GET'])
def home():
    return redirect(url_for('main.login'))

@main.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.get_by_email(form.email.data)
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            cursor = mysql.connection.cursor()
            cursor.execute("UPDATE `users` SET `is_active`=1 WHERE `id`=%s", (user.id,))
            mysql.connection.commit()
            cursor.close()
            return redirect(url_for('main.index'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('auth/login.html', title='Login', form=form)

@main.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        User.create(form.username.data, form.email.data, form.password.data, role=form.role.data)
        flash('Your account has been created!', 'success')
        return redirect(url_for('main.login'))
    return render_template('auth/register.html', title='Register', form=form)

@main.route("/logout")
def logout():
    if current_user.is_authenticated:
        user_id = current_user.id
        cursor = mysql.connection.cursor()
        cursor.execute("UPDATE `users` SET `is_active`=0, `last_login`=%s WHERE `id`=%s", (datetime.now(pytz.timezone('Asia/Jakarta')), user_id))
        mysql.connection.commit()
        cursor.close()
        logout_user()
    return redirect(url_for('main.login'))

@main.route('/dashboard')
@login_required
def index():
    return render_template('dashboard/index.html')

@main.route('/user')
@login_required
def user():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM users")
    data = cur.fetchall()
    cur.close()
    return render_template('user/index.html', users=data)

@main.route('/karyawan')
@login_required
def candidate():
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, nama_akun, kode, status FROM candidate")
    data = cur.fetchall()
    cur.close()
    return render_template('employ/index.html', candidates=data)

@main.route("/tambah_kandidat", methods=['GET', 'POST'])
def add_candidate():
    form = AddCandidateForm()
    form.generate_kode()
    if form.validate_on_submit():
        Candidate.create(form.nama_akun.data, form.kode.data, form.status.data)
        session['flash_message'] = ('Kandidat berhasil ditambahkan!', 'success')
        return redirect(url_for('main.employ'))  # Ganti 'index' dengan nama fungsi route halaman utama aplikasi Anda
    return render_template('employ/form.html', title='Tambah Kandidat', form=form)

@main.route('/form')
@login_required
def form():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM answer JOIN question ON question.id=answer.question_id JOIN candidate ON candidate.id=answer.candidate_id")
    data = cur.fetchall()
    cur.close()
    return render_template('form/index.html', forms=data)

@main.route('/detail_form', methods=['GET', 'POST'])
@login_required
def detail_form():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM answer JOIN question ON question.id=answer.question_id JOIN candidate ON candidate.id=answer.candidate_id")
    data = cur.fetchall()
    cur.close()
    return render_template('form/index.html', forms=data)

@main.route('/question')
@login_required
def question():
    return render_template('question/index.html')

@main.route("/generate_user")
@login_required
def generate_user():
    generated_username = 'user_' + str(uuid.uuid4())
    generated_code = str(uuid.uuid4())
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO generated_users (user_id, generated_username, generated_code) VALUES (%s, %s, %s)",
                (current_user.id, generated_username, generated_code))
    mysql.connection.commit()
    flash(f'Generated user: {generated_username} with code: {generated_code}', 'success')
    return redirect(url_for('main.index'))
