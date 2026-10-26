from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from feedback.forms import IssueForm
from accounts.models import Notification
from accounts.views import not_admin
from feedback.models import Review
from skills.models import UserSkill
from .models import Session


@login_required
def sessions(request):
    me = request.user
    my_sessions = Session.objects.filter(Q(teacher=me) | Q(learner=me))

    context = {
        "requests": my_sessions.filter(status="requested").order_by("date", "time"),
        "upcoming": my_sessions.filter(status__in=["accepted", "disputed"]).order_by("date", "time"),
        "past": my_sessions.filter(status__in=["completed", "cancelled", "rejected", "no_show"]),
        "reviewed_ids": list(
            Review.objects.filter(reviewer=me).values_list("session_id", flat=True)
        ),
        "tab": request.GET.get("tab", "upcoming"),
    }
    return render(request, "learning_sessions/sessions.html", context)


@login_required
def session_action(request, pk, action):
    session = get_object_or_404(Session, pk=pk)
    me = request.user

    if request.method != "POST" or me not in [session.teacher, session.learner]:
        return redirect("sessions")

    other = session.other_person(me)

    if action == "accept" and session.status == "requested" and me != session.requested_by:
        # A teacher-made offer locks the learner's credits only when it is accepted.
        if session.mode == "credits" and session.escrow == "none":
            if session.learner.credits < session.cost:
                messages.error(
                    request,
                    f"Not enough credits to accept this request: "
                    f"{session.cost} needed, {session.learner.credits} available.",
                )
                return redirect("sessions")
            session.lock_credits()
        session.status = "accepted"
        session.save()
        Notification.objects.create(user=other, text=f"{me} accepted your {session.skill} session.", link="/sessions/")
        messages.success(request, "Session confirmed.")

    elif action == "reject" and session.status == "requested" and me != session.requested_by:
        session.status = "rejected"
        session.save()
        session.refund()
        Notification.objects.create(user=other, text=f"{me} declined your {session.skill} session.", link="/sessions/")
        messages.info(request, "Request declined.")

    elif action == "cancel" and session.status in ["requested", "accepted"]:
        session.status = "cancelled"
        session.save()
        session.refund()
        Notification.objects.create(user=other, text=f"{me} cancelled the {session.skill} session.", link="/sessions/")
        messages.info(request, "Session cancelled.")

    elif action == "complete" and session.status == "accepted":
        if me != session.learner:
            messages.error(request, "Only the learner can mark this session as completed.")
        else:
            session.status = "completed"
            session.save()
            session.release()

            learn_entry = UserSkill.objects.filter(
                user=session.learner, skill=session.skill, kind="learn"
            ).first()
            UserSkill.objects.update_or_create(
                user=session.learner,
                skill=session.skill,
                kind="learned",
                defaults={"level": learn_entry.level if learn_entry else "beginner"},
            )
            if learn_entry:
                learn_entry.delete()

            Notification.objects.create(user=other, text=f"Your {session.skill} session is complete. Leave a review!", link="/sessions/?tab=past")
            messages.success(request, "Session completed. Don't forget to leave a review!")

    else:
        messages.error(request, "This action is not allowed.")

    return redirect("sessions")


@login_required
def session_issue(request, pk, kind):
    session = get_object_or_404(Session, pk=pk)
    me = request.user

    if me not in [session.teacher, session.learner] or session.status != "accepted":
        messages.error(request, "You can't do that for this session.")
        return redirect("sessions")

    other = session.other_person(me)
    form = IssueForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        report = form.save(commit=False)
        report.reporter = me
        report.reported_user = other
        report.session = session

        if kind == "no_show":
            report.category = "no_show"
            report.save()
            session.status = "no_show"
            session.save()
            if me == session.learner:
                session.refund()
            else:
                session.release()
            Notification.objects.create(user=other, text=f"{me} reported that you missed the {session.skill} session.", link="/sessions/")
            messages.success(request, "No-show reported.")
        else:
            report.category = "dispute"
            report.save()
            session.status = "disputed"
            session.save()
            Notification.objects.create(user=other, text=f"The {session.skill} session is under review. Credits stay in escrow.", link="/sessions/")
            messages.success(request, "Dispute opened. An admin will review it.")
        return redirect("sessions")

    if kind == "no_show":
        title = f"Report {other} as a no-show"
    else:
        title = "Open a dispute"
    context = {"form": form, "title": title, "session": session, "back_url": "/sessions/"}
    return render(request, "feedback/report_form.html", context)


@login_required
def admin_sessions(request):
    if not_admin(request):
        return redirect("dashboard")

    status = request.GET.get("status", "")
    all_sessions = Session.objects.all()
    if status:
        all_sessions = all_sessions.filter(status=status)
    context = {
        "sessions": all_sessions,
        "status": status,
        "status_choices": Session.STATUS_CHOICES,
    }
    return render(request, "learning_sessions/admin_sessions.html", context)
