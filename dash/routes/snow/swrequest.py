from urllib.parse import parse_qs, urlencode

from sanic import response
from sanic import Blueprint
from sanic.log import logger

from dash import settings 

swrequest = Blueprint('swrequest', url_prefix='/swrequest')


@swrequest.get('/')
async def swhandler(request):
    try:
        token = request.args.get('token')
        name = request.args.get('name')
        res = f'[S_WORLDLIST]|{token}|{name}|{settings.CJS_HOST}|{settings.CJS_PORT}||crowdcontrol|cjsnow_0|CPNext_dev_branch|example'
        return response.text(res)
    except Exception as error:
        logger.warning(error)
        return response.json({'hasError': True, 'error': 'Internal Error', 'data': error}, status=500)
