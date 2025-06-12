from django.contrib.admin import action
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template.context_processors import request

from django.contrib.auth.models import User
from  django.utils import timezone
from notifications.signals import notify

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
        # print(check)
        if check == "on":
            # print("Checked")
            form.instance.is_urgent = True
            # print(form.instance.id)
        task = form.save()
        # print(task.id)
        notify.send(form.instance.from_user, recipient=receiver, verb='назначил(а) Вам задание.', action_object=task)
        return super().form_valid(form)

class TaskUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Task
    template_name = 'tasks/task_create.html'
    context_object_name = 'task'
    form_class = TaskForm

    def test_func(self):
        task = self.get_object()
        if self.request.user == task.from_user:
            return True
        return False


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
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super(UserTaskListView, self).get_context_data(**kwargs)
        filter = self.request.GET.get('filter' or None)
        print(filter)
        if self.request.GET.get("filter") == "incoming":
            context['filter'] = 1
            context['filter_url'] = "filter=incoming"
        elif self.request.GET.get("filter") == "outgoing":
            context['filter'] = 2
            context['filter_url'] = "filter=outgoing"
        else:
            context['filter'] = 0

        return context

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        giver = self.request.user
        filters = {}
        if self.request.GET.get("filter") == "incoming":
            if (user == giver):
                filters['to_user'] = giver
            else:
                filters['from_user'] = giver
                filters['to_user'] = user

        elif self.request.GET.get("filter") == "outgoing":
            if (user == giver):
                filters['from_user'] = giver
            else:
                filters['to_user'] = giver
                filters['from_user'] = user
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
        return Task.objects.filter(**filters).order_by('-date_created')


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