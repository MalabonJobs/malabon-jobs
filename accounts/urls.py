from django.urls import path

from . import views


app_name = "accounts"


urlpatterns = [

    path(
        "",
        views.auth_page,
        name="home",
    ),

    path(
        "choose-account-type/",
        views.account_type_selection,
        name="account_type_selection",
    ),

    path(
        "home/",
        views.job_seeker_home,
        name="job_seeker_home",
    ),

    path(
        "employer-verification/",
        views.employer_verification,
        name="employer_verification",
    ),

    path(
        (
            "employer-verification/"
            "document/"
            "<int:verification_id>/"
            "<str:field_name>/"
        ),
        views.employer_verification_document,
        name=(
            "employer_verification_document"
        ),
    ),

    path(
        "forgot-password/",
        views.forgot_password,
        name="forgot_password",
    ),

    path(
        "verification-code/",
        views.verification_code,
        name="verification_code",
    ),

    path(
        "reset-password/",
        views.reset_password,
        name="reset_password",
    ),

    path(
        "password-changed/",
        views.password_changed,
        name="password_changed",
    ),

    path(
        "dashboard/",
        views.dashboard,
        name="dashboard",
    ),

    path(
        "logout/",
        views.logout_view,
        name="logout",
    ),

]