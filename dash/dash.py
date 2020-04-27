from dash.data.penguin import db

from dash import app, settings
from dash.routes.avatar import avatar
from dash.routes.autocomplete import autocomplete
from dash.routes.create.legacy import legacy_create, legacy_activate
from dash.routes.create.vanilla import vanilla_create, vanilla_activate
from dash.routes.session import session
from dash.routes.swrequest import swrequest

import i18n
import os


@app.listener('before_server_start')
async def connect_to_db(sanic, loop):
    await db.set_bind(f'postgresql://'
                      f'{app.config.POSTGRES_USER}:'
                      f'{app.config.POSTGRES_PASSWORD}@'
                      f'{app.config.POSTGRES_HOST}/'
                      f'{app.config.POSTGRES_NAME}')


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

    app.run(host=app.config.ADDRESS, port=app.config.PORT)
