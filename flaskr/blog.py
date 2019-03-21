from flask import (
    Blueprint, g, request
)
from flask import jsonify
from playhouse.shortcuts import model_to_dict

from flaskr.auth import login_required
from flaskr.models import Post

bp = Blueprint('blog', __name__)


@bp.route('/posts/', methods=('GET',))
def posts():
    qs = Post.select()
    result = []
    for item in qs:
        result.append(model_to_dict(item, exclude=[Post.user.password]))
    return jsonify(result)


@bp.route('/posts/create', methods=('POST',))
@login_required
def create():
    data = request.json

    if not data.get('title'):
        return jsonify({'error': 'Title is required.'})

    data['user_id'] = g.user.id
    instance = Post.create(
        **data
    )
    return jsonify(model_to_dict(instance, exclude=[Post.user.password]))


def get_post(id):
    try:
        instance = Post.get(Post.id == id)
    except Post.DoesNotExist:
        return jsonify({'data': 'NotFound'}, status=404)

    return instance


@bp.route('/posts/<int:id>/', methods=('GET',))
def post(id):
    instance = get_post(id)
    return jsonify(model_to_dict(instance, exclude=[Post.user.password]))
