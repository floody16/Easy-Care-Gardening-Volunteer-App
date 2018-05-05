from gtk.keysyms import Find

from app import db
from app.forms import RegistrationForm, LoginForm, ChangePasswordForm, FindUserForm, FeedbackForm
from app.models import User, Job, Feedback
from app.utils import day_pref_to_binary, get_suitable_jobs

from flask import Blueprint, flash, redirect, url_for, render_template
from flask_login import login_user, current_user, logout_user, login_required
import datetime

user = Blueprint('user', __name__, url_prefix='/user/', template_folder='templates')


@user.route('/register/', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        flash('You are already logged in.', 'info')
        return redirect(url_for('user.dashboard'))

    registration_form = RegistrationForm()

    if registration_form.validate_on_submit():
        new_user = User(email=registration_form.email.data,
                        full_name=registration_form.full_name.data,
                        user_type=registration_form.user_type.data,
                        join_date=registration_form.join_date.data,
                        next_police_check=registration_form.next_police_check.data,
                        time_pref=registration_form.time_pref.data,
                        day_pref=day_pref_to_binary(registration_form.day_prefs.data))
        new_user.set_password(registration_form.password.data)

        db.session.add(new_user)
        db.session.commit()

        login_user(new_user)
        flash('Registration successful.', 'success')
        return redirect(url_for('user.dashboard'))

    return render_template('user/register.html', title='Register', form=registration_form)


@user.route('/login/', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        flash('You are already logged in.', 'info')
        return redirect(url_for('user.dashboard'))

    login_form = LoginForm()

    if login_form.validate_on_submit():
        this_user = User.query.filter_by(email=login_form.email.data).scalar()

        if this_user is None or not this_user.check_password(login_form.password.data):
            flash('Invalid credentials.', 'danger')
            return redirect(url_for('user.login'))

        login_user(this_user)
        flash('Login successful.', 'success')
        return redirect(url_for('user.dashboard'))

    return render_template('user/login.html', title='Log in', form=login_form)


@user.route('/dashboard/')
@login_required
def dashboard():
    return render_template('user/dashboard.html', title='Dashboard')


@user.route('/profile/', methods=['GET', 'POST'])
@login_required
def profile():
    change_password_form = ChangePasswordForm()

    if change_password_form.validate_on_submit():
        user = User.query.filter_by(id=current_user.id).scalar()

        if not user.check_password(change_password_form.old_password.data):
            flash('Old password is incorrect.', 'danger')
            return redirect(url_for('user.profile'))

        user.set_password(change_password_form.new_password.data)
        db.session.commit()

        flash('Password changed.', 'success')
        return redirect(url_for('user.profile'))

    return render_template('user/profile.html', title=current_user.full_name, form=change_password_form)


@user.route('/roster/')
@login_required
def roster():
    jobs = Job.query.filter(Job.date >= datetime.date.today()).order_by(Job.date).all()

    data = {
        'title': 'Roster',
        'jobs': get_suitable_jobs(jobs, current_user.time_pref, current_user.day_pref)
    }

    return render_template('user/roster.html', **data)


@user.route('/feedback/', methods=['GET', 'POST'])
@login_required
def feedback():
    feedback_form = FeedbackForm()
    all_feedback = Feedback.query.filter_by(user_id=current_user.id).all()

    if feedback_form.validate_on_submit():
        new_feedback = Feedback(user_id=current_user.id,
                                job_id=feedback_form.job.data,
                                body=feedback_form.body.data)

        db.session.add(new_feedback)
        db.session.commit()

        flash('Feedback submitted.', 'success')
        return redirect(url_for('user.feedback'))

    data = {
        'title': 'Your Feedback',
        'form': feedback_form,
        'all_feedback': all_feedback
    }

    return render_template('user/feedback.html', **data)


@user.route('/')
def manage():
    find_user_form = FindUserForm()

    data = {
        'title': 'Manage Users',
        'form': find_user_form
    }

    return render_template('user/manage.html', **data)


@user.route('/user/logout/')
def logout():
    logout_user()
    flash('Log out successful.', 'info')
    return redirect(url_for('user.login'))
