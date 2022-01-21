from flask import Blueprint
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask import flash
from flask_login import current_user
from flask_login import login_required
from flask_login import login_user
from flask_login import logout_user
from werkzeug.urls import url_parse

from app.extensions import db
from app.extensions import login
from app.extensions import ldap
from app.forms import LoginForm
#from app.forms import RegistrationForm
from app.models import User

server_bp = Blueprint('main', __name__)
main_bp = Blueprint('main_bp', __name__,
                    template_folder='templates',
                    static_folder='static')

@server_bp.route('/')
def index():
# #    return render_template("login.html", title='Home Page')
    return render_template("index.html", title='Home Page')

 
@server_bp.route('/login/', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main_bp.home'))

    form = LoginForm()
    if form.validate_on_submit():
        ldapres = User.try_login(form.username.data, form.password.data)
        if not ldapres:
            flash(
                'Invalid username or password. Please try again.',
                'danger')
            error = 'Invalid username or password' 
            return render_template('login.html', form=form, error=error)

        user = User.query.filter_by(username=form.username.data).first()
 
        if not user:
            #user = User(username, password)
            user = User(username=form.username.data)
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
        login_user(user)
        flash('You have successfully logged in.', 'success')
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.index')
#            next_page = url_for('main_bp.home')
        return redirect(next_page)

    return render_template('login.html', title='Sign In', form=form)


@server_bp.route('/logout/')
@login_required
def logout():
    logout_user()

    return redirect(url_for('main.index'))


# @server_bp.route('/register/', methods=['GET', 'POST'])
# def register():
#     if current_user.is_authenticated:
#         return redirect(url_for('main.index'))

#     form = RegistrationForm()
#     if form.validate_on_submit():
#         user = User(username=form.username.data)
#         user.set_password(form.password.data)
#         db.session.add(user)
#         db.session.commit()

#         return redirect(url_for('main.login'))

#     return render_template('register.html', title='Register', form=form)




@main_bp.route('/dash/')
@login_required
def home():
    """Landing page."""
    return render_template('home.html',
                           title='home page',
                           body="under construction")

