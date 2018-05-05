from app import db
from app.forms import NewsForm
from app.models import NewsItem, NewsItemAcknowledgement

from flask import Blueprint, flash, redirect, url_for, render_template, abort
from flask_login import current_user, login_required

news = Blueprint('news', __name__, url_prefix='/news/', template_folder='templates')


@news.route('/', methods=['GET', 'POST'])
@login_required
def index():
    news_form = NewsForm()

    if news_form.validate_on_submit():
        new_news = NewsItem(user_id=current_user.id, title=news_form.title.data, body=news_form.body.data)

        db.session.add(new_news)
        db.session.commit()

        flash('News item posted.', 'success')
        return redirect(url_for('news.index'))

    news_items = NewsItem.query.order_by(NewsItem.created_at).all()

    data = {
        'editing': False,
        'title': 'News',
        'form': news_form,
        'news_items': news_items
    }

    return render_template('news/index.html', **data)


@news.route('/<news_item_id>/edit/', methods=['GET', 'POST'])
@login_required
def edit(news_item_id):
    news_item = NewsItem.query.filter_by(id=news_item_id).scalar()

    if not news_item:
        abort(404)

    news_form = NewsForm(obj=news_item)

    if news_form.validate_on_submit():
        news_form.populate_obj(news_item)
        db.session.commit()

        flash('News item edited.', 'success')
        return redirect(url_for('news.index'))

    data = {
        'editing': True,
        'title': 'Edit News Item',
        'form': news_form,
    }

    return render_template('news/index.html', **data)


@news.route('/<news_item_id>/delete/')
@login_required
def delete(news_item_id):
    news_item = NewsItem.query.filter_by(id=news_item_id).scalar()

    if not news_item:
        abort(404)

    db.session.delete(news_item)
    db.session.commit()

    flash('News item deleted.', 'success')
    return redirect(url_for('news.index'))


@news.route('/<news_item_id>/acknowledge/')
@login_required
def acknowledge(news_item_id):
    news_item = NewsItem.query.filter_by(id=news_item_id).scalar()

    if not news_item:
        abort(404)

    if news_item.is_acknowledged(current_user.id):
        flash('News item already acknowledged.', 'danger')
        return redirect(url_for('news.index'))

    new_acknowledgement = NewsItemAcknowledgement(user_id=current_user.id, news_item_id=news_item_id)

    db.session.add(new_acknowledgement)
    db.session.commit()

    flash('News item acknowledged.', 'success')
    return redirect(url_for('news.index'))


@news.route('/<news_item_id>/acknowledgements/', methods=['GET', 'POST'])
@login_required
def acknowledgements(news_item_id):
    all_acknowledgements = NewsItemAcknowledgement.query.filter_by(news_item_id=news_item_id).order_by(NewsItemAcknowledgement.created_at).all()

    data = {
        'acknowledgements': all_acknowledgements,
        'title': 'News Item #' + news_item_id + ' Acknowledgments'
    }

    return render_template('news/acknowledgements.html', **data)
