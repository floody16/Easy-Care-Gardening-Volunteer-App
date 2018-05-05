from app import db
from app.forms import RegistrationForm, LoginForm
from app.models import User, Invite

from flask import Blueprint, flash, redirect, url_for, render_template, abort
from flask_login import login_user, current_user, logout_user

auth = Blueprint('auth', __name__, template_folder='templates')


@auth.route('/register/<invite_key>', methods=['GET', 'POST'])
def register(invite_key):
    if current_user.is_authenticated:
        flash('You are already logged in.', 'info')
        return redirect(url_for('user.dashboard'))

    invite = Invite.query.filter_by(key=invite_key).scalar()

    if not invite:
        abort(404)

    registration_form = RegistrationForm()

    if registration_form.validate_on_submit():
        invite.user.set_password(registration_form.password.data)

        db.session.delete(invite)
        db.session.commit()

        login_user(invite.user)
        flash('Registration successful.', 'success')
        return redirect(url_for('user.dashboard'))

    data = {
        'title': 'Register',
        'form': registration_form,
        'user': invite.user
    }

    return render_template('auth/register.html', **data)


@auth.route('/login/', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        flash('You are already logged in.', 'info')
        return redirect(url_for('user.dashboard'))

    login_form = LoginForm()

    if login_form.validate_on_submit():
        this_user = User.query.filter_by(email=login_form.email.data).scalar()

        if this_user is None or not this_user.check_password(login_form.password.data):
            flash('Invalid credentials.', 'danger')
            return redirect(url_for('auth.login'))

        login_user(this_user)
        flash('Login successful.', 'success')
        return redirect(url_for('user.dashboard'))

    return render_template('auth/login.html', title='Log in', form=login_form)


@auth.route('/logout/')
def logout():
    logout_user()
    flash('Log out successful.', 'info')
    return redirect(url_for('auth.login'))
