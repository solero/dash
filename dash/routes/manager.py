from sanic import Blueprint, response
from urllib.parse import parse_qs
from dash import env, app
from dash.data.penguin import Penguin
from dash.data.moderator import Ban
from sqlalchemy import func
from datetime import datetime
from hashlib import md5

import os
import asyncio
import bcrypt
manager = Blueprint('manager', url_prefix='/manager')
manager.static('/static', os.path.join(os.path.dirname(os.path.abspath(__file__)), '../static'))


@manager.get('/')
async def login_page(_):
    template = env.get_template('manager/login.html')
    page = template.render(
        success_message='',
        error_message='',
        site_key=app.config.GSITE_KEY
    )
    return response.html(page)


@manager.get('/panel')
async def panel_page(request):
    if 'logged_in' not in request['session']:
        return response.redirect('/')
    else:
        data = await Penguin.query.where(func.lower(Penguin.username) == request['session']['username']).gino.first()
        template = env.get_template('manager/panel.html')
        page = template.render(
            penguin=data
        )
        return response.html(page)


@manager.post('/login')
async def login(request):
    query_string = request.body.decode('UTF-8')
    post_data = parse_qs(query_string)
    username = post_data.get('username', [None])[0]
    password = post_data.get('password', [None])[0]
    loop = asyncio.get_event_loop()
    template = env.get_template('manager/login.html')
    data = await Penguin.query.where(func.lower(Penguin.username) == username).gino.first()

    if data is None:
        page = template.render(
            success_message='',
            error_message='Your penguin was not found.',
            site_key=app.config.GSITE_KEY
        )
        return response.html(page)

    password_correct = await loop.run_in_executor(None, bcrypt.checkpw,
                                                  get_login_hash(password).encode('utf-8'),
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

    active_ban = await Ban.query.where((Ban.penguin_id == data.id) & (Ban.expires >= datetime.now())).gino.first()

    if active_ban is not None:
        hours_left = round((active_ban.expires - datetime.now()).total_seconds() / 60 / 60)
        page = template.render(
            success_message='',
            error_message=f'You are banned for the next {hours_left} hours',
            site_key=app.config.GSITE_KEY
        )
        return response.html(page)

    request['session']['username'] = username
    request['session']['logged_in'] = True
    return response.redirect('/panel')


def get_login_hash(password):
    login_hash = md5(password.encode('utf-8')).hexdigest().upper()
    login_hash = login_hash[16:32] + login_hash[0:16]
    login_hash += 'houdini'
    login_hash += 'Y(02.>\'H}t":E1'
    login_hash = md5(login_hash.encode('utf-8')).hexdigest()
    login_hash = login_hash[16:32] + login_hash[0:16]
    return login_hash
