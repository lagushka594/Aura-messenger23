from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q, OuterRef, Subquery
from .models import Conversation, Message, Server, Channel
from apps.users.models import User

@login_required
def index(request):
    # Получаем все беседы, в которых участвует пользователь, с последним сообщением
    conversations = Conversation.objects.filter(participants=request.user).annotate(
        last_msg_content=Subquery(
            Message.objects.filter(conversation=OuterRef('pk')).order_by('-timestamp').values('content')[:1]
        )
    ).order_by('-last_message__timestamp')
    return render(request, 'chat/index.html', {'conversations': conversations})

@login_required
def room(request, conversation_id):
    conversation = get_object_or_404(Conversation, id=conversation_id, participants=request.user)
    messages = Message.objects.filter(conversation=conversation).select_related('sender').order_by('timestamp')
    # Помечаем сообщения как прочитанные (упрощённо)
    messages.filter(is_read=False).exclude(sender=request.user).update(is_read=True)
    return render(request, 'chat/room.html', {
        'conversation': conversation,
        'messages': messages,
    })

@login_required
def server_detail(request, server_id):
    server = get_object_or_404(Server, id=server_id, members=request.user)
    channels = server.channels.all().order_by('position')
    return render(request, 'chat/server.html', {'server': server, 'channels': channels})

@login_required
def channel_detail(request, channel_id):
    channel = get_object_or_404(Channel, id=channel_id, server__members=request.user)
    if channel.type == 'text':
        # Для текстового канала создаём отдельную беседу? 
        # В упрощённом варианте можно использовать Conversation, привязанный к каналу.
        # Для демо создадим связь: у каждого канала может быть связанная беседа.
        # Упростим: пока не реализуем, просто заглушка.
        return render(request, 'chat/channel.html', {'channel': channel})
    else:
        # Голосовой канал — просто информация
        return render(request, 'chat/voice_channel.html', {'channel': channel})

# Дополнительные view для создания чатов, серверов и т.д. (можно добавить позже)