from flask import Blueprint

bp = Blueprint('NetworkServices', __name__)

from app.network_services import routes
