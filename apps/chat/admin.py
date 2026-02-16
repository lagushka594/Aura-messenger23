from django.contrib import admin
from .models import Conversation, ConversationParticipant, Message, FileMessage, StickerPack, Sticker, Invite, VoiceRoom, Bot, BotCommand, BotParticipant, Server, ServerMember, Channel

class ConversationParticipantInline(admin.TabularInline):
    model = ConversationParticipant
    extra = 0

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('id', 'type', 'name', 'created_at', 'last_message')
    inlines = [ConversationParticipantInline]

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'conversation', 'sender', 'timestamp', 'is_read', 'deleted')
    list_filter = ('is_read', 'deleted')

@admin.register(FileMessage)
class FileMessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'message', 'filename', 'file_size')

@admin.register(StickerPack)
class StickerPackAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'created_at', 'is_official')

@admin.register(Sticker)
class StickerAdmin(admin.ModelAdmin):
    list_display = ('id', 'pack', 'emoji')

@admin.register(Invite)
class InviteAdmin(admin.ModelAdmin):
    list_display = ('id', 'conversation', 'created_by', 'token', 'uses')

@admin.register(VoiceRoom)
class VoiceRoomAdmin(admin.ModelAdmin):
    list_display = ('id', 'conversation', 'name', 'is_active')

@admin.register(Bot)
class BotAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'is_active')

@admin.register(BotCommand)
class BotCommandAdmin(admin.ModelAdmin):
    list_display = ('bot', 'command', 'response')

@admin.register(BotParticipant)
class BotParticipantAdmin(admin.ModelAdmin):
    list_display = ('bot', 'conversation', 'added_by', 'joined_at')

@admin.register(Server)
class ServerAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'created_at')
    filter_horizontal = ('members',)

@admin.register(Channel)
class ChannelAdmin(admin.ModelAdmin):
    list_display = ('name', 'server', 'type', 'position')
    list_filter = ('type',)

admin.site.register(ServerMember)
admin.site.register(ConversationParticipant)