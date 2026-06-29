from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from models import User


class LoginForm(FlaskForm):
    email = StringField('Email Address', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Keep me signed in')
    submit = SubmitField('Sign In')


class RegisterForm(FlaskForm):
    name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=120)])
    email = StringField('Email Address', validators=[DataRequired(), Email(), Length(max=180)])
    phone = StringField('Phone Number', validators=[Length(max=20)])
    city = StringField('City', validators=[Length(max=80)])
    role = SelectField(
        'I am registering as',
        choices=[('trekker', 'Trekker (I want to go on treks)'),
                 ('staff', 'Trek Guide (I will lead treks)')],
        validators=[DataRequired()],
    )
    password = PasswordField(
        'Password',
        validators=[DataRequired(), Length(min=6, message='Password must be at least 6 characters.')]
    )
    confirm_password = PasswordField(
        'Confirm Password',
        validators=[DataRequired(), EqualTo('password', message='Passwords must match.')]
    )
    submit = SubmitField('Create Account')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data.lower()).first():
            raise ValidationError('An account with this email already exists.')