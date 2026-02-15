from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('', views.index, name='index'),
    path('room/<int:conversation_id>/', views.room, name='room'),
    path('server/<int:server_id>/', views.server_detail, name='server'),
    path('channel/<int:channel_id>/', views.channel_detail, name='channel'),
    # Создание чатов
    path('create/', views.create_chat, name='create_chat'),
    path('create/group/', views.create_group, name='create_group'),
    path('create/private/', views.create_private_chat, name='create_private_chat'),
]