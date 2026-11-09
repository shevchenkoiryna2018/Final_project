from django import forms
from .models import Plant, CareTask

from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User


class PlantForm(forms.ModelForm):
    class Meta:
        model = Plant

        fields = (
            'name',
            'species',
            'acquired_date',
            'watering_interval',
            'last_watered',
            'location',
            'notes'
        )

        widgets = {
            'acquired_date': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'last_watered': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'notes': forms.Textarea(attrs={'rows': 3})
        }

        labels = {
            'name': 'Назва рослини',
            'species': 'Вид рослини',
            'acquired_date': 'Дата придбання',
            'watering_interval': 'Інтервал поливу (днів)',
            'last_watered': 'Дата останнього поливу',
            'location': 'Розташування',
            'notes': 'Додаткова інформація'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


class CareTaskForm(forms.ModelForm):
    class Meta:
        model = CareTask

        fields = (
            'plant',
            'task_type',
            'scheduled_date',
            'priority',
            'notes'
        )

        widgets = {
            'scheduled_date': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'notes': forms.Textarea(attrs={'rows': 3})
        }

        labels = {
            'plant': 'Рослина',
            'task_type': 'Тип догляду',
            'scheduled_date': 'Запланована дата',
            'priority': 'Пріоритет',
            'notes': 'Примітки'
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super().__init__(*args, **kwargs)

        self.fields['plant'].queryset = Plant.objects.filter(owner=user)
        self.fields['plant'].empty_label = 'Оберіть рослину'
        self.fields['task_type'].choices = [('', 'Оберіть тип догляду'), *CareTask.TASK_TYPES]

        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


class LoginForm(AuthenticationForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'



