from django.db import models
from django.conf import settings
import secrets

class ConversationManager(models.Manager):
    def get_or_create_private(self, user1, user2):
        qs = self.filter(type='private', participants=user1).filter(participants=user2)
        if qs.exists():
            return qs.first(), False
        conv = self.create(type='private')
        conv.participants.add(user1, user2)
        return conv, True

class Conversation(models.Model):
    CONV_TYPE = [
        ('private', 'Личный'),
        ('group', 'Групповой'),
    ]
    type = models.CharField(max_length=10, choices=CONV_TYPE)
    name = models.CharField(max_length=100, blank=True, null=True)
    avatar = models.ImageField(upload_to='chat_avatars/', blank=True, null=True)
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, through='ConversationParticipant')
    created_at = models.DateTimeField(auto_now_add=True)
    last_message = models.ForeignKey('Message', on_delete=models.SET_NULL, null=True, blank=True, related_name='+')

    objects = ConversationManager()

    def __str__(self):
        if self.type == 'private':
            return f'Private chat {self.id}'
        return self.name or f'Group {self.id}'

class ConversationParticipant(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)
    last_read = models.DateTimeField(null=True, blank=True)
    is_admin = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'conversation')

class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.sender}: {self.content[:20]}'

class Invite(models.Model):
    """Приглашение в чат (для групп)"""
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='invites')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    token = models.CharField(max_length=64, unique=True, default=secrets.token_urlsafe)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    max_uses = models.IntegerField(default=0)
    uses = models.IntegerField(default=0)

    def __str__(self):
        return f'Invite to {self.conversation.name} by {self.created_by.username}'

class Server(models.Model):
    name = models.CharField(max_length=100)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='owned_servers')
    avatar = models.ImageField(upload_to='server_avatars/', blank=True, null=True)
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, through='ServerMember')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class ServerMember(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    server = models.ForeignKey(Server, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)
    role = models.CharField(max_length=50, default='member')

    class Meta:
        unique_together = ('user', 'server')

class Channel(models.Model):
    CHANNEL_TYPES = [
        ('text', 'Текстовый'),
        ('voice', 'Голосовой'),
    ]
    server = models.ForeignKey(Server, on_delete=models.CASCADE, related_name='channels')
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=10, choices=CHANNEL_TYPES, default='text')
    position = models.IntegerField(default=0)

    def __str__(self):
        return f'{self.server.name} - {self.name}'