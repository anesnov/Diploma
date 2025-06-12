from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.
class Message(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='%(class)s_requests_created')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = 'Message'