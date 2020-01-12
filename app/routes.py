from app import app, jwt
from werkzeug.exceptions import HTTPException
from flask import jsonify, request, abort, json
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from app.models import User

# Create a function that will be called whenever create_access_token
# is used. It will take whatever object is passed into the
# create_access_token method, and lets us define what custom claims
# should be added to the access token.
@jwt.user_claims_loader
def add_claims_to_access_token(user):
    return {'role': user.role}

# Create a function that will be called whenever create_access_token
# is used. It will take whatever object is passed into the
# create_access_token method, and lets us define what the identity
# of the access token should be.
@jwt.user_identity_loader
def user_identity_lookup(user):
    return user.username

@app.route('/')
def hello_world():
    return "Hello world"

@app.route('/login', methods=['POST'])
def login():
    if not request.is_json:
        abort(400, "Missing JSON in request")
    username = request.json.get('username', None)
    if not username:
        abort(400, "Missing username parameter")
    password = request.json.get('username', None)
    if not password:
        abort(400, "Missing password parameter")
    user =  User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        ret = {'access_token': create_access_token(identity=user)}
        return jsonify(ret), 200
    else:
        abort(401, "Bad username or passowrd")

@app.route('/user', methods=['GET'])
@jwt_required
def get_user():
    current_user = get_jwt_identity()
    print(current_user)
    return jsonify(logged_in_as=current_user), 200


@app.errorhandler(HTTPException)
def handle_exception(e):
    """Return JSON instead of HTML for HTTP errors (flask docs)."""
    # start with the correct headers and status code from the error
    response = e.get_response()
    # replace the body with JSON
    response.data = json.dumps({
        "code": e.code,
        "name": e.name,
        "description": e.description,
    })
    response.content_type = "application/json"
    return response