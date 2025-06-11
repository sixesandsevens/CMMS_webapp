from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    PasswordField,
    BooleanField,
    SubmitField,
    TextAreaField,
    SelectField,
    DateField,
    IntegerField,
)
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo
from app.models import User

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')


class AssetForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    location = StringField('Location')
    serial_number = StringField('Serial Number')
    description = TextAreaField('Description')
    submit = SubmitField('Submit')


class WorkOrderForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description')
    asset_id = SelectField('Asset', coerce=int)
    assigned_to = SelectField('Assign To', coerce=int)
    priority = SelectField(
        'Priority',
        choices=[('Low', 'Low'), ('Normal', 'Normal'), ('High', 'High')],
        default='Normal',
    )
    status = SelectField(
        'Status',
        choices=[('Open', 'Open'), ('In Progress', 'In Progress'), ('Completed', 'Completed')],
        default='Open',
    )
    due_date = DateField('Due Date', format='%Y-%m-%d')
    recurring_interval_days = IntegerField('Recurring Interval (days)')
    submit = SubmitField('Submit')
