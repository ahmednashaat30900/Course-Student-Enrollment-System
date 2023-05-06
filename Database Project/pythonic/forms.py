from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from flask_wtf.file import FileField, FileAllowed
from pythonic.models import Students



# ================================================================================================================
# Forms
class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',  validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = Students.query.filter_by(student_username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = Students.query.filter_by(student_email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(),Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class AddLessonForm(FlaskForm):
    lesson_name = StringField('Email', validators=[DataRequired()])
    lesson_file = FileField('Upload file', validators=[FileAllowed(['pdf'])])
    submit = SubmitField('Upload')


class UpdateAccountForm(FlaskForm):
    username = StringField('Username', validators=[ Length(min=2, max=20)])
    email = StringField('Email', validators=[])
    headline = StringField('Headline', validators=[])
    mobil = StringField('Mobil', validators=[])
    about = TextAreaField('About', validators=[])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')
# END OF FORMS
# ================================================================================================================