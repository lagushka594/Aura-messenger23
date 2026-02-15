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
    # Для создания личного чата нужно выбрать друга.
    # Но мы можем упростить: при нажатии на "Создать чат" можно предложить ввести ID друга или выбрать из списка.
    # Для простоты сделаем поле ввода ID друга.
    friend_id = forms.CharField(label='ID друга (никнейм#цифры)', max_length=50)