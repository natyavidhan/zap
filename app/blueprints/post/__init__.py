from flask import Blueprint

bp = Blueprint('post', __name__, url_prefix="/post")

from app.blueprints.post import routes