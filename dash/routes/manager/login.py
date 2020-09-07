import asyncio
from datetime import datetime
from functools import wraps
from urllib.parse import parse_qs

import aiohttp
import bcrypt
from sanic import Blueprint, response
from sqlalchemy import func

from dash import app, env
from dash.crypto import Crypto
from dash.data.moderator import Ban
from dash.data.penguin import Penguin

login = Blueprint('login', url_prefix='/login')
logout = Blueprint('logout', url_prefix='/logout')


@login.get('/')
async def login_page(_):
    template = env.get_template('manager/login.html')
    page = template.render(
        success_message='',
        error_message='',
        site_key=app.config.GSITE_KEY
    )
    return response.html(page)


@login.post('/')
async def login_request(request):
    username = request.form.get('username', None)
    username = username.lower()
    password = request.form.get('password', None)
    loop = asyncio.get_event_loop()
    template = env.get_template('manager/login.html')
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
    if not username:
        page = template.render(
            success_message='',
            error_message='You must provide a username.',
            site_key=app.config.GSITE_KEY
        )
        return response.html(page)
    elif not password:
        page = template.render(
            success_message='',
            error_message='You must provide a password.',
            site_key=app.config.GSITE_KEY
        )
        return response.html(page)

    data = await Penguin.query.where(func.lower(Penguin.username) == username).gino.first()
    if data is None:
        page = template.render(
            success_message='',
            error_message='Your penguin was not found.',
            site_key=app.config.GSITE_KEY
        )
        return response.html(page)

    password = Crypto.hash(password).upper()
    password = Crypto.get_login_hash(password, rndk=app.config.STATIC_KEY)
    password_correct = await loop.run_in_executor(None, bcrypt.checkpw,
                                                  password.encode('utf-8'),
                                                  data.password.encode('utf-8'))
    flood_key = f'{request.ip}.flood'
    if not password_correct:
        if await app.redis.exists(flood_key):
            tr = app.redis.multi_exec()
            tr.incr(flood_key)
            tr.expire(flood_key, app.config.LOGIN_FAILURE_TIMER)
            failure_count, _ = await tr.execute()
            if failure_count >= app.config.LOGIN_FAILURE_LIMIT:
                page = template.render(
                    success_message='',
                    error_message='Maximum login attempts exceeded. Please try again in an hour.',
                    site_key=app.config.GSITE_KEY
                )
                return response.html(page)
        else:
            await app.redis.setex(flood_key, app.config.LOGIN_FAILURE_TIMER, 1)
        page = template.render(
            success_message='',
            error_message='You have entered an incorrect password.',
            site_key=app.config.GSITE_KEY
        )
        return response.html(page)

    failure_count = await app.redis.get(flood_key)
    if failure_count:
        max_attempts_exceeded = int(failure_count) >= app.config.LOGIN_FAILURE_LIMIT
        if max_attempts_exceeded:
            page = template.render(
                success_message='',
                error_message='Maximum login attempts exceeded. Please try again in an hour.',
                site_key=app.config.GSITE_KEY
            )
            return response.html(page)
        else:
            await app.redis.delete(flood_key)
    if not data.active:
        page = template.render(
            success_message='',
            error_message='Your account has not been activated.',
            site_key=app.config.GSITE_KEY
        )
        return response.html(page)
    if data.permaban:
        page = template.render(
            success_message='',
            error_message='You are banned forever.',
            site_key=app.config.GSITE_KEY
        )
        return response.html(page)
    if not data.moderator:
        page = template.render(
            success_message='',
            error_message='You do not have permission to access this panel.',
            site_key=app.config.GSITE_KEY
        )
        return response.html(page)

    active_ban = await Ban.query.where((Ban.penguin_id == data.id) & (Ban.expires >= datetime.now())).gino.first()
    if active_ban is not None:
        hours_left = round((active_ban.expires - datetime.now()).total_seconds() / 60 / 60)
        page = template.render(
            success_message='',
            error_message=f'You are banned for the next {hours_left} hours.',
            site_key=app.config.GSITE_KEY
        )
        return response.html(page)
    request.ctx.session['username'] = username
    request.ctx.session['logged_in'] = True
    return response.redirect('/manager')


def login_auth():
    def decorator(f):
        @wraps(f)
        async def decorated_function(request, *args, **kwargs):
            if 'username' not in request.ctx.session:
                return response.redirect('/manager/login')
            elif request.ctx.session.get('username') is None:
                return response.redirect('/manager/login')
            elif 'logged_in' not in request.ctx.session:
                return response.redirect('/manager/login')
            elif request.ctx.session.get('logged_in') is not True:
                return response.redirect('/manager/login')
            return await f(request, *args, **kwargs)
        return decorated_function
    return decorator


@logout.get('/')
@login_auth()
async def logout_request(request):
    request.ctx.session['username'] = None
    request.ctx.session['logged_in'] = False
    return response.redirect('/manager/login')
