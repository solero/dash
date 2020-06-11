from sanic import Blueprint, response
from dash import env, app
from urllib.parse import parse_qs
from sqlalchemy import func
from dash.data.penguin import Penguin
from dash.routes.manager.login import login_auth

moderation = Blueprint('moderation', url_prefix='/panel')


@moderation.get('/verify/<lang>')
@login_auth()
async def verify_page(request, lang):
    template = env.get_template('manager/verify.html') # add diff lang in navbar as option
    data = await Penguin.query.where(func.lower(Penguin.username) == request['session']['username']).gino.first()
    unverified_penguins_en = await Penguin.query.where(
        Penguin.approval_en == False
    ).gino.all()
    unverified_penguins_de = await Penguin.query.where(
        Penguin.approval_de == False
    ).gino.all()
    unverified_penguins_es = await Penguin.query.where(
        Penguin.approval_es == False
    ).gino.all()
    unverified_penguins_fr = await Penguin.query.where(
        Penguin.approval_fr == False
    ).gino.all()
    unverified_penguins_pt = await Penguin.query.where(
        Penguin.approval_pt == False
    ).gino.all()
    unverified_penguins_ru = await Penguin.query.where(
        Penguin.approval_ru == False
    ).gino.all()
    page = template.render(
        success_message='',
        error_message='',
        unverified_penguins_en=unverified_penguins_en,
        unverified_penguins_de=unverified_penguins_de,
        unverified_penguins_es=unverified_penguins_es,
        unverified_penguins_fr=unverified_penguins_fr,
        unverified_penguins_pt=unverified_penguins_pt,
        unverified_penguins_ru=unverified_penguins_ru,
        penguin=data,
        language='en'
    )
    return response.html(page)


@moderation.post('/verify/<penguin_id>')
@login_auth()
async def verify_request(request, penguin_id):
    template = env.get_template('manager/verify.html')
    query_string = request.body.decode('UTF-8')
    post_data = parse_qs(query_string)
    language = post_data.get('language', [None])[0]
    unverified_penguins_en = await Penguin.query.where(
        Penguin.approval_en == False
    ).gino.all()
    unverified_penguins_de = await Penguin.query.where(
        Penguin.approval_de == False
    ).gino.all()
    unverified_penguins_es = await Penguin.query.where(
        Penguin.approval_es == False
    ).gino.all()
    unverified_penguins_fr = await Penguin.query.where(
        Penguin.approval_fr == False
    ).gino.all()
    unverified_penguins_pt = await Penguin.query.where(
        Penguin.approval_pt == False
    ).gino.all()
    unverified_penguins_ru = await Penguin.query.where(
        Penguin.approval_ru == False
    ).gino.all()
    data = await Penguin.query.where(func.lower(Penguin.username) == request['session']['username']).gino.first()
    if not language:
        page = template.render(
            success_message="You must pick from a valid language.",
            error_message='',
            unverified_penguins_en=unverified_penguins_en,
            unverified_penguins_de=unverified_penguins_de,
            unverified_penguins_es=unverified_penguins_es,
            unverified_penguins_fr=unverified_penguins_fr,
            unverified_penguins_pt=unverified_penguins_pt,
            unverified_penguins_ru=unverified_penguins_ru,
            penguin=data,
            language='en'
        )
        return response.html(page)
    penguin = await Penguin.query.where(Penguin.id == int(penguin_id)).gino.first()
    if not penguin:
        page = template.render(
            success_message=f"The penguin ID {penguin_id} does not exist ",
            error_message='',
            unverified_penguins_en=unverified_penguins_en,
            unverified_penguins_de=unverified_penguins_de,
            unverified_penguins_es=unverified_penguins_es,
            unverified_penguins_fr=unverified_penguins_fr,
            unverified_penguins_pt=unverified_penguins_pt,
            unverified_penguins_ru=unverified_penguins_ru,
            penguin=data,
            language=language
        )
        return response.html(page)

    if language == 'en':
        await Penguin.update.values(approval_en=True).where(Penguin.id == penguin.id).gino.status()
    elif language == 'de':
        await Penguin.update.values(approval_de=True).where(Penguin.id == penguin.id).gino.status()
    elif language == 'es':
        await Penguin.update.values(approval_es=True).where(Penguin.id == penguin.id).gino.status()
    elif language == 'fr':
        await Penguin.update.values(approval_fr=True).where(Penguin.id == penguin.id).gino.status()
    elif language == 'pt':
        await Penguin.update.values(approval_pt=True).where(Penguin.id == penguin.id).gino.status()
    elif language == 'ru':
        await Penguin.update.values(approval_ru=True).where(Penguin.id == penguin.id).gino.status()
    unverified_penguins_en = await Penguin.query.where(
        Penguin.approval_en == False
    ).gino.all()
    unverified_penguins_de = await Penguin.query.where(
        Penguin.approval_de == False
    ).gino.all()
    unverified_penguins_es = await Penguin.query.where(
        Penguin.approval_es == False
    ).gino.all()
    unverified_penguins_fr = await Penguin.query.where(
        Penguin.approval_fr == False
    ).gino.all()
    unverified_penguins_pt = await Penguin.query.where(
        Penguin.approval_pt == False
    ).gino.all()
    unverified_penguins_ru = await Penguin.query.where(
        Penguin.approval_ru == False
    ).gino.all()
    page = template.render(
        success_message=f"Successfully verified {penguin.username}'s name for {language} servers",
        error_message='',
        unverified_penguins_en=unverified_penguins_en,
        unverified_penguins_de=unverified_penguins_de,
        unverified_penguins_es=unverified_penguins_es,
        unverified_penguins_fr=unverified_penguins_fr,
        unverified_penguins_pt=unverified_penguins_pt,
        unverified_penguins_ru=unverified_penguins_ru,
        penguin=data,
        language=language
    )
    return response.html(page)
