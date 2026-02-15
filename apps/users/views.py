from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import User, Friendship
from .forms import UserRegistrationForm, LoginForm, AddFriendForm
from apps.chat.models import Conversation

def register_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            login(request, user)
            return redirect('chat:index')
    else:
        form = UserRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('chat:index')
    else:
        form = LoginForm()
    return render(request, 'registration/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('users:login')

@login_required
def profile_view(request):
    return render(request, 'users/profile.html', {'user': request.user})

@login_required
def friends_list(request):
    friendships = Friendship.objects.filter(
        (Q(from_user=request.user) | Q(to_user=request.user)),
        status='accepted'
    ).select_related('from_user', 'to_user')
    friends = []
    for fs in friendships:
        if fs.from_user == request.user:
            friends.append(fs.to_user)
        else:
            friends.append(fs.from_user)
    return render(request, 'users/friends.html', {'friends': friends})

@login_required
def friend_requests(request):
    incoming = Friendship.objects.filter(to_user=request.user, status='pending').select_related('from_user')
    outgoing = Friendship.objects.filter(from_user=request.user, status='pending').select_related('to_user')
    return render(request, 'users/friend_requests.html', {
        'incoming': incoming,
        'outgoing': outgoing,
    })

@login_required
def add_friend(request):
    if request.method == 'POST':
        form = AddFriendForm(request.POST, user=request.user)
        if form.is_valid():
            friend = form.cleaned_data['friend_id']
            if Friendship.objects.filter(
                (Q(from_user=request.user, to_user=friend) | Q(from_user=friend, to_user=request.user))
            ).exists():
                messages.error(request, 'Заявка уже существует или вы уже друзья.')
            else:
                Friendship.objects.create(from_user=request.user, to_user=friend, status='pending')
                messages.success(request, f'Заявка отправлена пользователю {friend.get_display_name()}')
            return redirect('users:friend_requests')
    else:
        form = AddFriendForm(user=request.user)
    return render(request, 'users/add_friend.html', {'form': form})

@login_required
def handle_request(request, friendship_id, action):
    friendship = get_object_or_404(Friendship, id=friendship_id, to_user=request.user, status='pending')
    if action == 'accept':
        friendship.status = 'accepted'
        friendship.save()
        # Создаём или получаем личный чат
        conv, created = Conversation.objects.get_or_create_private(request.user, friendship.from_user)
        messages.success(request, 'Заявка принята')
    elif action == 'reject':
        friendship.status = 'rejected'
        friendship.save()
        messages.success(request, 'Заявка отклонена')
    return redirect('users:friend_requests')

@login_required
def user_profile(request, user_id):
    profile_user = get_object_or_404(User, id=user_id)
    are_friends = Friendship.objects.filter(
        (Q(from_user=request.user, to_user=profile_user) | Q(from_user=profile_user, to_user=request.user)),
        status='accepted'
    ).exists()
    context = {
        'profile_user': profile_user,
        'are_friends': are_friends,
    }
    return render(request, 'users/user_profile.html', context)