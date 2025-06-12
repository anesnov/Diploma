from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from login_modal.models import Profile


# @receiver(post_save, sender=User)
# def create_profile(sender, instance, created, **kwargs):
#     if created:
#         Profile.objects.create(user=instance, first_name=instance.first_name, last_name=instance.last_name, middle_name=instance.middle_name)


# @receiver(post_save, sender=User)
# def save_profile(sender, instance, **kwargs):
#     instance.profile.save()