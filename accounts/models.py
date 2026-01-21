from django.db import models
from django.contrib.auth.models import User
from PIL import Image
from accounts.utils import image_resize
from django.contrib.auth.models import Group
from django.utils.text import slugify
#from .models import SubscriptionPlan

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  #, related_name='profile')
    #group = models.ForeignKey(Group, on_delete=models.CASCADE)
    logo = models.ImageField(default='default.jpg', upload_to='profile_logo')

    def __str__(self):
        return f'{self.user} profile'

    def save(self, *args, **kwargs):
        image_resize(self.logo, 120, 120)
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


class UserGroups(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)


    def __str__(self):
        return self.group


# class Group(models.Model):
#     myuser = models.ForeignKey(User, related_name='groups')


# #////////////////////////////////UserPendingSubscription//////////////////////////////////////////
# class UserPendingSubscription(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE)
#     billing_frequency = models.CharField(max_length=10,choices=[('monthly', 'Monthly'), ('quarterly', 'Quarterly'), ('yearly', 'Yearly')],default='monthly')
#     created_at = models.DateTimeField(auto_now_add=True)
#
#     def __str__(self):
#         return f"{self.user.username} → {self.plan.name} ({self.billing_frequency})"
#
#
# #////////////////////////////////SubscriptionPlan//////////////////////////////////////////
# class SubscriptionPlan(models.Model):
#     CUSTOMER = "customer"
#     INSTITUTION = "institution"
#
#     PLAN_CATEGORY_CHOICES = [
#         (CUSTOMER, "Customer"),
#         (INSTITUTION, "Institution"),
#     ]
#
#     BILLING_MONTHLY = "monthly"
#     BILLING_QUARTERLY = "quarterly"
#     BILLING_YEARLY = "yearly"
#
#     BILLING_CYCLE_CHOICES = [
#         (BILLING_MONTHLY, "Monthly"),
#         (BILLING_QUARTERLY, "Quarterly"),
#         (BILLING_YEARLY, "Yearly"),
#     ]
#
#     # -----------------------------
#     # CORE FIELDS
#     # -----------------------------
#     name = models.CharField(max_length=150)
#     slug = models.SlugField(unique=True, max_length=180)
#     category = models.CharField(
#         max_length=20,
#         choices=PLAN_CATEGORY_CHOICES,
#         default=CUSTOMER,
#     )
#
#     # Pricing for each billing cycle (some may be null if not offered)
#     price_monthly = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
#     price_quarterly = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
#     price_yearly = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
#
#     # Optional description
#     description = models.TextField(blank=True)
#
#     # Whether plan should be shown in UI
#     active = models.BooleanField(default=True)
#
#     # For ordering in pricing grid
#     sort_order = models.PositiveIntegerField(default=0)
#
#     # Timestamp
#     created_at = models.DateTimeField(auto_now_add=True)
#
#     # -----------------------------
#     # METHODS
#     # -----------------------------
#     def save(self, *args, **kwargs):
#         """Auto-generate slug on creation"""
#         if not self.slug:
#             self.slug = slugify(self.name)
#         super().save(*args, **kwargs)
#
#     def price_for_cycle(self, cycle: str):
#         """
#         Return the price for the given billing cycle.
#         """
#         cycle = (cycle or "").lower()
#
#         if cycle == self.BILLING_MONTHLY:
#             return self.price_monthly
#         if cycle == self.BILLING_QUARTERLY:
#             return self.price_quarterly
#         if cycle == self.BILLING_YEARLY:
#             return self.price_yearly
#
#         return None
#
#     def __str__(self):
#         return f"{self.name} ({self.category})"
