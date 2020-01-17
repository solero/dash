from sanic import Sanic
from sanic_session import Session, InMemorySessionInterface
from jinja2 import Environment, PackageLoader, select_autoescape

app = Sanic(name='Dash')
session = Session(app, interface=InMemorySessionInterface())

env = Environment(
    loader=PackageLoader('dash', 'templates'),
    autoescape=select_autoescape(['html', 'xml'])
)
