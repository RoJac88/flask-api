import pytest
from config import Config
from app import create_app, db
from app.models import User

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'

@pytest.fixture
def client():
    app = create_app(TestConfig)
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            admin = User(username="admin", role=0, email="admin@email.com")
            admin.set_password("admin")
            db.session.add(admin)
            user = User(username="user", email="user@email.com")
            user.set_password("user")
            db.session.add(user)
            db.session.commit()
        yield client
    db.session.remove()
