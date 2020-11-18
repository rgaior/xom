import os
basedir = os.path.abspath(os.path.dirname(__file__))


class BaseConfig:
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    MONGO_URI =os.environ.get('MONGODB_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ['SECRET_KEY']
    LDAP_USERNAME = os.environ.get('LDAP_USERNAME')
    LDAP_PASSWORD = os.environ.get('LDAP_PASSWORD')
    LDAP_HOST = os.environ.get('LDAP_HOST')
    LDAP_PORT = os.environ.get('LDAP_PORT')
    LDAP_BASE_DN = os.environ.get('LDAP_BASE_DN')
    LDAP_SCHEMA = os.environ.get('LDAP_SCHEMA')
    LDAP_USER_OBJECT_FILTER = os.environ.get('LDAP_USER_OBJECT_FILTER')
    LDAP_PROTOCOL_VERSION = 3
    LDAP_OPENLDAP=os.environ.get('LDAP_OPENLDAP')
