from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, OuterRef, Subquery, F, Count
from django.http import Http404, JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from .models import Conversation, Message, Server, Channel, ConversationParticipant, Invite, FileMessage, VoiceRoom, StickerPack, Sticker, PinnedMessage
from apps.users.models import User
from .forms import CreateGroupForm, CreatePrivateChatForm, EditChannelForm
import secrets
import os

@login_required
def index(request):
    # Аннотация непрочитанных сообщений и закрепления чата
    unread_subquery = Message.objects.filter(
        conversation=OuterRef('pk'),
        timestamp__gt=OuterRef('conversationparticipant__last_read')
    ).exclude(sender=request.user).values('id').annotate(cnt=Count('id')).values('cnt')

    conversations = Conversation.objects.filter(
        participants=request.user
    ).annotate(
        last_msg_content=Subquery(
            Message.objects.filter(conversation=OuterRef('pk')).order_by('-timestamp').values('content')[:1]
        ),
        unread_count=Subquery(unread_subquery),
        is_pinned=Subquery(
            ConversationParticipant.objects.filter(
                user=request.user,
                conversation=OuterRef('pk')
            ).values('is_pinned')[:1]
        )
    ).order_by(
        F('is_pinned').desc(),
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
                fav, _ = Conversation.objects.get_or_create(
                    type='favorite',
                    name='Избранное',
                    owner=request.user
                )
                fav.participants.add(request.user)
                return redirect('chat:room', conversation_id=fav.id)
            conversation, created = Conversation.objects.get_or_create_private(request.user, other_user)
            return redirect('chat:room', conversation_id=conversation.id)
        except User.DoesNotExist:
            raise Http404("Чат не найден")
    
    # Помечаем сообщения как прочитанные
    Message.objects.filter(conversation=conversation).exclude(sender=request.user).update(is_read=True)
    # Обновляем last_read
    participant = ConversationParticipant.objects.get(user=request.user, conversation=conversation)
    participant.last_read = timezone.now()
    participant.save()
    
    # Получаем закреплённое сообщение (если есть)
    try:
        pinned = PinnedMessage.objects.get(conversation=conversation)
        pinned_msg = pinned.message
    except PinnedMessage.DoesNotExist:
        pinned_msg = None

    messages_list = Message.objects.filter(conversation=conversation).select_related('sender', 'sticker').prefetch_related('file').order_by('timestamp')
    is_admin = participant.is_admin or conversation.type in ['private', 'favorite']
    
    invites = None
    if conversation.type == 'group' and is_admin:
        invites = conversation.invites.all()
    
    voice_room = None
    try:
        voice_room = conversation.voice_room
    except VoiceRoom.DoesNotExist:
        pass
    
    sticker_packs = StickerPack.objects.all().prefetch_related('stickers')
    
    return render(request, 'chat/room.html', {
        'conversation': conversation,
        'messages': messages_list,
        'pinned_message': pinned_msg,
        'is_admin': is_admin,
        'invites': invites,
        'participant': participant,
        'voice_room': voice_room,
        'sticker_packs': sticker_packs,
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

# --- Избранное ---
@login_required
def favorite_chat(request):
    fav, created = Conversation.objects.get_or_create(
        type='favorite',
        name='Избранное',
        owner=request.user
    )
    if created:
        fav.participants.add(request.user)
    return redirect('chat:room', conversation_id=fav.id)

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

# --- Загрузка файлов ---
@login_required
@csrf_exempt
def upload_file(request, conversation_id):
    if request.method == 'POST' and request.FILES.get('file'):
        conversation = get_object_or_404(Conversation, id=conversation_id, participants=request.user)
        uploaded_file = request.FILES['file']
        
        message = Message.objects.create(
            conversation=conversation,
            sender=request.user,
            content='📎 Файл'
        )
        file_msg = FileMessage.objects.create(
            message=message,
            file=uploaded_file,
            filename=uploaded_file.name,
            file_size=uploaded_file.size,
            file_type=uploaded_file.content_type
        )
        
        from channels.layers import get_channel_layer
        from asgiref.sync import async_to_sync
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'chat_{conversation_id}',
            {
                'type': 'chat_message',
                'id': message.id,
                'sender_id': request.user.id,
                'sender_name': request.user.get_display_name(),
                'sender_avatar': request.user.avatar.url if request.user.avatar else None,
                'content': f'📎 [{uploaded_file.name}]({file_msg.file.url})',
                'file_url': file_msg.file.url,
                'filename': uploaded_file.name,
                'timestamp': message.timestamp.isoformat(),
            }
        )
        
        return JsonResponse({'status': 'ok', 'file_url': file_msg.file.url})
    return JsonResponse({'status': 'error'}, status=400)

# --- Редактирование канала ---
@login_required
def edit_channel(request, conversation_id):
    conversation = get_object_or_404(Conversation, id=conversation_id, participants=request.user)
    participant = ConversationParticipant.objects.get(user=request.user, conversation=conversation)
    if not participant.is_admin and conversation.type != 'favorite':
        messages.error(request, 'Недостаточно прав')
        return redirect('chat:room', conversation_id=conversation.id)
    
    if request.method == 'POST':
        form = EditChannelForm(request.POST, request.FILES, instance=conversation)
        if form.is_valid():
            form.save()
            messages.success(request, 'Настройки канала обновлены')
            return redirect('chat:room', conversation_id=conversation.id)
    else:
        form = EditChannelForm(instance=conversation)
    return render(request, 'chat/edit_channel.html', {'form': form, 'conversation': conversation})

# --- Голосовой чат ---
@login_required
def voice_room(request, conversation_id):
    conversation = get_object_or_404(Conversation, id=conversation_id, participants=request.user)
    voice_room, created = VoiceRoom.objects.get_or_create(conversation=conversation)
    if created:
        voice_room.name = f"Voice of {conversation.name}"
        voice_room.save()
    return render(request, 'chat/voice_room.html', {
        'conversation': conversation,
        'voice_room': voice_room,
    })

@login_required
def join_voice(request, voice_room_id):
    voice_room = get_object_or_404(VoiceRoom, id=voice_room_id)
    if request.user not in voice_room.conversation.participants.all():
        messages.error(request, 'Вы не участник этого чата')
        return redirect('chat:index')
    voice_room.active_users.add(request.user)
    voice_room.is_active = True
    voice_room.save()
    from channels.layers import get_channel_layer
    from asgiref.sync import async_to_sync
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'voice_{voice_room.id}',
        {
            'type': 'user_joined',
            'user_id': request.user.id,
            'username': request.user.get_display_name(),
        }
    )
    return redirect('chat:voice_room', conversation_id=voice_room.conversation.id)

@login_required
def leave_voice(request, voice_room_id):
    voice_room = get_object_or_404(VoiceRoom, id=voice_room_id)
    voice_room.active_users.remove(request.user)
    if voice_room.active_users.count() == 0:
        voice_room.is_active = False
    voice_room.save()
    from channels.layers import get_channel_layer
    from asgiref.sync import async_to_sync
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'voice_{voice_room.id}',
        {
            'type': 'user_left',
            'user_id': request.user.id,
        }
    )
    return redirect('chat:room', conversation_id=voice_room.conversation.id)

# --- Стикеры ---
@login_required
def sticker_packs(request):
    packs = StickerPack.objects.all().prefetch_related('stickers')
    return render(request, 'chat/sticker_packs.html', {'packs': packs})

@login_required
def send_sticker(request, conversation_id, sticker_id):
    conversation = get_object_or_404(Conversation, id=conversation_id, participants=request.user)
    sticker = get_object_or_404(Sticker, id=sticker_id)
    message = Message.objects.create(
        conversation=conversation,
        sender=request.user,
        sticker=sticker,
        content=''
    )
    from channels.layers import get_channel_layer
    from asgiref.sync import async_to_sync
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'chat_{conversation_id}',
        {
            'type': 'chat_message',
            'id': message.id,
            'sender_id': request.user.id,
            'sender_name': request.user.get_display_name(),
            'sender_avatar': request.user.avatar.url if request.user.avatar else None,
            'content': '',
            'sticker_id': sticker.id,
            'sticker_url': sticker.image.url,
            'timestamp': message.timestamp.isoformat(),
        }
    )
    return redirect('chat:room', conversation_id=conversation.id)

# --- Редактирование и удаление сообщений ---
@login_required
def edit_message(request, message_id):
    message = get_object_or_404(Message, id=message_id, sender=request.user)
    if request.method == 'POST':
        new_content = request.POST.get('content')
        message.content = new_content
        message.edited_at = timezone.now()
        message.save()
        from channels.layers import get_channel_layer
        from asgiref.sync import async_to_sync
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'chat_{message.conversation.id}',
            {
                'type': 'edit_message',
                'id': message.id,
                'content': new_content,
                'edited_at': message.edited_at.isoformat(),
            }
        )
        return JsonResponse({'status': 'ok'})
    return render(request, 'chat/edit_message.html', {'message': message})

@login_required
def delete_message(request, message_id):
    message = get_object_or_404(Message, id=message_id, sender=request.user)
    message.deleted = True
    message.save()
    from channels.layers import get_channel_layer
    from asgiref.sync import async_to_sync
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'chat_{message.conversation.id}',
        {
            'type': 'delete_message',
            'id': message.id,
        }
    )
    return JsonResponse({'status': 'ok'})

# --- Боты (базовая заглушка) ---
@login_required
def bot_list(request):
    bots = Bot.objects.filter(owner=request.user)
    return render(request, 'chat/bot_list.html', {'bots': bots})

# --- Закрепление чата ---
@login_required
def pin_chat(request, conversation_id):
    participant = get_object_or_404(ConversationParticipant, user=request.user, conversation_id=conversation_id)
    participant.is_pinned = not participant.is_pinned
    participant.save()
    return redirect('chat:index')

# --- Удаление чата (скрыть) ---
@login_required
def delete_chat(request, conversation_id):
    participant = get_object_or_404(ConversationParticipant, user=request.user, conversation_id=conversation_id)
    participant.delete()
    messages.success(request, 'Чат удалён')
    return redirect('chat:index')

# --- Закрепление сообщения ---
@login_required
def pin_message(request, message_id):
    message = get_object_or_404(Message, id=message_id)
    conversation = message.conversation
    participant = ConversationParticipant.objects.get(user=request.user, conversation=conversation)
    if not (participant.is_admin or message.sender == request.user):
        messages.error(request, 'Недостаточно прав')
        return redirect('chat:room', conversation_id=conversation.id)
    
    pinned, created = PinnedMessage.objects.get_or_create(
        conversation=conversation,
        defaults={'message': message, 'pinned_by': request.user}
    )
    if not created:
        pinned.message = message
        pinned.pinned_by = request.user
        pinned.save()
        messages.success(request, 'Закреплённое сообщение изменено')
    else:
        messages.success(request, 'Сообщение закреплено')
    
    from channels.layers import get_channel_layer
    from asgiref.sync import async_to_sync
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'chat_{conversation.id}',
        {
            'type': 'pin_message',
            'message_id': message.id,
            'content': message.content[:50],
        }
    )
    return redirect('chat:room', conversation_id=conversation.id)

@login_required
def unpin_message(request, conversation_id):
    conversation = get_object_or_404(Conversation, id=conversation_id, participants=request.user)
    PinnedMessage.objects.filter(conversation=conversation).delete()
    messages.success(request, 'Сообщение откреплено')
    from channels.layers import get_channel_layer
    from asgiref.sync import async_to_sync
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'chat_{conversation.id}',
        {
            'type': 'unpin_message',
        }
    )
    return redirect('chat:room', conversation_id=conversation.id)

# --- Ответ на сообщение (заглушка) ---
@login_required
def reply_message(request, message_id):
    messages.info(request, 'Функция в разработке')
    return redirect('chat:room', conversation_id=get_object_or_404(Message, id=message_id).conversation.id)

# --- Пересылка сообщения (заглушка) ---
@login_required
def forward_message(request, message_id):
    messages.info(request, 'Функция в разработке')
    return redirect('chat:room', conversation_id=get_object_or_404(Message, id=message_id).conversation.id)