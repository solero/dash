from sanic import Blueprint, HTTPResponse, response
from sanic.log import logger
from dash import app

swrequest = Blueprint('swrequest', url_prefix='/swrequest')

def world_response(
    token: str,
    world_name: str,
    host: str,
    port: int,
    owner: str = 'crowdcontrol',
    branch: str = 'CPNext_dev_branch'
) -> HTTPResponse:
    return response.text(
        f'[S_WORLDLIST]|{token}|{world_name}|{host}|{port}||{owner}|{world_name}|{branch}|example'
    )

def error_response(
    code: int,
    title: str,
    message: str
) -> HTTPResponse:
    return response.text(
        f'[S_ERROR]|{code}|{title}|{message}'
    )

@swrequest.get('/')
async def swhandler(request):
    try:
        product_name = request.args.get('product_name')
        world_name = request.args.get('name')

        if not product_name or not world_name:
            return error_response(3518, 'Cannot Start World', 'Missing parameters')

        if product_name != 'cjsnow' or not world_name.startswith('cjsnow'):
            return error_response(3514, 'Cannot Start World', 'World type not supported')

        token = request.args.get('token')
        pid = request.args.get('owner')

        if not pid or not token:
            return error_response(3518, 'Cannot Start World', 'Missing parameters')

        if not pid.isdigit():
            return error_response(3518, 'Cannot Start World', 'Invalid parameters')

        session_key = await app.ctx.redis.get(f'{pid}.mpsession')

        if not session_key:
            return error_response(4408, 'Cannot Start World', 'Token timeout')

        if session_key.decode() != token:
            return error_response(3525, 'Cannot Start World', 'Invalid token')

        return world_response(token, world_name, app.config.CJS_HOST, app.config.CJS_PORT)
    except Exception as error:
        logger.warning(error)
        return error_response(1, 'Cannot Start World', 'Internal Error')
