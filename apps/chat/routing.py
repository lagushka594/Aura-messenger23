from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<conversation_id>\d+)/$', consumers.ChatConsumer.as_asgi()),
    re_path(r'ws/voice/(?P<voice_room_id>\d+)/$', consumers.VoiceConsumer.as_asgi()),
]