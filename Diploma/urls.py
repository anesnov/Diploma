"""
URL configuration for Diploma project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.template.defaulttags import url
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from django.views.decorators.cache import cache_page
from django.views.i18n import JavaScriptCatalog
from rest_framework.authtoken.views import obtain_auth_token
from forum.views import notification_view, read_all_notifications


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('forum.urls')),
    path('api-token-auth/', obtain_auth_token),
    path('inbox/notifications/', include('notifications.urls', namespace='notifications')),
    path('notifications/', notification_view, name='notification_list'),
    path('notifications/read_all', read_all_notifications, name='read_all_notifications'),
    path(
            'jsi18n/',
            cache_page(3600)(JavaScriptCatalog.as_view(packages=['formset'])),
            name='javascript-catalog'
        ),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)