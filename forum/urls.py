from django.urls import path
from django.contrib.auth import views as auth_views

from login_modal.views import profile_view, profile_update
from . import views
from rest_framework.routers import DefaultRouter

from login_modal import views as login_modal_views
from company_structure.views import structure
from tasks.views import *
import chat.views
from .views import (
    PostListView,
    PostDetailView,
    PostCreateView,
    PostUpdateView,
    PostDeleteView,
    UserPostListView,
    RepliesListView,
    sections, RepliesCreateView, replies
)

urlpatterns = [
    #path('',  PostListView.as_view(), name='home'), #views.index
    path('',  sections, name='home'),
    path('section/<int:pk>/', PostListView.as_view(), name='section'),
    path('about', views.about, name='about'),
    path('company/', structure, name='company'),
    path("user/", login_modal_views.profile_update, name="profile"),
    path("_login/", login_modal_views.login, name="login"),
    path("register/", login_modal_views.register, name="register"),
    # path("logout/", login_modal_views.logout, name="logout"),
    path('logout/', auth_views.LogoutView.as_view(template_name='homepage/frontpage.html'), name='logout'),

    path('user/<str:username>/', profile_view, name='profile'),
    path('user/<str:username>/update/', profile_update, name='profile-update'),
    path('user/<str:username>/posts/', UserPostListView.as_view(), name='user-posts'),

    path('user/<str:username>/promote_to_staff', views.promote, name="promote_to_staff"),
    path('user/<str:username>/demote_staff', views.demote, name="demote_staff"),

    path('user/<str:username>/dm/', chat.views.chat, name='chat'),
    path('user/<str:username>/dm/create-message/', chat.views.create_message, name='create-message'),
    path('user/<str:username>/dm/stream-chat-messages/', chat.views.stream_chat_messages, name='stream-chat-messages'),

    path('user/<str:username>/tasks/', UserTaskListView.as_view(), name='user-tasks'),
    path('user/<str:username>/tasks/new/', TaskCreateView.as_view(), name='task-create'),
    path('tasks/<int:pk>/', TaskDetailView.as_view(), name='task-detail'),
    path('tasks/<int:pk>/delete/', TaskDeleteView.as_view(), name='task-delete'),
    path('tasks/<int:pk>/update/', TaskUpdateView.as_view(), name='task-update'),
    path('tasks/<int:pk>/complete', task_complete, name='task-complete'),
    path('tasks/<int:pk>/uncomplete', task_uncomplete, name='task-uncomplete'),


    path('post/new/', PostCreateView.as_view(), name='post-create'),
    path('post/<int:pk>/', replies, name='post-detail'),
    path('post/<int:pk>/reply/', RepliesCreateView.as_view(), name='reply-create'),
    path('post/<int:pk>/update/', PostUpdateView.as_view(), name='post-update'),
    path('post/<int:pk>/delete/', PostDeleteView.as_view(), name='post-delete'),
]

router = DefaultRouter()
router.register(r'tasks', TaskViewSet, basename='task')
urlpatterns += router.urls