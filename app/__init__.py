import os
import rq
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from flask_marshmallow import Marshmallow
from sassutils.wsgi import SassMiddleware
from apifairy import APIFairy
from elasticsearch import Elasticsearch
from redis import Redis

from config import config

db = SQLAlchemy()
mg = Migrate()
login = LoginManager()
fairy = APIFairy()
ma = Marshmallow()
login.login_view:str = 'auth.login'
login.login_message:str = 'Please log in to access this page.'
login.login_message_category:str = 'warning'
mail = Mail()


def create_app(config_name:str = 'default'):
    """Create an application instance using the app factory pattern.
    :param config_name: the name of the configuration to use
    :return: the application instance
    """
    app = Flask(__name__)
    app.config_obj = config[config_name]
    app.config_obj.__init__()
    app.config.from_object(app.config_obj)

    app.url_map.strict_slashes:bool = False

    app.wsgi_app = SassMiddleware(app.wsgi_app, {
        'app': ('static/sass', 'static/css', '/static/css')
    })

    db.init_app(app)
    mg.init_app(app, db)
    login.init_app(app)
    mail.init_app(app)
    fairy.init_app(app)
    ma.init_app(app)
    app.elasticsearch = Elasticsearch([app.config['ELASTICSEARCH_URL']]) \
        if app.config['ELASTICSEARCH_URL'] else None
    app.redis = Redis.from_url(app.config['REDIS_URL'])
    app.task_queue = rq.Queue('app-tasks', connection=app.redis)

    from app.cli import bp as cli_bp
    app.register_blueprint(cli_bp)
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)
    from app.admin import bp as admin_bp
    app.register_blueprint(admin_bp)
    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp)
    from app.user import bp as user_bp
    app.register_blueprint(user_bp)
    from app.api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    @app.shell_context_processor
    def make_shell_context():
        """Create a shell context for flask shell.
        """
        from app import models
        ctx = {'db': db}
        for attr in dir(models):
            model = getattr(models, attr)
            if hasattr(model, '__bases__') and \
                    db.Model in getattr(model, '__bases__'):
                ctx[attr] = model
        return ctx

    with app.app_context():
        db.create_all()

    return app


def update_config(app: Flask, config_name: str) -> None:
    """Update the app's configuration with the specified configuration.
    :param app: The Flask app instance.
    :param config_name: The name of the configuration to use.
    """
    config_obj = config[config_name]
    config_obj.__init__()
    app.config.from_object(config_obj)
