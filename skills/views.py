from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render

from skills.forms import SkillForm
from accounts.views import not_admin
from .models import LEVEL_CHOICES, Skill, UserSkill


@login_required
def my_skills(request):

    me = request.user

    if request.method == "POST":
        action = request.POST.get("action", "")

        if action == "add":
            skill = get_object_or_404(Skill, pk=request.POST.get("skill"))
            kind = request.POST.get("kind", "")
            level = request.POST.get("level", "beginner")

            if kind not in ("teach", "learn"):
                messages.error(request, "Choose whether you can teach or want to learn this skill.")
            elif level not in dict(LEVEL_CHOICES):
                messages.error(request, "Choose a valid level.")
            elif UserSkill.objects.filter(user=me, skill=skill, kind=kind).exists():
                label = "teaching" if kind == "teach" else "learning"
                messages.error(request, f"{skill.name} is already on your {label} list.")
            else:
                UserSkill.objects.create(user=me, skill=skill, kind=kind, level=level)
                messages.success(request, f"{skill.name} added to your skills.")
            return redirect("skills")

        if action == "update":
            user_skill = get_object_or_404(UserSkill, pk=request.POST.get("user_skill"), user=me)
            level = request.POST.get("level", "")
            if level in dict(LEVEL_CHOICES):
                user_skill.level = level
                user_skill.save()
                messages.success(request, f"{user_skill.skill.name} updated.")
            else:
                messages.error(request, "Choose a valid level.")
            return redirect("skills")

        if action == "remove":
            user_skill = get_object_or_404(UserSkill, pk=request.POST.get("user_skill"), user=me)
            name = user_skill.skill.name
            user_skill.delete()
            messages.info(request, f"{name} removed from your skills.")
            return redirect("skills")

    query = request.GET.get("q", "").strip()
    category = request.GET.get("category", "")

    catalog = Skill.objects.annotate(
        teacher_total=Count("userskill", filter=Q(userskill__kind="teach")),
        learner_total=Count("userskill", filter=Q(userskill__kind="learn")),
    )
    if query:
        catalog = catalog.filter(Q(name__icontains=query) | Q(category__icontains=query))
    if category:
        catalog = catalog.filter(category=category)
    catalog = catalog.order_by("category", "name")

    # Most-used skills make the best starting point for someone new.
    popular = (
        Skill.objects.annotate(
            teacher_total=Count("userskill", filter=Q(userskill__kind="teach")),
            learner_total=Count("userskill", filter=Q(userskill__kind="learn")),
            total=Count("userskill"),
        )
        .order_by("-total", "category", "name")[:8]
    )

    context = {
        "teach_skills": me.skills.filter(kind="teach").select_related("skill").order_by("skill__name"),
        "learn_skills": me.skills.filter(kind="learn").select_related("skill").order_by("skill__name"),
        "learned_skills": me.skills.filter(kind="learned").select_related("skill").order_by("skill__name"),
        "teach_ids": set(me.skills.filter(kind="teach").values_list("skill_id", flat=True)),
        "learn_ids": set(me.skills.filter(kind="learn").values_list("skill_id", flat=True)),
        "learned_ids": set(me.skills.filter(kind="learned").values_list("skill_id", flat=True)),
        "popular": popular,
        "skills": catalog,
        "categories": Skill.objects.values_list("category", flat=True).distinct().order_by("category"),
        "query": query,
        "selected_category": category,
        "levels": LEVEL_CHOICES,
    }
    return render(request, "skills/my_skills.html", context)


@login_required
def delete_skill(request, pk):
    user_skill = get_object_or_404(UserSkill, pk=pk, user=request.user)
    if request.method == "POST":
        user_skill.delete()
        messages.info(request, "Skill removed.")
    return redirect("skills")


@login_required
def admin_skills(request):
    if not_admin(request):
        return redirect("dashboard")

    form = SkillForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        skill = form.save()
        messages.success(request, f"{skill} was added to the catalog.")
        return redirect("admin_skills")

    skills = Skill.objects.all()
    return render(request, "skills/admin_skills.html", {"form": form, "skills": skills})


@login_required
def admin_delete_skill(request, pk):
    if not_admin(request):
        return redirect("dashboard")

    skill = get_object_or_404(Skill, pk=pk)
    if request.method == "POST":
        skill.delete()
        messages.info(request, f"{skill} was removed from the catalog.")
    return redirect("admin_skills")
