from django.shortcuts import render, get_object_or_404, redirect
from datetime import datetime
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q

from .forms import MessageForm
from learning_sessions.forms import SessionRequestForm
from accounts.models import User, Notification
from skills.models import Skill, UserSkill
from learning_sessions.models import Session
from feedback.models import Review
from .models import Message

# Create your views here.


def get_match(me, other):
    my_wanted_ids = list(me.learn_skills().values_list("skill_id", flat=True))
    their_wanted_ids = list(other.learn_skills().values_list("skill_id", flat=True))

    they_teach = [s for s in other.teach_skills() if s.skill_id in my_wanted_ids]

    i_teach = [s for s in me.teach_skills() if s.skill_id in their_wanted_ids]

    is_swap = len(they_teach) > 0 and len(i_teach) > 0

    score = 0
    if they_teach:
        score += 50
    if is_swap:
        score += 30
    score += int(other.average_rating() * 4)
    if score > 100:
        score = 100

    return {
        "user": other,
        "they_teach": they_teach,
        "i_teach": i_teach,
        "is_swap": is_swap,
        "score": score,
    }


def get_all_matches(me):
    people = (
        User.objects.filter(role="user", is_active=True, skills__kind="teach")
        .exclude(id=me.id)
        .distinct()
    )
    matches = []
    for person in people:
        match = get_match(me, person)
        if match["they_teach"]:
            matches.append(match)
    matches.sort(key=lambda m: m["score"], reverse=True)
    return matches


@login_required
def discover(request):
    me = request.user
    query = request.GET.get("q", "").strip()
    category = request.GET.get("category", "")
    kind = request.GET.get("kind", "")

    matches = get_all_matches(me)
    if query:
        matches = [
            m for m in matches
            if query.lower() in m["user"].display_name().lower()
            or any(query.lower() in s.skill.name.lower() for s in m["user"].teach_skills())
        ]
    if category:
        matches = [m for m in matches if any(s.skill.category == category for s in m["they_teach"])]

    swap_matches = [m for m in matches if m["is_swap"]]

    entries = (
        UserSkill.objects.filter(kind__in=["teach", "learn"])
        .exclude(user=me)
        .filter(user__role="user", user__is_active=True)
        .select_related("user", "skill")
    )

    if query:
        entries = entries.filter(
            Q(skill__name__icontains=query)
            | Q(skill__category__icontains=query)
            | Q(user__first_name__icontains=query)
            | Q(user__last_name__icontains=query)
            | Q(user__username__icontains=query)
            | Q(user__location__icontains=query)
        )
    if category:
        entries = entries.filter(skill__category=category)
    if kind in ("teach", "learn"):
        entries = entries.filter(kind=kind)

    entries = sorted(
        entries,
        key=lambda e: (
            e.kind != "teach",
            e.skill.category.lower(),
            e.skill.name.lower(),
            e.user.display_name().lower(),
        ),
    )

    context = {
        "swap_matches": swap_matches,
        "entries": entries,
        "teach_count": sum(1 for entry in entries if entry.kind == "teach"),
        "learn_count": sum(1 for entry in entries if entry.kind == "learn"),
        "my_teach_ids": set(me.teach_skills().values_list("skill_id", flat=True)),
        "categories": Skill.objects.values_list("category", flat=True).distinct().order_by("category"),
        "query": query,
        "selected_category": category,
        "selected_kind": kind,
    }
    return render(request, "matching/discover.html", context)


@login_required
def user_profile(request, pk):
    person = get_object_or_404(User, pk=pk, role="user")
    me = request.user

    direction = request.GET.get("direction", "learn")
    if direction not in ("learn", "teach"):
        direction = "learn"

    if direction == "teach":
        teacher, learner = me, person
    else:
        teacher, learner = person, me

    match = get_match(me, person)
    reviews = Review.objects.filter(reviewed_user=person)

    initial_mode = "swap" if match["is_swap"] else "credits"
    initial = {"mode": initial_mode}
    requested_skill = request.GET.get("skill")
    if requested_skill:
        initial["skill"] = requested_skill

    form = SessionRequestForm(
        teacher=teacher, learner=learner, direction=direction, initial=initial
    )

    if request.method == "POST":
        form = SessionRequestForm(
            request.POST, teacher=teacher, learner=learner, direction=direction
        )
        if person == me:
            messages.error(request, "You can't book a session with yourself.")
        elif form.is_valid():
            session = form.save(commit=False)
            session.teacher = teacher
            session.learner = learner

            now = datetime.now()
            is_past = session.date < now.date() or (
                session.date == now.date() and session.time < now.time()
            )
            time_taken = Session.objects.filter(
                teacher=teacher,
                date=session.date,
                time=session.time,
                status__in=["requested", "accepted"],
            ).exists()

            if session.mode == "credits":
                teacher_skill = UserSkill.objects.get(user=teacher, skill=session.skill, kind="teach")
                session.cost = teacher_skill.price() * session.duration // 60
                session.swap_skill = None

            if direction == "teach" and not UserSkill.objects.filter(
                user=person, skill=session.skill, kind="learn"
            ).exists():
                messages.error(
                    request,
                    f"{person.display_name} is not looking to learn {session.skill}.",
                )
            elif is_past:
                messages.error(request, "Please pick a date and time in the future.")
            elif time_taken:
                messages.error(request, "That time is already booked. Please pick another time.")
            elif session.mode == "credits" and learner.credits < session.cost:
                if learner == me:
                    messages.error(
                        request,
                        f"Not enough credits. You need {session.cost} but have {learner.credits}. "
                        "Teach a session to earn more.",
                    )
                else:
                    messages.error(
                        request,
                        f"Not enough credits. {learner.display_name} needs {session.cost} "
                        f"but only has {learner.credits}.",
                    )
            else:
                session.requested_by = me
                session.save()

                if direction == "learn" and session.mode == "credits":
                    session.lock_credits()
                    Notification.objects.create(
                        user=learner,
                        text=f"{session.cost} credits are locked in escrow until your session is complete.",
                        link="/wallet/",
                    )

                if direction == "teach":
                    Notification.objects.create(
                        user=person,
                        text=f"{me} wants to teach you {session.skill}. Accept or decline the request.",
                        link="/sessions/",
                    )
                elif session.mode == "credits":
                    Notification.objects.create(
                        user=teacher,
                        text=f"{learner} wants to learn {session.skill} from you for {session.cost} credits.",
                        link="/sessions/",
                    )
                else:
                    Notification.objects.create(
                        user=teacher,
                        text=f"{learner} wants to swap {session.swap_skill} for {session.skill}.",
                        link="/sessions/",
                    )
                messages.success(request, "Session requested! You will be notified when it is confirmed.")
                return redirect("sessions")

    context = {
        "person": person,
        "match": match,
        "reviews": reviews,
        "form": form,
        "direction": direction,
        "sessions_taught": person.teaching_sessions.filter(status="completed").count(),
    }
    return render(request, "matching/user_profile.html", context)


@login_required
def inbox(request, user_id=None):
    me = request.user


    all_messages = Message.objects.filter(Q(sender=me) | Q(receiver=me)).order_by("-created_at")
    people = []
    for msg in all_messages:
        other = msg.receiver if msg.sender == me else msg.sender
        if other not in people:
            people.append(other)

    conversations = []
    for person in people:
        last_message = all_messages.filter(Q(sender=person) | Q(receiver=person)).first()
        unread = Message.objects.filter(sender=person, receiver=me, is_read=False).count()
        conversations.append({"user": person, "last": last_message, "unread": unread})

    other_user = None
    thread = []
    form = MessageForm()

    if user_id:
        other_user = get_object_or_404(User, pk=user_id)

        if request.method == "POST":
            form = MessageForm(request.POST)
            if form.is_valid():
                message = form.save(commit=False)
                message.sender = me
                message.receiver = other_user
                message.save()
                Notification.objects.create(
                    user=other_user, text=f"New message from {me}", link=f"/messages/{me.pk}/"
                )
                return redirect("conversation", user_id=other_user.pk)

        thread = Message.objects.filter(
            Q(sender=me, receiver=other_user) | Q(sender=other_user, receiver=me)
        )

        Message.objects.filter(sender=other_user, receiver=me, is_read=False).update(is_read=True)

    context = {
        "conversations": conversations,
        "other_user": other_user,
        "thread": thread,
        "form": form,
    }
    return render(request, "matching/messages.html", context)

