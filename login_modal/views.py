from datetime import datetime

from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.template.defaultfilters import first
from django.views.generic import DetailView
from django_htmx.http import HttpResponseClientRefresh
from .forms import LoginForm, UserRegisterForm
from django.contrib import messages
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm
from django.contrib.auth.decorators import login_required
from .models import Profile
import logging


logger = logging.getLogger("forum_logger")

def login(request):
    if request.method == "POST":
        form = LoginForm(request=request, data=request.POST, prefix="login")
        template_name = "login_form.html"
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            logger.warning(f'{datetime.now()}: Зашел пользователь {user}')
            return HttpResponseClientRefresh()
    else:
        form = LoginForm(request=request, prefix="login")
        template_name = "login_dialog.html"
    context = {"form": form}
    return render(request, template_name, context)


def logout(request):
    auth_logout(request)
    logger.warning(f'{datetime.now()}: Пользователь {request.user} вышел из системы')
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
                logger.warning(f'{datetime.now()}: Зарегестрирован пользователь {username}')
                return redirect('home')
        else:
            form = UserRegisterForm()
        return render(request, 'register.html', {'form': form})
    else:
        return redirect('home')


@login_required
def profile_update(request, *args, **kwargs):
    if request.user.username != kwargs.get('username'):
        return redirect('home')
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST,
                                   request.FILES,
                                   instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, f'Ваш профиль успешно обновлен.')
            logger.warning(f'{datetime.now()}: Пользователь {request.user} внёс изменения в профиль')
            return redirect('profile')

    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'u_form': u_form,
        'p_form': p_form
    }

    return render(request, 'profile_update.html', context)


def profile_view(request, *args, **kwargs):
    profile_user = get_object_or_404(User, username=kwargs.get('username'))
    profile = profile_user.profile

    return render(request, 'profile_detail.html', {'profile': profile, 'profile_user':profile_user})


def promote(request, *args, **kwargs):
    if request.user.is_superuser:
        # print(kwargs.get('username'))
        user = get_object_or_404(User, username=kwargs.get('username'))
        user.is_staff = True
        user.save()
        logger.warning(f'{datetime.now()}: {user} повышен до статуса персонала администратором {request.user}')
    return redirect('user-posts', username=kwargs.get('username'))

def demote(request, *args, **kwargs):
    if request.user.is_superuser:
        # print(kwargs.get('username'))
        user = get_object_or_404(User, username=kwargs.get('username'))
        user.is_staff = False
        user.save()
        logger.warning(f'{datetime.now()}: Пользователю {user} снял статус персонала администратор {request.user}')
    return redirect('user-posts', username=kwargs.get('username'))