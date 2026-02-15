import os
import pymysql
pymysql.install_as_MySQLdb()

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

django_asgi_app = get_asgi_application()

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from apps.users import routing as users_routing
from apps.chat import routing as chat_routing

application = ProtocolTypeRouter({
    'http': django_asgi_app,
    'websocket': AuthMiddlewareStack(
        URLRouter(
            users_routing.websocket_urlpatterns +
            chat_routing.websocket_urlpatterns
        )
    ),
})