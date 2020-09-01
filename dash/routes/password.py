import secrets

import aiohttp
import bcrypt
import i18n
from sanic import Blueprint, response
from sendgrid import Mail, SendGridAPIClient

from dash import app, env
from dash.crypto import Crypto
from dash.data.penguin import Penguin

password = Blueprint('password', url_prefix='/password')


@password.get('/<lang>')
async def password_reset_page(_, lang):
    if lang == 'fr':
        template = env.get_template('password/request/fr.html')
        page = template.render(
            VANILLA_PLAY_LINK=app.config.VANILLA_PLAY_LINK,
            site_key=app.config.GSITE_KEY
        )
        return response.html(page)
    
    elif lang == 'es':
        template = env.get_template('password/request/es.html')
        page = template.render(
            VANILLA_PLAY_LINK=app.config.VANILLA_PLAY_LINK,
            site_key=app.config.GSITE_KEY
        )
        return response.html(page)
    
    elif lang == 'pt':
        template = env.get_template('password/request/pt.html')
        page = template.render(
            VANILLA_PLAY_LINK=app.config.VANILLA_PLAY_LINK,
            site_key=app.config.GSITE_KEY
        )
        return response.html(page)
    
    else:
        template = env.get_template('password/request/en.html')
        page = template.render(
            VANILLA_PLAY_LINK=app.config.VANILLA_PLAY_LINK,
            site_key=app.config.GSITE_KEY
        )
        return response.html(page)


@password.get('/<lang>/<reset_token>')
async def choose_password_page(_, lang, reset_token):
    reset_key = await app.redis.get(f'{reset_token}.reset_key')
    if reset_key:
        if lang == 'fr':
            template = env.get_template('password/choose/fr.html')
            page = template.render(
                VANILLA_PLAY_LINK=app.config.VANILLA_PLAY_LINK,
                token=reset_token,
                site_key=app.config.GSITE_KEY
            )
            return response.html(page)
        elif lang == 'es':
            template = env.get_template('password/choose/es.html')
            page = template.render(
                VANILLA_PLAY_LINK=app.config.VANILLA_PLAY_LINK,
                token=reset_token,
                site_key=app.config.GSITE_KEY
            )
            return response.html(page)
        elif lang == 'pt':
            template = env.get_template('password/choose/pt.html')
            page = template.render(
                VANILLA_PLAY_LINK=app.config.VANILLA_PLAY_LINK,
                token=reset_token,
                site_key=app.config.GSITE_KEY
            )
            return response.html(page)
        
        else:
            template = env.get_template('password/choose/en.html')
            page = template.render(
                VANILLA_PLAY_LINK=app.config.VANILLA_PLAY_LINK,
                token=reset_token,
                site_key=app.config.GSITE_KEY
            )
            return response.html(page)
    return response.json({'message': 'Reset key not found'}, status=404)


@password.post('/<lang>')
async def request_password_reset(request, lang):
    username = request.form.get('name', '').lower()
    email = request.form.get('email', '').lower()
    if app.config.GSECRET_KEY:
        gclient_response = request.form.get('recaptcha_response', '')
        async with aiohttp.ClientSession() as session:
            async with session.post(app.config.GCAPTCHA_URL, data=dict(
                secret=app.config.GSECRET_KEY,
                response=gclient_response,
                remoteip=request.ip
            )) as resp:
                gresult = await resp.json()
                if not gresult['success']:
                    return response.text('Your captcha score was low, please try again.')

    if not username:
        return response.json(
            [
                _add_class('name', 'error')
            ],
            headers={
                'X-Drupal-Ajax-Token': 1
            }
        )
    elif not email or '@' not in email:
        return response.json(
            [
                _add_class('email', 'error')
            ],
            headers={
                'X-Drupal-Ajax-Token': 1
            }
        )

    data = await Penguin.query.where(
        Penguin.username == username
    ).gino.first()
    if data and data.email == email:
        reset_key = secrets.token_urlsafe(45)
        if lang == 'es':
            mail_template = env.get_template('emails/password/es.html')
        elif lang == 'pt':
            mail_template = env.get_template('emails/password/pt.html')
        elif lang == 'fr':
            mail_template = env.get_template('emails/password/fr.html')
        else:
            mail_template = env.get_template('emails/password/en.html')
        message = Mail(
            from_email=app.config.FROM_EMAIL, to_emails=email,
            subject=i18n.t('password.reset_password_subject', locale=lang),
            html_content=mail_template.render(
                username=username, 
                site_name=app.config.SITE_NAME,
                reset_link=f'{app.config.VANILLA_PLAY_LINK}/{lang}/penguin/forgot-password/{reset_key}'
            )
        )
        sg = SendGridAPIClient(app.config.SENDGRID_API_KEY)
        sg.send(message)
        await app.redis.setex(f'{reset_key}.reset_key', app.config.AUTH_TTL, data.id)
    return response.json(
        [
            _remove_selector('#edit-name'),
            _remove_selector('#edit-email'),
            _remove_selector('#edit-submit'),
            
            _edit_title(
                '#forgotpassword h2',
                i18n.t('password.password_title', locale=lang),
            ),
            _edit_prompt(
                '#penguin-forgot-password-form span',
                i18n.t('password.password_prompt', locale=lang),
            ) 
        ],
        headers={
            'X-Drupal-Ajax-Token': 1
        }
    )


@password.post('/<lang>/<reset_token>')
async def choose_password(request, lang, reset_token):
    new_password = request.form.get('password', None)
    confirm_password = request.form.get('confirm_password', None)
    player_id = await app.redis.get(f'{reset_token}.reset_key')
    try:
        player_id = player_id.decode()
    except AttributeError:
        return response.json({"message": "Something went wrong."}, status=500)
    data = await Penguin.query.where(
        Penguin.id == int(player_id)
    ).gino.first()
    if app.config.GSECRET_KEY:
        gclient_response = request.form.get('recaptcha_response', '')
        async with aiohttp.ClientSession() as session:
            async with session.post(app.config.GCAPTCHA_URL, data=dict(
                secret=app.config.GSECRET_KEY,
                response=gclient_response,
                remoteip=request.ip
            )) as resp:
                gresult = await resp.json()
                if not gresult['success']:
                    return response.text('Your captcha score was low, please try again.')
    if not new_password:
        return response.json(
            [
                _add_class('password', 'error')
            ],
            headers={
                'X-Drupal-Ajax-Token': 1
            }
        )
    elif not confirm_password:
        return response.json(
            [
                _add_class('confirm-password', 'error')
            ],
            headers={
                'X-Drupal-Ajax-Token': 1
            }
        )
    elif len(new_password) < 4:
        return response.json(
            [
                _add_class('password', 'error')
            ],
            headers={
                'X-Drupal-Ajax-Token': 1
            }
        )
    elif new_password != confirm_password:
        return response.json(
            [
                _add_class('password', 'error'),
                _add_class('confirm-password', 'error')
            ],
            headers={
                'X-Drupal-Ajax-Token': 1
            }
        )
    new_password = Crypto.hash(new_password).upper()
    new_password = Crypto.get_login_hash(new_password, rndk=app.config.STATIC_KEY)
    new_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt(12)).decode('utf-8')
    await app.redis.delete(f'{reset_token}.reset_key')
    await Penguin.update.values(password=new_password).where(Penguin.id == data.id).gino.status()
    return response.json(
        [
            _remove_selector('#edit-password'),
            _remove_selector('#edit-confirm-password'),
            _remove_selector('#edit-submit'),
            
            _edit_title(
                '#forgotpassword h2',
                i18n.t('password.success_title', locale=lang),
            ),
            _edit_prompt(
                '#penguin-forgot-password-form span',
                i18n.t('password.success_prompt', locale=lang),
            ) 
        ],
        headers={
            'X-Drupal-Ajax-Token': 1
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


def _remove_selector(name):
    return (
        {
            'command': 'remove',
            'selector': name,
        }
    )


def _edit_title(selector, message):
    title_template = env.get_template('html/title.html')
    return (
        {
            'command': 'insert',
            'selector': selector,
            'method': 'replaceWith',
            'data': title_template.render(
                message=message
            )
        }
    )


def _edit_prompt(selector, message):
    prompt_template = env.get_template('html/prompt.html')
    return (
        {
            'command': 'insert',
            'selector': selector,
            'method': 'replaceWith',
            'data': prompt_template.render(
                message=message
            )
        }
    )
