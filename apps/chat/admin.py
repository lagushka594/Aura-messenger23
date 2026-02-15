from django.contrib import admin
from .models import Conversation, ConversationParticipant, Message, Server, ServerMember, Channel

class ConversationParticipantInline(admin.TabularInline):
    model = ConversationParticipant
    extra = 0

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('id', 'type', 'name', 'created_at', 'last_message')
    inlines = [ConversationParticipantInline]

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'conversation', 'sender', 'timestamp', 'is_read')
    list_filter = ('is_read', 'timestamp')

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