from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from config import config

db = SQLAlchemy()
mg = Migrate()
login = LoginManager()
bs = Bootstrap()
mail = Mail()


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    # Initialize extensions
    db.init_app(app)
    mg.init_app(app, db)
    login.init_app(app)
    bs.init_app(app)
    mail.init_app(app)
    
    

