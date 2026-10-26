"""
URL configuration for skillShare project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static

from accounts import views as accounts_views
from matching import views as matching_views
from skills import views as skills_views
from learning_sessions import views as learning_sessions_views
from wallets import views as wallets_views
from feedback import views as feedback_views


urlpatterns = [
    path("django-admin/", admin.site.urls),
    
    # Public
    path("", accounts_views.home, name="home"),
    path("register/", accounts_views.register_view, name="register"),
    path("login/", accounts_views.login_view, name="login"),
    path("logout/", accounts_views.logout_view, name="logout"),

    # Users
    path("dashboard/", accounts_views.dashboard, name="dashboard"),
    path("discover/", matching_views.discover, name="discover"),
    path("people/<int:pk>/", matching_views.user_profile, name="user_profile"),
    path("people/<int:pk>/report/", feedback_views.report_user, name="report_user"),
    path("sessions/", learning_sessions_views.sessions, name="sessions"),
    path("sessions/<int:pk>/review/", feedback_views.review_session, name="review_session"),
    path("sessions/<int:pk>/issue/<str:kind>/", learning_sessions_views.session_issue, name="session_issue"),
    path("sessions/<int:pk>/<str:action>/", learning_sessions_views.session_action, name="session_action"),
    path("wallet/", wallets_views.wallet, name="wallet"),
    path("messages/", matching_views.inbox, name="inbox"),
    path("messages/<int:user_id>/", matching_views.inbox, name="conversation"),
    path("notifications/", accounts_views.notifications, name="notifications"),
    path("profile/", accounts_views.my_profile, name="my_profile"),
    path("skills/", skills_views.my_skills, name="skills"),
    path("profile/skills/<int:pk>/delete/", skills_views.delete_skill, name="delete_skill"),

    # Admin
    path("admin-panel/", accounts_views.admin_dashboard, name="admin_dashboard"),
    path("admin-panel/users/", accounts_views.admin_users, name="admin_users"),
    path("admin-panel/users/<int:pk>/", accounts_views.admin_user_detail, name="admin_user_detail"),
    path("admin-panel/users/<int:pk>/toggle/", accounts_views.admin_toggle_user, name="admin_toggle_user"),
    path("admin-panel/skills/", skills_views.admin_skills, name="admin_skills"),
    path("admin-panel/skills/<int:pk>/delete/", skills_views.admin_delete_skill, name="admin_delete_skill"),
    path("admin-panel/sessions/", learning_sessions_views.admin_sessions, name="admin_sessions"),
    path("admin-panel/transactions/", wallets_views.admin_transactions, name="admin_transactions"),
    path("admin-panel/reports/", feedback_views.admin_reports, name="admin_reports"),
    path("admin-panel/reports/<int:pk>/resolve/", feedback_views.admin_resolve_report, name="admin_resolve_report"),
    path("admin-panel/reviews/", feedback_views.admin_reviews, name="admin_reviews"),
    path("admin-panel/reviews/<int:pk>/delete/", feedback_views.admin_delete_review, name="admin_delete_review"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)