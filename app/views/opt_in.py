from app import db
from app.models import Job, OptIn
from flask import Blueprint, flash, redirect, url_for, render_template
from flask_login import current_user, login_required

opt_in = Blueprint('opt_in', __name__, url_prefix='/opt-in/', template_folder='templates')


@opt_in.route('/')
@login_required
def index():
    return redirect(url_for('job.index'))


@opt_in.route('/<job_id>')
@login_required
def show(job_id):
    if not Job.query.filter_by(id=job_id).scalar():
        flash('Job does not exist.', 'danger')
        return redirect(url_for('job.index'))

    all_opt_ins = OptIn.query.filter_by(job_id=job_id).all()

    return render_template('job/opt_in.html', title='Job #' + job_id + ' opt-ins', opt_ins=all_opt_ins)


@opt_in.route('/toggle/<job_id>')
@login_required
def toggle(job_id):
    job = Job.query.filter_by(id=job_id).scalar()

    if not job:
        flash('Cannot opt-into/opt-out of a non-existent job.', 'danger')
        return redirect(url_for('user.roster'))

    if job.cancelled:
        flash('Cannot opt-into/opt-out of a cancelled job.', 'danger')
        return redirect(url_for('user.roster'))

    this_opt_in = OptIn.query.filter_by(job_id=job_id, user_id=current_user.id).scalar()

    # An opt-in for that job exists. Opt-out...
    if this_opt_in:
        db.session.delete(this_opt_in)
        db.session.commit()

        flash('Opted-out.', 'success')
        return redirect(url_for('user.roster'))

    # No opt-in yet. Opt-in...
    new_opt_in = OptIn(job_id=job_id, user_id=current_user.id)

    db.session.add(new_opt_in)
    db.session.commit()

    flash('Opted-in.', 'success')
    return redirect(url_for('user.roster'))
