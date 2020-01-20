from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired



class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RequestDataForm(FlaskForm):
    startDate = StringField('From', validators=[DataRequired()])
    endDate = StringField('To', validators=[DataRequired()])
    getData = SubmitField('Get Data Entries')
