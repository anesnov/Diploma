from django.contrib.auth.models import User

from login_modal.models import Profile
from .models import Task
from django.forms import ModelForm, TextInput, DateTimeInput, CheckboxInput, models
from formset.widgets import Selectize
from django.conf import settings


class TaskForm(ModelForm):
    users = models.ModelChoiceField(
        queryset = Profile.objects.select_related('user'),
        label = "Выполняющий",
        widget = Selectize(
            search_lookup="full_name__icontains",
            placeholder="Выберите, кому передать задачу",
            #group_field_name="full_name",
        ),
        required = False,
    )
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
                'placeholder': "Дата конца",
                'required': False,

            }),
            "is_urgent": CheckboxInput(attrs={
                'class': 'required checkbox form-control'
            })
        }