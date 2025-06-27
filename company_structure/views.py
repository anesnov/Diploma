from django.contrib.auth.decorators import login_required

from login_modal.models import Profile
from .models import Department, Position
from django.shortcuts import render, get_object_or_404


@login_required
def structure(request):
    users = Profile.objects.all().order_by('-position__is_head')
    departments = Department.objects.all().order_by('-is_director')
    other_users = Profile.objects.filter(department__isnull=True)
    for user in other_users:
        print(user)
    # print(departments[0])
    return render(request, 'hierarchy.html', {'users': users, 'departments': departments, 'other_users': other_users})

