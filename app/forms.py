from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Length, EqualTo, Email, Optional
from flask_wtf.file import FileField, FileAllowed


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=100)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6, max=128)])
    remember = BooleanField('Remember me')


class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=100)])
    reg_no = StringField('Registration Number', validators=[Optional()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6, max=128)])
    confirm = PasswordField('Confirm password', validators=[DataRequired(), EqualTo('password', message='Passwords must match')])
    role = SelectField('Role', choices=[('student', 'Student'), ('admin', 'Admin')])
    admin_code = StringField('Admin code')


class StudentProfileForm(FlaskForm):
    reg_no = StringField('Registration Number', validators=[DataRequired()])
    full_name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=120)])
    email = StringField('Email', validators=[Email(), Optional()])
    phone = StringField('Phone Number', validators=[Length(max=20), Optional()])
    date_of_birth = StringField('Date of Birth (YYYY-MM-DD)', validators=[Optional()])
    class_level = StringField('Class/Level', validators=[Optional()])
    submit = SubmitField('Update Profile')


class IDSubmissionForm(FlaskForm):
    photo = FileField('Student Photo', validators=[FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')])
    notes = TextAreaField('Additional Notes', validators=[Optional(), Length(max=500)])
    submit = SubmitField('Submit for Review')


class AdminReviewForm(FlaskForm):
    status = SelectField('Status', choices=[
        ('approved', 'Approve'),
        ('rejected', 'Reject')
    ])
    rejection_reason = TextAreaField('Rejection Reason (if rejected)', validators=[Optional(), Length(max=500)])
    notes = TextAreaField('Admin Notes', validators=[Optional(), Length(max=500)])
    submit = SubmitField('Submit Review')

