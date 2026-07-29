from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path

from analyzer import views


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.landing, name="landing"),
    path("register/", views.register, name="register"),
    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="registration/login.html",
            authentication_form=views.EmailAuthenticationForm,
        ),
        name="login",
    ),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path(
        "password-reset/",
        auth_views.PasswordResetView.as_view(
            template_name="registration/password_reset_form.html",
            email_template_name="registration/password_reset_email.html",
            success_url="/password-reset/done/",
        ),
        name="password_reset",
    ),
    path(
        "password-reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="registration/password_reset_done.html"
        ),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="registration/password_reset_confirm.html",
            success_url="/reset/done/",
        ),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="registration/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("profile/", views.profile, name="profile"),
    path("assess/start/", views.select_role, name="select_role"),
    path("assess/<int:role_id>/", views.assessment_form, name="assessment_form"),
    path("assess/submit/", views.submit_assessment, name="submit_assessment"),
    path("results/<int:assessment_id>/", views.results, name="results"),
    path(
        "reports/<int:assessment_id>/download/",
        views.download_report,
        name="download_report",
    ),
    path("history/", views.history, name="history"),
    path("progress/", views.progress, name="progress"),
]
