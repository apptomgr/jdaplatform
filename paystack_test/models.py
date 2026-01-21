from django.db import models

class Payment(models.Model):
    email = models.EmailField()
    amount = models.PositiveIntegerField(help_text="Amount in kobo")
    reference = models.CharField(max_length=100, unique=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ("initialized", "Initialized"),
            ("paid", "Paid"),
            ("failed", "Failed"),
        ],
        default="initialized",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def amount_display(self):
        return self.amount / 100

    def __str__(self):
        return f"{self.email} - {self.amount_display()} - {self.status}"
