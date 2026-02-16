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
    # Избранное
    path('favorite/', views.favorite_chat, name='favorite'),
    # Приглашения
    path('invite/<int:conversation_id>/', views.create_invite, name='create_invite'),
    path('join/<str:token>/', views.join_via_invite, name='join_via_invite'),
    # Загрузка файлов
    path('upload/<int:conversation_id>/', views.upload_file, name='upload_file'),
    # Редактирование канала
    path('edit/<int:conversation_id>/', views.edit_channel, name='edit_channel'),
    # Голосовые комнаты
    path('voice/<int:conversation_id>/', views.voice_room, name='voice_room'),
    path('voice/join/<int:voice_room_id>/', views.join_voice, name='join_voice'),
    path('voice/leave/<int:voice_room_id>/', views.leave_voice, name='leave_voice'),
    # Стикеры
    path('stickers/', views.sticker_packs, name='sticker_packs'),
    path('send_sticker/<int:conversation_id>/<int:sticker_id>/', views.send_sticker, name='send_sticker'),
    # Редактирование/удаление сообщений
    path('edit_message/<int:message_id>/', views.edit_message, name='edit_message'),
    path('delete_message/<int:message_id>/', views.delete_message, name='delete_message'),
    # Боты
    path('bots/', views.bot_list, name='bot_list'),
]