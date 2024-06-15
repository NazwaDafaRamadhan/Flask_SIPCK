from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, HiddenField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Regexp
import random

class RegistrationForm(FlaskForm):
    username = StringField('username', validators=[DataRequired(message='Harap isikan form ini.')])
    email = StringField('email', validators=[DataRequired(message='Harap isikan form ini.'), Email(message='Periksa kembali email anda.')])
    password = PasswordField('password', validators=[
        DataRequired(),
        Length(min=6, message='Password harus lebih dari 6 karakter.'),
        Regexp(r'(?=.*[0-9])(?=.*[a-zA-Z])', message='Password harus terdiri dari huruf dan angka.')
        ])
    confirm_password = PasswordField('confirm_password', validators=[DataRequired(), EqualTo('password', message='Harap pastikan password anda telah sesuai.')])
    role = HiddenField('Role', default='Admin')
    submit = SubmitField('Sign Up')

class LoginForm(FlaskForm):
    email = StringField('email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('RememberPassword')
    submit = SubmitField('Login')

class AddCandidateForm(FlaskForm):
    nama_akun = StringField('Nama Akun', validators=[DataRequired()])
    kode = StringField('Kode', render_kw={'readonly': True})
    status = HiddenField('Status', default=0)
    submit = SubmitField('Tambah Akun')

    def generate_kode(self):
        kode = ''.join(random.choices('0123456789', k=10))
        self.kode.data = kode