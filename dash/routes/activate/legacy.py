from sanic import Blueprint, response

from dash import app
from dash.data.penguin import ActivationKey, Penguin

legacy_activate = Blueprint('legacy_activate', url_prefix='/activate/legacy')


@legacy_activate.get('/<activation_key>')
async def activate(_, activation_key):
    data = await ActivationKey.query.where(ActivationKey.activation_key == activation_key).gino.first()
    if data is not None:
        await Penguin.update.values(active=True) \
            .where(Penguin.id == data.penguin_id).gino.status()
        await ActivationKey.delete.where((ActivationKey.penguin_id == data.penguin_id)).gino.status()
        return response.redirect(app.config.LEGACY_ACTIVATE_REDIRECT)
    return response.json({'message': 'Not found'}, status=404)
