from urllib.parse import parse_qs
from sanic import Sanic, response

import re
import urllib.parse

config = {
    'allowed_chars': re.compile(r"^[^<>/{}[\]~`]*$"),
    'port': 3000
}

app = Sanic()
@app.route('/', methods=["POST"])
def register(request):
    query_string = request.body.decode('UTF-8')
    global post_data
    post_data = parse_qs(query_string)
    action = attempt_data_retrieval('action')[0]
    lang = attempt_data_retrieval('lang')[0]
    if action == 'validate_agreement':
        agree_terms = int(attempt_data_retrieval('agree_to_terms')[0])
        agree_rules = int(attempt_data_retrieval('agree_to_rules')[0])
        if not agree_terms or not agree_rules:
            return response.text(build_query({'error': localization[lang]['terms']}))
        return response.text(build_query({'success': 1}))
    elif action == 'validate_username':
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

        elif not config['allowed_chars'].match(username[0]):
            return response.text(build_query({'error': localization[lang]['name_not_allowed']}))

        elif not color.isdigit() or int(color) not in range(1, 15):
            return response.text(build_query({'error': ''}))


def attempt_data_retrieval(key):
    if key in post_data.keys():
        return post_data[key]


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

