import secrets
import string
from datetime import timedelta

from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.core.mail import EmailMessage
from django.utils import timezone

from .models import PasswordResetOTP


OTP_EXPIRY_MINUTES = 5
OTP_RESEND_COOLDOWN_SECONDS = 60
OTP_MAX_ATTEMPTS = 5


def generate_otp():
    """
    Generate a secure random 4-digit verification code.
    """

    return "".join(
        secrets.choice(string.digits)
        for _ in range(4)
    )


def create_password_reset_otp(user):
    """
    Create or replace the user's current password-reset OTP.
    """

    code = generate_otp()
    now = timezone.now()

    otp, _ = PasswordResetOTP.objects.update_or_create(
        user=user,
        defaults={
            "code_hash": make_password(code),
            "expires_at": (
                now
                + timedelta(minutes=OTP_EXPIRY_MINUTES)
            ),
            "last_sent_at": now,
            "attempt_count": 0,
            "verified_at": None,
        },
    )

    return otp, code


def send_registration_email(user):
    """
    Send a welcome email to whoever registered.
    """

    full_name = user.get_full_name().strip()

    if full_name:
        greeting = f"Hello {full_name},"
    else:
        greeting = "Hello,"

    email = EmailMessage(
        subject="Welcome to Malabon Jobs",
        body=(
            f"{greeting}\n\n"
            "Your Malabon Jobs account has been "
            "registered successfully.\n\n"
            f"Registered email: {user.email}\n\n"
            "You may now use your email address and "
            "password to log in to Malabon Jobs.\n\n"
            "If you did not create this account, "
            "please contact the Malabon Jobs administrator.\n\n"
            "Thank you,\n"
            "Malabon Jobs"
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,

        # IMPORTANT:
        # Automatically sends to the user who registered.
        to=[user.email],
    )

    return email.send(
        fail_silently=False,
    )


def send_password_reset_otp_email(user, code):
    """
    Send the 4-digit password-reset code to the user's email.
    """

    full_name = user.get_full_name().strip()

    if full_name:
        greeting = f"Hello {full_name},"
    else:
        greeting = "Hello,"

    email = EmailMessage(
        subject="Malabon Jobs Password Reset Code",
        body=(
            f"{greeting}\n\n"
            "We received a request to reset the password "
            "for your Malabon Jobs account.\n\n"
            "Your 4-digit verification code is:\n\n"
            f"{code}\n\n"
            f"This code expires in "
            f"{OTP_EXPIRY_MINUTES} minutes.\n\n"
            "Do not share this code with anyone.\n\n"
            "If you did not request a password reset, "
            "you may safely ignore this email.\n\n"
            "Thank you,\n"
            "Malabon Jobs"
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,

        # Automatically sends to the user requesting reset.
        to=[user.email],
    )

    return email.send(
        fail_silently=False,
    )