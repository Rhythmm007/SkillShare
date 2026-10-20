from django.db import models

# Create your models here.

import uuid
from django.conf import settings


class Wallet(models.Model):
    wallet_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    balance = models.PositiveIntegerField(default=0)
    locked_balance = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.user.username}'s Wallet"


class Transaction(models.Model):

    TRANSACTION_TYPE_CHOICES = [
        ('deposit', 'Deposit'),
        ('reserve', 'Reserve Credits'),
        ('release', 'Release to Teacher'),
        ('refund', 'Refund'),
        ('transfer', 'Transfer'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]

    transaction_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)

    session = models.ForeignKey('learning_sessions.LearningSession',
                                on_delete=models.SET_NULL, null=True, blank=True)

    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE_CHOICES)

    amount = models.PositiveIntegerField()

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.transaction_type}: {self.amount} credits"
