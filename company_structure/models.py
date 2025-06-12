from django.db import models


class Position(models.Model):
    name = models.CharField(max_length=150)
    is_head = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Должность"
        verbose_name_plural = "Должности"

class Department(models.Model):
    name = models.CharField(max_length=150)
    is_director = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Отдел"
        verbose_name_plural = "Отделы"

# Create your models here.
