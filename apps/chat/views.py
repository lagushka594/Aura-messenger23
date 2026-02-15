from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, OuterRef, Subquery
from django.http import Http404
from .models import Conversation, Message, Server, Channel
from apps.users.models import User
from .forms import CreateGroupForm, CreatePrivateChatForm

@login_required
def index(request):
    conversations = Conversation.objects.filter(participants=request.user).annotate(
        last_msg_content=Subquery(
            Message.objects.filter(conversation=OuterRef('pk')).order_by('-timestamp').values('content')[:1]
        )
    ).order_by('-last_message__timestamp')
    return render(request, 'chat/index.html', {'conversations': conversations})

@login_required
def room(request, conversation_id):
    # Проверяем, может conversation_id на самом деле является user_id?
    try:
        conversation = Conversation.objects.get(id=conversation_id, participants=request.user)
    except Conversation.DoesNotExist:
        # Возможно, это user_id? Попробуем найти или создать приватный чат с этим пользователем
        try:
            other_user = User.objects.get(id=conversation_id)
            if other_user == request.user:
                messages.error(request, 'Нельзя открыть чат с самим собой')
                return redirect('chat:index')
            conversation, created = Conversation.objects.get_or_create_private(request.user, other_user)
            return redirect('chat:room', conversation_id=conversation.id)
        except User.DoesNotExist:
            raise Http404("Чат не найден")
    messages_list = Message.objects.filter(conversation=conversation).select_related('sender').order_by('timestamp')
    messages_list.filter(is_read=False).exclude(sender=request.user).update(is_read=True)
    return render(request, 'chat/room.html', {
        'conversation': conversation,
        'messages': messages_list,
    })

@login_required
def server_detail(request, server_id):
    server = get_object_or_404(Server, id=server_id, members=request.user)
    channels = server.channels.all().order_by('position')
    return render(request, 'chat/server.html', {'server': server, 'channels': channels})

@login_required
def channel_detail(request, channel_id):
    channel = get_object_or_404(Channel, id=channel_id, server__members=request.user)
    return render(request, 'chat/channel.html', {'channel': channel})

# --- Создание чатов ---

@login_required
def create_chat(request):
    """Меню выбора типа чата."""
    return render(request, 'chat/create_chat_menu.html')

@login_required
def create_group(request):
    if request.method == 'POST':
        form = CreateGroupForm(request.POST, request.FILES)
        if form.is_valid():
            group = form.save(commit=False)
            group.type = 'group'
            group.save()
            group.participants.add(request.user, through_defaults={'is_admin': True})
            messages.success(request, 'Группа создана')
            return redirect('chat:room', conversation_id=group.id)
    else:
        form = CreateGroupForm()
    return render(request, 'chat/create_group.html', {'form': form})

@login_required
def create_private_chat(request):
    if request.method == 'POST':
        form = CreatePrivateChatForm(request.POST)
        if form.is_valid():
            friend_id = form.cleaned_data['friend_id']
            try:
                username, discriminator = friend_id.split('#')
                friend = User.objects.get(username=username, discriminator=discriminator)
            except (ValueError, User.DoesNotExist):
                messages.error(request, 'Пользователь с таким ID не найден')
                return redirect('chat:create_private_chat')
            if friend == request.user:
                messages.error(request, 'Нельзя создать чат с самим собой')
                return redirect('chat:create_private_chat')
            conv, created = Conversation.objects.get_or_create_private(request.user, friend)
            if created:
                messages.success(request, 'Чат создан')
            else:
                messages.info(request, 'Чат уже существует')
            return redirect('chat:room', conversation_id=conv.id)
    else:
        form = CreatePrivateChatForm()
    return render(request, 'chat/create_private_chat.html', {'form': form})