import re

config = {
    'allowed_chars': re.compile(r"^[^<>\W/{}[\]~`]*$"),
    'email_regex': re.compile(r"[^@]+@[^@]+\.[^@]+"),
    'port': 3000,
    'database': {
        'host': 'localhost',
        'username': 'postgres',
        'password': 'password',
        'name': 'houdini'
    },
    'forced_case': True,
    'cloudflare': False,
    'secret_key': '',
    # 'email_white_list': ["gmail.com", "hotmail.com"],
    # 'email_white_list': '/path/to/whitelist',
    'email_white_list': '',
    'max_per_email': 5,
    'activate': False,
    'approve': False,
    'sendgrid_api_key': '',
    'hostname': 'houdi.ni',
    'external': 'http://play.houdi.ni'
}