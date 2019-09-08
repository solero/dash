import re

config = {
    'allowed_chars': re.compile(r"^[^<>\W/{}[\]~`]*$"),
    'email_regex': re.compile(r"[^@]+@[^@]+\.[^@]+"),
    'port': 3000,
    'database': {
        'Address': 'localhost',
        'Username': 'postgres',
        'Password': 'password',
        'Name': 'houdini'
    },
    'ForcedCase': True,
    'CloudFlare': False,
    'SecretKey': '6Lc-NbcUAAAAAAwk7mJ3p_B66ov7y-MXdiP7vQ8u',
    # 'EmailWhiteList': ["gmail.com", "hotmail.com"],
    # 'EmailWhiteList': '/path/to/whitelist',
    'EmailWhiteList': '',
    'MaxPerEmail': 5,
    'Activate': False,
    'Approve': False
}