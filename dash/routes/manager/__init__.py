from sanic import Blueprint, response
from dash.routes.manager.login import login, logout, login_auth
from dash.routes.manager.panel import panel
from dash.routes.manager.moderation import moderation

import os
main = Blueprint('main', url_prefix='/')
static = Blueprint('static', url_prefix='/static')
static.static('/', os.path.join(os.path.dirname(os.path.abspath(__file__)), './static'))

manager = Blueprint.group(
    main,
    login,
    logout,
    panel,
    moderation,
    static,
    url_prefix='/manager'
)


@main.get('/')
@login_auth()
async def main_page(_):
    return response.redirect('/panel')






