from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template.context_processors import request

from django.contrib.auth.models import User
from login_modal.models import Profile
from  django.utils import timezone
from .models import Department, Position
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView
)
# Create your views here.


@login_required
def structure(request):
    users = Profile.objects.all().order_by('-position__is_head')
    departments = Department.objects.all().order_by('-is_director')
    other_users = Profile.objects.filter(department__isnull=True)
    for user in other_users:
        print(user)
    # print(departments[0])
    return render(request, 'hierarchy.html', {'users': users, 'departments': departments, 'other_users': other_users})

