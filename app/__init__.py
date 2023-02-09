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


def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    # Initialize extensions
    db.init_app(app)
    mg.init_app(app, db)
    login.init_app(app)
    bs.init_app(app)
    mail.init_app(app)

    # Register cli commands blueprint
    from app.cli import bp as cli_bp 
    app.register_blueprint(cli_bp)
    # Register route blueprints
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app import models
    @app.shell_context_processor
    def make_shell_context():
        ctx = {'db': db}
        for attr in dir(models):
            model = getattr(models, attr)
            if hasattr(model, '__bases__') and \
                    db.Model in getattr(model, '__bases__'):
                ctx[attr] = model
        return ctx

    return app