import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.db import models
from .models import Friendship

logger = logging.getLogger(__name__)
User = get_user_model()

class StatusConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        if self.user.is_anonymous:
            logger.warning("Anonymous user rejected from status socket")
            await self.close(code=4001)
        else:
            self.user_group_name = f'user_{self.user.id}'
            await self.channel_layer.group_add(self.user_group_name, self.channel_name)

            # Устанавливаем статус онлайн, если не невидимка
            if self.user.manual_status != 'invisible':
                await self.set_online_status(True)
            await self.accept()
            logger.info(f"User {self.user.id} connected to status socket")

    async def disconnect(self, close_code):
        if hasattr(self, 'user') and not self.user.is_anonymous:
            await self.set_online_status(False)
            await self.channel_layer.group_discard(self.user_group_name, self.channel_name)
            logger.info(f"User {self.user.id} disconnected from status socket, code {close_code}")

    async def receive(self, text_data):
        data = json.loads(text_data)
        if data['type'] == 'status_change':
            new_status = data['status']
            self.user.manual_status = new_status
            await database_sync_to_async(self.user.save)()
            if new_status != 'invisible':
                await self.broadcast_status_to_friends(new_status)
            logger.info(f"User {self.user.id} changed status to {new_status}")

    async def set_online_status(self, is_online):
        status = 'online' if is_online else 'offline'
        await self.broadcast_status_to_friends(status)

    async def broadcast_status_to_friends(self, status):
        friends = await self.get_friends()
        for friend in friends:
            await self.channel_layer.group_send(
                f'user_{friend.id}',
                {
                    'type': 'friend_status',
                    'user_id': self.user.id,
                    'status': status,
                }
            )

    @database_sync_to_async
    def get_friends(self):
        friendships = Friendship.objects.filter(
            (models.Q(from_user=self.user) | models.Q(to_user=self.user)),
            status='accepted'
        ).select_related('from_user', 'to_user')
        friends = []
        for fs in friendships:
            if fs.from_user == self.user:
                friends.append(fs.to_user)
            else:
                friends.append(fs.from_user)
        return friends

    async def friend_status(self, event):
        await self.send(text_data=json.dumps({
            'type': 'friend_status',
            'user_id': event['user_id'],
            'status': event['status'],
        }))