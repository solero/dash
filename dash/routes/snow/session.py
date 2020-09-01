from sanic import Blueprint, response
from sanic.log import logger

session = Blueprint('session', url_prefix='/session')


@session.post('/')
async def snfgenerator(request):
    try:
        res = request.form.get('pid') + '.' + request.form.get('token')
        return response.json({'hasError': False, 'error': '', 'data': res})
    except TypeError as error:
        logger.warning(error)
        return response.json({'hasError': True, 'error': 'Internal Error', 'data': ''}, status=500)
