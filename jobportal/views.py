from django.shortcuts import render


def home(request):
    return render(request, "logres.html")


def forgot_password(request):
    return render(request, "forgot_password.html")


def verification_code(request):
    return render(request, "verification_code.html")


def reset_password(request):
    return render(request, "reset_password.html")


def password_changed(request):
    return render(request, "password_changed.html")