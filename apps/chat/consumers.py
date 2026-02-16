import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import Conversation, Message

logger = logging.getLogger(__name__)

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        if self.user.is_anonymous:
            logger.warning("Anonymous user tried to connect")
            await self.close()
        else:
            self.conversation_id = self.scope['url_route']['kwargs']['conversation_id']
            self.room_group_name = f'chat_{self.conversation_id}'
            if await self.is_participant():
                await self.channel_layer.group_add(self.room_group_name, self.channel_name)
                await self.accept()
                logger.info(f"User {self.user.id} connected to chat {self.conversation_id}")
            else:
                logger.warning(f"User {self.user.id} not participant of chat {self.conversation_id}")
                await self.close()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        logger.info(f"User {self.user.id} disconnected from chat {self.conversation_id}")

    async def receive(self, text_data):
        logger.info(f"Received message: {text_data}")
        data = json.loads(text_data)
        if data['type'] == 'message':
            content = data['content']
            message = await self.save_message(content)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'id': message.id,
                    'sender_id': self.user.id,
                    'sender_name': self.user.get_display_name(),
                    'sender_avatar': self.user.avatar.url if self.user.avatar else None,
                    'content': content,
                    'timestamp': message.timestamp.isoformat(),
                }
            )
            logger.info(f"Message sent to group {self.room_group_name}")

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))
        logger.info(f"Message forwarded to client: {event['id']}")

    @database_sync_to_async
    def is_participant(self):
        return Conversation.objects.filter(
            id=self.conversation_id,
            participants=self.user
        ).exists()

    @database_sync_to_async
    def save_message(self, content):
        conv = Conversation.objects.get(id=self.conversation_id)
        msg = Message.objects.create(
            conversation=conv,
            sender=self.user,
            content=content
        )
        conv.last_message = msg
        conv.save()
        return msg