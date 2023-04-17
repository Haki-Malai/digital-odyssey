from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from apifairy import APIFairy
from flask_marshmallow import Marshmallow
from elasticsearch import Elasticsearch
from redis import Redis
import rq
from config import config

db = SQLAlchemy()
mg = Migrate()
login = LoginManager()
fairy = APIFairy()
ma = Marshmallow()
login.login_view = 'auth.login'
login.login_message = 'Please log in to access this page.'
login.login_message_category = 'warning'
mail = Mail()


def create_app(config_name='default'):
    app = Flask(__name__)
    app.config_obj = config[config_name]
    app.config.from_object(app.config_obj)

    # Disable trailing slash 
    app.url_map.strict_slashes = False

    # Initialize extensions
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

    # Register blueprints
    from app.cli import bp as cli_bp
    app.register_blueprint(cli_bp)
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)
    from app.admin import bp as admin_bp
    app.register_blueprint(admin_bp)
    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp)
    from app.api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    # Create shell context for flask shell
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

    # Create database tables for our data models
    with app.app_context():
        db.create_all()

    return app
    