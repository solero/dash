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
from stegano import lsb
from io import BytesIO
from PIL import Image

import aiohttp
import secrets
import re
import i18n
import bcrypt
import string
import random
import base64

vanilla_create = Blueprint('vanilla_create', url_prefix='/create/vanilla')
vanilla_activate = Blueprint('vanilla_activate', url_prefix='/activate/vanilla')

all_captchas = [
    ('balloon', Image.open('./dash/templates/images/balloon.png')),
    ('cheese', Image.open('./dash/templates/images/cheese.png')),
    ('igloo', Image.open('./dash/templates/images/igloo.png')),
    ('pizza', Image.open('./dash/templates/images/pizza.png')),
    ('popcorn', Image.open('./dash/templates/images/popcorn.png')),
    ('watermelon', Image.open('./dash/templates/images/watermelon.png'))
]


@vanilla_activate.get('/<lang>/<code>')
async def activate(request, lang, code):
    activation_data = await ActivationKey.query.where(ActivationKey.activation_key == code).gino.first()
    if not code:
        return response.json({'message': 'An error occured, please try again.'}, status=404)
    elif not activation_data:
        return response.json({'message': 'Activation key not found.'}, status=404)
    else:
        await Penguin.update.values(active=True) \
        .where(Penguin.id == activation_data.penguin_id).gino.status()
        await ActivationKey.delete.where((ActivationKey.penguin_id == activation_data.penguin_id)).gino.status()
        return response.redirect(app.config.ACTIVATE_REDIRECT)


@vanilla_create.get('/<lang>')
async def create_page(request, lang):
    base64_captchas = []
    captchas = random.sample(all_captchas, min(len(all_captchas), 3))
    captcha_answer = random.choice(captchas)[0]
    captcha_object = [captcha for captcha in captchas if captcha_answer in captcha]

    if 'anon_token' not in request['session']:
        anon_token = secrets.token_urlsafe(32)
        request['session']['anon_token'] = anon_token

    request['session']['captcha_answer'] = captchas.index(captcha_object[0])
    request['session']['captcha'] = {
        'passed': 0
    }
    request['session']['errors'] = {
        'name': True,
        'pass': True,
        'email': True,
        'terms': True,
        'captcha': True
    }

    request['session']['captcha_answer'] = captchas.index(captcha_object[0])
    
    for captcha_image in captchas:
        captcha_encoded = lsb.hide(captcha_image[1].copy(), request['session']['anon_token'])
        buffered = BytesIO()
        captcha_encoded.save(buffered, format='PNG')
        captcha_base64 = base64.b64encode(buffered.getvalue())
        base64_captchas.append(captcha_base64.decode('utf-8'))

    if lang == 'fr':
        register_template = env.get_template('fr_register.html')
        page = register_template.render(
            play_subdomain=app.config.PLAY_SUBDOMAIN,
            anon_token=request['session']['anon_token'],
            captcha_1=base64_captchas[0],
            captcha_2=base64_captchas[1],
            captcha_3=base64_captchas[2],
            captcha_answer=i18n.t(f'create.{captcha_answer}', locale=lang),
            site_key=app.config.GSITE_KEY
        )
        return response.html(page)
    elif lang == 'es':
        register_template = env.get_template('es_register.html')
        page = register_template.render(
            play_subdomain=app.config.PLAY_SUBDOMAIN,
            anon_token=request['session']['anon_token'],
            captcha_1=base64_captchas[0],
            captcha_2=base64_captchas[1],
            captcha_3=base64_captchas[2],
            captcha_answer=i18n.t(f'create.{captcha_answer}', locale=lang),
            site_key=app.config.GSITE_KEY
        )
        return response.html(page)
    elif lang == 'pt':
        register_template = env.get_template('pt_register.html')
        page = register_template.render(
            play_subdomain=app.config.PLAY_SUBDOMAIN,
            anon_token=request['session']['anon_token'],
            captcha_1=base64_captchas[0],
            captcha_2=base64_captchas[1],
            captcha_3=base64_captchas[2],
            captcha_answer=i18n.t(f'create.{captcha_answer}', locale=lang),
            site_key=app.config.GSITE_KEY
        )
        return response.html(page)
    else:
        register_template = env.get_template('en_register.html')
        page = register_template.render(
            play_subdomain=app.config.PLAY_SUBDOMAIN,
            anon_token=request['session']['anon_token'],
            captcha_1=base64_captchas[0],
            captcha_2=base64_captchas[1],
            captcha_3=base64_captchas[2],
            captcha_answer=i18n.t(f'create.{captcha_answer}', locale=lang),
            site_key=app.config.GSITE_KEY
        )
        return response.html(page)


@vanilla_create.post('/<lang>')
async def register(request, lang):
    query_string = request.body.decode('UTF-8')
    post_data = parse_qs(query_string)
    trigger = post_data.get('_triggering_element_name', [None])[0]
    anon_token = post_data.get('anon_token', [None])[0]
    if 'anon_token' not in request['session']:
        return response.json(
            {
                'message': '403 Forbidden'
            },
            status=403
        )
    elif not anon_token or request['session']['anon_token'] != anon_token:
        return response.json(
            {
                'message': '403 Forbidden'
            },
            status=403
        )

    if trigger == 'name':
        return await _validate_username(request, post_data, lang)
    elif trigger == 'pass':
        return _validate_password(request, post_data, lang)
    elif trigger == 'email':
        return await _validate_email(request, post_data, lang)
    elif trigger == 'terms':
        return _validate_terms(request, post_data, lang)
    elif trigger == 'captcha':
        return _validate_captcha(request, post_data, lang)
    else:
        return await _validate_registration(request, post_data, lang)


@vanilla_activate.get('/<lang>')
async def activate_page(request, lang):
    if lang == 'fr':
        register_template = env.get_template('fr_vanilla_activation.html')
        page = register_template.render(
            play_subdomain=app.config.PLAY_SUBDOMAIN,
            site_key=app.config.GSITE_KEY
        )
        return response.html(page)
    elif lang == 'es':
        register_template = env.get_template('es_vanilla_activation.html')
        page = register_template.render(
            play_subdomain=app.config.PLAY_SUBDOMAIN,
            site_key=app.config.GSITE_KEY
        )
        return response.html(page)
    elif lang == 'pt':
        register_template = env.get_template('pt_vanilla_activation.html')
        page = register_template.render(
            play_subdomain=app.config.PLAY_SUBDOMAIN,
            site_key=app.config.GSITE_KEY
        )
        return response.html(page)
    else:
        register_template = env.get_template('en_vanilla_activation.html')
        page = register_template.render(
            play_subdomain=app.config.PLAY_SUBDOMAIN,
            site_key=app.config.GSITE_KEY
        )
        return response.html(page)


@vanilla_activate.post('/<lang>')
async def activate_page(request, lang):
    query_string = request.body.decode('UTF-8')
    post_data = parse_qs(query_string)
    username = post_data.get('name', [None])[0]
    activation_code = post_data.get('activationcode', [None])[0]
    user_data = await Penguin.query.where(Penguin.username == username).gino.first()
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
                    return response.text(urlencode({
                        'error': gresult
                    }))
    # TODO: Better responses for these?
    if not username or not activation_code:
        return response.json({'message': 'An error occured, please try again.'}, status=404)
    elif not activation_data:
        return response.json({'message': 'Activation key not found.'}, status=404)
    elif not user_data:
        return response.json({'message': 'Username not found.'}, status=404)
    else:
        await Penguin.update.values(active=True).where(
            Penguin.id == activation_data.penguin_id
        ).gino.status()
        await ActivationKey.delete.where((ActivationKey.penguin_id == activation_data.penguin_id)).gino.status()
        return response.redirect(app.config.ACTIVATE_REDIRECT)


async def _validate_registration(request, post_data, lang):
    username = post_data.get('name', [None])[0] 
    password = post_data.get('pass', [None])[0] 
    email = post_data.get('email', [None])[0]
    color = post_data.get('color', [None])[0]  
    if 'username' not in request['session'] or request['session']['username'] != username:
        return response.json(
            {
                'message': '403 Forbidden'
            },
            status=403
        )
    elif 'password' not in request['session'] or request['session']['password'] != password:
        return response.json(
            {
                'message': '403 Forbidden'
            },
            status=403
        )
    elif 'email' not in request['session'] or request['session']['email'] != email:
        return response.json(
            {
                'message': '403 Forbidden'
            },
            status=403
        )
    elif not color.isdigit() or int(color) not in range(1, 16):
        return response.json(
            {
                'message': '403 Forbidden'
            },
            status=403
        )

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
                    return response.text(urlencode({
                        'error': gresult
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
        if lang == 'es':
            mail_template = env.get_template('es_vanilla_email.html')
        elif lang == 'pt':
            mail_template = env.get_template('pt_vanilla_email.html')
        elif lang == 'fr':
            mail_template = env.get_template('fr_vanilla_email.html')
        else:
            mail_template = env.get_template('en_vanilla_email.html')
        message = Mail(
            from_email=app.config.FROM_EMAIL, to_emails=email,
            subject=i18n.t('create.activate_mail_subject', locale=lang),
            html_content=mail_template.render(
                penguin=penguin, site_name=app.config.SITE_NAME,
                activation_code=activation_key,
                play_subdomain=app.config.PLAY_SUBDOMAIN,
                activate_link=f'{app.config.VANILLA_ACTIVATE_LINK}/{lang}/penguin/activate'
            )
        )
        sg = SendGridAPIClient(app.config.SENDGRID_API_KEY)
        sg.send(message)
        await ActivationKey.create(penguin_id=penguin.id, activation_key=activation_key)

    return response.redirect(app.config.PLAY_SUBDOMAIN)


async def _validate_username(request, post_data, lang):
    username = post_data.get('name', [None])[0] 
    if not username:
        request['session']['errors']['name'] = True
        return response.json(
            [
                _make_error_message('name', i18n.t('create.name_missing', locale=lang)), 
                _remove_class('name', 'valid'),
                _add_class('name', 'error'),
                _update_errors(request['session']['errors'])
            ],
            headers={
                'X-Drupal-Ajax-Token': 1
            }
        )
    
    elif len(username) < 4 or len(username) > 12:
        request['session']['errors']['name'] = True
        return response.json(
            [
                _make_error_message('name', i18n.t('create.name_short', locale=lang)), 
                _remove_class('name', 'valid'),
                _add_class('name', 'error'),
                _update_errors(request['session']['errors'])
            ],
            headers={
                'X-Drupal-Ajax-Token': 1
            }
        )
    
    elif len(re.sub('[^0-9]', '', username)) > 5:
        request['session']['errors']['name'] = True
        return response.json(
            [
                _make_error_message('name', i18n.t('create.name_number', locale=lang)), 
                _remove_class('name', 'valid'),
                _add_class('name', 'error'),
                _update_errors(request['session']['errors'])
            ],
            headers={
                'X-Drupal-Ajax-Token': 1
            }
        )

    elif re.search('[a-zA-Z]', username) is None:
        request['session']['errors']['name'] = True
        return response.json(
            [
                _make_error_message('name', i18n.t('create.name_letter', locale=lang)), 
                _remove_class('name', 'valid'),
                _add_class('name', 'error'),
                _update_errors(request['session']['errors'])
            ],
            headers={
                'X-Drupal-Ajax-Token': 1
            }
        )

    elif not username.isalnum():
        request['session']['errors']['name'] = True
        return response.json(
            [
                _make_error_message('name', i18n.t('create.name_not_allowed', locale=lang)), 
                _remove_class('name', 'valid'),
                _add_class('name', 'error'),
                _update_errors(request['session']['errors'])
            ],
            headers={
                'X-Drupal-Ajax-Token': 1
            }
        )

    nickname = username.rstrip(string.digits)
    names = await db.select([Penguin.username]).where(Penguin.username.like(f'{nickname.lower()}%')).gino.all()
    names = {name for name, in names}
    if username.lower() in names:
        request['session']['errors']['name'] = True
        max_digits = min(5, 12 - len(nickname))
        usernames_gen = (f'{nickname}{i}' for i in range(1, int('9' * max_digits)) if f'{nickname.lower()}{i}' not in names)
        usernames = [next(usernames_gen) for _ in range(3)]
        
        if usernames is None:
            return response.json(
                [
                    _make_error_message('name', i18n.t('create.name_taken', locale=lang)), 
                    _remove_class('name', 'valid'),
                    _add_class('name', 'error'),
                    _update_errors(request['session']['errors'])
                ],
                headers={
                    'X-Drupal-Ajax-Token': 1
                }
            )

        return response.json(
                [
                    _make_name_suggestion(usernames, i18n.t('create.vanilla_name_suggest', locale=lang)),
                    _remove_class('name', 'valid'),
                    _add_class('name', 'error'),
                    _update_errors(request['session']['errors'])
                ],
                headers={
                    'X-Drupal-Ajax-Token': 1
                }
            )
    
    else:
        request['session']['errors']['name'] = False
        request['session']['username'] = username
        return response.json(
            [ 
                _remove_class('name', 'error'),
                _add_class('name', 'valid'),
                _update_errors(request['session']['errors'])
            ],
            headers={
                'X-Drupal-Ajax-Token': 1
            }
        )


def _validate_password(request, post_data, lang):
    password = post_data.get('pass', [None])[0]
    if not password:
        request['session']['errors']['pass'] = True
        return response.json( 
            [
                _make_error_message('pass', i18n.t('create.password_short', locale=lang)), 
                _remove_class('pass', 'valid'),
                _add_class('pass', 'error'),
                _update_errors(request['session']['errors'])
            ],
            headers={
                'X-Drupal-Ajax-Token': 1
            }
        )
    
    elif len(password) < 4:
        request['session']['errors']['pass'] = True
        return response.json(
            [
                _make_error_message('pass', i18n.t('create.password_short', locale=lang)), 
                _remove_class('pass', 'valid'),
                _add_class('pass', 'error'),
                _update_errors(request['session']['errors'])
            ],
            headers={
                'X-Drupal-Ajax-Token': 1
            }
        )
    
    else:
        request['session']['errors']['pass'] = False
        request['session']['password'] = password
        return response.json(
            [
                _remove_class('pass', 'error'),
                _add_class('pass', 'valid'),
                _update_errors(request['session']['errors'])
            ],
            headers={
                'X-Drupal-Ajax-Token': 1
            }
        )


async def _validate_email(request, post_data, lang):
    email = post_data.get('email', [None])[0]
    _, email = parseaddr(email)
    domain = email.rsplit('@', 1)[-1]
    if not email or '@' not in email:
        request['session']['errors']['email'] = True
        return response.json(
            [
                _make_error_message('email', i18n.t('create.email_invalid', locale=lang)), 
                _remove_class('email', 'valid'),
                _add_class('email', 'error'),
                _update_errors(request['session']['errors'])
            ],
            headers={
                'X-Drupal-Ajax-Token': 1
            }
        )
    elif app.config.EMAIL_WHITELIST and domain not in app.config.EMAIL_WHITELIST:
        request['session']['errors']['email'] = True
        return response.json(
            [
                _make_error_message('email', i18n.t('create.email_invalid', locale=lang)), 
                _remove_class('email', 'valid'),
                _add_class('email', 'error'),
                _update_errors(request['session']['errors'])
            ],
            headers={
                'X-Drupal-Ajax-Token': 1
            }
        )

    email_count = await db.select([db.func.count(Penguin.email)]).where(
        db.func.lower(Penguin.email) == email.lower()).gino.scalar()

    if email_count >= app.config.MAX_ACCOUNT_EMAIL:
        request['session']['errors']['email'] = True
        return response.json( 
            [
                _make_error_message('email', i18n.t('create.email_invalid', locale=lang)), 
                _remove_class('email', 'valid'),
                _add_class('email', 'error'),
                _update_errors(request['session']['errors'])
            ],
            headers={
                'X-Drupal-Ajax-Token': 1
            }
        )
    
    else:
        request['session']['errors']['email'] = False
        request['session']['email'] = email
        return response.json(
            [
                _remove_class('email', 'error'),
                _add_class('email', 'valid'),
                _update_errors(request['session']['errors'])
            ],
            headers={
                'X-Drupal-Ajax-Token': 1
            }
        )


def _validate_terms(request, post_data, lang):
    terms = post_data.get('terms', [None])[0]
    if not terms:
        request['session']['errors']['terms'] = True
        return response.json(
            [
                _make_error_message('terms', i18n.t('create.terms', locale=lang)),
                _remove_class('terms', 'valid'),
                _add_class('terms', 'error'),
                _update_errors(request['session']['errors'])
            ],
            headers={
                'X-Drupal-Ajax-Token': 1
            }
        )
    else:
        request['session']['errors']['terms'] = False
        return response.json(
            [
                _add_class('terms', 'checked'),
                _update_errors(request['session']['errors'])
            ],
            headers={
                'X-Drupal-Ajax-Token': 1
            }
        )


def _validate_captcha(request, post_data, lang):
    captcha_answer = post_data.get('captcha', [None])[0]
    if 'captcha_answer' not in request['session']:
        return response.json(
            {
                'message': '403 Forbidden'
            },
            status=403
        )

    elif int(captcha_answer) == int(request['session']['captcha_answer']):
        request['session']['errors']['captcha'] = False
        request['session']['captcha']['passed'] = 1
        return response.json(
            [
                _update_captcha(request['session']['captcha']['passed']),
                _update_errors(request['session']['errors'])
            ],
            headers={
                'X-Drupal-Ajax-Token': 1
            }
        )
    else:
        return response.json(
            [
                _make_error_message('captcha', i18n.t('create.captcha_invalid', locale=lang)),
            ],
            headers={
                'X-Drupal-Ajax-Token': 1
            }
        )


def _update_errors(new_setting):
    return (
        {
            'command': 'settings',
            'merge': True,
            'settings': {
                'penguin': {
                    'errors': new_setting
                }
            }
        }
    )


def _update_captcha(new_setting):
    return (
        {
            'command': 'settings',
            'merge': True,
            'settings': {
                'penguin': {
                    'captcha': {
                        'passed': new_setting
                    }
                }
            }
        }
    )


def _make_name_suggestion(names, message):
    name_suggestion_template = env.get_template('name_suggestion.html')
    return (
        {
            'command': 'insert',
            'selector': '#name-error',
            'method': 'html',
            'data': name_suggestion_template.render(
                names=names,
                message=message
            )
        }
    )


def _make_error_message(name, message):
    error_template = env.get_template('error.html')
    return (
        {
            'command': 'insert',
            'selector': f'#{name}-error',
            'method': 'html',
            'data': error_template.render(
                message=message
            )
        }
    )


def _add_class(name, arguments):
    return (
        {
            'command': 'invoke',
            'selector': f'#edit-{name}',
            'method': 'addClass',
            'arguments': [arguments]
        }
    )


def _remove_class(name, arguments):
    return (
        {
            'command': 'invoke',
            'selector': f'#edit-{name}',
            'method': 'removeClass',
            'arguments': [arguments]
        }
    )
