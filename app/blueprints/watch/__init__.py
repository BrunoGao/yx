from flask import Blueprint
watch_bp = Blueprint('watch', __name__, url_prefix='/watch')
from . import routes 