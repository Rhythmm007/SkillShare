from django.db import models

# Create your models here.

import uuid

from django.db import models
from django.conf import settings


class Match(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    match_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user1 = models.ForeignKey( settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='matches_as_user1')

    user2 = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='matches_as_user2')

    skill_offered = models.ForeignKey('skills.Skill', on_delete=models.CASCADE, related_name='matches_offering')

    skill_requested = models.ForeignKey('skills.Skill', on_delete=models.CASCADE, related_name='matches_requesting')

    match_score = models.FloatField(default=0.0)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user1.username} - {self.user2.username}"

