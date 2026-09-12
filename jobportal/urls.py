from django.contrib import admin
from django.urls import include, path

from accounts import views


urlpatterns = [

    # =====================================================
    # ADMIN
    # =====================================================

    path(
        "admin/",
        admin.site.urls,
    ),


    # =====================================================
    # HOME PAGE
    # =====================================================

    path(
        "home/",
        views.job_seeker_home,
        name="home_page",
    ),


    # =====================================================
    # JOBS PAGE
    # =====================================================

    path(
        "jobs/",
        views.jobs_page,
        name="jobs_page",
    ),


    # =====================================================
    # ANALYTICS PAGE
    # =====================================================

    path(
        "analytics/",
        views.analytics_page,
        name="analytics_page",
    ),


    # =====================================================
    # PROFILE PAGE
    # =====================================================

    path(
        "profile/",
        views.profile_page,
        name="profile_page",
    ),


    # =====================================================
    # EXISTING ACCOUNTS URLS
    # =====================================================

    path(
        "",
        include("accounts.urls"),
    ),

]