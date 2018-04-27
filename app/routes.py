from app import app, db
from app.forms import RegistrationForm, LoginForm, NewsForm, JobForm
from app.models import User, NewsItem, NewsItemAck, Job

from flask import render_template, redirect, url_for, flash, request
from flask_login import current_user, login_user, login_required, logout_user


@app.route('/')
@app.route('/index')
def index():
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        flash('You are already logged in!', 'info')
        return redirect(url_for('dashboard'))

    register = RegistrationForm()

    if register.validate_on_submit():
        user = User(email=register.email.data,
                    full_name=register.full_name.data,
                    user_type=register.user_type.data,
                    join_date=register.join_date.data)
        user.set_password(register.password.data)

        db.session.add(user)
        db.session.commit()

        login_user(user)
        flash('You are now registered. Welcome!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('register.html', title='Register', form=register)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        flash('You are already logged in!', 'info')
        return redirect(url_for('dashboard'))

    login = LoginForm()

    if login.validate_on_submit():
        user = User.query.filter_by(email=login.email.data).first()

        if user is None or not user.check_password(login.password.data):
            flash('Invalid credentials. Please try again', 'danger')
            return redirect(url_for('login'))

        login_user(user)
        flash('Login successful.', 'success')
        return redirect(url_for('dashboard'))

    return render_template('login.html', title='Log in', form=login)


@app.route('/logout')
def logout():
    logout_user()
    flash('You were logged out. Goodbye.', 'info')
    return redirect(url_for('login'))


@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', title='Dashboard')


@app.route('/news', methods=['GET', 'POST'])
@login_required
def news():
    form = NewsForm()

    if form.validate_on_submit():
        news = NewsItem(user_id=current_user.id, title=form.title.data, body=form.body.data)

        db.session.add(news)
        db.session.commit()

        flash('News item posted!', 'success')
        return redirect(url_for('news'))

    newsitems = NewsItem.query.all()

    return render_template('news.html', title='News', form=form, newsitems=newsitems)


@app.route('/news/<newsitem_id>')
@login_required
def newsitem(newsitem_id):
    newsitem = NewsItem.query.filter_by(id=newsitem_id).first()
    acks = NewsItemAck.query.filter_by(newsitem_id=newsitem_id).all()

    return render_template('newsitem.html', title=newsitem.title, newsitem=newsitem, acks=acks)


@app.route('/ack/<newsitem_id>', methods=['GET', 'POST'])
@login_required
def ack(newsitem_id):
    if not NewsItem.query.filter_by(id=newsitem_id).first():
        flash('Cannot acknowledge a non-existent news item!', 'danger')
        return redirect(url_for('news'))

    if NewsItemAck.query.filter_by(newsitem_id=newsitem_id, user_id=current_user.id).first():
        flash('You have already acknowledged that news item!', 'danger')
        return redirect(url_for('news'))

    ack = NewsItemAck(user_id=current_user.id, newsitem_id=newsitem_id)

    db.session.add(ack)
    db.session.commit()

    flash('News item acknowledged!', 'success')
    return redirect(url_for('news'))


@app.route('/roster')
@login_required
def roster():
    return render_template('roster.html', title='Roster')


@app.route('/jobs', methods=['GET', 'POST'])
@login_required
def jobs():
    form = JobForm()

    if form.validate_on_submit():
        job = Job(address=form.address.data, date=form.date.data, time=form.time.data, notes=form.notes.data)

        db.session.add(job)
        db.session.commit()

        flash('Job created successfully!', 'success')
        return redirect(url_for('jobs'))

    jobs = Job.query.all()

    return render_template('jobs.html', title='Jobs', form=form, jobs=jobs)
