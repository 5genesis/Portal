from flask import Blueprint

bp = Blueprint('eastWest', __name__)

from app.east_west import routes
