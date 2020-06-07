from sanic import Blueprint

manager = Blueprint('manager', url_prefix='/manager')


@manager.get('/')
async def manager_page(_):
