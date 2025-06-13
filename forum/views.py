from lib2to3.fixes.fix_input import context

from django.db.models import Count
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template.context_processors import request

from login_modal.forms import SearchForm
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView
)

from .forms import PostForm, ReplyForm, SectionForm, SectionThemeForm
from .models import *
from notifications.models import Notification
from notifications.views import AllNotificationsList
from django.contrib.contenttypes.models import ContentType
import chat.models


"""
Оповещения
"""
def notification_view(request):
    if request.user.is_authenticated:
        user = request.user
        unread_notification_list = Notification.objects.filter(recipient=user, unread=True)
        notification_list = Notification.objects.filter(recipient=user, unread=False)
        #Notification.objects.mark_all_as_read(recipient=user)
        # for notif in notification_list:
        #     if ContentType.objects.get_for_model(chat.models.Message).id == notif.action_object_content_type.id:
        #         print("notif.action_object_content_type.id")
            # if notif is not None:
            #     print(notif.action_object_content_type.id)
            # else:
            #     print("What?")
        return render(request, 'homepage/notifications.html', {'notification_list': notification_list, 'unread_notification_list':unread_notification_list})

def read_all_notifications(request):
    if request.user.is_authenticated:
        Notification.objects.mark_all_as_read(recipient=request.user)
    return redirect('notification_list')

# def index(request):
#     if request.user.is_authenticated:
#         context = {
#             'posts': Post.objects.all()
#         }
#         return render(request, 'forum/section_posts.html', context)
#     if request.GET:
#         form = SearchForm(data=request.GET, prefix="search")
#         if form.is_valid():
#             pass
#     else:
#         form = SearchForm(data=request.GET, prefix="search")
#     request.combined_media = form.media
#     context = {
#         "form": form,
#     }
#     return render(request, "homepage/frontpage.html", context)

def about(request):
    return render(request, 'homepage/about.html')

"""
Разделы
"""
def sections(request):
    themes = SectionTheme.objects.all().order_by('priority')
    sections = Section.objects.all()

    return render(request, 'forum/sections.html', {'themes': themes, 'sections': sections})

class SectionCreateView(LoginRequiredMixin, CreateView):
    model = Section
    template_name = 'forum/section_form.html'
    context_object_name = 'section'
    form_class = SectionForm
    success_url = '/'

    def form_valid(self, form):
        form.instance.theme = get_object_or_404(SectionTheme, id=self.kwargs.get('pk'))
        return super().form_valid(form)

class SectionThemeCreateView(LoginRequiredMixin, CreateView):
    model = SectionTheme
    template_name = 'forum/section_theme_form.html'
    context_object_name = 'section_theme'
    form_class = SectionThemeForm
    success_url = '/'


"""
Обсуждения
"""

class PostListView(ListView):
    model = Post
    template_name = 'forum/section_posts.html'
    context_object_name = 'posts'
    ordering = ['-date_created']
    paginate_by = 5
    def get_queryset(self):
        posts = Post.objects.filter(section=self.kwargs.get('pk')).order_by('-date_created')
        for post in posts:
            post.count = Replies.objects.filter(post=post).count()
            if post.count > 0:
                date = Replies.objects.filter(post=post).order_by('-date_posted').first().date_posted
                post.last_reply = date
                print(date)
            else:
                post.last_reply = 'Никогда'
        return posts

class UserPostListView(ListView):
    model = Post
    template_name = 'forum/user_posts.html'
    context_object_name = 'posts'
    paginate_by = 5

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return Post.objects.filter(author=user).order_by('-date_created')


class PostDetailView(DetailView):
    model = Post

class PostCreateView(LoginRequiredMixin, CreateView):
    # model = Post
    # fields = ['title', 'content']
    #
    # def form_valid(self, form):
    #     form.instance.author = self.request.user
    #     return super().form_valid(form)
    model = Post
    template_name = 'forum/post_form.html'
    context_object_name = 'post'
    form_class = PostForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.date_posted = timezone.now()
        return super().form_valid(form)

class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    # model = Post
    # fields = ['title', 'content']
    #
    # def form_valid(self, form):
    #     form.instance.author = self.request.user
    #     return super().form_valid(form)
    #
    # def test_func(self):
    #     post = self.get_object()
    #     if self.request.user == post.author:
    #         return True
    #     return False
    model = Post
    template_name = 'forum/post_form.html'
    context_object_name = 'post'
    form_class = PostForm

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    success_url = '/'

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False



"""
Ответы
"""

class RepliesListView(ListView):
    model = Replies
    template_name = 'forum/replies.html'
    context_object_name = 'replies'
    ordering = ['-date_posted']
    paginate_by = 50

    def get_queryset(self):
        post = get_object_or_404(Post, id=self.kwargs.get('pk'))
        replies = Replies.objects.filter(post=post).order_by('-date_posted')
        # image_extensions = ["png", "jpg", "jpeg", "bmp"]
        # i = 0
        # for reply in replies:
        #     ext = reply.attachments.name.split('.')[-1]
        #     if ext not in image_extensions:
        #         replies[i].attachments.name = "default_file.png"
        #     i += 1
        return replies

def replies(request, *args, **kwargs):
    post = get_object_or_404(Post, id=kwargs.get('pk'))
    replies = Replies.objects.filter(post=post).order_by('date_posted')
    return render(request, 'forum/replies.html', {'replies': replies, 'post': post})

class RepliesCreateView(LoginRequiredMixin, CreateView):
    model = Replies
    template_name = 'forum/reply.html'
    context_object_name = 'replies'
    form_class = ReplyForm
    def form_valid(self, form):
        form.instance.post_id = self.kwargs.get('pk')
        form.instance.author = self.request.user
        form.instance.date_posted = timezone.now()
        #form.instance.attachments = self.request.POST.get('attachments')
        return super().form_valid(form)


