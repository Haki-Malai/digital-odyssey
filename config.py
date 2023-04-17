import os
import json

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    config_file = os.path.join(basedir, "app/static/uploads/config.json")
    
    def __init__(self, config_file=config_file):
        """Load config from json file.
        """
        with open(config_file) as f:
            config = json.load(f)

        for key, value in config.items():
            setattr(self, key, value)

    def update_config(self, key, value):
        """Update config file with new value.
        """
        with open(self.config_file) as f:
            config = json.load(f)

        config[key.upper()] = value

        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=4)

 
class DevelopmentConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir,
                                                          "dev-data.sqlite")
    DEBUG = True


class TestingConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir,
                                                          "test-data.sqlite")
    TESTING = True

    
class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir,
                                                          "prod-data.sqlite")
    PRODUCTION = True


config = {
    'default': DevelopmentConfig(),
    'production': ProductionConfig(),
    'development': DevelopmentConfig(),
    'testing': TestingConfig()
}