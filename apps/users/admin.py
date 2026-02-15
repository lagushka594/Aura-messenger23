from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Friendship

class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ('username', 'email', 'discriminator', 'manual_status', 'last_activity', 'is_staff')
    fieldsets = UserAdmin.fieldsets + (
        ('Дополнительно', {'fields': ('discriminator', 'avatar', 'bio', 'manual_status')}),
    )
    readonly_fields = ('discriminator', 'last_activity')

admin.site.register(User, CustomUserAdmin)

@admin.register(Friendship)
class FriendshipAdmin(admin.ModelAdmin):
    list_display = ('from_user', 'to_user', 'status', 'created_at')
    list_filter = ('status',)