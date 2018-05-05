from app import address, db
from app.forms import UserForm
from app.models import User, Invite
from app.utils import day_pref_to_binary, generate_invite_key

from flask import Blueprint, flash, redirect, url_for, render_template, abort
from flask_login import login_required

invite = Blueprint('invite', __name__, url_prefix='/invite/', template_folder='templates')


@invite.route('/', methods=['GET', 'POST'])
# @login_required
def index():
    user_form = UserForm()

    if user_form.validate_on_submit():
        partial_user = User(email=user_form.email.data,
                            full_name=user_form.full_name.data,
                            user_type=user_form.user_type.data,
                            join_date=user_form.join_date.data,
                            next_police_check=user_form.next_police_check.data,
                            time_pref=user_form.time_pref.data,
                            day_pref=day_pref_to_binary(user_form.day_prefs.data))

        db.session.add(partial_user)
        db.session.commit()

        key = generate_invite_key()
        new_invite = Invite(user_id=partial_user.id, key=key)

        db.session.add(new_invite)
        db.session.commit()

        flash('Invitation created. The user can register at: ' + address + '/register/' + key, 'success')
        return redirect(url_for('invite.index'))

    data = {
        'editing': False,
        'title': 'Invite User',
        'form': user_form
    }

    return render_template('user/invite.html', **data)


@invite.route('/<int:invite_id>/reissue/', methods=['GET', 'POST'])
@login_required
def reissue(invite_id):
    this_invite = Invite.query.filter_by(id=invite_id).scalar()

    if not this_invite:
        abort(404)

    new_key = generate_invite_key()
    this_invite.key = new_key

    db.session.commit()

    flash('Invite key reissued. The user must now register at: ' + address + '/register/' + new_key, 'success')
    return redirect(url_for('manage.index'))
