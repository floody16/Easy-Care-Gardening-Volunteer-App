from app import db
from app.forms import JobForm, FeedbackForm
from app.models import Job, Feedback

from flask import Blueprint, flash, redirect, url_for, render_template
from flask_login import current_user, login_required
import datetime

job = Blueprint('job', __name__, url_prefix='/job/', template_folder='templates')


@job.route('/', methods=['GET', 'POST'])
@login_required
def index():
    job_form = JobForm()

    if job_form.validate_on_submit():
        if job_form.date.data < datetime.date.today():
            flash('Date cannot be in the past.', 'danger')
            return redirect(url_for('job.index'))

        if job_form.date.data.weekday() == 6:
            flash('Date cannot fall on a Sunday.', 'danger')
            return redirect(url_for('job.index'))

        new_job = Job(user_id=current_user.id,
                      address=job_form.address.data,
                      date=job_form.date.data,
                      time=job_form.time.data,
                      notes=job_form.notes.data)

        db.session.add(new_job)
        db.session.commit()

        flash('Job created successfully.', 'success')
        return redirect(url_for('job.index'))

    all_jobs = Job.query.filter(Job.date >= datetime.date.today()).order_by(Job.date).all()

    return render_template('job/index.html', title='Jobs', form=job_form, jobs=all_jobs)


@job.route('/cancel/<job_id>')
@login_required
def cancel(job_id):
    this_job = Job.query.filter_by(id=job_id).scalar()

    if not this_job:
        flash('Job does not exist.', 'danger')
        return redirect(url_for('job.index'))

    this_job.cancelled = not this_job.cancelled
    db.session.commit()

    if this_job.cancelled:
        flash('Job cancelled.', 'success')
    else:
        flash('Job un-cancelled.', 'success')

    return redirect(url_for('job.index'))


@job.route('/feedback/', methods=['GET', 'POST'])
@login_required
def feedback():
    feedback_form = FeedbackForm()

    if feedback_form.validate_on_submit():
        new_feedback = Feedback(user_id=current_user.id,
                                job_id=feedback_form.job.data,
                                body=feedback_form.body.data)

        db.session.add(new_feedback)
        db.session.commit()

        flash('Feedback submitted.', 'success')
        return redirect(url_for('job.feedback'))

    all_feedback = Feedback.query.all()

    return render_template('job/feedback.html', title='Feedback', form=feedback_form, all_feedback=all_feedback)
