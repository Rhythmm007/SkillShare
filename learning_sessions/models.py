from django.db import models
from accounts.models import User
from skills.models import Skill


class Session(models.Model):

    MODE_CHOICES = [
        ("swap", "Swap skills"),
        ("credits", "Pay with credits"),
    ]
    STATUS_CHOICES = [
        ("requested", "Pending"),
        ("accepted", "Confirmed"),
        ("rejected", "Declined"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
        ("disputed", "In dispute"),
        ("no_show", "No-show"),
    ]
    ESCROW_CHOICES = [
        ("none", "None"),
        ("locked", "Locked"),
        ("released", "Released"),
        ("refunded", "Refunded"),
    ]
    DURATION_CHOICES = [
        (30, "30 minutes"),
        (60, "1 hour"),
        (90, "1.5 hours"),
        (120, "2 hours"),
    ]

    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name="teaching_sessions")
    learner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="learning_sessions")
    requested_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="requested_sessions"
    )
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name="sessions")
    swap_skill = models.ForeignKey(
        Skill, on_delete=models.SET_NULL, null=True, blank=True, related_name="swap_sessions"
    )
    mode = models.CharField(max_length=10, choices=MODE_CHOICES, default="swap")
    cost = models.IntegerField(default=0)
    date = models.DateField()
    time = models.TimeField()
    duration = models.IntegerField(choices=DURATION_CHOICES, default=60)
    note = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="requested")
    escrow = models.CharField(max_length=10, choices=ESCROW_CHOICES, default="none")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date", "-time"]

    def other_person(self, user):
        if user == self.teacher:
            return self.learner
        return self.teacher

    def lock_credits(self):
        from wallets.models import Transaction
        self.learner.credits -= self.cost
        self.learner.save()
        self.escrow = "locked"
        self.save()
        Transaction.objects.create(
            user=self.learner,
            session=self,
            type="lock",
            status="escrow",
            amount=-self.cost,
            description=f"{self.skill.name} lesson with {self.teacher}",
        )

    def refund(self):
        from wallets.models import Transaction
        from accounts.models import Notification
        if self.escrow != "locked":
            return
        self.learner.credits += self.cost
        self.learner.save()
        self.escrow = "refunded"
        self.save()
        Transaction.objects.filter(session=self, type="lock").update(status="refunded")
        Transaction.objects.create(
            user=self.learner,
            session=self,
            type="refund",
            status="refunded",
            amount=self.cost,
            description=f"Refund for {self.skill.name} lesson",
        )
        Notification.objects.create(
            user=self.learner,
            text=f"{self.cost} credits were refunded to your wallet.",
            link="/wallet/",
        )

    def release(self):
        from wallets.models import Transaction
        from accounts.models import Notification
        if self.escrow != "locked":
            return
        self.teacher.credits += self.cost
        self.teacher.save()
        self.escrow = "released"
        self.save()
        Transaction.objects.filter(session=self, type="lock").update(status="released")
        Transaction.objects.create(
            user=self.teacher,
            session=self,
            type="earn",
            status="earned",
            amount=self.cost,
            description=f"Taught {self.skill.name} to {self.learner}",
        )
        Notification.objects.create(
            user=self.teacher,
            text=f"You earned {self.cost} credits for teaching {self.skill.name}.",
            link="/wallet/",
        )

    def __str__(self):
        return f"{self.skill} - {self.teacher} teaches {self.learner}"

