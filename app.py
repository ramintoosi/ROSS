from flask import Flask, jsonify
import flask.scaffold
flask.helpers._endpoint_from_view_func = flask.scaffold._endpoint_from_view_func
from flask_restful import Api
from flask_jwt_extended import JWTManager

from flask_jwt import JWT

from db import db
from blacklist import BLACKLIST


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'#'sqlite:///:memory:' # 'sqlite:///data.db' 
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PROPAGATE_EXCEPTIONS'] = True   

app.secret_key = 'g!\x8d3\xd8\xaa\n{A[\xff\xfe\x08\x05\xd7\x85'

api = Api(app)
