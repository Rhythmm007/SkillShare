from django import forms
from .models import Session
from skills.models import Skill
from accounts.forms import add_bootstrap_classes

class SessionRequestForm(forms.ModelForm):
    class Meta:
        model = Session
        fields = ["mode", "skill", "swap_skill", "date", "time", "duration", "note"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "time": forms.TimeInput(attrs={"type": "time"}),
            "note": forms.Textarea(attrs={"rows": 3, "placeholder": "What would you like to focus on?"}),
        }
        labels = {
            "skill": "Skill you want to learn",
            "swap_skill": "Skill you will teach in return (for swaps)",
        }

    def __init__(self, *args, teacher=None, learner=None, direction="learn", **kwargs):

        super().__init__(*args, **kwargs)
        self.direction = direction

        teacher_skill_ids = teacher.teach_skills().values_list("skill_id", flat=True)
        self.fields["skill"].queryset = Skill.objects.filter(id__in=teacher_skill_ids)
        learner_skill_ids = learner.teach_skills().values_list("skill_id", flat=True)

        self.fields["swap_skill"].queryset = Skill.objects.filter(id__in=learner_skill_ids)
        self.fields["swap_skill"].required = False

        if direction == "teach":
            self.fields["skill"].label = "Skill you will teach"
            self.fields["swap_skill"].label = "Skill they will teach you in return (for swaps)"


        add_bootstrap_classes(self)

    def clean(self):

        cleaned_data = super().clean()
        mode = cleaned_data.get("mode")
        swap_skill = cleaned_data.get("swap_skill")


        if mode == "swap" and not swap_skill:
            if self.direction == "teach":
                self.add_error("swap_skill", "Choose a skill they will teach you in return.")
            else:
                self.add_error("swap_skill", "Choose a skill to teach in return.")
        return cleaned_data