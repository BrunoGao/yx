from flask import Blueprint

bigscreen_bp = Blueprint('bigscreen', __name__, url_prefix='/bigscreen')

from . import routes 