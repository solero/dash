import aiohttp
import i18n
from sanic import Blueprint, response

from dash import app, env
from dash.data.penguin import ActivationKey, Penguin

vanilla_activate = Blueprint('vanilla_activate', url_prefix='/activate/vanilla')


@vanilla_activate.get('/<lang>/<code>')
async def activate_page_autofill(_, lang, code):
    if lang == 'fr':
        register_template = env.get_template('activate/fr.html')
        page = register_template.render(
            VANILLA_PLAY_LINK=app.config.VANILLA_PLAY_LINK,
            site_key=app.config.GSITE_KEY,
            activation_key=code
        )
        return response.html(page)
    elif lang == 'es':
        register_template = env.get_template('activate/es.html')
        page = register_template.render(
            VANILLA_PLAY_LINK=app.config.VANILLA_PLAY_LINK,
            site_key=app.config.GSITE_KEY,
            activation_key=code
        )
        return response.html(page)
    elif lang == 'pt':
        register_template = env.get_template('activate/pt.html')
        page = register_template.render(
            VANILLA_PLAY_LINK=app.config.VANILLA_PLAY_LINK,
            site_key=app.config.GSITE_KEY,
            activation_key=code
        )
        return response.html(page)
    register_template = env.get_template('activate/en.html')
    page = register_template.render(
        VANILLA_PLAY_LINK=app.config.VANILLA_PLAY_LINK,
        site_key=app.config.GSITE_KEY,
        activation_key=code
    )
    return response.html(page)


@vanilla_activate.get('/<lang>')
async def activate_page(_, lang):
    if lang == 'fr':
        register_template = env.get_template('activate/fr.html')
        page = register_template.render(
            VANILLA_PLAY_LINK=app.config.VANILLA_PLAY_LINK,
            site_key=app.config.GSITE_KEY
        )
        return response.html(page)
    elif lang == 'es':
        register_template = env.get_template('activate/es.html')
        page = register_template.render(
            VANILLA_PLAY_LINK=app.config.VANILLA_PLAY_LINK,
            site_key=app.config.GSITE_KEY
        )
        return response.html(page)
    elif lang == 'pt':
        register_template = env.get_template('activate/pt.html')
        page = register_template.render(
            VANILLA_PLAY_LINK=app.config.VANILLA_PLAY_LINK,
            site_key=app.config.GSITE_KEY
        )
        return response.html(page)
    register_template = env.get_template('activate/en.html')
    page = register_template.render(
        VANILLA_PLAY_LINK=app.config.VANILLA_PLAY_LINK,
        site_key=app.config.GSITE_KEY
    )
    return response.html(page)


@vanilla_activate.post('/<lang>')
async def activate_page(request, lang):
    query_string = request.body.decode('UTF-8')
    post_data = parse_qs(query_string)
    username = post_data.get('name', [None])[0]
    activation_code = post_data.get('activationcode', [None])[0]
    data = await Penguin.query.where(Penguin.username == username.lower()).gino.first()
    activation_data = await ActivationKey.query.where(
        ActivationKey.activation_key == activation_code
    ).gino.first()
    if app.config.GSECRET_KEY:
        gclient_response = post_data.get('recaptcha_response', [None])[0]
        async with aiohttp.ClientSession() as session:
            async with session.post(app.config.GCAPTCHA_URL, data=dict(
                secret=app.config.GSECRET_KEY,
                response=gclient_response,
                remoteip=request.ip
            )) as resp:
                gresult = await resp.json()
                if not gresult['success']:
                    return response.text('Your captcha score was low, please try again.')
    if not username or not activation_code:
        return response.json({'message': i18n.t('activate.error', locale=lang)}, status=404)
    elif not activation_data:
        return response.json({'message': i18n.t('activate.activation_key_404', locale=lang)}, status=404)
    elif not data:
        return response.json({'message': i18n.t('activate.username_404', locale=lang)}, status=404)
    elif data.id != activation_data.penguin_id:
        return response.json({'message': i18n.t('activate.incorrect_username', locale=lang)}, status=404)
    await Penguin.update.values(active=True).where(
        Penguin.id == activation_data.penguin_id
    ).gino.status()
    await ActivationKey.delete.where((ActivationKey.penguin_id == activation_data.penguin_id)).gino.status()
    return response.redirect(app.config.VANILLA_ACTIVATE_REDIRECT)
