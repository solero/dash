import asyncio
import os
import aiohttp
import bcrypt

from email.utils import parseaddr
from sanic import Blueprint, response
from sqlalchemy import func

from dash import app, env
from dash.crypto import Crypto
from dash.data import db
from dash.data.penguin import Login, Penguin
from dash.routes.manager.login import login, login_auth, login_auth, logout
from dash.routes.manager.moderation import moderation
from dash.routes.manager.verification import verification

panel = Blueprint('main', url_prefix='/')
static = Blueprint('static', url_prefix='/static')
static.static('/', os.path.join(os.path.dirname(os.path.abspath(__file__)), './static'))

manager = Blueprint.group(
    panel,
    login,
    logout,
    verification,
    moderation,
    static,
    url_prefix='/manager'
)


@panel.get('')
@login_auth()
async def main_page(request):
    data = await Penguin.query.where(func.lower(Penguin.username) == request.ctx.session.get('username')).gino.first()
    login_history = await Login.query.where(Login.penguin_id == data.id).order_by(Login.date.desc()).limit(5).gino.all()
    template = env.get_template('manager/panel.html')
    page = template.render(
        penguin=data,
        play_link=app.config.VANILLA_PLAY_LINK,
        login_history=login_history,
        success_message='',
        error_message='',
        site_key=app.config.GSITE_KEY
    )
    return response.html(page)


@panel.get('password')
@login_auth()
async def password_page(_):
    template = env.get_template('manager/password.html')
    page = template.render(
        success_message='',
        error_message='',
        site_key=app.config.GSITE_KEY
    )
    return response.html(page)


@panel.post('password')
@login_auth()
async def password_request(request):
    old_password = request.form.get('old_password', None)
    password = request.form.get('password', None)
    password_confirm = request.form.get('password_confirm', None)
    template = env.get_template('manager/password.html')
    if app.config.GSECRET_KEY:
        gclient_response = request.form.get('recaptcha_response', None)
        async with aiohttp.ClientSession() as session:
            async with session.post(app.config.GCAPTCHA_URL, data=dict(
                secret=app.config.GSECRET_KEY,
                response=gclient_response,
                remoteip=request.ip
            )) as resp:
                gresult = await resp.json()
                if not gresult['success']:
                    page = template.render(
                        success_message='',
                        error_message='Your captcha score was low. Please try again.',
                        site_key=app.config.GSITE_KEY
                    )
                    return response.html(page)

    if not old_password:
        page = template.render(
            success_message='',
            error_message='You must provide your old password.',
            site_key=app.config.GSITE_KEY
        )
        return response.html(page)
    elif not password or not password_confirm:
        page = template.render(
            success_message='',
            error_message='You must provide a new password.',
            site_key=app.config.GSITE_KEY
        )
        return response.html(page)
    elif len(password) < 5 or len(password) < 5:
        page = template.render(
            success_message='',
            error_message='Your new password must be more than 5 characters..',
            site_key=app.config.GSITE_KEY
        )
        return response.html(page)
    elif password != password_confirm:
        page = template.render(
            success_message='',
            error_message='Your new passwords must match.',
            site_key=app.config.GSITE_KEY
        )
        return response.html(page)
    data = await Penguin.query.where(func.lower(Penguin.username) == request.ctx.session.get('username')).gino.first()
    loop = asyncio.get_event_loop()

    old_password = Crypto.hash(old_password).upper()
    old_password = Crypto.get_login_hash(old_password, rndk=app.config.STATIC_KEY)
    password_correct = await loop.run_in_executor(None, bcrypt.checkpw,
                                                  old_password.encode('utf-8'),
                                                  data.password.encode('utf-8'))

    if not password_correct:
        page = template.render(
            success_message='',
            error_message='Your old password is incorrect.',
            site_key=app.config.GSITE_KEY
        )
        return response.html(page)

    password = Crypto.hash(password).upper()
    password = Crypto.get_login_hash(password, rndk=app.config.STATIC_KEY)
    password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(12)).decode('utf-8')
    await Penguin.update.values(password=password).where(Penguin.id == data.id).gino.status()
    data = await Penguin.query.where(func.lower(Penguin.username) == request.ctx.session.get('username')).gino.first()
    login_history = await Login.query.where(Login.penguin_id == data.id).order_by(Login.date.desc()).limit(5).gino.all()
    template = env.get_template('manager/panel.html')
    page = template.render(
        penguin=data,
        play_link=app.config.VANILLA_PLAY_LINK,
        login_history=login_history,
        success_message='You have successfully updated your password.',
        error_message='',
        site_key=app.config.GSITE_KEY
    )
    return response.html(page)


@panel.get('email')
@login_auth()
async def email_page(_):
    template = env.get_template('manager/email.html')
    page = template.render(
        success_message='',
        error_message='',
        site_key=app.config.GSITE_KEY
    )
    return response.html(page)


@panel.post('email')
@login_auth()
async def email_request(request):
    email = request.form.get('email', None)
    email_confirm = request.form.get('email_confirm', None)
    template = env.get_template('manager/email.html')
    if app.config.GSECRET_KEY:
        gclient_response = request.form.get('recaptcha_response', None)
        async with aiohttp.ClientSession() as session:
            async with session.post(app.config.GCAPTCHA_URL, data=dict(
                secret=app.config.GSECRET_KEY,
                response=gclient_response,
                remoteip=request.ip
            )) as resp:
                gresult = await resp.json()
                if not gresult['success']:
                    page = template.render(
                        success_message='',
                        error_message='Your captcha score was low. Please try again.',
                        site_key=app.config.GSITE_KEY
                    )
                    return response.html(page)

    elif not email or not email_confirm:
        page = template.render(
            success_message='',
            error_message='You must provide your email.',
            site_key=app.config.GSITE_KEY
        )
        return response.html(page)
    _, email = parseaddr(email)
    domain = email.rsplit('@', 1)[-1]
    if not email or '@' not in email:
        page = template.render(
            success_message='',
            error_message='You must enter a valid email.',
            site_key=app.config.GSITE_KEY
        )
        return response.html(page)
    elif app.config.EMAIL_WHITELIST and domain not in app.config.EMAIL_WHITELIST:
        page = template.render(
            success_message='',
            error_message='You must enter an email provider that is whitelisted from out system.',
            site_key=app.config.GSITE_KEY
        )
        return response.html(page)

    email_count = await db.select([db.func.count(Penguin.email)]).where(
        db.func.lower(Penguin.email) == email.lower()).gino.scalar()

    if email_count >= app.config.MAX_ACCOUNT_EMAIL:
        page = template.render(
            success_message='',
            error_message=f'There are more than ${app.config.MAX_ACCOUNT_EMAIL} '
                          f'emails under this address. Please try another email address.',
            site_key=app.config.GSITE_KEY
        )
        return response.html(page)

    await Penguin.update.values(email=email).where(Penguin.username == request['session']['username']).gino.status()
    data = await Penguin.query.where(func.lower(Penguin.username) == request['session']['username']).gino.first()
    login_history = await Login.query.where(Login.penguin_id == data.id).order_by(Login.date.desc()).limit(5).gino.all()
    template = env.get_template('manager/panel.html')
    page = template.render(
        penguin=data,
        play_link=app.config.VANILLA_PLAY_LINK,
        login_history=login_history,
        success_message='You have successfully updated your email.',
        error_message='',
        site_key=app.config.GSITE_KEY
    )
    return response.html(page)


