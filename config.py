import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    # General Configs
    TITLE = "Flask Boilerplate"
    NAVIGATION = {
        "Home": "main.index",
        "Shop": "main.index",
        "About": "main.index",
        "Other": {
            "Subpage": "main.index", 
            "Subpage2": "main.index",
            "Subpage3": "main.index",
            "Subpage4": "main.index",
            "Subpage5": "main.index",
        },
        "Contact": "main.index",
    }

    SECRET_KEY = os.environ.get("SECRET_KEY")
    SQLALCHEMY_TRACK_NOTIFICATIONS = False

    @staticmethod
    def init_app(app):
        pass

    @classmethod
    def update_config(cls, app):
        for key in dir(cls):
            if key.isupper():
                app.config[key] = getattr(cls, key)

 
class DevelopmentConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, "dev-data.sqlite")
    DEBUG = True


class TestingConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, "test-data.sqlite")
    TESTING = True

    
class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, "prod-data.sqlite")
    PRODUCTION = True


config = {
    'default': DevelopmentConfig,
    'production': ProductionConfig,
    'development': DevelopmentConfig,
    'testing': TestingConfig
}