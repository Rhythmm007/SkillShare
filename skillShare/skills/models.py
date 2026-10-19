from django.db import models

# Create your models here.

import uuid

from django.db import models
from django.conf import settings


class Skill(models.Model):
    skill_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name


class UserSkill(models.Model):
    userSkill_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user_skills')

    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name='users')
    skill_type = models.CharField(max_length=20)
    experience = models.IntegerField()
    credit_rate = models.IntegerField()
    progress = models.FloatField(default=0.0)

    def __str__(self):
        return f"{self.user.username} - {self.skill.name} ({self.skill_type})"

