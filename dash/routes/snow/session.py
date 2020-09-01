from sanic import Blueprint, response
from sanic.log import logger

session = Blueprint('session', url_prefix='/session')


@session.post('/')
async def snfgenerator(request):
    try:
        query_string = request.body.decode('UTF-8')
        post_data = parse_qs(query_string)
        res = post_data.get('pid')[0] + '.' + post_data.get('token')[0]
        return response.json({'hasError': False, 'error': '', 'data': res})
    except Exception as error:
        logger.warning(error)
        return response.json({'hasError': True, 'error': 'Internal Error', 'data': ''}, status=500)
