from cProfile import label

from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from crispy_forms.helper import FormHelper
from crispy_forms.bootstrap import FieldWithButtons
from crispy_forms.layout import Layout, Submit
from crispy_bootstrap5 import bootstrap5
from django.contrib.auth.models import User

from .models import Profile


class SearchForm(forms.Form):
    q = forms.CharField(label="Search", required=False)

    class Media:
        js = [
            "js/search.js",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["q"].label = ""

        self.helper = FormHelper()
        self.helper.form_tag = True
        self.helper.form_method = "GET"
        self.helper.include_media = False
        self.helper.layout = Layout(
            FieldWithButtons(
                bootstrap5.Field("q", type="search"),
                Submit("search", "Search"),
            )
        )


class LoginForm(AuthenticationForm):
    class Media:
        js = [
            "js/login.js",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.include_media = False
        self.helper.layout = Layout(
            bootstrap5.FloatingField("username", autocomplete="username"),
            bootstrap5.FloatingField("password", autocomplete="current-password"),
        )

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()
    first_name = forms.CharField(label="Имя")
    last_name = forms.CharField(label="Фамилия")
    middle_name = forms.CharField(label="Отчество", required=False)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'middle_name', 'email', 'password1', 'password2']


class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(required=False)
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), label='Имя пользователя', required=False)
    class Meta:
        model = User
        fields = ['username', 'email']


class ProfileUpdateForm(forms.ModelForm):
    first_name = forms.CharField(label="Имя")
    last_name = forms.CharField(label="Фамилия")
    middle_name = forms.CharField(label="Отчество", required=False)
    image = forms.ImageField(label="Аватар", required=False)
    class Meta:
        model = Profile
        fields = ['first_name', 'last_name', 'middle_name', 'image']
