from django.db import models
from accounts.models import User


# Credits per hour for each teaching level
PRICE_PER_HOUR = {
    "beginner": 6,
    "intermediate": 8,
    "advanced": 12,
}

LEVEL_CHOICES = [
    ("beginner", "Beginner"),
    ("intermediate", "Intermediate"),
    ("advanced", "Advanced"),
]


class Skill(models.Model):
    """A skill in the catalog. Only admins can add skills."""

    name = models.CharField(max_length=60, unique=True)
    category = models.CharField(max_length=60, default="Other")

    class Meta:
        ordering = ["category", "name"]

    def teacher_count(self):
        return UserSkill.objects.filter(skill=self, kind="teach").count()

    def learner_count(self):
        return UserSkill.objects.filter(skill=self, kind="learn").count()

    def __str__(self):
        return self.name


class UserSkill(models.Model):
    """A skill that a user can teach or wants to learn."""

    KIND_CHOICES = [
        ("teach", "I can teach"),
        ("learn", "I want to learn"),
        ("learned", "I have learned"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="skills")
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    kind = models.CharField(max_length=10, choices=KIND_CHOICES)
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default="beginner")

    class Meta:
        unique_together = ["user", "skill", "kind"]

    def price(self):
        return PRICE_PER_HOUR[self.level]

    def __str__(self):
        return f"{self.skill.name} ({self.get_level_display()})"

