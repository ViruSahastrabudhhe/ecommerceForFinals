from main import app
from itsdangerous.url_safe import URLSafeTimedSerializer as Serializer
from flask import Blueprint

models_bp = Blueprint("models", __name__, static_folder='static', template_folder='templates')

