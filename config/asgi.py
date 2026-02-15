import os
import pymysql

# Эмулируем MySQLdb с помощью pymysql (до импорта Django)
pymysql.install_as_MySQLdb()

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Инициализируем Django ASGI application до импорта остальных модулей,
# чтобы гарантировать, что настройки загружены.
django_asgi_app = get_asgi_application()

# Теперь можно импортировать остальные модули, использующие Django
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