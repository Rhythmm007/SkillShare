from django import forms
from .models import UserSkill, Skill
from accounts.forms import add_bootstrap_classes

class UserSkillForm(forms.ModelForm):

    class Meta:
        model = UserSkill
        fields = ["skill", "level"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        add_bootstrap_classes(self)


class SkillForm(forms.ModelForm):

    class Meta:
        model = Skill
        fields = ["name", "category"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        add_bootstrap_classes(self)
