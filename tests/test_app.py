import pytest
from app import create_app, db


@pytest.fixture(scope='module')
def test_client():
    app = create_app(config_name='testing')
    app.testing = True
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client

        with app.app_context():
            db.drop_all()


def test_index(test_client):
    response = test_client.get('/')
    assert response.status_code == 200
