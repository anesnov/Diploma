from datetime import timezone

from django.db import models
from django.contrib.auth.models import User
from tagging.registry import register
from django.utils import timezone
from django.urls import reverse


# Create your models here.
class Task(models.Model):
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='%(class)s_requests_created') # От кого
    to_user = models.ForeignKey(User, on_delete=models.CASCADE) # Кому
    title = models.CharField(max_length=100)
    description = models.TextField()
    done = models.BooleanField(default=False) # Статус
    is_urgent = models.BooleanField(default=False) # Важность
    date_created = models.DateTimeField(default=timezone.now) # Дата создания
    date_completion = models.DateTimeField(default=timezone.now, blank=True, null=True) # Дата окончания

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('task-detail', kwargs={'pk': self.pk})

    class Meta:
        verbose_name = "Задача"
        verbose_name_plural = "Задачи"


register(Task)

# class Tag(models.Model):
#     name = models.CharField(max_length=100)
#     color = models.CharField(max_length=10, default='#5EFF00')
#     def __str__(self):
#         return self.name
#     class Meta:
#         verbose_name = "Тег"
#
# class TaggedItem(models.Model):
#     tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
#     task = models.ForeignKey(Task, on_delete=models.CASCADE)