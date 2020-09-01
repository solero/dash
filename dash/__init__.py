from jinja2 import Environment, FileSystemLoader, select_autoescape
from sanic import Sanic
from sanic_session import InMemorySessionInterface, Session

app = Sanic(name='Dash')
session = Session(app, interface=InMemorySessionInterface())

env = Environment(
    loader=FileSystemLoader('dash/templates'),
    autoescape=select_autoescape(['html', 'xml'])
)
