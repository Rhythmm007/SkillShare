from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from accounts.forms import ReportForm, ReviewForm
from accounts.models import User, Notification
from accounts.views import not_admin
from .models import Report, Review
from learning_sessions.models import Session


@login_required
def report_user(request, pk):
    person = get_object_or_404(User, pk=pk)
    form = ReportForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        report = form.save(commit=False)
        report.reporter = request.user
        report.reported_user = person
        report.save()
        messages.success(request, "Report sent. An admin will review it.")
        return redirect("user_profile", pk=person.pk)

    context = {"form": form, "title": f"Report {person}", "back_url": f"/people/{person.pk}/"}
    return render(request, "feedback/report_form.html", context)


@login_required
def review_session(request, pk):
    session = get_object_or_404(Session, pk=pk)
    me = request.user

    already_reviewed = Review.objects.filter(session=session, reviewer=me).exists()
    if me not in [session.teacher, session.learner] or session.status != "completed" or already_reviewed:
        messages.error(request, "You can't review this session.")
        return redirect("sessions")

    other = session.other_person(me)
    form = ReviewForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        review = form.save(commit=False)
        review.session = session
        review.reviewer = me
        review.reviewed_user = other
        review.save()
        Notification.objects.create(user=other, text=f"{me} rated you {review.rating} stars.", link=f"/people/{other.pk}/")
        messages.success(request, "Thanks for your review!")
        return redirect("/sessions/?tab=past")

    return render(request, "feedback/review_form.html", {"form": form, "session": session, "other": other})


@login_required
def admin_reports(request):
    if not_admin(request):
        return redirect("dashboard")

    status = request.GET.get("status", "open")
    reports = Report.objects.all()
    if status:
        reports = reports.filter(status=status)
    return render(request, "feedback/admin_reports.html", {"reports": reports, "status": status})


@login_required
def admin_resolve_report(request, pk):
    """Close a report. For disputes the admin decides: refund the learner or pay the teacher."""
    if not_admin(request):
        return redirect("dashboard")

    report = get_object_or_404(Report, pk=pk)
    action = request.POST.get("action")

    if request.method == "POST" and report.status == "open":
        session = report.session

        if action == "refund" and session:
            session.status = "cancelled"
            session.save()
            session.refund()
            report.status = "resolved"
            report.resolution = "Credits refunded to the learner."
        elif action == "release" and session:
            session.status = "completed"
            session.save()
            session.release()
            report.status = "resolved"
            report.resolution = "Credits released to the teacher."
        elif action == "dismiss":
            report.status = "dismissed"
            report.resolution = "Dismissed by admin."
        else:
            report.status = "resolved"
            report.resolution = "Resolved by admin."

        report.save()
        Notification.objects.create(
            user=report.reporter,
            text=f"Your report was reviewed: {report.resolution}",
            link="/notifications/",
        )
        messages.success(request, "Report updated.")

    return redirect("admin_reports")


@login_required
def admin_reviews(request):
    if not_admin(request):
        return redirect("dashboard")
    return render(request, "feedback/admin_reviews.html", {"reviews": Review.objects.all()})


@login_required
def admin_delete_review(request, pk):
    if not_admin(request):
        return redirect("dashboard")

    review = get_object_or_404(Review, pk=pk)
    if request.method == "POST":
        review.delete()
        messages.info(request, "Review deleted.")
    return redirect("admin_reviews")
