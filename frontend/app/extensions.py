from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_pymongo import PyMongo
from flask_simpleldap import LDAP

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
mongo = PyMongo()
ldap = LDAP()
