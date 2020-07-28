import os
from flask import Flask
from flask_cors import CORS, cross_origin
from playhouse.flask_utils import FlaskDB


app = Flask(__name__)
app.config.from_pyfile('config.py')

if os.environ.get('YOURAPPLICATION_SETTINGS'):
    app.config.from_envvar('YOURAPPLICATION_SETTINGS')

db_wrapper = FlaskDB(app)
CORS(app, supports_credentials=True)
app.config['CORS_HEADERS'] = 'Content-Type'

