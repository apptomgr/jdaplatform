from django.db.models.signals import post_save #Import a post_save signal when a user is created
from django.contrib.auth.models import User # Import the built-in User model, which is a sender
from django.dispatch import receiver # Import the receiver
from .models import Profile
from django.db.models.signals import pre_save
import os


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    instance.profile.save()


@receiver(pre_save, sender=Profile)
def delete_old_file(sender, instance, **kwargs):
    # on creation, signal callback won't be triggered
    if instance._state.adding and not instance.pk:
        return False

    try:
        old_file = sender.objects.get(pk=instance.pk).logo
        #print(f'signal 28: {old_file} type: {type(old_file)} name: {old_file.name}')
    except sender.DoesNotExist:
        return False

    # comparing the new file with the old one
    file = instance.logo

    if not old_file == file:
        if old_file != 'default.jpg':
            if os.path.isfile(old_file.path):
                os.remove(old_file.path)
        else:
            pass
            #print(f"signal 41: same_name")