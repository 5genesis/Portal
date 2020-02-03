from flask import Blueprint

bp = Blueprint('auth', __name__)

from app.dispatcher_auth import routes
