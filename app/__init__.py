from flask import Flask
from flask_wtf import CSRFProtect
from flask_mysqldb import MySQL
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from config import Config

csrf = CSRFProtect()
mysql = MySQL()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'main.login'

def create_app():
    app = Flask(__name__)
    
    app.config.from_object(Config)

    csrf.init_app(app)
    mysql.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    # Daftarkan blueprint
    from app.routes import main as main_blueprint
    app.register_blueprint(main_blueprint)
    
    return app
