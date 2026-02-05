from django.db import models
from django.conf import settings

class Payment(models.Model):
    STATUS_CHOICES = (
        ("initialized", "Initialized"),
        ("success", "Success"),
        ("failed", "Failed"),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField()  # kobo
    reference = models.CharField(max_length=100, unique=True)
    #paystack_reference = models.CharField(max_length=100, unique=True, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    raw_response = models.JSONField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} – {self.reference} – {self.status}"
