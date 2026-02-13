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
    submit = SubmitField('Register as Student')


class AdminRegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=100)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6, max=128)])
    confirm = PasswordField('Confirm password', validators=[DataRequired(), EqualTo('password', message='Passwords must match')])
    submit = SubmitField('Create Admin Account')


class AdminInviteForm(FlaskForm):
    email = StringField('Email Address', validators=[DataRequired(), Email()])
    submit = SubmitField('Send Invitation')


class StudentProfileForm(FlaskForm):
    reg_no = StringField('Registration Number', validators=[DataRequired()])
    full_name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=120)])
    school_name = StringField('School Name', validators=[DataRequired(), Length(min=2, max=200)])
    course = StringField('Course/Program', validators=[DataRequired(), Length(min=2, max=200)])
    email = StringField('Email', validators=[Email(), Optional()])
    phone = StringField('Phone Number', validators=[Length(max=20), Optional()])
    date_of_birth = StringField('Date of Birth (YYYY-MM-DD)', validators=[Optional()])
    class_level = SelectField('Class/Level', validators=[Optional()], choices=[
        ('', 'Select a class level'),
        ('Form 1', 'Form 1'),
        ('Form 2', 'Form 2'),
        ('Form 3', 'Form 3'),
        ('Form 4', 'Form 4'),
        ('Form 5', 'Form 5'),
        ('Form 6', 'Form 6'),
        ('Year 1', 'Year 1'),
        ('Year 2', 'Year 2'),
        ('Year 3', 'Year 3'),
        ('Year 4', 'Year 4'),
        ('Diploma 1', 'Diploma 1'),
        ('Diploma 2', 'Diploma 2'),
        ('Diploma 3', 'Diploma 3'),
    ])
    valid_until = StringField('Valid Until (YYYY-MM-DD)', validators=[Optional()])
    blood_type = StringField('Blood Type (e.g., O+, A-, AB+)', validators=[Optional(), Length(max=10)])
    allergies = StringField('Allergies', validators=[Optional(), Length(max=200)])
    emergency_contact_name = StringField('Emergency Contact Name', validators=[Optional(), Length(max=120)])
    emergency_contact_phone = StringField('Emergency Contact Phone', validators=[Optional(), Length(max=20)])
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

