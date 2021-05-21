from django.db import models
from django.contrib.auth.models import User
from PIL import Image
from accounts.utils import image_resize


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    logo = models.ImageField(default='default.jpg', upload_to='profile_logo')

    def __str__(self):
        return f'{self.user.username} Profile'


    def save(self, *args, **kwargs):
        image_resize(self.image, 80, 80)
        super().save(*args, **kwargs)

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
