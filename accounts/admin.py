from django.contrib import admin
from django.contrib.auth.admin import (
    UserAdmin as DjangoUserAdmin,
)
from django.urls import reverse
from django.utils.html import format_html

from .models import (
    AuthenticationEvent,
    EmployerVerification,
    PasswordResetOTP,
    User,
)


# =========================================================
# USER ADMIN
# =========================================================

@admin.register(User)
class UserAdmin(DjangoUserAdmin):

    ordering = (
        "email",
    )

    list_display = (
        "email",
        "first_name",
        "last_name",
        "account_type",
        "employment_status",
        "is_active",
        "is_staff",
    )

    list_filter = (
        "account_type",
        "employment_status",
        "is_active",
        "is_staff",
    )

    search_fields = (
        "email",
        "first_name",
        "last_name",
    )

    fieldsets = (

        (
            None,
            {
                "fields": (
                    "email",
                    "password",
                )
            },
        ),

        (
            "Personal information",
            {
                "fields": (
                    "first_name",
                    "last_name",
                )
            },
        ),

        (
            "Malabon Jobs account",
            {
                "fields": (
                    "account_type",
                    "employment_status",
                )
            },
        ),

        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),

        (
            "Important dates",
            {
                "fields": (
                    "last_login",
                    "date_joined",
                )
            },
        ),

    )

    add_fieldsets = (

        (
            None,
            {
                "classes": (
                    "wide",
                ),

                "fields": (
                    "email",
                    "first_name",
                    "last_name",
                    "password1",
                    "password2",
                    "account_type",
                    "employment_status",
                    "is_active",
                    "is_staff",
                ),
            },
        ),

    )


# =========================================================
# AUTHENTICATION EVENT ADMIN
# =========================================================

@admin.register(AuthenticationEvent)
class AuthenticationEventAdmin(
    admin.ModelAdmin
):

    list_display = (
        "email",
        "event_type",
        "ip_address",
        "created_at",
    )

    list_filter = (
        "event_type",
        "created_at",
    )

    search_fields = (
        "email",
        "user__email",
    )

    readonly_fields = (
        "user",
        "email",
        "event_type",
        "ip_address",
        "user_agent",
        "created_at",
    )

    ordering = (
        "-created_at",
    )


# =========================================================
# PASSWORD RESET OTP ADMIN
# =========================================================

@admin.register(PasswordResetOTP)
class PasswordResetOTPAdmin(
    admin.ModelAdmin
):

    list_display = (
        "user",
        "created_at",
        "expires_at",
        "attempt_count",
        "verified_at",
    )

    search_fields = (
        "user__email",
    )

    readonly_fields = (
        "code_hash",
        "created_at",
        "expires_at",
        "last_sent_at",
        "attempt_count",
        "verified_at",
    )


# =========================================================
# EMPLOYER VERIFICATION ADMIN
# =========================================================

@admin.action(
    description=(
        "Set selected applications "
        "to Access Accepted"
    )
)
def mark_access_accepted(
    modeladmin,
    request,
    queryset,
):

    for verification in queryset:
        # Approve the employer verification.
        verification.status = (
            EmployerVerification
            .Status
            .ACCESS_ACCEPTED
        )

        verification.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        # Once the employer is approved, mark the
        # associated user as Employed.
        user = verification.user
        user.employment_status = (
            User.EmploymentStatus.EMPLOYED
        )
        user.save(
            update_fields=[
                "employment_status",
            ]
        )


@admin.action(
    description=(
        "Set selected applications "
        "to Access Denied"
    )
)
def mark_access_denied(
    modeladmin,
    request,
    queryset,
):

    queryset.update(
        status=(
            EmployerVerification
            .Status
            .ACCESS_DENIED
        )
    )


@admin.register(EmployerVerification)
class EmployerVerificationAdmin(
    admin.ModelAdmin
):

    def save_model(
        self,
        request,
        obj,
        form,
        change,
    ):
        super().save_model(
            request,
            obj,
            form,
            change,
        )

        # If an administrator manually changes the
        # verification status to Access Accepted,
        # also mark the employer as Employed.
        if (
            obj.status
            == EmployerVerification.Status.ACCESS_ACCEPTED
        ):
            user = obj.user
            user.employment_status = (
                User.EmploymentStatus.EMPLOYED
            )
            user.save(
                update_fields=[
                    "employment_status",
                ]
            )

    list_display = (
        "email",
        "first_name",
        "last_name",
        "account_type",
        "status",
        "uploaded_documents",
        "submitted_at",
        "updated_at",
    )

    list_filter = (
        "status",
        "submitted_at",
        "created_at",
    )

    search_fields = (
        "user__email",
        "user__first_name",
        "user__last_name",
    )

    ordering = (
        "-updated_at",
    )

    actions = (
        mark_access_accepted,
        mark_access_denied,
    )

    readonly_fields = (
        "user",
        "email",
        "first_name",
        "last_name",
        "account_type",
        "uploaded_documents",
        "business_permit_document",
        "barangay_clearance_document",
        "mayors_permit_document",
        "cedula_document",
        "valid_id_document",
        "submitted_at",
        "created_at",
        "updated_at",
    )

    fieldsets = (

        (
            "Employer",
            {
                "fields": (
                    "user",
                    "email",
                    "first_name",
                    "last_name",
                    "account_type",
                )
            },
        ),

        (
            "Verification",
            {
                "fields": (
                    "status",
                    "uploaded_documents",
                    "submitted_at",
                    "created_at",
                    "updated_at",
                )
            },
        ),

        (
            "Submitted Documents",
            {
                "fields": (
                    "business_permit_document",
                    "barangay_clearance_document",
                    "mayors_permit_document",
                    "cedula_document",
                    "valid_id_document",
                )
            },
        ),

    )

    @admin.display(
        description="Email"
    )
    def email(self, obj):
        return obj.user.email

    @admin.display(
        description="First Name"
    )
    def first_name(self, obj):
        return (
            obj.user.first_name
            or "-"
        )

    @admin.display(
        description="Last Name"
    )
    def last_name(self, obj):
        return (
            obj.user.last_name
            or "-"
        )

    @admin.display(
        description="Account Type"
    )
    def account_type(self, obj):
        return (
            obj.user
            .get_account_type_display()
        )

    @admin.display(
        description="Uploaded"
    )
    def uploaded_documents(
        self,
        obj,
    ):

        return (
            f"{obj.uploaded_count} of 5"
        )

    def document_link(
        self,
        obj,
        field_name,
    ):

        document = getattr(
            obj,
            field_name,
        )

        if not document:
            return "Not uploaded"

        url = reverse(
            (
                "accounts:"
                "employer_verification_document"
            ),
            kwargs={
                "verification_id": (
                    obj.pk
                ),
                "field_name": (
                    field_name
                ),
            },
        )

        return format_html(
            '<a href="{}">'
            'Download file'
            '</a>',
            url,
        )

    @admin.display(
        description="Business Permit"
    )
    def business_permit_document(
        self,
        obj,
    ):

        return self.document_link(
            obj,
            "business_permit",
        )

    @admin.display(
        description="Barangay Clearance"
    )
    def barangay_clearance_document(
        self,
        obj,
    ):

        return self.document_link(
            obj,
            "barangay_clearance",
        )

    @admin.display(
        description="Mayor's Permit"
    )
    def mayors_permit_document(
        self,
        obj,
    ):

        return self.document_link(
            obj,
            "mayors_permit",
        )

    @admin.display(
        description="Cedula"
    )
    def cedula_document(
        self,
        obj,
    ):

        return self.document_link(
            obj,
            "cedula",
        )

    @admin.display(
        description="Valid ID"
    )
    def valid_id_document(
        self,
        obj,
    ):

        return self.document_link(
            obj,
            "valid_id",
        )

    def has_add_permission(
        self,
        request,
    ):

        return False