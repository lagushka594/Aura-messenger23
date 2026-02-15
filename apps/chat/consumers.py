import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import Conversation, Message

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        if self.user.is_anonymous:
            await self.close()
        else:
            self.conversation_id = self.scope['url_route']['kwargs']['conversation_id']
            self.room_group_name = f'chat_{self.conversation_id}'
            if await self.is_participant():
                await self.channel_layer.group_add(self.room_group_name, self.channel_name)
                await self.accept()
            else:
                await self.close()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        if data['type'] == 'message':
            content = data['content']
            message = await self.save_message(content)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message_id': message.id,
                    'sender_id': self.user.id,
                    'sender_name': self.user.get_display_name(),
                    'content': content,
                    'timestamp': str(message.timestamp),
                }
            )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))

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