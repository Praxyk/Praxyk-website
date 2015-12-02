import os, sys
from flask import Flask
from flask.ext.restful import Api, Resource

sys.path.append('../')
from app.util import *

app = Flask(__name__)
api = Api(app)
app.secret_key = os.urandom(24)
from app import views
