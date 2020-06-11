from sanic import Blueprint, response
from dash.routes.manager.login import login, logout, login_auth
from dash.routes.manager.panel import panel

import os
main = Blueprint('main', url_prefix='/')
static = Blueprint('static', url_prefix='/static')
static.static('/', os.path.join(os.path.dirname(os.path.abspath(__file__)), './static'))

manager = Blueprint.group(
    main,
    panel,
    logout,
    login,
    static,
    url_prefix='/manager'
)

# make crypto back to what it originally was and use that method (check vanilla.py)
# web sockets


@main.get('/')
@login_auth()
async def main_page(_):
    return response.redirect('/panel')






