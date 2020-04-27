from urllib.parse import parse_qs, urlencode
from email.utils import parseaddr

from dash.data import db
from dash.data.penguin import Penguin, ActivationKey
from dash.data.item import PenguinItem
from dash.data.mail import PenguinPostcard

from sendgrid import SendGridAPIClient, Mail
from sanic import response
from sanic import Blueprint
from dash import env, app
from dash.crypto import Crypto

import aiohttp
import secrets
import re
import i18n
import bcrypt
import string


legacy_create = Blueprint('legacy_create', url_prefix='/create/legacy')
legacy_activate = Blueprint('legacy_activate', url_prefix='/activate/legacy')


@legacy_create.post('/')
async def register(request):
    query_string = request.body.decode('UTF-8')
    post_data = parse_qs(query_string)
    action = post_data.get('action')[0]
    if action == 'validate_agreement':
        return await validate_agreement(request, post_data)
    elif action == 'validate_username':
        return await validate_username(request, post_data)
    elif action == 'validate_password_email':
        return await validate_password_email(request, post_data)


@legacy_activate.get('/<activation_key>')
async def activate(_, activation_key):
    data = await ActivationKey.query.where(ActivationKey.activation_key == activation_key).gino.first()
    if data is not None:
        await Penguin.update.values(active=True) \
            .where(Penguin.id == data.penguin_id).gino.status()
        await ActivationKey.delete.where((ActivationKey.penguin_id == data.penguin_id)).gino.status()
        return response.redirect(app.config.ACTIVATE_REDIRECT)
    return response.json({'message': 'Not found'}, status=404)


async def validate_agreement(_, post_data):
    agree_terms = post_data.get('agree_to_terms')[0]
    agree_rules = post_data.get('agree_to_rules')[0]
    lang = post_data.get('lang', 'en')[0]
    if not int(agree_terms) or not int(agree_rules):
        return response.text(urlencode({
            'error': i18n.t('create.terms', locale=lang)
        }))
    return response.text(urlencode({'success': 1}))


async def validate_username(request, post_data):
    username = post_data.get('username', [None])[0]
    color = post_data.get('colour')[0]
    lang = post_data.get('lang')[0]

    if not username:
        return response.text(urlencode({
            'error': i18n.t('create.name_missing', locale=lang)
        }))
    elif len(username) < 4 or len(username) > 12:
        return response.text(urlencode({
            'error': i18n.t('create.name_short', locale=lang)
        }))
    elif len(re.sub('[^0-9]', '', username)) > 5:
        return response.text(urlencode({
            'error': i18n.t('create.name_number', locale=lang)
        }))
    elif re.search('[a-zA-Z]', username) is None:
        return response.text(urlencode({
            'error': i18n.t('create.name_letter', locale=lang)
        }))
    elif not username.isalnum():
        return response.text(urlencode({
            'error': i18n.t('create.name_not_allowed', locale=lang)
        }))
    elif not color.isdigit() or int(color) not in range(1, 16):
        return response.text(urlencode({'error': ''}))

    nickname = username.rstrip(string.digits)
    names = await db.select([Penguin.username]).where(Penguin.username.like(f'{nickname.lower()}%')).gino.all()
    names = {name for name, in names}

    if username.lower() in names:
        max_digits = min(5, 12 - len(nickname))
        username = next((f'{nickname}{i}' for i in range(1, int('9' * max_digits))
                         if f'{nickname.lower()}{i}' not in names), None)

        if username is None:
            return response.text(urlencode({
                'error': i18n.t('create.name_taken', locale=lang)
            }))

        return response.text(urlencode({
            'error': i18n.t('create.name_suggest', suggestion=username, locale=lang)
        }))

    request['session']['sid'] = secrets.token_urlsafe(16)
    request['session']['username'] = username
    request['session']['color'] = color

    return response.text(urlencode({'success': 1, 'sid': request['session']['sid']}))


async def validate_password_email(request, post_data):
    session_id = post_data.get('sid')[0]
    session = request['session']
    username = session.get('username', None)
    color = session.get('color', None)
    password = post_data.get('password')[0]
    password_confirm = post_data.get('password_confirm')[0]
    email = post_data.get('email')[0]
    lang = post_data.get('lang')[0]

    if session_id != session['sid']:
        return response.text(urlencode({
            'error': i18n.t('create.passwords_match', locale=lang)
        }))

    if app.config.GSECRET_KEY:
        gclient_response = post_data.get('gtoken', [None])[0]
        async with aiohttp.ClientSession() as session:
            async with session.post(app.config.GCAPTCHA_URL, data=dict(
                secret=app.config.GSECRET_KEY,
                response=gclient_response,
                remoteip=request.ip
            )) as resp:
                gresult = await resp.json()
                if not gresult['success']:
                    return response.text(urlencode({
                        'error': gresult
                    }))

    if username is None or color is None:
        return response.text(urlencode({'error': ''}))
    elif str(password) != str(password_confirm):
        return response.text(urlencode({
            'error': i18n.t('create.passwords_match', locale=lang)
        }))
    elif len(password) < 4:
        return response.text(urlencode({
            'error': i18n.t('create.password_short', locale=lang)
        }))

    _, email = parseaddr(email)
    domain = email.rsplit('@', 1)[-1]
    if not email or '@' not in email:
        return response.text(urlencode({
            'error': i18n.t('create.email_invalid', locale=lang)
        }))
    elif app.config.EMAIL_WHITELIST and domain not in app.config.EMAIL_WHITELIST:
        return response.text(urlencode({
            'error': i18n.t('create.email_invalid', locale=lang)
        }))

    email_count = await db.select([db.func.count(Penguin.email)]).where(
        db.func.lower(Penguin.email) == email.lower()).gino.scalar()
    if email_count >= app.config.MAX_ACCOUNT_EMAIL:
        return response.text(urlencode({
            'error': i18n.t('create.email_invalid', locale=lang)
        }))

    password = Crypto.hash(password).upper()
    password = Crypto.get_login_hash(password, rndk=app.config.STATIC_KEY)
    password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(12)).decode('utf-8')

    if app.config.USERNAME_FORCE_CASE:
        username = username.title()

    penguin = await Penguin.create(username=username.lower(), nickname=username, password=password, email=email,
                                   color=int(color),
                                   approval_en=app.config.APPROVE_USERNAME,
                                   approval_pt=app.config.APPROVE_USERNAME,
                                   approval_fr=app.config.APPROVE_USERNAME,
                                   approval_es=app.config.APPROVE_USERNAME,
                                   approval_de=app.config.APPROVE_USERNAME,
                                   approval_ru=app.config.APPROVE_USERNAME,
                                   active=app.config.ACTIVATE_PLAYER)

    await PenguinItem.create(penguin_id=penguin.id, item_id=int(color))
    await PenguinPostcard.create(penguin_id=penguin.id, sender_id=None, postcard_id=125)

    if not app.config.ACTIVATE_PLAYER:
        activation_key = secrets.token_urlsafe(45)

        mail_template = env.get_template('en_legacy_activation.html')
        message = Mail(
            from_email=app.config.FROM_EMAIL, to_emails=email,
            subject=i18n.t('create.activate_mail_subject', locale=lang),
            html_content=mail_template.render(
                penguin=penguin, site_name=app.config.SITE_NAME,
                activate_link=app.config.LEGACY_ACTIVATE_LINK + activation_key
            )
        )
        sg = SendGridAPIClient(app.config.SENDGRID_API_KEY)
        sg.send(message)
        await ActivationKey.create(penguin_id=penguin.id, activation_key=activation_key)

    return response.text(urlencode({'success': 1}))
