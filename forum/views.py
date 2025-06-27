import logging
from datetime import datetime
from django.shortcuts import render, redirect
from notifications.signals import notify
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
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


logger = logging.getLogger("forum_logger")

"""
Поиск
"""
def search_view(request):
    object_type = request.GET.get('category')
    query = request.GET.get('query')

    if object_type == 'tasks':
        return redirect(f'/user/{request.user.username}/tasks/?query={query}')

    replies = Replies.objects.filter(reply__icontains=query).order_by('-date_posted')
    paginator = Paginator(replies, 5)

    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(request, 'forum/replies_search.html', {'replies': replies, "page_obj": page_obj, "query": query})

"""
Оповещения
"""
def notification_view(request):
    if request.user.is_authenticated:
        user = request.user
        unread_notification_list = Notification.objects.filter(recipient=user, unread=True)
        notification_list = Notification.objects.filter(recipient=user, unread=False)
        for un in unread_notification_list:
            print(un.action_object_content_type_id)
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

    for section in sections:
        section.count = Post.objects.filter(section=section).count()
        if section.count > 0:
            date = Post.objects.filter(section=section).order_by('-date_created').first().date_created
            section.last_reply = date
        else:
            section.last_reply = 'Никогда'

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
    model = Post
    template_name = 'forum/post_form.html'
    context_object_name = 'post'
    form_class = PostForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.date_posted = timezone.now()
        section_id = self.kwargs.get('pk')
        section = get_object_or_404(Section, id=section_id)
        form.instance.section = section
        logger.warning(f'{datetime.now()}: {self.request.user} создал обсуждение {form.instance.title}')
        return super().form_valid(form)

class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
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

class RepliesListView(LoginRequiredMixin, ListView):
    model = Replies
    template_name = 'forum/replies.html'
    context_object_name = 'replies'
    #ordering = ['-date_posted']
    paginate_by = 5

    def get_context_data(self, **kwargs):
        context = super(RepliesListView, self).get_context_data(**kwargs)
        context['post'] = get_object_or_404(Post, id=self.kwargs.get('pk'))
        context['list_view'] = True
        return context

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
    template_name = 'forum/reply_form.html'
    context_object_name = 'replies'
    form_class = ReplyForm

    def get_success_url(self):
        # print(self.pk)
        return reverse('post-detail', kwargs={'pk': self.kwargs.get('pk')})

    def get_context_data(self, **kwargs):
        context = super(RepliesCreateView, self).get_context_data(**kwargs)
        reply = self.request.GET.get('reply_to' or None)
        if reply is not None:
            context['reply'] = get_object_or_404(Replies, id=reply)
            context['is_reply'] = True
        return context

    def form_valid(self, form):
        form.instance.post_id = self.kwargs.get('pk')
        form.instance.author = self.request.user
        form.instance.date_posted = timezone.now()
        reply_to = self.request.GET.get('reply_to' or None)
        if reply_to is not None:
            reply = get_object_or_404(Replies, id=reply_to)
            form.instance.reply_to = reply
            if self.request.user != reply.author:
                notify.send(self.request.user, recipient=reply.author, verb="ответил(а) на Ваше сообщение в обсуждении.", action_object=reply.post)
        logger.warning(f'{datetime.now()}: {form.instance.author} ответил в обсуждении {form.instance.post_id}: {form.instance.reply}')
        # obj = form.save(commit=False)
        # if self.request.FILES:
        #     for f in self.request.FILES.getlist('attachments'):
        #         print(f)
        #         obj = self.model.objects.create(file=f)

        # if form.instance.reply_to.post.id != form.instance.post_id:
        #     return redirect('post-detail', pk=form.instance.post_id)
        #form.instance.attachments = self.request.POST.get('attachments')
        return super().form_valid(form)

class RepliesUpdateView(LoginRequiredMixin, UpdateView):
    model = Replies
    template_name = 'forum/reply_form.html'
    context_object_name = 'replies'
    form_class = ReplyForm

    def get_success_url(self):
        # print(self.pk)
        return reverse('post-detail', kwargs={'pk': self.kwargs.get('pk')})

    def get_context_data(self, **kwargs):
        context = super(RepliesUpdateView, self).get_context_data(**kwargs)
        # reply = self.request.GET.get('reply_to' or None)
        # if reply is not None:
        #     context['reply'] = get_object_or_404(Replies, id=reply)
        #     context['is_reply'] = True

        context['update'] = True
        return context

    def get_object(self, queryset=None):
        reply_id = self.kwargs.get('reply_pk')
        return get_object_or_404(Replies, id=reply_id)

    def form_valid(self, form):
        reply = self.get_object()
        logger.warning(f'{datetime.now()}: {form.instance.author} изменил своё сообщение в обсуждении {reply.post_id} с "{reply.reply}" на {form.instance.reply}')
        return super().form_valid(form)

class ReplyDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Replies

    def get_success_url(self):
        return reverse('post-detail', kwargs={'pk': self.kwargs.get('pk')})

    def get_object(self, queryset=None):
        reply_id = self.kwargs.get('reply_pk')
        return get_object_or_404(Replies, id=reply_id)

    def test_func(self):
        reply = self.get_object()
        if self.request.user == reply.author or self.request.user.is_staff:
            return True
        return False
