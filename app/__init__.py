from flask import Flask
from flask_wtf import CSRFProtect
from flask_mysqldb import MySQL
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_babel import Babel, format_currency
import joblib
from config import Config

csrf = CSRFProtect()
mysql = MySQL()
bcrypt = Bcrypt()
babel = Babel()
login_manager = LoginManager()
login_manager.login_view = 'main.login'

def create_app():
    app = Flask(__name__)
    
    app.config.from_object(Config)

    csrf.init_app(app)
    babel.init_app(app)
    mysql.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    app.model = joblib.load('app/models/identifikasi_potensi_RF.pkl')

    # Register the format_currency filter
    app.jinja_env.filters['format_currency'] = format_currency

    # Daftarkan blueprint
    from app.routes import main as main_blueprint
    app.register_blueprint(main_blueprint)
    
    return app
