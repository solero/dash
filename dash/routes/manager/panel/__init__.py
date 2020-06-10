from dash import env, app
from sqlalchemy import func
from sanic import Blueprint, response
from dash.data.penguin import Penguin
from functools import wraps


panel = Blueprint('panel', url_prefix='/')


def login_auth():
    def decorator(f):
        @wraps(f)
        async def decorated_function(request, *args, **kwargs):
            if 'username' in request['session']:
                route = await f(request, *args, **kwargs)
                return route
            return response.redirect('/login')
        return decorated_function
    return decorator


@panel.get('/')
@login_auth()
async def panel_page(request):
    data = await Penguin.query.where(func.lower(Penguin.username) == request['session']['username']).gino.first()
    template = env.get_template('manager/panel.html')
    page = template.render(
        penguin=data,
        play_link=app.config.VANILLA_PLAY_LINK
    )
    return response.html(page)
