from app import db, ma 
from marshmallow import fields 
from datetime import datetime as dt
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    email = db.Column(db.String(120), unique=True, nullable=False)
    role = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, index=True, default=dt.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

class UserSchema(ma.ModelSchema):

    email = fields.Email()
    
    class Meta:
        model = User 
        exclude = (["password_hash"])

user_schema = UserSchema()
users_schema = UserSchema(many=True)