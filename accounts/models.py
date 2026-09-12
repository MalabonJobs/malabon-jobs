from pathlib import Path
from uuid import uuid4

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils import timezone

from .managers import UserManager


# =========================================================
# EMPLOYER VERIFICATION FILE SETTINGS
# =========================================================

ALLOWED_EMPLOYER_DOCUMENT_EXTENSIONS = [
    "pdf",
    "jpg",
    "jpeg",
    "png",
]

MAX_EMPLOYER_DOCUMENT_SIZE = 10 * 1024 * 1024


def validate_employer_document_size(uploaded_file):
    if uploaded_file.size > MAX_EMPLOYER_DOCUMENT_SIZE:
        raise ValidationError(
            "The uploaded file must not exceed 10 MB."
        )


def employer_verification_upload_path(instance, filename):
    extension = Path(filename).suffix.lower()

    return (
        f"employer_verification/"
        f"user_{instance.user_id}/"
        f"{uuid4().hex}{extension}"
    )


employer_document_validators = [
    FileExtensionValidator(
        allowed_extensions=ALLOWED_EMPLOYER_DOCUMENT_EXTENSIONS
    ),
    validate_employer_document_size,
]


# =========================================================
# USER
# =========================================================

class User(AbstractUser):

    class AccountType(models.TextChoices):
        JOB_SEEKER = "job_seeker", "Job Seeker"
        EMPLOYER = "employer", "Employer"

    class EmploymentStatus(models.TextChoices):
        UNEMPLOYED = "unemployed", "Unemployed"
        EMPLOYED = "employed", "Employed"

    username = None

    email = models.EmailField(
        unique=True
    )

    account_type = models.CharField(
        max_length=20,
        choices=AccountType.choices,
        blank=True,
        null=True,
        default=None,
    )

    employment_status = models.CharField(
        max_length=20,
        choices=EmploymentStatus.choices,
        blank=True,
        null=True,
        default=None,
    )

    USERNAME_FIELD = "email"

    REQUIRED_FIELDS = []

    objects = UserManager()

    def save(self, *args, **kwargs):
        if self.email:
            self.email = (
                self.email
                .strip()
                .lower()
            )

        super().save(
            *args,
            **kwargs,
        )

    def __str__(self):
        return self.email


# =========================================================
# AUTHENTICATION EVENT
# =========================================================

class AuthenticationEvent(models.Model):

    class EventType(models.TextChoices):
        REGISTRATION = (
            "registration",
            "Registration",
        )

        LOGIN_SUCCESS = (
            "login_success",
            "Login Success",
        )

        LOGIN_FAILED = (
            "login_failed",
            "Login Failed",
        )

        LOGOUT = (
            "logout",
            "Logout",
        )

        PASSWORD_RESET = (
            "password_reset",
            "Password Reset",
        )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="authentication_events",
        blank=True,
        null=True,
    )

    email = models.EmailField(
        blank=True,
    )

    event_type = models.CharField(
        max_length=30,
        choices=EventType.choices,
    )

    ip_address = models.GenericIPAddressField(
        blank=True,
        null=True,
    )

    user_agent = models.TextField(
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = [
            "-created_at",
        ]

    def __str__(self):
        return (
            f"{self.email} - "
            f"{self.get_event_type_display()}"
        )


# =========================================================
# PASSWORD RESET OTP
# =========================================================

class PasswordResetOTP(models.Model):

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="password_reset_otp",
    )

    code_hash = models.CharField(
        max_length=128,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    expires_at = models.DateTimeField()

    last_sent_at = models.DateTimeField(
        default=timezone.now,
    )

    attempt_count = models.PositiveSmallIntegerField(
        default=0,
    )

    verified_at = models.DateTimeField(
        blank=True,
        null=True,
    )

    @property
    def is_expired(self):
        return (
            timezone.now()
            >= self.expires_at
        )

    @property
    def is_verified(self):
        return (
            self.verified_at
            is not None
        )

    def __str__(self):
        return (
            f"Password reset OTP "
            f"for {self.user.email}"
        )


# =========================================================
# EMPLOYER VERIFICATION
# =========================================================

class EmployerVerification(models.Model):

    class Status(models.TextChoices):

        DRAFT = (
            "draft",
            "Draft",
        )

        PENDING = (
            "pending",
            "Pending",
        )

        ACCESS_ACCEPTED = (
            "access_accepted",
            "Access Accepted",
        )

        ACCESS_DENIED = (
            "access_denied",
            "Access Denied",
        )

    DOCUMENT_FIELDS = (
        "business_permit",
        "barangay_clearance",
        "mayors_permit",
        "cedula",
        "valid_id",
    )

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="employer_verification",
    )

    business_permit = models.FileField(
        upload_to=employer_verification_upload_path,
        validators=employer_document_validators,
        blank=True,
    )

    barangay_clearance = models.FileField(
        upload_to=employer_verification_upload_path,
        validators=employer_document_validators,
        blank=True,
    )

    mayors_permit = models.FileField(
        upload_to=employer_verification_upload_path,
        validators=employer_document_validators,
        blank=True,
    )

    cedula = models.FileField(
        upload_to=employer_verification_upload_path,
        validators=employer_document_validators,
        blank=True,
    )

    valid_id = models.FileField(
        upload_to=employer_verification_upload_path,
        validators=employer_document_validators,
        blank=True,
    )

    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.DRAFT,
    )

    submitted_at = models.DateTimeField(
        blank=True,
        null=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        verbose_name = (
            "Employer Verification"
        )

        verbose_name_plural = (
            "Employer Verifications"
        )

        ordering = [
            "-updated_at",
        ]

    @property
    def uploaded_count(self):
        return sum(
            bool(
                getattr(
                    self,
                    field_name,
                )
            )
            for field_name
            in self.DOCUMENT_FIELDS
        )

    @property
    def all_documents_uploaded(self):
        return (
            self.uploaded_count
            == len(
                self.DOCUMENT_FIELDS
            )
        )

    @property
    def progress_percent(self):
        return int(
            (
                self.uploaded_count
                / len(
                    self.DOCUMENT_FIELDS
                )
            )
            * 100
        )

    def __str__(self):
        return (
            f"{self.user.email} - "
            f"{self.get_status_display()}"
        )