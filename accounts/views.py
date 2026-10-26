from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ProfileForm, RegisterForm, add_bootstrap_classes
from .models import User, Notification

def home(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    return render(request, "accounts/home.html")


def register_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()

        Notification.objects.create(
            user=user,
            text="Welcome to SkillShare! You received 20 credits. Add your skills to get matched.",
            link="/profile/",
        )
        login(request, user)
        messages.success(request, "Account created! Add your skills to get matched.")
        return redirect("my_profile")

    return render(request, "accounts/register.html", {"form": form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    form = AuthenticationForm(request, data=request.POST or None)
    add_bootstrap_classes(form)
    if request.method == "POST" and form.is_valid():
        login(request, form.get_user())
        messages.success(request, "Welcome back!")
        return redirect("dashboard")

    return render(request, "accounts/login.html", {"form": form})


def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect("home")


@login_required
def dashboard(request):
    if request.user.is_admin():
        return redirect("admin_dashboard")

    me = request.user


    context = {
        "locked": me.locked_credits(),
        "earned": me.earned_credits(),
    }
    return render(request, "accounts/dashboard.html", context)


@login_required
def notifications(request):
    my_notifications = list(request.user.notifications.all()[:50])
    # Visiting the page marks everything as read
    request.user.notifications.filter(is_read=False).update(is_read=True)
    return render(request, "accounts/notifications.html", {"notifications": my_notifications})


@login_required
def my_profile(request):
    me = request.user
    profile_form = ProfileForm(instance=me)

    if request.method == "POST":
        form_type = request.POST.get("form_type")

        if form_type == "profile":
            # Removing the photo is its own action: it applies immediately.
            if "remove_photo" in request.POST:
                if me.photo:
                    me.photo.delete(save=False)
                    me.photo = None
                    me.save()
                messages.success(request, "Profile photo removed.")
                return redirect("my_profile")

            profile_form = ProfileForm(request.POST, request.FILES, instance=me)
            new_photo = request.FILES.get("photo")

            if new_photo and not (new_photo.content_type or "").startswith("image/"):
                messages.error(request, "Please choose an image file for your profile photo.")
            elif profile_form.is_valid():
                me = profile_form.save()
                if new_photo:
                    me.photo = new_photo
                    me.save()
                messages.success(request, "Profile saved.")
                return redirect("my_profile")

    context = {
        "profile_form": profile_form,
        "taught": me.teaching_sessions.filter(status="completed").count(),
        "learned": me.learning_sessions.filter(status="completed").count(),
    }
    return render(request, "accounts/my_profile.html", context)


def not_admin(request):
    """Returns True (and shows a message) if the user is not an admin."""
    if not request.user.is_admin():
        messages.error(request, "Only admins can open that page.")
        return True
    return False


@login_required
def admin_dashboard(request):
    if not_admin(request):
        return redirect("dashboard")

    users = User.objects.filter(role="user")
    context = {
        "total_users": users.count(),
        "active_users": users.filter(is_active=True).count(),

        "new_users": users.order_by("-date_joined")[:5],
    }
    return render(request, "accounts/admin_dashboard.html", context)


@login_required
def admin_users(request):
    if not_admin(request):
        return redirect("dashboard")

    query = request.GET.get("q", "")
    users = User.objects.all().order_by("-date_joined")
    if query:
        users = users.filter(
            Q(username__icontains=query)
            | Q(first_name__icontains=query)
            | Q(last_name__icontains=query)
            | Q(email__icontains=query)
        )
    return render(request, "accounts/admin_users.html", {"users": users, "query": query})


@login_required
def admin_user_detail(request, pk):
    if not_admin(request):
        return redirect("dashboard")

    person = get_object_or_404(User, pk=pk)
    context = {
        "person": person,
        "transactions": person.transactions.all()[:20],
    }
    return render(request, "accounts/admin_user_detail.html", context)


@login_required
def admin_toggle_user(request, pk):

    #toggle user accounts status

    if not_admin(request):
        return redirect("dashboard")

    person = get_object_or_404(User, pk=pk)
    if request.method == "POST":
        if person == request.user:
            messages.error(request, "You can't suspend yourself.")
        else:
            person.is_active = not person.is_active
            person.save()
            if person.is_active:
                messages.success(request, f"{person} is active again.")
            else:
                messages.warning(request, f"{person} has been suspended.")
    return redirect("admin_user_detail", pk=person.pk)



def counts(request):

    """   for shwoing the numbers  """

    if not request.user.is_authenticated:
        return {}
    return {
        "unread_notifications": Notification.objects.filter(user=request.user, is_read=False).count(),

    }

