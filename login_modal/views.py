from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.template.defaultfilters import first
from django_htmx.http import HttpResponseClientRefresh
from .forms import LoginForm, UserRegisterForm
from django.contrib import messages
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm
from django.contrib.auth.decorators import login_required
from .models import Profile

def login(request):
    if request.method == "POST":
        form = LoginForm(request=request, data=request.POST, prefix="login")
        template_name = "login_form.html"
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            return HttpResponseClientRefresh()
    else:
        form = LoginForm(request=request, prefix="login")
        template_name = "login_dialog.html"
    context = {"form": form}
    return render(request, template_name, context)


def logout(request):
    auth_logout(request)
    return redirect("home")


def register(request):
    if not request.user.is_authenticated:
        if request.method == 'POST':
            form = UserRegisterForm(request.POST)
            if form.is_valid():
                user = form.save()
                first_name = form.cleaned_data['first_name']
                last_name = form.cleaned_data['last_name']
                middle_name = form.cleaned_data['middle_name']
                Profile.objects.create(user=user, first_name=first_name, last_name=last_name,
                                       middle_name=middle_name)
                username = form.cleaned_data.get('username')
                messages.success(request, f'Создан аккаунт {username}!')
                return redirect('home')
        else:
            form = UserRegisterForm()
        return render(request, 'register.html', {'form': form})
    else:
        return redirect('home')


@login_required
def profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST,
                                   request.FILES,
                                   instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, f'Ваш профиль успешно обновлен.')
            return redirect('profile')

    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'u_form': u_form,
        'p_form': p_form
    }

    return render(request, 'profile_update.html', context)