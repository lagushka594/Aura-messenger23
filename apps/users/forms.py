from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import User, Friendship

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label='Пароль')
    confirm_password = forms.CharField(widget=forms.PasswordInput, label='Подтвердите пароль')

    class Meta:
        model = User
        fields = ['username', 'email', 'avatar', 'bio']
        labels = {
            'username': 'Никнейм',
            'email': 'Email',
            'avatar': 'Аватар',
            'bio': 'О себе',
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm = cleaned_data.get('confirm_password')
        if password and confirm and password != confirm:
            raise forms.ValidationError('Пароли не совпадают')
        return cleaned_data

class LoginForm(AuthenticationForm):
    username = forms.CharField(label='Email или никнейм')

class AddFriendForm(forms.Form):
    friend_id = forms.CharField(label='ID друга (никнейм#цифры)')

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)

    def clean_friend_id(self):
        data = self.cleaned_data['friend_id']
        try:
            username, discriminator = data.split('#')
            friend = User.objects.get(username=username, discriminator=discriminator)
        except (ValueError, User.DoesNotExist):
            raise forms.ValidationError('Пользователь с таким ID не найден')
        if self.user == friend:
            raise forms.ValidationError('Нельзя добавить самого себя')
        return friend

# Формы для настроек
class ChangePasswordForm(forms.Form):
    old_password = forms.CharField(widget=forms.PasswordInput, label='Старый пароль')
    new_password1 = forms.CharField(widget=forms.PasswordInput, label='Новый пароль')
    new_password2 = forms.CharField(widget=forms.PasswordInput, label='Подтвердите новый пароль')

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('new_password1')
        p2 = cleaned_data.get('new_password2')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError('Новые пароли не совпадают')
        return cleaned_data

class ChangeEmailForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email']
        labels = {'email': 'Новый email'}

class ChangeUsernameForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username']
        labels = {'username': 'Новый никнейм'}

class ChangeBioForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['bio']
        labels = {'bio': 'О себе'}
        widgets = {'bio': forms.Textarea(attrs={'rows': 3})}

class ChangeStatusForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['manual_status']
        labels = {'manual_status': 'Статус'}