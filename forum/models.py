from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse

class SectionTheme(models.Model):
    name = models.CharField(max_length=150)
    priority = models.IntegerField(default=0)

    def __str__(self):
        return self.name

    def count(self):
        return Section.objects.filter(section_theme=self).count()

    class Meta:
        verbose_name = "Тематика раздела"
        verbose_name_plural = "Тематики разделов"


class Section(models.Model):
    name = models.CharField(max_length=300)
    theme = models.ForeignKey(SectionTheme, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Раздел"
        verbose_name_plural = "Разделы"

class Post(models.Model):
    title = models.CharField(max_length=500)
    content = models.TextField()
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    date_created = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('post-detail', kwargs={'pk': self.pk})

    class Meta:
        verbose_name = "Обсуждение"
        verbose_name_plural = "Обсуждения"

class Replies(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    reply = models.TextField()
    date_posted = models.DateTimeField(default=timezone.now)
    attachments = models.FileField(upload_to='attachments', blank=True, null=True)
    reply_to = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.reply

    def is_reply(self):
        return self.reply_to is not None

    # def get_absolute_url(self):
    #     return reverse('post-detail', kwargs={'pk': self.post.id})

    class Meta:
        verbose_name = "Ответ"
        verbose_name_plural = "Ответы"