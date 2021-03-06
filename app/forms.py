from app.models import User
from app.utils import past_jobs_pretty

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, SubmitField, TextAreaField, SelectMultipleField, widgets
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from wtforms.fields.html5 import DateField

user_types = [('0', 'Volunteer'), ('1', 'Team Leader'), ('2', 'Coordinator'), ('3', 'Administrator')]
times = [('AM', 'AM'), ('PM', 'PM'), ('AP', 'AM/PM')]
days = [('0', 'Monday'), ('1', 'Tuesday'), ('2', 'Wednesday'), ('3', 'Thursday'), ('4', 'Friday'), ('5', 'Saturday')]


class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class RegistrationForm(FlaskForm):
    password = PasswordField('Password*', validators=[DataRequired()])
    password_again = PasswordField('Repeat*', validators=[DataRequired(), EqualTo('password', message='Passwords must match.')])
    submit = SubmitField('Register')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Log In')


class NewsForm(FlaskForm):
    title = StringField('Title*', validators=[DataRequired()])
    body = TextAreaField('Body*', validators=[DataRequired()])
    submit = SubmitField('Post')


class JobForm(FlaskForm):
    address = StringField('Address*', validators=[DataRequired()])
    date = DateField('Date*', validators=[DataRequired()])
    time = SelectField('Time*', choices=times[:-1], validators=[DataRequired()])
    notes = TextAreaField('Notes')
    submit = SubmitField('New Job')


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('Old Password*', validators=[DataRequired()])
    new_password = PasswordField('New Password*', validators=[DataRequired()])
    new_password_again = PasswordField('Repeat*', validators=[DataRequired(), EqualTo('new_password', message='Passwords must match.')])
    submit = SubmitField('Change Password')


class FeedbackForm(FlaskForm):
    job = SelectField('Past Job*', validators=[DataRequired()])
    body = TextAreaField('Feedback*', validators=[DataRequired()])
    submit = SubmitField('Submit Feedback')

    def __init__(self, *args, **kwargs):
        super(FeedbackForm, self).__init__(*args, **kwargs)
        self.job.choices = past_jobs_pretty()


class FindUserForm(FlaskForm):
    email = StringField('Email*', validators=[DataRequired(), Email()])
    submit = SubmitField('Find')


class UserForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    full_name = StringField('Full Name', validators=[DataRequired()])
    user_type = SelectField('User Type', choices=user_types, validators=[DataRequired()])
    join_date = DateField('Join Date', validators=[DataRequired()])
    next_police_check = DateField('Next Police Check', validators=[DataRequired()])
    time_pref = SelectField('Time Preference', choices=times, validators=[DataRequired()])
    day_prefs = MultiCheckboxField('Day Preference', choices=days, validators=[DataRequired()])
    submit = SubmitField('Invite')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()

        if user is not None:
            raise ValidationError('Email exists!')
