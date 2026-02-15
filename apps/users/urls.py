from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/<int:user_id>/', views.user_profile, name='user_profile'),
    path('friends/', views.friends_list, name='friends'),
    path('friend-requests/', views.friend_requests, name='friend_requests'),
    path('add-friend/', views.add_friend, name='add_friend'),
    path('handle-request/<int:friendship_id>/<str:action>/', views.handle_request, name='handle_request'),
]