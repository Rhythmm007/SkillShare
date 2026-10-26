from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Our custom user. A 'user' can teach and learn. An 'admin' manages the site."""

    ROLE_CHOICES = [
        ("user", "User"),
        ("admin", "Admin"),
    ]

    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="user")
    bio = models.TextField(blank=True)
    location = models.CharField(max_length=100, blank=True)
    photo = models.ImageField(upload_to="photos/", blank=True, null=True)
    credits = models.IntegerField(default=20)  # every new user gets 20 credits

    def save(self, *args, **kwargs):
        # A superuser (created with createsuperuser) is always an admin
        if self.is_superuser:
            self.role = "admin"
        super().save(*args, **kwargs)

    def is_admin(self):
        return self.role == "admin"

    def display_name(self):
        return self.get_full_name() or self.username

    def teach_skills(self):
        return self.skills.filter(kind="teach")

    def learn_skills(self):
        return self.skills.filter(kind="learn")

    def learned_skills(self):
        return self.skills.filter(kind="learned")

    def average_rating(self):
        from feedback.models import Review
        # ratings = [review.rating for review in Review.objects.filter(reviewed_user=self)]
        ratings = []

        for review in Review.objects.filter(reviewed_user=self):
            ratings.append(review.rating)

        if not ratings:
            return 0
        return round(sum(ratings) / len(ratings), 1)

    def review_count(self):
        from feedback.models import Review
        return Review.objects.filter(reviewed_user=self).count()

    def locked_credits(self):
        from learning_sessions.models import Session
        sessions = Session.objects.filter(learner=self, escrow="locked")
        return sum(session.cost for session in sessions)

    def earned_credits(self):
        from wallets.models import Transaction
        transactions = Transaction.objects.filter(user=self, type="earn")
        return sum(t.amount for t in transactions)

    def __str__(self):
        return self.display_name()


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    text = models.CharField(max_length=255)
    link = models.CharField(max_length=200, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.text

