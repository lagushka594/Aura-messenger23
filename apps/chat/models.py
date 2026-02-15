from django.db import models
from django.conf import settings

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