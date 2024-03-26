from sanic import Blueprint, Request, response
from sanic.log import logger

from dash.data.penguin import Penguin
from dash import app

import secrets

session = Blueprint('session', url_prefix='/session')

@session.post('/')
async def snfgenerator(request: Request):
    try:
        pid = request.form.get('pid')
        token = request.form.get('token')

        if not pid or not token:
            return response.json(
                {'hasError': True, 'error': 'Missing parameters', 'data': ''},
                status=400
            )

        if not pid.isdigit():
            return response.json(
                {'hasError': True, 'error': 'Invalid parameters', 'data': ''},
                status=400
            )

        username = await Penguin.select('username').where(Penguin.id == int(pid)).gino.first()

        if not username:
            return response.json(
                {'hasError': True, 'error': 'User not found', 'data': ''},
                status=401
            )

        login_key = await app.ctx.redis.get(f'{username[0]}.loginkey') or b''

        if login_key.decode() != token:
            return response.json(
                {'hasError': True, 'error': 'Invalid token', 'data': ''},
                status=401
            )

        session_token = secrets.token_hex(16)

        await app.ctx.redis.setex(
            f'{pid}.mpsession', 60,
            session_token
        )

        return response.json(
            {'hasError': False, 'error': '', 'data': session_token}
        )
    except TypeError as error:
        logger.warning(error)
        return response.json(
            {'hasError': True, 'error': 'Internal Error', 'data': ''},
            status=500
        )
