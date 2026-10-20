import uuid
from django.db import models
from django.conf import settings

# Create your models here.



class LearningSession(models.Model):

    SESSION_TYPE_CHOICES = [
        ('online', 'Online'),
        ('in_person', 'In Person'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    session_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='teaching_sessions')

    learner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='learning_sessions', null=True, blank=True)

    skill = models.ForeignKey('skills.Skill', on_delete=models.CASCADE)

    match = models.ForeignKey('matching.Match', on_delete=models.SET_NULL, null=True, blank=True)

    session_date = models.DateField()
    start_time = models.TimeField()
    duration_minutes = models.PositiveIntegerField()

    session_type = models.CharField(
        max_length=20,
        choices=SESSION_TYPE_CHOICES
    )

    meeting_link = models.URLField(blank=True)

    credit_cost = models.PositiveIntegerField(default=0)

    teacher_confirmed = models.BooleanField(default=False)
    learner_confirmed = models.BooleanField(default=False)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"{self.skill.name} session with {self.teacher.username}"
