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
        ('favorite', 'Избранное'),
    ]
    type = models.CharField(max_length=10, choices=CONV_TYPE)
    name = models.CharField(max_length=100, blank=True, null=True)
    avatar = models.ImageField(upload_to='chat_avatars/', blank=True, null=True)
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, through='ConversationParticipant')
    created_at = models.DateTimeField(auto_now_add=True)
    last_message = models.ForeignKey('Message', on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='owned_chats')

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
    content = models.TextField(blank=True)  # может быть пустым для стикеров
    sticker = models.ForeignKey('Sticker', on_delete=models.SET_NULL, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    edited_at = models.DateTimeField(null=True, blank=True)
    is_read = models.BooleanField(default=False)
    deleted = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.sender}: {self.content[:20] if self.content else "Стикер"}'

class FileMessage(models.Model):
    message = models.OneToOneField(Message, on_delete=models.CASCADE, related_name='file')
    file = models.FileField(upload_to='chat_files/%Y/%m/%d/')
    filename = models.CharField(max_length=255)
    file_size = models.IntegerField()
    file_type = models.CharField(max_length=100, blank=True)

class StickerPack(models.Model):
    name = models.CharField(max_length=100)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_official = models.BooleanField(default=False)
    cover = models.ImageField(upload_to='sticker_packs/', blank=True, null=True)

    def __str__(self):
        return self.name

class Sticker(models.Model):
    pack = models.ForeignKey(StickerPack, on_delete=models.CASCADE, related_name='stickers')
    image = models.ImageField(upload_to='stickers/')
    emoji = models.CharField(max_length=10, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Sticker {self.id} from {self.pack.name}'

class Invite(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='invites')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    token = models.CharField(max_length=64, unique=True, default=secrets.token_urlsafe)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    max_uses = models.IntegerField(default=0)
    uses = models.IntegerField(default=0)

    def __str__(self):
        return f'Invite to {self.conversation.name} by {self.created_by.username}'

class VoiceRoom(models.Model):
    conversation = models.OneToOneField(Conversation, on_delete=models.CASCADE, related_name='voice_room')
    name = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    active_users = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='active_voice_rooms')
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return f'Voice room for {self.conversation.name}'

class Bot(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bots')
    name = models.CharField(max_length=100)
    token = models.CharField(max_length=64, unique=True, default=secrets.token_urlsafe)
    webhook_url = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class BotCommand(models.Model):
    bot = models.ForeignKey(Bot, on_delete=models.CASCADE, related_name='commands')
    command = models.CharField(max_length=50)
    response = models.TextField()

class BotParticipant(models.Model):
    bot = models.ForeignKey(Bot, on_delete=models.CASCADE)
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE)
    added_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('bot', 'conversation')

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