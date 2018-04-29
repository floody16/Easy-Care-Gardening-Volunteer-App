from app import db
from app.forms import NewsForm
from app.models import NewsItem

from flask import Blueprint, flash, redirect, url_for, render_template
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

        flash('News item posted successfully.', 'success')
        return redirect(url_for('news.index'))

    news_items = NewsItem.query.order_by(NewsItem.created_at).all()

    data = {
        'title': 'News',
        'form': news_form,
        'news_items': news_items
    }

    return render_template('news/index.html', **data)
