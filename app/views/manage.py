from app import address
from app.forms import FindUserForm
from app.models import User, Invite

from flask import Blueprint, flash, redirect, url_for, render_template
from flask_login import login_required

manage = Blueprint('manage', __name__, url_prefix='/manage/', template_folder='templates')


@manage.route('/', methods=['GET', 'POST'])
@login_required
def index():
    find_user_form = FindUserForm()

    if find_user_form.validate_on_submit():
        this_user = User.query.filter_by(email=find_user_form.email.data).scalar()

        if not this_user:
            flash('That user does not exist. You can create one with that email by clicking \'New Invite\' below, however.', 'warning')
            return redirect(url_for('manage.index'))

        return redirect(url_for('user.edit', user_id=this_user.id))

    invites = Invite.query.all()

    data = {
        'title': 'Manage',
        'form': find_user_form,
        'invites': invites,
        'address': address
    }

    return render_template('manage.html', **data)
