import random
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models import Q

def generate_discriminator():
    return f'{random.randint(1000, 9999)}'

class User(AbstractUser):
    username = models.CharField(max_length=32, unique=True, verbose_name='Никнейм')
    email = models.EmailField(unique=True)
    discriminator = models.CharField(max_length=4, default=generate_discriminator, editable=False)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    bio = models.TextField(max_length=500, blank=True)
    manual_status = models.CharField(
        max_length=20,
        choices=[
            ('online', 'Онлайн'),
            ('idle', 'Не активен'),
            ('offline', 'Офлайн'),
            ('invisible', 'Невидимка')
        ],
        default='offline'
    )
    last_activity = models.DateTimeField(auto_now=True)

    def get_display_name(self):
        return f'{self.username}#{self.discriminator}'

    def __str__(self):
        return self.get_display_name()

class Friendship(models.Model):
    from_user = models.ForeignKey(User, related_name='friends_from', on_delete=models.CASCADE)
    to_user = models.ForeignKey(User, related_name='friends_to', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=[('pending', 'Ожидание'), ('accepted', 'Принято'), ('rejected', 'Отклонено')],
        default='pending'
    )

    class Meta:
        unique_together = ('from_user', 'to_user')