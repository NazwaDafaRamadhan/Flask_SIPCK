from flask import render_template, current_app, request, redirect, url_for, Blueprint, flash, session
from datetime import datetime
from flask_login import login_user, current_user, logout_user, login_required
from flask_babel import format_currency
from app import mysql, bcrypt
from app.forms import RegistrationForm, LoginForm, AddCandidateForm, AddQuestionForm, DetailCandidateForm, SignInForm
from app.models import User, Candidate, Question
import logging
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
    return render_template('user/index.html', users=data, title='Data Pengguna')

@main.route('/karyawan')
@login_required
def candidate():
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, nama_akun, kode, status FROM candidate")
    data = cur.fetchall()
    cur.close()
    return render_template('employ/index.html', candidates=data, title='Data Calon Karyawan')

@main.route("/tambah_kandidat", methods=['GET', 'POST'])
def add_candidate():
    form = AddCandidateForm()
    form.generate_kode()
    if form.validate_on_submit():
        form.generate_kode() 
        candidate_uuid = 'user_' + str(uuid.uuid4())
        form.uuid.data = candidate_uuid
        Candidate.create(form.nama_akun.data, form.kode.data, form.status.data, form.uuid.data)
        session['flash_message'] = ('Kandidat berhasil ditambahkan!', 'success')
        return redirect(url_for('main.candidate'))  
    return render_template('employ/form.html', title='Tambah Kandidat', form=form)

@main.route('/form')
@login_required
def form():
    cur = mysql.connection.cursor()
    cur.execute("SELECT DISTINCT candidate.id, candidate.nama_kandidat, candidate.posisi, candidate.gaji, candidate.hasil, answer.candidate_id FROM candidate JOIN answer ON answer.candidate_id = candidate.id")
    data = cur.fetchall()
    cur.close()
    return render_template('form/index.html', data=data)

@main.route('/form/<int:id>/detail', methods=['GET', 'POST'])
@login_required
def view_form(id):
    form = DetailCandidateForm()
    cur = mysql.connection.cursor()
    query = """
    SELECT answer.*, question.*, candidate.*
    FROM answer
    JOIN question ON question.id = answer.question_id
    JOIN candidate ON candidate.id = answer.candidate_id
    WHERE answer.candidate_id = %s
    """
    try:
        cur.execute(query, (id,))
        data = cur.fetchall()
        cur.close()
        
    except Exception as e:
        # Cetak kesalahan jika terjadi
        print("Error executing query:", e)
        data = []

    nilai_gaji = data[0][23]
    nilai_gaji_formatted = format_currency(nilai_gaji, 'IDR')

    gaji = nilai_gaji_formatted.replace('IDR', 'IDR ').replace('.00', '')

    pertanyaan1 = data[0][7]
    pertanyaan2 = data[1][7]
    pertanyaan3 = data[2][7]
    pertanyaan4 = data[3][7]
    pertanyaan5 = data[4][7]
    pertanyaan6 = data[5][7]
    pertanyaan7 = data[6][7]
    pertanyaan8 = data[7][7]
    pertanyaan9 = data[8][7]
    pertanyaan10 = data[9][7]
    pertanyaan11 = data[10][7]
    pertanyaan12 = data[11][7]
    pertanyaan13 = data[12][7]
    pertanyaan14 = data[13][7]
    pertanyaan15 = data[14][7]
    pertanyaan16 = data[15][7]
    pertanyaan17 = data[16][7]
    
    form.nama_kandidat.data = data[0][15]
    form.email_kandidat.data = data[0][16]
    form.no_telp.data = data[0][17]
    form.alamat.data = data[0][18]
    form.tgl_lahir.data = data[0][19]
    form.pendidikan.data = data[0][20]
    form.j_kel.data = data[0][21]
    form.posisi.data = data[0][22]
    form.gaji.data = gaji
    form.hasil.data = data[0][25]
    form.opsi1.data = data[0][3]
    form.uraian1.data = data[0][4]
    form.opsi2.data = data[1][3]
    form.uraian2.data = data[1][4]
    form.opsi3.data = data[2][3]
    form.uraian3.data = data[2][4]
    form.opsi4.data = data[3][3]
    form.uraian4.data = data[3][4]
    form.opsi10.data = data[4][3]
    form.uraian5.data = data[4][4]
    form.opsi9.data = data[5][3]
    form.uraian6.data = data[5][4]
    form.opsi9.data = data[5][3]
    form.uraian6.data = data[5][4]
    form.opsi7.data = data[6][3]
    form.uraian7.data = data[6][4]
    form.opsi8.data = data[7][3]
    form.uraian8.data = data[7][4]
    form.opsi9.data = data[8][3]
    form.uraian9.data = data[8][4]
    form.opsi10.data = data[9][3]
    form.uraian10.data = data[9][4]
    form.opsi11.data = data[10][3]
    form.uraian11.data = data[10][4]
    form.opsi12.data = data[11][3]
    form.uraian12.data = data[11][4]
    form.opsi13.data = data[12][3]
    form.uraian13.data = data[12][4]
    form.opsi14.data = data[13][3]
    form.uraian14.data = data[13][4]
    form.opsi15.data = data[14][3]
    form.uraian15.data = data[14][4]
    form.opsi16.data = data[15][3]
    form.uraian16.data = data[15][4]
    form.opsi17.data = data[16][3]
    form.uraian17.data = data[16][4]

    prediction = None

    def convert_label_opsi1(opsi1):
        if opsi1 == 'Laki-laki':
            return 1
        else:
            return 2
    
    def convert_label_opsi2(opsi2):
        if opsi2 == 'Sains dan Teknologi':
            return 1
        elif opsi2 == 'Ekonomi dan Manajemen':
            return 2
        elif opsi2 == 'Pertanian':
            return 3
        else:
            return 4
        
    def convert_label_opsi3(opsi3):
        if opsi3 == 'Perkotaan':
            return 1
        else:
            return 2
        
    def convert_label_opsi4(opsi4):
        if opsi4 == 'Punya':
            return 1
        else:
            return 2

    def convert_label_opsi5(opsi5):
        if opsi5 == 'Punya':
            return 1
        else:
            return 2
        
    def convert_label_opsi6(opsi6):
        if opsi6 == 'Sangat tidak tertarik':
            return 1
        elif opsi6 == 'Tidak tertarik':
            return 2
        elif opsi6 == 'Tertarik':
            return 3
        elif opsi6 == 'Lebih tertarik':
            return 4
        else:
            return 5
        
    def convert_label_opsi7(opsi7):
        if opsi7 == 'Buruk':
            return 1
        elif opsi7 == 'Sedang':
            return 2
        else:
            return 3
        
    def convert_label_opsi8(opsi8):
        if opsi8 == 'Buruk':
            return 1
        elif opsi8 == 'Rata-rata':
            return 2
        else:
            return 3
        
    def convert_label_opsi9(opsi9):
        if opsi9 == 'Harga diri':
            return 1
        elif opsi9 == 'Minat pribadi':
            return 2
        elif opsi9 == 'Gaji':
            return 3
        elif opsi9 == 'Lingkungan kerja':
            return 4
        elif opsi9 == 'Prospek kerja':
            return 5
        elif opsi9 == 'Keselarasan profesi':
            return 6
        else:
            return 7
        
    def convert_label_opsi10(opsi10):
        if opsi10 == 'Punya':
            return 1
        else:
            return 2
        
    def convert_label_opsi11(opsi11):
        if opsi11 == 'Punya':
            return 1
        else:
            return 2
        
    def convert_label_opsi12(opsi12):
        if opsi12 == 'Buruk':
            return 1
        elif opsi12 == 'Sedang':
            return 2
        else:
            return 3
        
    def convert_label_opsi13(opsi13):
        if opsi13 == 'Otoriter':
            return 1
        elif opsi13 == 'Permisif':
            return 2
        else:
            return 3
        
    def convert_label_opsi14(opsi14):
        if opsi14 == 'Dukungan':
            return 1
        elif opsi14 == 'Penolakan':
            return 2
        else:
            return 3

    def convert_label_opsi15(opsi15):
        if opsi15 == 'Serius':
            return 1
        elif opsi15 == 'Rata-rata':
            return 2
        else:
            return 3
        
    def convert_label_opsi16(opsi16):
        if opsi16 == 'Iya':
            return 1
        else:
            return 2

    def convert_label_opsi17(opsi17):
        if opsi17 == 'Iya':
            return 1
        else:
            return 2
        
    def convert_label_opsi18(opsi18):
        if opsi18 == 'Kurang':
            return 1
        elif opsi18 == 'Cukup':
            return 2
        else:
            return 3
        
    input_opsi1 = convert_label_opsi1(form.j_kel.data)
    input_opsi2 = convert_label_opsi2(form.opsi1.data)
    input_opsi3 = convert_label_opsi3(form.opsi2.data)
    input_opsi4 = convert_label_opsi4(form.opsi3.data)
    input_opsi5 = convert_label_opsi5(form.opsi4.data)
    input_opsi6 = convert_label_opsi6(form.opsi5.data)
    input_opsi7 = convert_label_opsi7(form.opsi6.data)
    input_opsi8 = convert_label_opsi8(form.opsi7.data)
    input_opsi9 = convert_label_opsi9(form.opsi8.data)
    input_opsi10 = convert_label_opsi10(form.opsi9.data)
    input_opsi11 = convert_label_opsi11(form.opsi10.data)
    input_opsi12 = convert_label_opsi12(form.opsi11.data)
    input_opsi13 = convert_label_opsi13(form.opsi12.data)
    input_opsi14 = convert_label_opsi14(form.opsi13.data)
    input_opsi15 = convert_label_opsi15(form.opsi14.data)
    input_opsi16 = convert_label_opsi16(form.opsi15.data)
    input_opsi17 = convert_label_opsi17(form.opsi16.data)
    input_opsi18 = convert_label_opsi18(form.opsi17.data)

    input_data = [
        input_opsi1, input_opsi2, input_opsi3, input_opsi4 ,input_opsi5, input_opsi6, input_opsi7, input_opsi8 ,input_opsi9, input_opsi10, input_opsi11, input_opsi12 ,input_opsi13, input_opsi14, input_opsi15, input_opsi16 ,input_opsi17, input_opsi18
    ]
            
    prediction = current_app.model.predict([input_data])[0]
    prediction = 'Berpotensi' if prediction == 1 else 'Tidak berpotensi'

    return render_template('form/detail.html', data=data, form=form, pertanyaan1=pertanyaan1, pertanyaan2=pertanyaan2, pertanyaan3=pertanyaan3, pertanyaan4=pertanyaan4, pertanyaan5=pertanyaan5, pertanyaan6=pertanyaan6, pertanyaan7=pertanyaan7, pertanyaan8=pertanyaan8, pertanyaan9=pertanyaan9, pertanyaan10=pertanyaan11, pertanyaan12=pertanyaan12, pertanyaan13=pertanyaan13, pertanyaan14=pertanyaan14, pertanyaan15=pertanyaan15, pertanyaan16=pertanyaan16, pertanyaan17=pertanyaan17, prediction=prediction)

@main.route('/question')
@login_required
def question():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 5, type=int) 
    question, total_rows = Question.get_question(page, per_page)
    total_pages = total_rows // per_page + (1 if total_rows % per_page > 0 else 0)
    return render_template('question/index.html', question=question, page=page, per_page=per_page, total_pages=total_pages)

@main.route("/tambah_pertanyaan", methods=['GET', 'POST'])
def add_question():
    form = AddQuestionForm()
    if form.validate_on_submit():
        Question.create(form.fitur.data, form.pertanyaan.data)
        session['flash_message'] = ('Pertanyaan berhasil ditambahkan!', 'success')
        return redirect(url_for('main.question'))  
    return render_template('question/form.html', title='Tambah Pertanyaan', form=form)

@main.route('/question/<int:id>/detail', methods=['GET', 'POST'])
def view_question(id):
    form = AddQuestionForm()
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, fitur, pertanyaan FROM question WHERE id = %s", (id,))
    question = cur.fetchone()

    if not question:
        return "Pertanyaan tidak ditemukan", 404

    if request.method == 'POST' and form.validate_on_submit():
        fitur = form.fitur.data
        pertanyaan = form.pertanyaan.data
        
        try:
            cur.execute("UPDATE question SET fitur = %s, pertanyaan = %s WHERE id = %s",
                        (fitur, pertanyaan, id))
            mysql.connection.commit()
            session['flash_message'] = ('Pertanyaan berhasil diperbarui!', 'success')
            return redirect(url_for('main.question'))
        except Exception as e:
            mysql.connection.rollback()
            logging.error(f"Error: {e}")
            return "Terjadi kesalahan saat memperbarui pertanyaan", 500
    cur.close()

    # Populate form fields with existing question data
    form.fitur.data = question[1]
    form.pertanyaan.data = question[2]

    return render_template('question/detail.html', title='Detail Pertanyaan', form=form)

@main.route("/form_kandidat", methods=['GET', 'POST'])
def form_kandidat():
    form = SignInForm()
    if form.validate_on_submit():
        username = form.username.data
        kode = form.kode.data

        user = Candidate.get_by_username(username)
        if user and user.kode == kode:
            # Simpan ke session atau lakukan aksi signin lainnya
            login_user(user)  # Asumsi menggunakan Flask-Login untuk manajemen login
            flash('Signin berhasil!', 'success')
            return redirect(url_for('main.index'))
        else:
            flash('Signin gagal. Silakan periksa username dan kode Anda.', 'danger')

    return render_template('form_kandidat/signin.html', form=form)

@main.route("/form_kandidat/biodata", methods=['GET', 'POST'])
def biodata_kandidat():
    # form = BiodataForm()
    # candidate = Candidate.get_by_uuid(uuid)
    # if request.method == 'POST' and form.validate_on_submit():
    #     biodata = form.biodata.data
    #     candidate.biodata = biodata
    #     db.session.commit()
    #     flash('Biodata berhasil diperbarui!', 'success')
    #     return redirect(url_for('main.biodata_kandidat', uuid=uuid))
    # form.biodata.data = candidate.biodata
    return render_template('form_kandidat/biodata.html')

@main.route("/form_kandidat/pertanyaan1", methods=['GET','POST'])
def pertanyaan1_kandidat():
        return render_template('form_kandidat/pertanyaan1.html')
