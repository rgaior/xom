from flask_login import UserMixin
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash

from app.extensions import db
from app.extensions import login
from app.extensions import ldap
 
@login.user_loader
def load_user(id):
    if id is None or id == 'None': 
        id =-1
    print ('ID leaving load_user', (id))
    return User.query.get(int(id))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(128))

#    username = db.Column(db.String(100))
    def __init__(self, username):
        self.username = username

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    @staticmethod
    def try_login(username, password):
        res = ldap.bind_user(username,password)
#        print ('bind resuls = ', res,flush=True)
        return res

    def __repr__(self):
        return '<User {}>'.format(self.username)






