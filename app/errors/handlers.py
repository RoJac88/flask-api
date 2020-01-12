from flask import jsonify, json
from werkzeug.exceptions import HTTPException
from app import jwt
from app.errors import bp

@bp.app_errorhandler(HTTPException)
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

@jwt.unauthorized_loader
def unauthorized_callback(msg):
    return jsonify({
        'code': 401,
        'name': 'Unauthorized',
        'description': msg
    }), 401

@jwt.expired_token_loader
def expired_token_callback(token):
    token_type = token['type']
    return jsonify({
        'code': 401,
        'name': 'Unauthorized',
        'description': f'The {token_type} token has expired'
    }), 401

@jwt.invalid_token_loader
def invalid_token_callback(msg):
    return jsonify({
        'code': 401,
        'name': 'Unauthorized',
        'description': msg
    }), 401