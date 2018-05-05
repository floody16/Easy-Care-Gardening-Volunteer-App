from app import db
from app.forms import JobForm
from app.models import Job, OptIn

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

    data = {
        'title': 'Jobs',
        'form': job_form,
        'upcoming_jobs': Job.query.filter(Job.date >= datetime.date.today()).order_by(Job.date).all(),
        'past_jobs': Job.query.filter(Job.date < datetime.date.today()).order_by(Job.date).all()
    }

    return render_template('job/index.html', **data)


@job.route('/<job_id>/cancel/')
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


@job.route('/<job_id>/feedback/')
@login_required
def feedback(job_id):
    this_job = Job.query.filter_by(id=job_id).scalar()

    if not this_job:
        flash('No feedback for that address.', 'danger')
        return redirect(url_for('job.index'))

    all_feedback = this_job.get_feedback(job_id)

    return render_template('job/feedback.html', title='Feedback For Address', job=this_job, all_feedback=all_feedback)


@job.route('/<job_id>/opt-in/')
@login_required
def opt_in(job_id):
    this_job = Job.query.filter_by(id=job_id).scalar()

    if not this_job:
        flash('Cannot opt-into/opt-out of a non-existent job.', 'danger')
        return redirect(url_for('user.roster'))

    if this_job.cancelled:
        flash('Cannot opt-into/opt-out of a cancelled job.', 'danger')
        return redirect(url_for('user.roster'))

    this_opt_in = OptIn.query.filter_by(job_id=job_id, user_id=current_user.id).scalar()

    if this_opt_in:
        db.session.delete(this_opt_in)
        db.session.commit()

        flash('Opted-out.', 'success')
        return redirect(url_for('user.roster'))

    new_opt_in = OptIn(job_id=job_id, user_id=current_user.id)

    db.session.add(new_opt_in)
    db.session.commit()

    flash('Opted-in.', 'success')
    return redirect(url_for('user.roster'))


@job.route('/<job_id>/opt-ins/')
@login_required
def opt_ins(job_id):
    if not Job.query.filter_by(id=job_id).scalar():
        flash('Job does not exist.', 'danger')
        return redirect(url_for('job.index'))

    all_opt_ins = OptIn.query.filter_by(job_id=job_id).all()

    return render_template('job/opt_ins.html', title='Job #' + job_id + ' Opt-ins', opt_ins=all_opt_ins)
