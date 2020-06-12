from sanic import Blueprint, response
from dash import env
from urllib.parse import parse_qs
from sqlalchemy import func
from dash.data.penguin import Penguin
from dash.routes.manager.login import login_auth

verification = Blueprint('verification', url_prefix='/verify')


@verification.get('/')
@login_auth()
async def verify_page(_):
    return response.redirect('/manager/verify/en')


@verification.get('/<lang>')
@login_auth()
async def verify_page(request, lang):
    template = env.get_template('manager/verify.html')
    data = await Penguin.query.where(func.lower(Penguin.username) == request['session']['username']).gino.first()
    if lang == 'de':
        unverified_penguins = await Penguin.query.where(
            (Penguin.approval_de == False) & (Penguin.rejection_de == False)
        ).gino.all()
    elif lang == 'es':
        unverified_penguins = await Penguin.query.where(
            (Penguin.approval_es == False) & (Penguin.rejection_es == False)
        ).gino.all()
    elif lang == 'fr':
        unverified_penguins = await Penguin.query.where(
            (Penguin.approval_fr == False) & (Penguin.rejection_fr == False)
        ).gino.all()
    elif lang == 'pt':
        unverified_penguins = await Penguin.query.where(
            (Penguin.approval_pt == False) & (Penguin.rejection_pt == False)
        ).gino.all()
    elif lang == 'ru':
        unverified_penguins = await Penguin.query.where(
            (Penguin.approval_ru == False) & (Penguin.rejection_ru == False)
        ).gino.all()
    else:
        lang = 'en'
        unverified_penguins = await Penguin.query.where(
            (Penguin.approval_en == False) & (Penguin.rejection_en == False)
        ).gino.all()
    unverified_penguins = get_paginated_result(unverified_penguins)
    page = template.render(
        success_message='',
        error_message='',
        unverified_penguins=unverified_penguins,
        penguin=data,
        language=lang
    )
    return response.html(page)


@verification.post('/search')
@login_auth()
async def search_username(request):
    template = env.get_template('manager/verify.html')
    query_string = request.body.decode('UTF-8')
    post_data = parse_qs(query_string)
    username = post_data.get('username', [None])[0]
    language = post_data.get('language', [None])[0]
    data = await Penguin.query.where(func.lower(Penguin.username) == request['session']['username']).gino.first()
    if not language:
        return response.redirect(f'/manager/verify/en')
    if language == 'en':
        unverified_penguins = await Penguin.query.where(
            (Penguin.approval_en == False) & (Penguin.rejection_en == False)
            & (Penguin.username.ilike(f"%{username}%"))
        ).gino.all()
    elif language == 'de':
        unverified_penguins = await Penguin.query.where(
            (Penguin.approval_de == False) & (Penguin.rejection_de == False)
            & (Penguin.username.ilike(f"%{username}%"))
        ).gino.all()
    elif language == 'es':
        unverified_penguins = await Penguin.query.where(
            (Penguin.approval_es == False) & (Penguin.rejection_es == False)
            & (Penguin.username.ilike(f"%{username}%"))
        ).gino.all()
    elif language == 'fr':
        unverified_penguins = await Penguin.query.where(
            (Penguin.approval_fr == False) & (Penguin.rejection_fr == False)
            & (Penguin.username.ilike(f"%{username}%"))
        ).gino.all()
    elif language == 'pt':
        unverified_penguins = await Penguin.query.where(
            (Penguin.approval_pt == False) & (Penguin.rejection_pt == False)
            & (Penguin.username.ilike(f"%{username}%"))
        ).gino.all()
    elif language == 'ru':
        unverified_penguins = await Penguin.query.where(
            (Penguin.approval_ru == False) & (Penguin.rejection_ru == False)
            & (Penguin.username.ilike(f"%{username}%"))
        ).gino.all()
    else:
        language = 'en'
        unverified_penguins = await Penguin.query.where(
            (Penguin.approval_en == False) & (Penguin.rejection_en == False)
            & (Penguin.username.ilike(f"%{username}%"))
        ).gino.all()
    unverified_penguins = get_paginated_result(unverified_penguins)
    page = template.render(
        success_message=f"Searched usernames similar to {username}",
        error_message='',
        unverified_penguins=unverified_penguins,
        penguin=data,
        language=language
    )
    return response.html(page)


@verification.post('/approve/<penguin_id>')
@login_auth()
async def approve_request(request, penguin_id):
    template = env.get_template('manager/verify.html')
    query_string = request.body.decode('UTF-8')
    post_data = parse_qs(query_string)
    language = post_data.get('language', [None])[0]
    data = await Penguin.query.where(func.lower(Penguin.username) == request['session']['username']).gino.first()
    penguin = await Penguin.query.where(Penguin.id == int(penguin_id)).gino.first()
    if not language:
        return response.redirect(f'/manager/verify/en')
    if not penguin:
        return response.redirect(f'/manager/verify/{language}')
    if language == 'en':
        await Penguin.update.values(approval_en=True).where(Penguin.id == penguin.id).gino.status()
        unverified_penguins = await Penguin.query.where(
            (Penguin.approval_en == False) & (Penguin.rejection_en == False)
        ).gino.all()
    elif language == 'de':
        await Penguin.update.values(approval_de=True).where(Penguin.id == penguin.id).gino.status()
        unverified_penguins = await Penguin.query.where(
            (Penguin.approval_de == False) & (Penguin.rejection_de == False)
        ).gino.all()
    elif language == 'es':
        await Penguin.update.values(approval_es=True).where(Penguin.id == penguin.id).gino.status()
        unverified_penguins = await Penguin.query.where(
            (Penguin.approval_es == False) & (Penguin.rejection_es == False)
        ).gino.all()
    elif language == 'fr':
        await Penguin.update.values(approval_fr=True).where(Penguin.id == penguin.id).gino.status()
        unverified_penguins = await Penguin.query.where(
            (Penguin.approval_fr == False) & (Penguin.rejection_fr == False)
        ).gino.all()
    elif language == 'pt':
        await Penguin.update.values(approval_pt=True).where(Penguin.id == penguin.id).gino.status()
        unverified_penguins = await Penguin.query.where(
            (Penguin.approval_pt == False) & (Penguin.rejection_pt == False)
        ).gino.all()
    elif language == 'ru':
        await Penguin.update.values(approval_ru=True).where(Penguin.id == penguin.id).gino.status()
        unverified_penguins = await Penguin.query.where(
            (Penguin.approval_ru == False) & (Penguin.rejection_ru == False)
        ).gino.all()
    else:
        language = 'en'
        unverified_penguins = await Penguin.query.where(
            (Penguin.approval_en == False) & (Penguin.rejection_en == False)
        ).gino.all()
    unverified_penguins = get_paginated_result(unverified_penguins)
    page = template.render(
        success_message=f"Successfully approved {penguin.username}'s username.",
        error_message='',
        unverified_penguins=unverified_penguins,
        penguin=data,
        language=language
    )
    return response.html(page)


@verification.post('/reject/<penguin_id>')
@login_auth()
async def reject_request(request, penguin_id):
    template = env.get_template('manager/verify.html')
    query_string = request.body.decode('UTF-8')
    post_data = parse_qs(query_string)
    language = post_data.get('language', [None])[0]
    data = await Penguin.query.where(func.lower(Penguin.username) == request['session']['username']).gino.first()
    penguin = await Penguin.query.where(Penguin.id == int(penguin_id)).gino.first()
    if not language:
        return response.redirect(f'/manager/verify/en')
    if not penguin:
        return response.redirect(f'/manager/verify/{language}')
    if language == 'en':
        await Penguin.update.values(rejection_en=True).where(Penguin.id == penguin.id).gino.status()
        unverified_penguins = await Penguin.query.where(
            (Penguin.approval_en == False) & (Penguin.rejection_en == False)
        ).gino.all()
    elif language == 'de':
        await Penguin.update.values(rejection_de=True).where(Penguin.id == penguin.id).gino.status()
        unverified_penguins = await Penguin.query.where(
            (Penguin.approval_de == False) & (Penguin.rejection_de == False)
        ).gino.all()
    elif language == 'es':
        await Penguin.update.values(rejection_es=True).where(Penguin.id == penguin.id).gino.status()
        unverified_penguins = await Penguin.query.where(
            (Penguin.approval_es == False) & (Penguin.rejection_es == False)
        ).gino.all()
    elif language == 'fr':
        await Penguin.update.values(rejection_fr=True).where(Penguin.id == penguin.id).gino.status()
        unverified_penguins = await Penguin.query.where(
            (Penguin.approval_fr == False) & (Penguin.rejection_fr == False)
        ).gino.all()
    elif language == 'pt':
        await Penguin.update.values(rejection_pt=True).where(Penguin.id == penguin.id).gino.status()
        unverified_penguins = await Penguin.query.where(
            (Penguin.approval_pt == False) & (Penguin.rejection_pt == False)
        ).gino.all()
    elif language == 'ru':
        await Penguin.update.values(rejection_ru=True).where(Penguin.id == penguin.id).gino.status()
        unverified_penguins = await Penguin.query.where(
            (Penguin.approval_ru == False) & (Penguin.rejection_ru == False)
        ).gino.all()
    else:
        language = 'en'
        unverified_penguins = await Penguin.query.where(
            (Penguin.approval_en == False) & (Penguin.rejection_en == False)
        ).gino.all()
    unverified_penguins = get_paginated_result(unverified_penguins)
    page = template.render(
        success_message=f"Successfully rejected {penguin.username}'s username.",
        error_message='',
        unverified_penguins=unverified_penguins,
        penguin=data,
        language=language
    )
    return response.html(page)


def get_paginated_result(unverified_penguins):
    all_unverified_penguins = {}
    current_count = 0
    pagination_limit = current_count + 10
    page = 1
    for unverified_penguin in unverified_penguins:
        if current_count == 0:
            all_unverified_penguins[page] = []
            all_unverified_penguins[page].append(unverified_penguin)
        elif current_count == pagination_limit:
            page += 1
            pagination_limit = current_count + 10
            all_unverified_penguins[page] = []
            all_unverified_penguins[page].append(unverified_penguin)
        else:
            all_unverified_penguins[page].append(unverified_penguin)
        current_count += 1
    return all_unverified_penguins
