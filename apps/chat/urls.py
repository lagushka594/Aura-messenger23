from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('', views.index, name='index'),
    path('room/<int:conversation_id>/', views.room, name='room'),
    path('server/<int:server_id>/', views.server_detail, name='server'),
    path('channel/<int:channel_id>/', views.channel_detail, name='channel'),
]