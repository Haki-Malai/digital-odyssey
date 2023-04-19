import pytest
from flask import Flask
from typing import Generator

from app import create_app


@pytest.fixture
def app() -> Generator[Flask, None, None]:
    """Create and configure a new app instance for each test.
    """
    app = create_app('testing')
    with app.app_context():
        yield app


@pytest.fixture
def client(app: Flask) -> Flask.test_client:
    """A test client for the app.
    :param app: The app fixture.
    """
    return app.test_client()


@pytest.fixture
def db(app: Flask) -> Generator:
    """Create a new database for a test.
    :param app: The app fixture.
    """
    with app.app_context():
        db = app.extensions['sqlalchemy'].db
        db.drop_all()
        db.create_all()
        yield db


def test_config(app: Flask) -> None:
    """Test that the app is configured correctly.
    :param app: The app fixture.
    """
    assert app.config['TESTING'] is True
    assert isinstance(app.config['SQLALCHEMY_DATABASE_URI'], str)
    assert app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] is False


def test_base(app: Flask, client: Flask.test_client) -> None:
    """Test that the app is created and configured correctly.
    :param app: The app fixture.
    :param client: The client fixture.
    """
    assert client.get('/').status_code == 200
    assert app.config['TITLE'] in client.get('/').data.decode('utf-8')
