from .models import Task
from django.forms import ModelForm, TextInput, DateTimeInput, CheckboxInput
from django.conf import settings


class TaskForm(ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'date_completion', 'is_urgent']
        widgets = {
            "title": TextInput(attrs={
                'class': 'form-control',
                'placeholder': "Название"
            }),
            "description": TextInput(attrs={
                'class': 'form-control',
                'placeholder': "Задача"
            }),
            "date_completion": DateTimeInput(attrs={
                'type': 'datetime-local',
                'placeholder': "Дата конца"
            }),
            "is_urgent": CheckboxInput(attrs={
                'class': 'required checkbox form-control'
            })
        }