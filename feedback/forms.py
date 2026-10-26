from django import forms
from .models import Review, Report
from accounts.forms import add_bootstrap_classes

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ["rating", "comment"]
        widgets = {
            "comment": forms.Textarea(attrs={"rows": 4, "placeholder": "What did you learn? How was it?"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        add_bootstrap_classes(self)



class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ["category", "details"]
        widgets = {
            "details": forms.Textarea(attrs={"rows": 4, "placeholder": "Tell us what happened..."}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["category"].choices = [
            ("fake_skill", "Fake skill"),
            ("misleading_profile", "Misleading profile"),
            ("inappropriate", "Inappropriate behavior"),
            ("session_complaint", "Session complaint"),
        ]
        add_bootstrap_classes(self)


class IssueForm(forms.ModelForm):

    class Meta:
        model = Report
        fields = ["details"]
        widgets = {
            "details": forms.Textarea(attrs={"rows": 4, "placeholder": "Tell us what happened..."}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        add_bootstrap_classes(self)
