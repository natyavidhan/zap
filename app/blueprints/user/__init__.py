from flask import Blueprint

bp = Blueprint('user', __name__, url_prefix="/user")

from app.blueprints.user import routes