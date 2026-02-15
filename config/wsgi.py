import os
import pymysql

# Эмулируем MySQLdb с помощью pymysql (до импорта Django)
pymysql.install_as_MySQLdb()

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

application = get_wsgi_application()