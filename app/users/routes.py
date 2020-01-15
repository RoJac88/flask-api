from functools import wraps
from marshmallow import ValidationError

from app import jwt
from flask import jsonify, request, abort, json
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity, get_jwt_claims, verify_jwt_in_request
from app.models import db, User, user_schema, users_schema
from app.users import bp

def admin_required(fn):
    """Custum decorator to check for admin permissions (role=0)"""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        claims = get_jwt_claims()
        if claims['role'] > 0:
            abort(403, "You are not allowed to view this resource")
        else:
            return fn(*args, **kwargs)
    return wrapper

# Create a function that will be called whenever create_access_token
# is used. It will take whatever object is passed into the
# create_access_token method, and lets us define what custom claims
# should be added to the access token.
@jwt.user_claims_loader
def add_claims_to_access_token(user):
    return {'role': user.role, 'username': user.username}

# ... define what the identity of the access token should be.
@jwt.user_identity_loader
def user_identity_lookup(user):
    return user.id

@bp.route('/login', methods=['POST'])
def login():
    if not request.is_json:
        abort(400, "Missing JSON in request")
    username = request.json.get('username', None)
    if not username:
        abort(400, "Missing username parameter")
    password = request.json.get('password', None)
    if not password:
        abort(400, "Missing password parameter")
    user =  User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        ret = {'access_token': create_access_token(identity=user)}
        return jsonify(ret), 200
    else:
        abort(401, "Bad username or passowrd")

@bp.route('/register', methods=['POST'])
@admin_required
def register():
    if not request.is_json:
        abort(400, "Missing JSON in request")
    username = request.json.get('username', None)
    if not username:
        abort(400, "Missing username parameter")
    password = request.json.get('password', None)
    if not password:
        abort(400, "Missing password parameter")
    if User.query.filter_by(username=username).first() != None:
        abort(409, "Username already registered")
    try:
        email = request.json.get('email', None)
        new_user = user_schema.load({'username': username, 'email': email})
    except ValidationError as e:
        abort(400, e.messages)
    if User.query.filter_by(email=email).first() != None:
        abort(409, "Email already registered")
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()
    return user_schema.dump(new_user), 201

@bp.route('/users', methods=['GET'])
@admin_required
def get_users():
    all_users = User.query.all()
    res = users_schema.dump(all_users)
    return jsonify(res), 200

@bp.route('/users/<int:user_id>', methods=['GET', 'DELETE'])
@jwt_required
def user(user_id):
    claims = get_jwt_claims()
    if claims['role'] > 0 and get_jwt_identity() != user_id:
        abort(403, "You are not allowed to view this resource")
    user = User.query.get(user_id)
    if not user:
        abort(404, "User not found")
    if request.method == 'GET':
        res = user_schema.dump(user)
        return jsonify(res), 200
    elif request.method == 'DELETE':
        db.session.delete(user)
        db.session.commit()
        return jsonify(), 204
    else:
        abort(405, "The method is not allowed for the requested URL.")