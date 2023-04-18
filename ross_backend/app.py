import flask.scaffold

from db import db

flask.helpers._endpoint_from_view_func = flask.scaffold._endpoint_from_view_func
from flask_restful import Api
from blacklist import BLACKLIST
from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from resources.sort import SortDefault, Sort
from resources.project import Project, Projects
from resources.data import RawData, RawDataDefault
from resources.detect import Detect, DetectDefault
from resources.sorting_result import SortingResultDefault
from resources.detection_result import DetectionResultDefault
from resources.user import UserRegister, UserLogin, User, TokenRefresh, UserLogout

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'  # 'sqlite:///:memory:' # 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PROPAGATE_EXCEPTIONS'] = True
app.secret_key = 'g!\x8d3\xd8\xaa\n{A[\xff\xfe\x08\x05\xd7\x85'
api = Api(app)


@app.before_first_request
def create_tables():
    db.create_all()


app.config['JWT_BLACKLIST_ENABLED'] = True  # enable blacklist feature
app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']  # allow blacklisting for access and refresh tokens
jwt = JWTManager(app)


# This method will check if a token is blacklisted, and will be called automatically when blacklist is enabled
@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    return decrypted_token['jti'] in BLACKLIST


# The following callbacks are used for customizing jwt response/error messages.
# The original ones may not be in a very pretty format (opinionated)
@jwt.expired_token_loader
def expired_token_callback():
    return jsonify({
        'message': 'The token has expired.',
        'error': 'token_expired'
    }), 401


@jwt.invalid_token_loader
def invalid_token_callback(error):  # we have to keep the argument here, since it's passed in by the caller internally
    return jsonify({
        'message': 'Signature verification failed.',
        'error': 'invalid_token'
    }), 401


@jwt.unauthorized_loader
def missing_token_callback(error):
    return jsonify({
        "description": "Request does not contain an access token.",
        'error': 'authorization_required'
    }), 401


@jwt.needs_fresh_token_loader
def token_not_fresh_callback():
    return jsonify({
        "description": "The token is not fresh.",
        'error': 'fresh_token_required'
    }), 401


@jwt.revoked_token_loader
def revoked_token_callback():
    return jsonify({
        "description": "The token has been revoked.",
        'error': 'token_revoked'
    }), 401


api.add_resource(UserRegister, '/register')
api.add_resource(UserLogin, '/login')
api.add_resource(TokenRefresh, '/refresh')
api.add_resource(UserLogout, '/logout')
api.add_resource(User, '/user/<int:user_id>')

api.add_resource(RawData, '/raw/<string:name>')
api.add_resource(RawDataDefault, '/raw')
api.add_resource(DetectDefault, '/detect')
api.add_resource(Detect, '/detect/<string:name>')
api.add_resource(SortDefault, '/sort')
api.add_resource(Sort, '/sort/<string:name>')

api.add_resource(DetectionResultDefault, '/detection_result')
api.add_resource(SortingResultDefault, '/sorting_result')

api.add_resource(Projects, '/projects')
api.add_resource(Project, '/project/<string:name>')

if __name__ == '__main__':
    db.init_app(app)
    app.run(port=5000, debug=False)
