from django import forms
from .models import Message
from accounts.forms import add_bootstrap_classes

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ["text"]
        widgets = {
            "text": forms.TextInput(attrs={"placeholder": "Write a message..."}),
        }
        labels = {"text": ""}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        add_bootstrap_classes(self)
