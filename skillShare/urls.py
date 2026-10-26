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

    # Admin
    path("admin-panel/", accounts_views.admin_dashboard, name="admin_dashboard"),
    path("admin-panel/users/", accounts_views.admin_users, name="admin_users"),
    path("admin-panel/users/<int:pk>/", accounts_views.admin_user_detail, name="admin_user_detail"),
    path("admin-panel/users/<int:pk>/toggle/", accounts_views.admin_toggle_user, name="admin_toggle_user"),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)