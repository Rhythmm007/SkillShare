from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Skill, UserSkill

admin.site.register(Skill)
admin.site.register(UserSkill)