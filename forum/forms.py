from .models import Post, Replies, SectionTheme, Section
from django.forms import ModelForm, TextInput, IntegerField, ImageField, FileInput, NumberInput, FileField
from django.conf import settings


class SectionThemeForm(ModelForm):
    class Meta:
        model = SectionTheme
        fields = '__all__'
        widgets = {
            "name": TextInput(attrs={
                'class': 'form-control',
                'placeholder': "Категория"
            }),
            "priority": NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 10
            })
        }

class SectionForm(ModelForm):
    class Meta:
        model = Section
        fields = ['name']
        widgets = {
            "name": TextInput(attrs={
                'class': 'form-control',
                'placeholder': "Раздел"
            })
        }

class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content']
        widgets = {
            "title": TextInput(attrs={
                'class': 'form-control',
                'placeholder': "Тема"
            }),
            "content": TextInput(attrs={
                'class': 'form-control',
                'placeholder': "Описание"
            })
        }


class ReplyForm(ModelForm):
    # attachments = FileField(widget=TextInput(attrs={
    #     "name": "images",
    #     "type": "File",
    #     "class": "form-control",
    #     "multiple": "True",
    # }), label="")

    class Meta:
        model = Replies
        fields = ['reply', 'attachments']
        widgets = {
            "reply": TextInput(attrs={
                'class': 'form-control',
                'placeholder': "Ответ"
            }),
            # "attachments": FileInput(attrs={
            #     'class': 'form-control',
            #     'placeholder': "Вложения"
            # })
        }


