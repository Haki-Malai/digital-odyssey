import os
import json

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Configuration base, for all environments.
    :param config_file: path to config file
    """
    config_file: str|None = None

    def __init__(self) -> None:
        """Load config from json file.
        """
        if not self.config_file:
            return

        with open(self.config_file) as f:
            config = json.load(f)

        for key, value in config.items():
            setattr(self, key, value)

    def update_config(self, key: str, value: str) -> None:
        """Update config file with new value.
        """
        with open(self.config_file) as f:
            config = json.load(f)

        config[key.upper()] = value

        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=4)


class DevelopmentConfig(Config):
    """Development configuration.
    """
    SQLALCHEMY_DATABASE_URI:str = 'sqlite:///' + os.path.join(basedir,
                                                          "dev-data.sqlite")
    DEBUG: bool = True

    def __init__(self) -> None:
        self.config_file = os.path.join(basedir, 'dev_config.json')
        super().__init__()


class TestingConfig(Config):
    """Testing configuration.
    """
    SQLALCHEMY_DATABASE_URI:str = 'sqlite:///' + os.path.join(basedir,
                                                          "test-data.sqlite")
    TESTING: bool = True

    def __init__(self) -> None:
        self.config_file = os.path.join(basedir, 'test_config.json')
        super().__init__()


class ProductionConfig(Config):
    """Production configuration.
    """

    SQLALCHEMY_DATABASE_URI:str = 'sqlite:///' + os.path.join(basedir,
                                                          "prod-data.sqlite")
    PRODUCTION: bool = True

    def __init__(self) -> None:
        self.config_file = os.path.join(basedir, 'config.json')
        super().__init__()


config = {
    'default': DevelopmentConfig(),
    'production': ProductionConfig(),
    'development': DevelopmentConfig(),
    'testing': TestingConfig()
}
