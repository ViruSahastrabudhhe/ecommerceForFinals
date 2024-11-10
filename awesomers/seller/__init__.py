from flask import Blueprint

seller=Blueprint('seller', __name__)

from . import routes