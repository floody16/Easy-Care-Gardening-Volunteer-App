from app import db
from app.forms import ChangePasswordForm, FeedbackForm, UserForm
from app.models import User, Job, Feedback
from app.utils import get_suitable_jobs

from flask import Blueprint, flash, redirect, url_for, render_template, abort
from flask_login import current_user, login_required
import datetime

user = Blueprint('user', __name__, template_folder='templates')


@user.route('/')
@user.route('/index/')
@user.route('/dashboard/')
@login_required
def dashboard():
    return render_template('user/dashboard.html', title='Dashboard')


@user.route('/profile/', methods=['GET', 'POST'])
@login_required
def profile():
    change_password_form = ChangePasswordForm()

    if change_password_form.validate_on_submit():
        this_user = User.query.filter_by(id=current_user.id).scalar()

        if not this_user.check_password(change_password_form.old_password.data):
            flash('Old password is incorrect.', 'danger')
            return redirect(url_for('user.profile'))

        this_user.set_password(change_password_form.new_password.data)
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


@user.route('/user/<int:user_id>/edit/', methods=['GET', 'POST'])
@login_required
def edit(user_id):
    this_user = User.query.filter_by(id=user_id).scalar()

    if not this_user:
        abort(404)

    user_form = UserForm(obj=this_user)

    if user_form.validate_on_submit():
        user_form.populate_obj(this_user)
        db.session.commit()

        flash('User edited.', 'success')
        return redirect(url_for('manage.index'))

    data = {
        'editing': True,
        'title': 'Edit User',
        'form': user_form
    }

    return render_template('user/edit.html', **data)
