import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from flask import jsonify
from werkzeug.security import generate_password_hash

from flaskr.db import get_db
from flaskr.models import User

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.json.get('username')
        password = request.json.get('password')
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        elif User.select().where(User.username == username).exists():
            error = 'Username exists in database'

        if error is None:
            instance = User.create(
                username=username,
                password=generate_password_hash(password)
            )
            return redirect(url_for('auth.login'))
        else:
            return jsonify({'error': error})

    return redirect(url_for('index'))


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.json.get('username')
        password = request.json.get('password')
        user = User.select().where(User.username == username)
        if not user.exists() or not user[0].check_password(password):
            return jsonify({'error': 'Authentication failed'})

        user = user[0]

        session.clear()
        session['user_id'] = user.id
    return redirect(url_for('index'))


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        get_db()
        try:
            g.user = User.get(User.id == user_id)
        except User.DoesNotExist:
            g.user = None


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view
