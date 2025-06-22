from django.contrib.admin import action
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template.context_processors import request

from django.contrib.auth.models import User
from  django.utils import timezone
from notifications.signals import notify
from twisted.names.client import query

from login_modal.models import Profile
from .forms import TaskForm
from .models import Task
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView
)
from rest_framework import viewsets, permissions
from .serializers import TaskSerializer

class TaskCreateView(LoginRequiredMixin, CreateView):
    model = Task
    template_name = 'tasks/task_create.html'
    context_object_name = 'task'
    form_class = TaskForm

    def form_valid(self, form):
        form.instance.from_user = self.request.user
        receiver = get_object_or_404(User, username=self.kwargs.get('username'))
        form.instance.to_user = receiver
        form.instance.date_created = timezone.now()

        check = self.request.POST.get('urgent_check')
        form.instance.is_urgent = check == "on"

        task = form.save()
        notify.send(form.instance.from_user, recipient=receiver, verb='назначил(а) Вам задание.', action_object=task)
        return super().form_valid(form)

class TaskUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Task
    template_name = 'tasks/task_create.html'
    context_object_name = 'task'
    form_class = TaskForm

    def get_context_data(self, **kwargs):
        context = super(TaskUpdateView, self).get_context_data(**kwargs)
        context['update'] = True
        return context

    def test_func(self):
        task = self.get_object()
        if self.request.user == task.from_user:
            return True
        return False

    def form_valid(self, form):
        pid = self.request.POST.get('users')
        if (pid != ""):
            profile = get_object_or_404(Profile, id=pid)
            form.instance.to_user = profile.user

        check = self.request.POST.get('urgent_check')
        form.instance.is_urgent = check == "on"

        form.save()
        return super().form_valid(form)


class TaskDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Task
    success_url = '/'

    def test_func(self):
        task = self.get_object()
        if self.request.user == task.from_user:
            return True
        return False

class UserTaskListView(ListView):
    model = Task
    template_name = 'tasks/user_tasks.html'
    context_object_name = 'tasks'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super(UserTaskListView, self).get_context_data(**kwargs)
        context['username'] = self.kwargs.get('username')
        query = self.request.GET.get('query' or None)
        filter = self.request.GET.get('filter_select' or None)
        is_done = self.request.GET.get('is_done_select' or None)
        filter_params = {}

        # if filter is not None or is_done is not None:
            # context['filter_url'] = ''
        if filter is not None:
            filter_params['filter'] = filter
        if is_done is not None:
            filter_params['is_done'] = is_done
        if query is not None:
            filter_params['query'] = query
        # print(filter)
        # if filter == "incoming":
        #     filter_params['filter'] = 1
        #     # context['filter'] = 1
        #     # context['filter_url'] += "filter=incoming"
        # elif filter == "outgoing":
        #     filter_params['filter'] = 2
        #     # context['filter'] = 2
        #     # context['filter_url'] += "filter=outgoing"
        # else:
        #     # context['filter'] = 0
        #     filter_params['filter'] = 0

        if is_done is not None:
            filter_params['is_done'] = is_done
            # context['is_done'] = is_done
        if filter is not None or is_done is not None or query is not None:
            context['filter_params'] = filter_params

        return context

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        giver = self.request.user
        filter = self.request.GET.get('filter_select')
        is_done = self.request.GET.get('is_done_select')
        query = self.request.GET.get('query')
        # queries = {}
        filters = {}

        if query is None:
            query = ""
        #     filters['description__icontains'] = query
        #     queries['title__icontains'] = query

        if is_done is not None and is_done != "all":
            done = is_done == "True"
            filters['done'] = done

        if filter == "incoming":
            if (user == giver):
                filters['to_user'] = giver
            else:
                filters['from_user'] = giver
                filters['to_user'] = user

        elif filter == "outgoing":
            if (user == giver):
                filters['from_user'] = giver
            else:
                filters['from_user'] = user
                filters['to_user'] = giver

        elif filter == "all":
            if (user == giver):
                q1 = Q(from_user=user)
                q2 = Q(to_user=user)
            else:
                q1 = Q(from_user=user, to_user=giver)
                q2 = Q(from_user=giver, to_user=user)
            queryset =  Task.objects.filter(q1 | q2).filter(**filters, description__icontains=query).order_by('-date_created')

            return queryset

        else:
            filters['to_user'] = user

        # if self.request.GET.get("filter") == "incoming":
        #
        #     if (user == giver):
        #
        #         return Task.objects.filter(to_user=giver).order_by('-date_created')
        #     return Task.objects.filter(from_user=giver, to_user=user).order_by('-date_created')
        #
        # elif self.request.GET.get("filter") == "outgoing":
        #     if (user == giver):
        #         return Task.objects.filter(from_user=giver).order_by('-date_created')
        #     return Task.objects.filter(to_user=giver, from_user=user).order_by('-date_created')

        # if (user == giver):
        #     return Task.objects.filter(to_user=user).order_by('-date_created')

        queryset = Task.objects.filter(**filters, description__icontains=query).order_by('-date_created')

        return queryset

def add_filters(request, *args, **kwargs):
    pass
#     if request.method == 'POST':
#         print("Hello!")
#     # user = get_object_or_404(User, username=kwargs['username'])
#     user = kwargs.get('username')
#     print(user)
#     filter = request.POST.get('filter_select')
#     # filter = request.GET['filter_select']
#     # is_done = request.GET['is_done_select']
#     is_done = request.POST.get('is_done_select')
#     print("Adding filters")
#     print(filter)
#     print(is_done)
#
#     query = ""
#
#     if filter is not None or is_done is not None:
#         query += "?"
#
#     if filter is not None:
#         query += "filter=" + filter + "&"
#
#     if is_done is not None and is_done != "all":
#         query += "is_done=" + is_done + "&"
#
#     return redirect(f'/user/{user}/tasks/'+query)


class TaskDetailView(DetailView):
    model = Task


@login_required
def task_complete(request, *args, **kwargs):
    id = kwargs.get('pk')
    task = get_object_or_404(Task, id=id)

    task.done = True
    task.save()
    return redirect(request.GET.get('next'))
    # return redirect('user-tasks', username=task.to_user.username)

@login_required
def task_uncomplete(request, *args, **kwargs):
    id = kwargs.get('pk')
    task = get_object_or_404(Task, id=id)

    task.done = False
    task.save()
    return redirect(request.GET.get('next'))
    #return redirect('user-tasks', username=task.to_user.username)


class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Task.objects.filter(to_user=self.request.user)