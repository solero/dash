from urllib.parse import parse_qs
from sanic import response
from sanic import Blueprint
from dash import env, app
from dash.data.penguin import Penguin

import i18n

password = Blueprint('password', url_prefix='/password')


@password.get('/<lang>')
async def password_reset_page(request, lang):
    if lang == 'fr':
        template = env.get_template('password/fr.html')
        page = template.render(
            VANILLA_PLAY_LINK=app.config.VANILLA_PLAY_LINK,
        )
        return response.html(page)
    
    elif lang == 'es':
        template = env.get_template('password/es.html')
        page = template.render(
            VANILLA_PLAY_LINK=app.config.VANILLA_PLAY_LINK,
        )
        return response.html(page)
    
    elif lang == 'pt':
        template = env.get_template('password/pt.html')
        page = template.render(
            VANILLA_PLAY_LINK=app.config.VANILLA_PLAY_LINK,
        )
        return response.html(page)
    
    else:
        template = env.get_template('password/en.html')
        page = template.render(
            VANILLA_PLAY_LINK=app.config.VANILLA_PLAY_LINK,
        )
        return response.html(page)


@password.post('/<lang>')
async def password_reset(request, lang):
    query_string = request.body.decode('UTF-8')
    post_data = parse_qs(query_string)
    username = post_data.get('name', [None])[0]
    email = post_data.get('email', [None])[0]
    if not username or not email or '@' not in email:
        if not username:
            return response.json(
                _add_class('name', 'error'),
                headers={
                    'X-Drupal-Ajax-Token': 1
                }
            )
        else:
            return response.json(
                _remove_class('name', 'error'),
                headers={
                    'X-Drupal-Ajax-Token': 1
                }
            )
        if not email or '@' not in email:
            return response.json(
                _add_class('email', 'error'),
                headers={
                    'X-Drupal-Ajax-Token': 1
                }
            )
        else:
            return response.json(
                _remove_class('email', 'error'),
                headers={
                    'X-Drupal-Ajax-Token': 1
                }
            )
    else:
        player_data = await Penguin.query.where(
            Penguin.email == email
        ).gino.first()
        if player_data and player_data.username == username:
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

