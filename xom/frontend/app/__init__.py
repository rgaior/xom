from flask import Flask
from config import Config
from flask_bootstrap import Bootstrap
from flask_pymongo import PyMongo
from datetime import datetime

app = Flask(__name__)

app.config.from_object(Config)
bootstrap = Bootstrap(app)

app.jinja_env.globals.update(date_time=datetime)

from app import routes
from app import myserver
