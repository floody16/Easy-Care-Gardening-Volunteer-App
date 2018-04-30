from app import db
from app.models import NewsItem, NewsItemAcknowledgement

from flask import Blueprint, flash, redirect, url_for, render_template
from flask_login import current_user, login_required

acknowledgement = Blueprint('acknowledgement', __name__, url_prefix='/acknowledgement/', template_folder='templates')


@acknowledgement.route('/')
@login_required
def index():
    return redirect(url_for('news.index'))


@acknowledgement.route('/<news_item_id>')
@login_required
def show(news_item_id):
    acknowledgements = NewsItemAcknowledgement.query.filter_by(news_item_id=news_item_id).order_by(NewsItemAcknowledgement.created_at).all()

    data = {
        'acknowledgements': acknowledgements,
        'title': 'News Item #' + news_item_id + ' Acknowledgments'
    }

    return render_template('news/acknowledgements.html', **data)


@acknowledgement.route('/new/<news_item_id>')
@login_required
def new(news_item_id=None):
    news_item = NewsItem.query.filter_by(id=news_item_id).scalar()

    if not news_item:
        flash('News item does not exist.', 'danger')
        return redirect(url_for('news'))

    if news_item.is_acknowledged(current_user.id):
        flash('News item already acknowledged.', 'danger')
        return redirect(url_for('news.index'))

    new_acknowledgement = NewsItemAcknowledgement(user_id=current_user.id, news_item_id=news_item_id)

    db.session.add(new_acknowledgement)
    db.session.commit()

    flash('News item acknowledged.', 'success')
    return redirect(url_for('news.index'))
