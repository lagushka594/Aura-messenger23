import json
import logging
import traceback
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import Conversation, Message, VoiceRoom

logger = logging.getLogger(__name__)

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    # ... (остаётся как было, см. предыдущие ответы)

class VoiceConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        self.voice_room_id = self.scope['url_route']['kwargs']['voice_room_id']
        self.room_group_name = f'voice_{self.voice_room_id}'

        if self.user.is_anonymous:
            await self.close()
            return

        # Проверяем, что пользователь в голосовой комнате
        self.voice_room = await self.get_voice_room()
        if not self.voice_room or self.user not in self.voice_room.active_users.all():
            await self.close()
            return

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()
        logger.info(f"User {self.user.id} connected to voice room {self.voice_room_id}")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        # Сигнализация WebRTC: пересылаем SDP и ICE кандидаты всем остальным в комнате
        if data['type'] in ['offer', 'answer', 'candidate']:
            # Добавляем отправителя
            data['sender_id'] = self.user.id
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'voice_signal',
                    'data': data,
                }
            )

    async def voice_signal(self, event):
        # Исключаем отправку самому себе (по желанию)
        if event['data']['sender_id'] != self.user.id:
            await self.send(text_data=json.dumps(event['data']))

    @database_sync_to_async
    def get_voice_room(self):
        try:
            return VoiceRoom.objects.get(id=self.voice_room_id)
        except VoiceRoom.DoesNotExist:
            return None