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
    async def connect(self):
        self.user = self.scope['user']
        self.conversation_id = self.scope['url_route']['kwargs']['conversation_id']
        self.room_group_name = f'chat_{self.conversation_id}'

        logger.info(f"WebSocket connect attempt: user={self.user.id if not self.user.is_anonymous else 'anonymous'}, conversation_id={self.conversation_id}")

        if self.user.is_anonymous:
            logger.warning("Anonymous user rejected")
            await self.close(code=4001)
            return

        try:
            if not await self.is_participant():
                logger.warning(f"User {self.user.id} not participant of chat {self.conversation_id}")
                await self.close(code=4003)
                return

            await self.channel_layer.group_add(self.room_group_name, self.channel_name)
            await self.accept()
            logger.info(f"User {self.user.id} connected to chat {self.conversation_id}")
        except Exception as e:
            logger.error(f"Error in connect: {e}\n{traceback.format_exc()}")
            await self.close(code=1011)

    async def disconnect(self, close_code):
        logger.info(f"User {self.user.id if hasattr(self, 'user') else 'unknown'} disconnected from chat {getattr(self, 'conversation_id', 'unknown')} with code {close_code}")
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        logger.info(f"Received message: {text_data}")
        try:
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
        except Exception as e:
            logger.error(f"Error in receive: {e}\n{traceback.format_exc()}")

    async def chat_message(self, event):
        try:
            await self.send(text_data=json.dumps(event))
            logger.info(f"Message forwarded to client: {event['id']}")
        except Exception as e:
            logger.error(f"Error in chat_message: {e}")

    async def edit_message(self, event):
        try:
            await self.send(text_data=json.dumps({
                'type': 'edit_message',
                'id': event['id'],
                'content': event['content'],
                'edited_at': event['edited_at'],
            }))
        except Exception as e:
            logger.error(f"Error in edit_message: {e}")

    async def delete_message(self, event):
        try:
            await self.send(text_data=json.dumps({
                'type': 'delete_message',
                'id': event['id'],
            }))
        except Exception as e:
            logger.error(f"Error in delete_message: {e}")

    async def pin_message(self, event):
        try:
            await self.send(text_data=json.dumps({
                'type': 'pin_message',
                'message_id': event['message_id'],
                'content': event['content'],
            }))
        except Exception as e:
            logger.error(f"Error in pin_message: {e}")

    async def unpin_message(self, event):
        try:
            await self.send(text_data=json.dumps({
                'type': 'unpin_message',
            }))
        except Exception as e:
            logger.error(f"Error in unpin_message: {e}")

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


class VoiceConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        self.voice_room_id = self.scope['url_route']['kwargs']['voice_room_id']
        self.room_group_name = f'voice_{self.voice_room_id}'

        if self.user.is_anonymous:
            await self.close()
            return

        self.voice_room = await self.get_voice_room()
        if not self.voice_room:
            await self.close()
            return

        if not await self.user_in_room():
            await self.close()
            return

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()
        logger.info(f"User {self.user.id} connected to voice room {self.voice_room_id}")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        if data['type'] in ['offer', 'answer', 'candidate']:
            data['sender_id'] = self.user.id
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'voice_signal',
                    'data': data,
                }
            )

    async def voice_signal(self, event):
        if event['data']['sender_id'] != self.user.id:
            await self.send(text_data=json.dumps(event['data']))

    async def user_joined(self, event):
        await self.send(text_data=json.dumps({
            'type': 'user_joined',
            'user_id': event['user_id'],
            'username': event['username'],
        }))

    async def user_left(self, event):
        await self.send(text_data=json.dumps({
            'type': 'user_left',
            'user_id': event['user_id'],
        }))

    @database_sync_to_async
    def get_voice_room(self):
        try:
            return VoiceRoom.objects.get(id=self.voice_room_id)
        except VoiceRoom.DoesNotExist:
            return None

    @database_sync_to_async
    def user_in_room(self):
        return self.user in self.voice_room.active_users.all()