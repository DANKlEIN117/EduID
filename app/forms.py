from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length, EqualTo


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=100)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6, max=128)])
    remember = BooleanField('Remember me')


class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=100)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6, max=128)])
    confirm = PasswordField('Confirm password', validators=[DataRequired(), EqualTo('password', message='Passwords must match')])
    role = SelectField('Role', choices=[('student', 'Student'), ('admin', 'Admin')])
    admin_code = StringField('Admin code')
