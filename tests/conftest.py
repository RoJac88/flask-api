import pytest
from config import Config
from app import create_app, db as _db
from app.models import User

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'

@pytest.fixture
def app():
    return create_app(TestConfig)

@pytest.fixture
def client(app):
    with app.test_client() as client:
        return client

@pytest.fixture
def db(app):
    with app.app_context():
        _db.create_all()
        admin = User(username="admin", role=0, email="admin@email.com")
        admin.set_password("admin")
        _db.session.add(admin)
        user = User(username="user", email="user@email.com")
        user.set_password("user")
        _db.session.add(user)
        _db.session.commit()
        yield _db
        _db.drop_all()
        _db.session.commit()
        _db.session.remove()