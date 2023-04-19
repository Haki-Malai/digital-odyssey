import os
import json
import pytest

from config import config


@pytest.fixture(scope='module')
def app_config() -> object:
    """Return app config.
    """
    return config['testing']


def test_config_file_exists() -> None:
    """Test that config file exists.
    """
    assert os.path.isfile(config['default'].config_file)


def test_config_loaded() -> None:
    """Test that config file is loaded.
    """
    assert hasattr(config['default'], 'DEBUG')
    assert hasattr(config['default'], 'SQLALCHEMY_DATABASE_URI')


def test_update_config_file(app_config: object) -> None:
    """Test that config file is updated with new value.
    :param app_config: The app config fixture.
    """
    key = 'DATABASE_URI'
    value = 'sqlite:///new_database.sqlite'
    app_config.update_config(key, value)

    with open(app_config.config_file) as f:
        config = json.load(f)

    assert config.get(key.upper()) == value
