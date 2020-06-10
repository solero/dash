from sanic import Blueprint
from .login import login
from .panel import panel
from .static import static

manager = Blueprint.group(
    panel,
    login,
    static,
    url_prefix='/manager'
)







