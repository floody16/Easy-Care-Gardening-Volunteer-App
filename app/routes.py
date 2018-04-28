from app import app, db
from app.utils import get_suitable_jobs, day_pref_to_binary
from app.forms import RegistrationForm, LoginForm, NewsForm, JobForm
from app.models import User, NewsItem, NewsItemAcknowledgement, Job, OptIn

from flask import render_template, redirect, url_for, flash
from flask_login import current_user, login_user, login_required, logout_user
import datetime


@app.route('/')
@app.route('/index/')
def index():
    return redirect(url_for('login'))


@app.route('/register/', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        flash('You are already logged in.', 'info')
        return redirect(url_for('dashboard'))

    registration_form = RegistrationForm()

    if registration_form.validate_on_submit():
        user = User(email=registration_form.email.data,
                    full_name=registration_form.full_name.data,
                    user_type=registration_form.user_type.data,
                    join_date=registration_form.join_date.data,
                    next_police_check=registration_form.next_police_check.data,
                    time_pref=registration_form.time_pref.data,
                    day_pref=day_pref_to_binary(registration_form.day_pref.data))
        user.set_password(registration_form.password.data)

        db.session.add(user)
        db.session.commit()

        login_user(user)
        flash('Registration successful.', 'success')
        return redirect(url_for('dashboard'))

    return render_template('register.html', title='Register', form=registration_form)


@app.route('/login/', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        flash('You are already logged in.', 'info')
        return redirect(url_for('dashboard'))

    login_form = LoginForm()

    if login_form.validate_on_submit():
        user = User.query.filter_by(email=login_form.email.data).scalar()

        if user is None or not user.check_password(login_form.password.data):
            flash('Invalid credentials.', 'danger')
            return redirect(url_for('login'))

        login_user(user)
        flash('Login successful.', 'success')
        return redirect(url_for('dashboard'))

    return render_template('login.html', title='Log in', form=login_form)


@app.route('/logout/')
def logout():
    logout_user()
    flash('Log out successful.', 'info')
    return redirect(url_for('login'))


@app.route('/dashboard/')
@login_required
def dashboard():
    return render_template('dashboard.html', title='Dashboard')


@app.route('/news/', methods=['GET', 'POST'])
@login_required
def news():
    news_form = NewsForm()

    if news_form.validate_on_submit():
        new_news = NewsItem(user_id=current_user.id, title=news_form.title.data, body=news_form.body.data)

        db.session.add(new_news)
        db.session.commit()

        flash('News item posted successfully.', 'success')
        return redirect(url_for('news'))

    news_items = NewsItem.query.order_by(NewsItem.created_at).all()

    data = {
        'title': 'News',
        'form': news_form,
        'news_items': news_items
    }

    return render_template('news.html', **data)


@app.route('/acknowledgements/')
@login_required
def acknowledgments():
    return redirect(url_for('news'))


@app.route('/acknowledgements/<news_item_id>')
@login_required
def acknowledgment_show(news_item_id):
    acknowledgements = NewsItemAcknowledgement.query.filter_by(news_item_id=news_item_id).order_by(NewsItemAcknowledgement.created_at).all()

    data = {
        'acknowledgements': acknowledgements,
        'title': 'News item #' + news_item_id + ' acknowledgments'
    }

    return render_template('acknowledgements.html', **data)


@app.route('/acknowledgements/new/<news_item_id>')
@login_required
def acknowledgement_new(news_item_id=None):
    news_item = NewsItem.query.filter_by(id=news_item_id).scalar()

    if not news_item:
        flash('News item does not exist.', 'danger')
        return redirect(url_for('news'))

    if news_item.is_acknowledged(current_user.id):
        flash('News item already acknowledged.', 'danger')
        return redirect(url_for('news'))

    new_acknowledgement = NewsItemAcknowledgement(user_id=current_user.id, news_item_id=news_item_id)

    db.session.add(new_acknowledgement)
    db.session.commit()

    flash('News item acknowledged.', 'success')
    return redirect(url_for('news'))


@app.route('/roster/')
@login_required
def roster():
    jobs = Job.query.filter(Job.date >= datetime.date.today()).order_by(Job.date).all()
    suitable_jobs = get_suitable_jobs(jobs, current_user.time_pref, current_user.day_pref)

    data = {
        'title': 'Roster',
        'jobs': suitable_jobs
    }

    return render_template('roster.html', **data)


@app.route('/jobs/', methods=['GET', 'POST'])
@login_required
def jobs():
    job_form = JobForm()

    if job_form.validate_on_submit():
        if job_form.date.data < datetime.date.today():
            flash('Date cannot be in the past.', 'danger')
            return redirect(url_for('jobs'))

        if job_form.date.data.weekday() == 6:
            flash('Date cannot fall on a Sunday.', 'danger')
            return redirect(url_for('jobs'))

        job = Job(user_id=current_user.id,
                  address=job_form.address.data,
                  date=job_form.date.data,
                  time=job_form.time.data,
                  notes=job_form.notes.data)

        db.session.add(job)
        db.session.commit()

        flash('Job created successfully.', 'success')
        return redirect(url_for('jobs'))

    jobs = Job.query.order_by(Job.date).all()

    return render_template('jobs.html', title='Jobs', form=job_form, jobs=jobs)


@app.route('/jobs/cancel/<job_id>')
@login_required
def job_cancel(job_id):
    job = Job.query.filter_by(id=job_id).scalar()

    if not job:
        flash('Job does not exist.', 'danger')
        return redirect(url_for('jobs'))

    job.cancelled = not job.cancelled
    db.session.commit()

    if job.cancelled:
        flash('Job cancelled.', 'success')
    else:
        flash('Job un-cancelled.', 'success')

    return redirect(url_for('jobs'))


@app.route('/opt-ins/')
@login_required
def opt_ins():
    return redirect(url_for('jobs'))


@app.route('/opt-ins/<job_id>')
@login_required
def opt_ins_show(job_id):
    if not Job.query.filter_by(id=job_id).scalar():
        flash('Job does not exist.', 'danger')
        return redirect(url_for('jobs'))

    opt_ins = OptIn.query.filter_by(job_id=job_id).all()

    return render_template('opt-ins.html', title='Job #' + job_id + ' opt-ins', opt_ins=opt_ins)


@app.route('/opt-ins/toggle/<job_id>')
@login_required
def opt_ins_toggle(job_id):
    job = Job.query.filter_by(id=job_id).scalar()

    if not job:
        flash('Cannot opt-into/opt-out of a non-existent job.', 'danger')
        return redirect(url_for('roster'))

    if job.cancelled:
        flash('Cannot opt-into/opt-out of a cancelled job.', 'danger')
        return redirect(url_for('roster'))

    opt_in = OptIn.query.filter_by(job_id=job_id, user_id=current_user.id).scalar()

    # An opt-in for that job exists. Opt-out...
    if opt_in:
        db.session.delete(opt_in)
        db.session.commit()

        flash('Opted-out.', 'success')
        return redirect(url_for('roster'))

    # No opt-in yet. Opt-in...
    new_opt_in = OptIn(job_id=job_id, user_id=current_user.id)

    db.session.add(new_opt_in)
    db.session.commit()

    flash('Opted-in.', 'success')
    return redirect(url_for('roster'))
