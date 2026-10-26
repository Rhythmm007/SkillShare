from django.db import models
from accounts.models import User
from learning_sessions.models import Session


class Transaction(models.Model):
    TYPE_CHOICES = [
        ("lock", "Session booked"),
        ("earn", "Teaching"),
        ("refund", "Refund"),
        ("bonus", "Bonus"),
    ]
    STATUS_CHOICES = [
        ("escrow", "Escrow"),
        ("released", "Released"),
        ("refunded", "Refunded"),
        ("earned", "Earned"),
        ("bonus", "Bonus"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="transactions")
    session = models.ForeignKey(Session, on_delete=models.SET_NULL, null=True, blank=True)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    amount = models.IntegerField()
    description = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user} {self.amount}"

