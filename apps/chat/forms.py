from django import forms
from .models import Conversation

class CreateGroupForm(forms.ModelForm):
    class Meta:
        model = Conversation
        fields = ['name', 'avatar']
        labels = {
            'name': 'Название группы',
            'avatar': 'Аватар группы (необязательно)',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите название группы'}),
        }

class CreatePrivateChatForm(forms.Form):
    friend_id = forms.CharField(label='ID друга (никнейм#цифры)', max_length=50)

class EditChannelForm(forms.ModelForm):
    class Meta:
        model = Conversation
        fields = ['name', 'avatar']
        labels = {
            'name': 'Название канала',
            'avatar': 'Аватар канала',
        }