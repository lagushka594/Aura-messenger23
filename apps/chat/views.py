from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, OuterRef, Subquery, F
from django.http import Http404, JsonResponse
from django.utils import timezone
from .models import Conversation, Message, Server, Channel, ConversationParticipant, Invite
from apps.users.models import User
from .forms import CreateGroupForm, CreatePrivateChatForm
import secrets

@login_required
def index(request):
    # Показываем все чаты, в которых участвует пользователь (без фильтра по deleted)
    conversations = Conversation.objects.filter(
        participants=request.user
    ).annotate(
        last_msg_content=Subquery(
            Message.objects.filter(conversation=OuterRef('pk')).order_by('-timestamp').values('content')[:1]
        )
    ).order_by(
        F('last_message__timestamp').desc(nulls_last=True)
    ).select_related('last_message')
    
    return render(request, 'chat/index.html', {'conversations': conversations})

@login_required
def room(request, conversation_id):
    try:
        conversation = Conversation.objects.get(id=conversation_id, participants=request.user)
    except Conversation.DoesNotExist:
        try:
            other_user = User.objects.get(id=conversation_id)
            if other_user == request.user:
                messages.error(request, 'Нельзя открыть чат с самим собой')
                return redirect('chat:index')
            conversation, created = Conversation.objects.get_or_create_private(request.user, other_user)
            return redirect('chat:room', conversation_id=conversation.id)
        except User.DoesNotExist:
            raise Http404("Чат не найден")
    
    Message.objects.filter(conversation=conversation).exclude(sender=request.user).update(is_read=True)
    messages_list = Message.objects.filter(conversation=conversation).select_related('sender').order_by('timestamp')
    participant = ConversationParticipant.objects.get(user=request.user, conversation=conversation)
    is_admin = participant.is_admin or conversation.type == 'private'
    
    invites = None
    if conversation.type == 'group' and is_admin:
        invites = conversation.invites.all()
    
    return render(request, 'chat/room.html', {
        'conversation': conversation,
        'messages': messages_list,
        'is_admin': is_admin,
        'invites': invites,
        'participant': participant,
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

# --- Действия с чатами (удалено) ---
# Функция delete_chat удалена, так как кнопка удаления больше не нужна

# --- Приглашения ---

@login_required
def create_invite(request, conversation_id):
    conversation = get_object_or_404(Conversation, id=conversation_id, type='group')
    participant = get_object_or_404(ConversationParticipant, user=request.user, conversation=conversation)
    if not participant.is_admin:
        messages.error(request, 'Только администраторы могут создавать приглашения')
        return redirect('chat:room', conversation_id=conversation.id)
    
    invite = Invite.objects.create(
        conversation=conversation,
        created_by=request.user,
        token=secrets.token_urlsafe(32)
    )
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'token': invite.token,
            'link': request.build_absolute_uri(f'/chat/join/{invite.token}/')
        })
    messages.success(request, 'Приглашение создано')
    return redirect('chat:room', conversation_id=conversation.id)

@login_required
def join_via_invite(request, token):
    invite = get_object_or_404(Invite, token=token)
    if invite.expires_at and invite.expires_at < timezone.now():
        messages.error(request, 'Срок действия приглашения истёк')
        return redirect('chat:index')
    if invite.max_uses and invite.uses >= invite.max_uses:
        messages.error(request, 'Приглашение уже использовано максимальное количество раз')
        return redirect('chat:index')
    
    if invite.conversation.participants.filter(id=request.user.id).exists():
        messages.info(request, 'Вы уже участник этого чата')
        return redirect('chat:room', conversation_id=invite.conversation.id)
    
    invite.conversation.participants.add(request.user)
    invite.uses += 1
    invite.save()
    messages.success(request, f'Вы присоединились к чату {invite.conversation.name}')
    return redirect('chat:room', conversation_id=invite.conversation.id)