from django.db import models
from django.contrib.auth.models import User
from PIL import Image
from accounts.utils import image_resize
from django.contrib.auth.models import Group


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  #, related_name='profile')
    #group = models.ForeignKey(Group, on_delete=models.CASCADE)
    logo = models.ImageField(default='profile_logo/default.jpg', upload_to='profile_logo')

    def __str__(self):
        return f'{self.user} profile'

    def save(self, *args, **kwargs):
        image_resize(self.logo, 120, 120)
        super().save(*args, **kwargs)

    # def delete(self, *args, **kwargs):
    #     self.logo.delete()
    #     self.logo.profile.image.delete(save=False)
    #     super().delete(*args, **kwargs)

    def SetUserImageDefault(self):
        self.user.profile.logo.delete(save=False)  # delete old image file
        self.user.profile.logo = 'default.jpg'  # set default image
        self.user.profile.save()



    # # Override the save method of the model
    # def save(self, *args, **kwargs):
    #     super(Profile, self).save(*args, **kwargs)
    #
    #     img = Image.open(self.logo.path)  # Open image
    #
    #     # resize image
    #     if img.height > 70 or img.width > 70:
    #         output_size = (70, 70)
    #         img.thumbnail(output_size)  # Resize image
    #         img.save(self.logo.path)  # Save it again and override the larger image


class UserGroups(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)


    def __str__(self):
        return self.group


# class Group(models.Model):
#     myuser = models.ForeignKey(User, related_name='groups')