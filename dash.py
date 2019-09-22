from urllib.parse import parse_qs
from sanic import Sanic, response
from data.penguin import Penguin, PenguinItem, PenguinPostcard, ActivationKey, db
from config import config
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import re
import urllib.parse
import urllib.request
import secrets
import json
import string
import hashlib
import bcrypt


if config['EmailWhiteList'] and isinstance(config['EmailWhiteList'], str):
    email_list = open(config['EmailWhiteList'], 'r')
    white_list = email_list.readlines()
    email_list.close()
    config['EmailWhiteList'] = []
    for email in white_list:
        config['EmailWhiteList'].append(str(email))

app = Sanic()


@app.route('/create_account', methods=["POST"])
async def register(request):
    query_string = request.body.decode('UTF-8')
    global post_data
    post_data = parse_qs(query_string)
    action = attempt_data_retrieval('action')[0]
    lang = attempt_data_retrieval('lang')[0]
    if action == 'validate_agreement':
        return validate_agreement(response, lang)
    elif action == 'validate_username':
        return await validate_username(response, lang)
    elif action == 'validate_password_email':
        return await validate_password_email(request, response, lang)


@app.route('/activation/<activation_key>', methods=["GET"])
async def activate(request, activation_key):
    await db.set_bind(
        f"postgresql://{config['database']['Username']}:{config['database']['Password']}@{config['database']['Address']}/{config['database']['Name']}")
    data = await ActivationKey.query.where(ActivationKey.activation_key == activation_key).gino.first()
    if data is not None:
        return await handle_activation(data)

    return response.text('Activation key was not found in our records.')


@app.route('/avatar/<penguin_id>', methods=["GET"])
async def avatar(request, penguin_id):
    await db.set_bind(
        f"postgresql://{config['database']['Username']}:{config['database']['Password']}@{config['database']['Address']}/{config['database']['Name']}")
    if not penguin_id.isdigit():
        return response.text('Penguin ID is not a digit')
    penguin_id = int(penguin_id)
    user_count = await id_count(penguin_id)
    if not user_count:
        return response.text('This penguin ID does not exist')

    items = await Penguin.select('color', 'head', 'face', 'neck', 'body', 'hand', 'feet', 'photo', 'flag').where(Penguin.id == penguin_id).gino.first()

    return response.text(items)


async def handle_activation(data):
    await Penguin.update.values(active=True) \
        .where(Penguin.id == data.penguin_id).gino.status()
    await ActivationKey.delete.where((ActivationKey.penguin_id == data.penguin_id)).gino.status()
    return response.text('Activated penguin, you may now login.')


def validate_agreement(response, lang):
    agree_terms = int(attempt_data_retrieval('agree_to_terms')[0])
    agree_rules = int(attempt_data_retrieval('agree_to_rules')[0])
    if not agree_terms or not agree_rules:
        return response.text(build_query({'error': localization[lang]['terms']}))
    return response.text(build_query({'success': 1}))


async def validate_username(response, lang):
    username = attempt_data_retrieval('username')
    color = attempt_data_retrieval("colour")[0]
    if not username:
        return response.text(build_query({'error': localization[lang]['name_missing']}))

    elif len(username[0]) < 4 or len(username[0]) > 12:
        return response.text(build_query({'error': localization[lang]['name_short']}))

    elif len(re.sub("[^0-9]", "", username[0])) > 5:
        return response.text(build_query({'error': localization[lang]['name_number']}))

    elif len(re.sub("[^a-zA-Z]", "", username[0])) < 1:
        return response.text(build_query({'error': localization[lang]['penguin_letter']}))

    elif not config["allowed_chars"].match(username[0]):
        return response.text(build_query({'error': localization[lang]['name_not_allowed']}))

    elif not color.isdigit() or int(color) not in range(1, 15):
        return response.text(build_query({'error': ''}))

    await db.set_bind(f"postgresql://{config['database']['Username']}:{config['database']['Password']}@{config['database']['Address']}/{config['database']['Name']}")

    user_count = await username_count(username[0])
    if user_count:
        i = 0
        username = re.sub(r'\d+$', '', username[0])
        while True:
            i += 1
            suggestion = username + str(i)
            if sum(char.isdigit() for char in username) > 1:
                return response.text(build_query({'error': localization[lang]['name_taken']}))
            if not await username_count(suggestion.lower()):
                break
        return response.text(
            build_query({'error': localization[lang]['name_suggest'].replace('[suggestion]', suggestion)}))

    username = username[0]
    global session
    session = {'sid': secrets.token_urlsafe(16),
               'username': username[0].lower() + username[1:] if config['ForcedCase'] else username, 'color': color}
    return response.text(build_query({'success': 1, "sid": session['sid']}))


async def validate_password_email(request, response, lang):
    session_id = attempt_data_retrieval("sid", True)
    username = attempt_data_retrieval("username", True)
    color = attempt_data_retrieval("color", True)
    password = attempt_data_retrieval('password')
    password_confirm = attempt_data_retrieval('password_confirm')
    email = attempt_data_retrieval('email')
    if config['SecretKey']:
        g_token = attempt_data_retrieval('gtoken')[0]
        ip = request.headers.get('cf-connecting-ip') if config['CloudFlare'] else request.headers.get(
            'x-forwarded-for')
        url = f"https://www.google.com/recaptcha/api/siteverify?secret={config['SecretKey']}&response={g_token}&remoteip={ip}"
        result = urllib.request.urlopen(url)
        captcha = json.loads(result.read().decode('utf-8'))

    if session_id != session['sid']:
        return response.text(build_query({'error': localization[lang]['passwords_match']}))

    elif not captcha['success'] and config['SecretKey']:
        return response.text(build_query({'error': ''}))

    elif str(password[0]) != str(password_confirm[0]):
        return response.text(build_query({'error': localization[lang]['passwords_match']}))

    elif len(password[0]) < 4:
        return response.text(build_query({'error': localization[lang]['password_short']}))

    elif not email:
        return response.text(build_query({'error': localization[lang]['email_invalid']}))

    elif not config['email_regex'].match(email[0]):
        return response.text(build_query({'error': localization[lang]['email_invalid']}))

    elif email[0].split('@')[1] not in str(config['EmailWhiteList']) and not isinstance(config['EmailWhiteList'], str):
        return response.text(build_query({'error': localization[lang]['email_invalid']}))

    elif await email_count(email[0]):
        return response.text(build_query({'error': localization[lang]['email_invalid']}))

    approve = False if config['Approve'] else True
    activate = False if config['Activate'] else True
    password = generate_bcrypt(password[0]).decode('UTF-8')
    await Penguin.create(username=username, nickname=username, password=password, approval_en=approve,
                         approval_pt=approve, approval_fr=approve, approval_es=approve,
                         approval_de=approve, approval_ru=approve, email=email[0], active=activate, color=int(color))

    data = await Penguin.query.where(Penguin.username == username).gino.first()
    await PenguinItem.create(penguin_id=data.id, item_id=int(color))
    await PenguinPostcard.create(penguin_id=data.id, sender_id=None, postcard_id=125)

    if config['Activate']:
        activation_key = secrets.token_urlsafe(45)
        link = f"{config['External']}/activation/{activation_key}"
        message = Mail(
            from_email=f"noreply@{config['Hostname']}",
            to_emails=email[0],
            subject='Activate your penguin!',
            html_content=f"<p>Hello,</p> <p>Thank you for creating a penguin on {config['Hostname']}. Please click below to activate your penguin account.</p> <a href='{link}'>Activate</a>"
        )
        sg = SendGridAPIClient(f"{config['SendGridAPIKey']}")
        sg.send(message)
        await ActivationKey.create(penguin_id=data.id, activation_key=activation_key)

    return response.text(build_query({'success': 1}))


def generate_random_key():
    _alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(_alphabet) for _ in range(16))


async def username_count(value):
    user_count = await db.select([db.func.count(Penguin.username)]).where(
        db.func.lower(Penguin.username) == value.lower()).gino.scalar()
    return user_count >= 1


async def id_count(value):
    user_count = await db.select([db.func.count(Penguin.id)]).where(Penguin.id == value).gino.scalar()
    return user_count >= 1


async def email_count(value):
    email_count = await db.select([db.func.count(Penguin.email)]).where(
        db.func.lower(Penguin.email) == value.lower()).gino.scalar()
    return email_count >= config['MaxPerEmail']


def hash(undigested):
    if type(undigested) == str:
        undigested = undigested.encode('utf-8')
    return hashlib.md5(undigested).hexdigest()


def encrypt_password(password, digest=True):
    if digest:
        password = hash(password)

    swapped_hash = password[16:32] + password[0:16]
    return swapped_hash


def generate_bcrypt(password):
    password = hashlib.md5(password.encode('utf-8')).hexdigest().upper()
    key = encrypt_password(password, False)
    key += 'houdini'
    key += 'Y(02.>\'H}t":E1'
    hash = encrypt_password(key)
    return bcrypt.hashpw(hash.encode('utf-8'), bcrypt.gensalt(12))


def attempt_data_retrieval(key, session_retrieval=False):
    if not session_retrieval and key in post_data.keys():
        return post_data[key]

    if session_retrieval and key in session.keys():
        return session[key]


def build_query(data):
    return urllib.parse.urlencode(data)


localization = {
        'en': {
                "terms": "You must agree to the Rules and Terms of Use.",
                "name_missing": "You need to name your penguin.",
                "name_short": "Penguin name is too short.",
                "name_number": "Penguin names can only contain 5 numbers.",
                "penguin_letter": "Penguin names must contain at least 1 letter.",
                "name_not_allowed": "That penguin name is not allowed.",
                "name_taken": "That penguin name is already taken.",
                "name_suggest": "That penguin name is already taken. Try [suggestion].",
                "passwords_match": "Passwords do not match.",
                "password_short": "Password is too short.",
                "email_invalid": "Invalid email address."
        },

        'fr': {
                "terms": "Tu dois accepter les conditions d'utilisation.",
                "name_missing": "Tu dois donner un nom à ton pingouin.",
                "name_short": "Le nom de pingouin est trop court.",
                "name_number": "Un nom de pingouin ne peut contenir plus de 5 nombres.",
                "penguin_letter": "Un nom de pingouin doit contenir au moins une lettre.",
                "name_not_allowed": "Ce nom de pingouing n'est pas autorisé.",
                "name_taken": "Ce nom de pingouin est pris.",
                "name_suggest": "Ce nom de pingouin est pris. Essaye [suggestion].",
                "passwords_match": "Les mots de passes ne correspondent pas.",
                "password_short": "Le mot de passe est trop court.",
                "email_invalid": "Adresse email invalide."
        },

        'es': {
                "terms": "Debes seguir las reglas y los términos de uso.",
                "name_missing": "Debes escoger un nombre para tu pingüino.",
                "name_short": "El nombre de tu pingüino es muy corto.",
                "name_number": "Los nombres de usuario sólo pueden tener 5 números.",
                "penguin_letter": "Los nombres de usuario deben tener por lo menos 1 letra.",
                "name_not_allowed": "Ese nombre de usuario no está permitido.",
                "name_taken": "Ese nombre de usuario ya ha sido escogido.",
                "name_suggest": "Ese nombre de usuario ya ha sido escogido. Intenta éste [suggestion].",
                "passwords_match": "Las contraseñas no coinciden.",
                "password_short": "La contraseña es muy corta.",
                "email_invalid": "El correo eléctronico es incorrecto."
        },

        'pt': {
                "terms": "Você precisa concordar com as Regras e com os Termos de Uso.",
                "name_missing": "Você precisa nomear seu pinguim.",
                "name_short": "O nome do pinguim é muito curto.",
                "name_number": "O nome do pinguim só pode conter 5 números",
                "penguin_letter": "O nome do seu pinguim tem de conter pelo menos uma letra.",
                "name_not_allowed": "Esse nome de pinguim não é permitido.",
                "name_taken": "Esse nome de pinguim já foi escolhido.",
                "name_suggest": "Esse nome de pinguim já foi escolhido. Tente [suggestion].",
                "passwords_match": "As senhas não correspondem.",
                "password_short": "A senha é muito curta.",
                "email_invalid": "Esse endereço de E-Mail é invalido."
        }
}


app.run(host='127.0.0.1', port=config['port'])

