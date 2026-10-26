from django.db import models
from accounts.models import User
from learning_sessions.models import Session


class Review(models.Model):
    RATING_CHOICES = [
        (5, "5 - Excellent"),
        (4, "4 - Good"),
        (3, "3 - Okay"),
        (2, "2 - Poor"),
        (1, "1 - Bad"),
    ]

    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name="reviews")
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviews_given")
    reviewed_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviews_received")
    rating = models.IntegerField(choices=RATING_CHOICES, default=5)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        unique_together = ["session", "reviewer"]

    def __str__(self):
        return f"{self.reviewer} rated {self.reviewed_user} {self.rating}"


class Report(models.Model):
    CATEGORY_CHOICES = [
        ("fake_skill", "Fake skill"),
        ("misleading_profile", "Misleading profile"),
        ("inappropriate", "Inappropriate behavior"),
        ("session_complaint", "Session complaint"),
        ("no_show", "No-show"),
        ("dispute", "Credit dispute"),
    ]
    STATUS_CHOICES = [
        ("open", "Open"),
        ("resolved", "Resolved"),
        ("dismissed", "Dismissed"),
    ]

    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reports_made")
    reported_user = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True, related_name="reports_received"
    )
    session = models.ForeignKey(Session, on_delete=models.SET_NULL, null=True, blank=True)
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES)
    details = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="open")
    resolution = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.get_category_display()} by {self.reporter}"

