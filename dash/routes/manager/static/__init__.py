from sanic import Blueprint
import os
static = Blueprint('static', url_prefix='/static')
static.static('/', os.path.join(os.path.dirname(os.path.abspath(__file__)), '.'))

