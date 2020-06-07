from dash.data.penguin import db

from dash import app, settings
from dash.routes.avatar import avatar
from dash.routes.autocomplete import autocomplete
from dash.routes.create.legacy import legacy_create
from dash.routes.create.vanilla import vanilla_create
from dash.routes.activate.legacy import legacy_activate
from dash.routes.activate.vanilla import vanilla_activate
from dash.routes.password import password
from dash.routes.snow.session import session
from dash.routes.snow.swrequest import swrequest
from dash.routes.manager import manager

import i18n
import os
import aioredis


@app.listener('before_server_start')
async def start_services(sanic, loop):
    await db.set_bind(f'postgresql://'
                      f'{app.config.POSTGRES_USER}:'
                      f'{app.config.POSTGRES_PASSWORD}@'
                      f'{app.config.POSTGRES_HOST}/'
                      f'{app.config.POSTGRES_NAME}')

    app.redis = await aioredis.create_redis_pool(
        f'redis://{app.config.REDIS_ADDRESS}:{app.config.REDIS_PORT}',
        minsize=5, 
        maxsize=10
    )

def main(args):
    i18n.load_path.append(os.path.abspath('locale'))   
    if args.config:
        app.config.from_pyfile(args.config)
    else:
        app.config.from_object(settings)

    app.blueprint(avatar)
    app.blueprint(autocomplete)
    app.blueprint(legacy_create)
    app.blueprint(vanilla_create)
    app.blueprint(legacy_activate)
    app.blueprint(vanilla_activate)
    app.blueprint(session)
    app.blueprint(swrequest)
    app.blueprint(password)
    app.blueprint(manager)

    app.run(host=app.config.ADDRESS, port=app.config.PORT)
