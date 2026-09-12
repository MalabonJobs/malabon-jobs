import mimetypes
from datetime import timedelta
from pathlib import Path

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import (
    authenticate,
    get_user_model,
    login,
    logout,
)
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password
from django.http import FileResponse, Http404
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)
from django.utils import timezone

from .forms import (
    EmployerVerificationForm,
    ForgotPasswordForm,
    LoginForm,
    RegistrationForm,
    ResetPasswordForm,
    VerificationCodeForm,
)
from .models import (
    AuthenticationEvent,
    EmployerVerification,
    PasswordResetOTP,
)
from .services import (
    OTP_MAX_ATTEMPTS,
    OTP_RESEND_COOLDOWN_SECONDS,
    create_password_reset_otp,
    send_password_reset_otp_email,
    send_registration_email,
)

EMPLOYER_REVIEW_POPUP_SESSION_KEY = (
    "employer_review_popup_status"
)

User = get_user_model()


RESET_USER_SESSION_KEY = "password_reset_user_id"
RESET_VERIFIED_SESSION_KEY = "password_reset_verified"



# =========================================================
# HELPER FUNCTIONS
# =========================================================

def first_form_error(form):

    for errors in form.errors.values():

        if errors:
            return str(errors[0])

    return "Please correct the form and try again."


def get_request_details(request):

    forwarded_for = request.META.get(
        "HTTP_X_FORWARDED_FOR"
    )

    if forwarded_for:

        ip_address = (
            forwarded_for
            .split(",")[0]
            .strip()
        )

    else:

        ip_address = request.META.get(
            "REMOTE_ADDR"
        )


    user_agent = request.META.get(
        "HTTP_USER_AGENT",
        "",
    )[:1000]


    return ip_address, user_agent


def record_authentication_event(
    request,
    event_type,
    user=None,
    email="",
):

    ip_address, user_agent = (
        get_request_details(request)
    )


    try:

        AuthenticationEvent.objects.create(
            user=user,
            email=email or (
                user.email
                if user
                else ""
            ),
            event_type=event_type,
            ip_address=ip_address,
            user_agent=user_agent,
        )

    except Exception as error:

        print(
            "Authentication event logging error:",
            repr(error),
        )


# =========================================================
# ACCOUNT TYPE REDIRECT
# =========================================================

def redirect_user_by_account_type(user):

    # =====================================================
    # NO ACCOUNT TYPE YET
    # =====================================================

    if not user.account_type:
        return redirect(
            "accounts:account_type_selection"
        )


    # =====================================================
    # JOB SEEKER
    # =====================================================

    if (
        user.account_type
        == User.AccountType.JOB_SEEKER
    ):
        return redirect(
            "accounts:job_seeker_home"
        )


    # =====================================================
    # EMPLOYER
    # =====================================================

    if (
        user.account_type
        == User.AccountType.EMPLOYER
    ):

        verification = (
            EmployerVerification.objects
            .filter(user=user)
            .first()
        )


        # APPROVED EMPLOYER
        if (
            verification
            and verification.status
            == EmployerVerification
            .Status
            .ACCESS_ACCEPTED
        ):
            return redirect(
                "accounts:job_seeker_home"
            )


        # NOT YET APPROVED
        return redirect(
            "accounts:employer_verification"
        )


    # =====================================================
    # SAFETY FALLBACK
    # =====================================================

    return redirect(
        "accounts:account_type_selection"
    )

# =========================================================
# LOGIN + REGISTRATION
# =========================================================

def auth_page(request):

    context = {
        "login_error": "",
        "register_error": "",
        "register_error_popup": "",
        "register_mode": False,
    }


    # =====================================================
    # USER ALREADY LOGGED IN
    # =====================================================

    if request.user.is_authenticated:

        return redirect_user_by_account_type(
            request.user
        )


    # =====================================================
    # POST REQUEST
    # =====================================================

    if request.method == "POST":

        action = request.POST.get(
            "action"
        )


        # =================================================
        # REGISTRATION
        # =================================================

        if action == "register":

            context["register_mode"] = True


            form = RegistrationForm(
                request.POST
            )


            if form.is_valid():

                user = form.save()


                # =========================================
                # RECORD REGISTRATION
                # =========================================

                record_authentication_event(
                    request=request,
                    event_type=(
                        AuthenticationEvent
                        .EventType
                        .REGISTRATION
                    ),
                    user=user,
                    email=user.email,
                )


                # =========================================
                # SEND WELCOME EMAIL
                # =========================================

                try:

                    send_registration_email(
                        user
                    )

                except Exception as email_error:

                    print(
                        "Registration email error:",
                        repr(email_error),
                    )


                    messages.warning(
                        request,
                        (
                            "Your account was created, "
                            "but the welcome email could "
                            "not be sent."
                        ),
                    )

                else:

                    messages.success(
                        request,
                        (
                            "Registration successful. "
                            "A welcome email was sent "
                            "to your email address."
                        ),
                    )


                return redirect(
                    "accounts:home"
                )


            context["register_error"] = (
                first_form_error(form)
            )

            # Show the same registration result popup only for
            # the two requested registration validation errors.
            if form.has_error(
                "email",
                code="email_already_used",
            ):

                context["register_error_popup"] = (
                    "Email already used, try a new one."
                )

                # The popup is the only error message shown
                # for this validation case.
                context["register_error"] = ""

            elif form.has_error(
                "confirm_password",
                code="password_mismatch",
            ):

                context["register_error_popup"] = (
                    "Passwords do not match, please try again."
                )

                # The popup is the only error message shown
                # for this validation case.
                context["register_error"] = ""


        # =================================================
        # LOGIN
        # =================================================

        elif action == "login":

            form = LoginForm(
                request.POST
            )


            if form.is_valid():

                email = (
                    form.cleaned_data[
                        "email"
                    ]
                )

                password = (
                    form.cleaned_data[
                        "password"
                    ]
                )


                user = authenticate(
                    request,
                    email=email,
                    password=password,
                )


                # =========================================
                # LOGIN SUCCESS
                # =========================================

                if user is not None:

                    # =====================================
                    # REMEMBER PREVIOUS LOGIN TIME
                    # =====================================
                    #
                    # Django updates user.last_login when
                    # login() is called. We keep the old
                    # value so an Employer approved by the
                    # Admin can receive the Congratulations
                    # popup exactly on the next login.
                    # =====================================

                    previous_last_login = (
                        user.last_login
                    )


                    login(
                        request,
                        user,
                    )


                    record_authentication_event(
                        request=request,
                        event_type=(
                            AuthenticationEvent
                            .EventType
                            .LOGIN_SUCCESS
                        ),
                        user=user,
                        email=user.email,
                    )


                    # =====================================
                    # EMPLOYER VERIFICATION STATUS
                    # =====================================
                    #
                    # The database is the source of truth.
                    # JavaScript does not decide whether
                    # the Employer is Pending, Accepted,
                    # or Denied.
                    # =====================================

                    if (
                        user.account_type
                        == User.AccountType.EMPLOYER
                    ):

                        verification = (
                            EmployerVerification
                            .objects
                            .filter(
                                user=user
                            )
                            .first()
                        )


                        # =================================
                        # NO VERIFICATION RECORD YET
                        # =================================

                        if verification is None:

                            return redirect(
                                "accounts:"
                                "employer_verification"
                            )


                        # =================================
                        # PENDING
                        # =================================

                        if (
                            verification.status
                            == EmployerVerification
                            .Status
                            .PENDING
                        ):

                            request.session[
                                EMPLOYER_REVIEW_POPUP_SESSION_KEY
                            ] = (
                                EmployerVerification
                                .Status
                                .PENDING
                            )

                            return redirect(
                                "accounts:"
                                "employer_verification"
                            )


                        # =================================
                        # ACCESS DENIED
                        # =================================

                        if (
                            verification.status
                            == EmployerVerification
                            .Status
                            .ACCESS_DENIED
                        ):

                            request.session[
                                EMPLOYER_REVIEW_POPUP_SESSION_KEY
                            ] = (
                                EmployerVerification
                                .Status
                                .ACCESS_DENIED
                            )

                            return redirect(
                                "accounts:"
                                "employer_verification"
                            )


                        # =================================
                        # ACCESS ACCEPTED
                        # =================================

                        if (
                            verification.status
                            == EmployerVerification
                            .Status
                            .ACCESS_ACCEPTED
                        ):

                            approval_is_new = (
                                previous_last_login
                                is None
                                or (
                                    verification
                                    .updated_at
                                    and
                                    previous_last_login
                                    < verification
                                    .updated_at
                                )
                            )


                            # First login after the Admin
                            # approved the Employer:
                            # show Congratulations popup.
                            if approval_is_new:

                                request.session[
                                    EMPLOYER_REVIEW_POPUP_SESSION_KEY
                                ] = (
                                    EmployerVerification
                                    .Status
                                    .ACCESS_ACCEPTED
                                )

                                return redirect(
                                    "accounts:"
                                    "employer_verification"
                                )


                            # Approval was already seen on
                            # an earlier login.
                            return redirect(
                                "accounts:"
                                "job_seeker_home"
                            )


                        # =================================
                        # DRAFT / OTHER STATUS
                        # =================================

                        return redirect(
                            "accounts:"
                            "employer_verification"
                        )


                    # =====================================
                    # JOB SEEKER / NORMAL REDIRECT
                    # =====================================

                    return (
                        redirect_user_by_account_type(
                            user
                        )
                    )


                # =========================================
                # LOGIN FAILED
                # =========================================

                existing_user = (
                    User.objects.filter(
                        email__iexact=email
                    ).first()
                )


                record_authentication_event(
                    request=request,
                    event_type=(
                        AuthenticationEvent
                        .EventType
                        .LOGIN_FAILED
                    ),
                    user=existing_user,
                    email=email,
                )


                context["login_error"] = (
                    "Invalid email or password."
                )


            else:

                context["login_error"] = (
                    first_form_error(form)
                )


    return render(
        request,
        "logres.html",
        context,
    )


# =========================================================
# ACCOUNT TYPE SELECTION
# =========================================================

@login_required
def account_type_selection(request):

    user = request.user


    # =====================================================
    # ACCOUNT TYPE ALREADY SELECTED
    # =====================================================

    if user.account_type:

        return redirect_user_by_account_type(
            user
        )


    error = ""


    if request.method == "POST":

        selected_type = request.POST.get(
            "account_type"
        )


        # =================================================
        # JOB SEEKER
        # =================================================

        if (
            selected_type
            == User.AccountType.JOB_SEEKER
        ):

            user.account_type = (
                User.AccountType.JOB_SEEKER
            )

            user.employment_status = (
                User.EmploymentStatus.UNEMPLOYED
            )


            user.save(
                update_fields=[
                    "account_type",
                    "employment_status",
                ]
            )


            return redirect(
                "accounts:job_seeker_home"
            )


        # =================================================
        # EMPLOYER
        # =================================================

        if (
            selected_type
            == User.AccountType.EMPLOYER
        ):

            user.account_type = (
                User.AccountType.EMPLOYER
            )

            user.employment_status = None


            user.save(
                update_fields=[
                    "account_type",
                    "employment_status",
                ]
            )


            return redirect(
                "accounts:employer_verification"
            )


        error = (
            "Please select a valid account type."
        )


    return render(
        request,
        "account_type_selection.html",
        {
            "error": error,
        },
    )


# =========================================================
# JOB SEEKER ACCESS
# =========================================================

def job_seeker_page_access(request):

    user = request.user


    # =====================================================
    # NO ACCOUNT TYPE
    # =====================================================

    if not user.account_type:

        return redirect(
            "accounts:account_type_selection"
        )


    # =====================================================
    # JOB SEEKER
    # =====================================================

    if (
        user.account_type
        == User.AccountType.JOB_SEEKER
    ):

        return None


    # =====================================================
    # EMPLOYER
    # =====================================================

    if (
        user.account_type
        == User.AccountType.EMPLOYER
    ):

        verification = (
            EmployerVerification.objects
            .filter(
                user=user
            )
            .first()
        )


        # Only Employers approved by the Admin
        # may use the normal portal pages.
        if (
            verification
            and verification.status
            == EmployerVerification
            .Status
            .ACCESS_ACCEPTED
        ):

            return None


        # Draft, Pending, and Access Denied Employers
        # remain on Employer Verification.
        return redirect(
            "accounts:employer_verification"
        )


    # =====================================================
    # SAFETY FALLBACK
    # =====================================================

    return redirect(
        "accounts:account_type_selection"
    )


# =========================================================
# JOB SEEKER HOME
# =========================================================

@login_required
def job_seeker_home(request):

    redirect_response = (
        job_seeker_page_access(
            request
        )
    )


    if redirect_response is not None:

        return redirect_response


    return render(
        request,
        "home.html",
    )


# =========================================================
# JOBS PAGE
# =========================================================

@login_required
def jobs_page(request):

    redirect_response = (
        job_seeker_page_access(
            request
        )
    )


    if redirect_response is not None:

        return redirect_response


    return render(
        request,
        "jobs.html",
    )


# =========================================================
# ANALYTICS PAGE
# =========================================================

@login_required
def analytics_page(request):

    redirect_response = (
        job_seeker_page_access(
            request
        )
    )


    if redirect_response is not None:

        return redirect_response


    return render(
        request,
        "analytics.html",
    )


# =========================================================
# PROFILE PAGE
# =========================================================

@login_required
def profile_page(request):

    redirect_response = (
        job_seeker_page_access(
            request
        )
    )


    if redirect_response is not None:

        return redirect_response


    return render(
        request,
        "profile.html",
    )


# =========================================================
# EMPLOYER VERIFICATION
# =========================================================

@login_required
def employer_verification(request):

    user = request.user


    # =====================================================
    # NO ACCOUNT TYPE
    # =====================================================

    if not user.account_type:

        return redirect(
            "accounts:account_type_selection"
        )


    # =====================================================
    # JOB SEEKER CANNOT ACCESS EMPLOYER VERIFICATION
    # =====================================================

    if (
        user.account_type
        == User.AccountType.JOB_SEEKER
    ):

        return redirect(
            "accounts:job_seeker_home"
        )


    # =====================================================
    # GET EXISTING EMPLOYER VERIFICATION
    # =====================================================

    application = (
        EmployerVerification.objects
        .filter(
            user=user
        )
        .first()
    )


    if application is None:

        application = EmployerVerification(
            user=user
        )


    # =====================================================
    # POST REQUEST
    # =====================================================

    if request.method == "POST":

        # =================================================
        # DETERMINE ACTION
        # =================================================

        auto_action = request.POST.get(
            "auto_action"
        )

        normal_action = request.POST.get(
            "action"
        )

        action = (
            auto_action
            or normal_action
            or "save_progress"
        )


        # =================================================
        # REMEMBER OLD FILES
        # =================================================

        old_files = {}


        if application.pk:

            for field_name in (
                EmployerVerification
                .DOCUMENT_FIELDS
            ):

                old_document = getattr(
                    application,
                    field_name,
                )


                if old_document:

                    old_files[
                        field_name
                    ] = {
                        "name": (
                            old_document.name
                        ),
                        "storage": (
                            old_document.storage
                        ),
                    }


        # =================================================
        # FORM
        # =================================================

        form = EmployerVerificationForm(
            request.POST,
            request.FILES,
            instance=application,
        )


        # =================================================
        # INVALID FILE
        # =================================================

        if not form.is_valid():

            messages.error(
                request,
                first_form_error(form),
            )


            return redirect(
                "accounts:"
                "employer_verification"
            )


        # =================================================
        # SAVE DOCUMENT
        # =================================================

        verification = form.save(
            commit=False
        )

        verification.user = user


        uploaded_field_names = [

            field_name

            for field_name in (
                EmployerVerification
                .DOCUMENT_FIELDS
            )

            if field_name
            in request.FILES

        ]


        # =================================================
        # IF USER CHANGES FILE AFTER SUBMISSION,
        # RETURN APPLICATION TO DRAFT
        # =================================================

        if (
            uploaded_field_names
            and verification.status
            != EmployerVerification.Status.DRAFT
        ):

            verification.status = (
                EmployerVerification
                .Status
                .DRAFT
            )

            verification.submitted_at = None


        verification.save()


        # =================================================
        # DELETE OLD REPLACED FILES
        # =================================================

        for field_name in (
            uploaded_field_names
        ):

            old_file_info = old_files.get(
                field_name
            )


            if not old_file_info:

                continue


            new_document = getattr(
                verification,
                field_name,
            )


            new_name = (
                new_document.name
                if new_document
                else ""
            )


            old_name = old_file_info[
                "name"
            ]


            if (
                old_name
                and old_name != new_name
            ):

                try:

                    old_file_info[
                        "storage"
                    ].delete(
                        old_name
                    )

                except Exception as error:

                    print(
                        "Old employer document "
                        "deletion error:",
                        repr(error),
                    )


        # =================================================
        # AUTOMATIC UPLOAD
        # =================================================

        if action == "auto_upload":

            return redirect(
                "accounts:"
                "employer_verification"
            )


        # =================================================
        # SAVE AND CONTINUE LATER
        # =================================================

        if action == "save_progress":

            messages.success(
                request,
                "Your progress has been saved.",
            )


            return redirect(
                "accounts:"
                "employer_verification"
            )


        # =================================================
        # SUBMIT FOR VERIFICATION
        # =================================================

        if (
            action
            == "submit_for_verification"
        ):

            # =============================================
            # ALL 5 DOCUMENTS ARE REQUIRED
            # =============================================

            if not (
                verification
                .all_documents_uploaded
            ):

                verification.status = (
                    EmployerVerification
                    .Status
                    .DRAFT
                )

                verification.submitted_at = (
                    None
                )


                verification.save(
                    update_fields=[
                        "status",
                        "submitted_at",
                        "updated_at",
                    ]
                )


                messages.error(
                    request,
                    (
                        "All 5 required documents "
                        "must be uploaded before "
                        "submitting for verification."
                    ),
                )


                return redirect(
                    "accounts:"
                    "employer_verification"
                )


            # =============================================
            # SET STATUS TO PENDING
            # =============================================

            verification.status = (
                EmployerVerification
                .Status
                .PENDING
            )

            verification.submitted_at = (
                timezone.now()
            )


            verification.save(
                update_fields=[
                    "status",
                    "submitted_at",
                    "updated_at",
                ]
            )


            # =============================================
            # SHOW SUCCESS POPUP ON NEXT PAGE LOAD
            # =============================================

            request.session[
                "employer_verification_submitted"
            ] = True


            return redirect(
                "accounts:"
                "employer_verification"
            )


        return redirect(
            "accounts:"
            "employer_verification"
        )


    # =====================================================
    # GET REQUEST
    # =====================================================

    form = EmployerVerificationForm(
        instance=application
    )


    # =====================================================
    # SHOW SUBMISSION SUCCESS POPUP ONLY ONCE
    # =====================================================

    show_submission_success = (
        request.session.pop(
            "employer_verification_submitted",
            False,
        )
    )


    # =====================================================
    # EMPLOYER LOGIN REVIEW POPUP
    # =====================================================
    #
    # The login flow temporarily stores which popup should
    # be shown. Before displaying anything, this view checks
    # that the value still matches the Employer's CURRENT
    # verification status in the database.
    #
    # This keeps the database as the source of truth.
    # =====================================================

    login_review_status = (
        request.session.pop(
            EMPLOYER_REVIEW_POPUP_SESSION_KEY,
            None,
        )
    )


    employer_review_popup = None


    if (
        application.pk
        and login_review_status
        == application.status
    ):

        # =================================================
        # PENDING
        # =================================================

        if (
            application.status
            == EmployerVerification
            .Status
            .PENDING
        ):

            employer_review_popup = {
                "title": (
                    "We are still reviewing your "
                    "requirements, please wait"
                ),
                "message": "",
                "redirect_home": False,
            }


        # =================================================
        # ACCESS ACCEPTED
        # =================================================

        elif (
            application.status
            == EmployerVerification
            .Status
            .ACCESS_ACCEPTED
        ):

            employer_review_popup = {
                "title": "Congratulations!",
                "message": (
                    "You may now use Malabon Job "
                    "Portal as an Employer!"
                ),
                "redirect_home": True,
            }


        # =================================================
        # ACCESS DENIED
        # =================================================

        elif (
            application.status
            == EmployerVerification
            .Status
            .ACCESS_DENIED
        ):

            employer_review_popup = {
                "title": "Access Denied",
                "message": (
                    "Please make sure to submit all "
                    "the correct requirements."
                ),
                "redirect_home": False,
                "icon_type": "denied",
            }


    # =====================================================
    # TEMPLATE CONTEXT
    # =====================================================

    context = {

        "form": form,

        "verification": application,

        "uploaded_count": (
            application.uploaded_count
        ),

        "progress_percent": (
            application.progress_percent
        ),

        "show_submission_success": (
            show_submission_success
        ),

        "employer_review_popup": (
            employer_review_popup
        ),

    }


    # =====================================================
    # RENDER PAGE
    # =====================================================

    return render(
        request,
        "employer_verification.html",
        context,
    )


# =========================================================
# EMPLOYER DOCUMENT DOWNLOAD
# ADMIN / STAFF ONLY
# =========================================================

@staff_member_required
def employer_verification_document(
    request,
    verification_id,
    field_name,
):

    # =====================================================
    # VALID DOCUMENT FIELD
    # =====================================================

    if (
        field_name
        not in EmployerVerification
        .DOCUMENT_FIELDS
    ):

        raise Http404(
            "Document not found."
        )


    # =====================================================
    # GET VERIFICATION
    # =====================================================

    verification = get_object_or_404(
        EmployerVerification,
        pk=verification_id,
    )


    document = getattr(
        verification,
        field_name,
    )


    # =====================================================
    # DOCUMENT DOES NOT EXIST
    # =====================================================

    if not document:

        raise Http404(
            "Document not found."
        )


    # =====================================================
    # DOWNLOAD FILE
    # =====================================================

    extension = (
        Path(document.name)
        .suffix
        .lower()
    )


    content_type = (
        mimetypes.guess_type(
            document.name
        )[0]
        or "application/octet-stream"
    )


    document.open(
        "rb"
    )


    response = FileResponse(
        document,
        as_attachment=True,
        filename=(
            f"{field_name}{extension}"
        ),
        content_type=content_type,
    )


    response[
        "X-Content-Type-Options"
    ] = "nosniff"


    return response


# =========================================================
# FORGOT PASSWORD
# =========================================================

def forgot_password(request):

    error = ""


    if request.method == "POST":

        form = ForgotPasswordForm(
            request.POST
        )


        if form.is_valid():

            email = (
                form.cleaned_data[
                    "email"
                ]
            )


            user = (
                User.objects.filter(
                    email__iexact=email,
                    is_active=True,
                )
                .first()
            )


            # =============================================
            # EMAIL NOT FOUND
            # =============================================

            if user is None:

                error = (
                    "No account was found for "
                    "that email address."
                )


            # =============================================
            # USER FOUND
            # =============================================

            else:

                try:

                    _, code = (
                        create_password_reset_otp(
                            user
                        )
                    )


                    send_password_reset_otp_email(
                        user,
                        code,
                    )

                except Exception as email_error:

                    print(
                        "Password reset email error:",
                        repr(email_error),
                    )


                    error = (
                        "The verification code could "
                        "not be sent. Please check the "
                        "Gmail configuration."
                    )

                else:

                    request.session[
                        RESET_USER_SESSION_KEY
                    ] = user.pk


                    request.session[
                        RESET_VERIFIED_SESSION_KEY
                    ] = False


                    request.session.cycle_key()


                    return redirect(
                        "accounts:"
                        "verification_code"
                    )


        else:

            error = first_form_error(
                form
            )


    return render(
        request,
        "forgot_password.html",
        {
            "error": error,
        },
    )


# =========================================================
# OTP VERIFICATION
# =========================================================

def verification_code(request):

    user_id = request.session.get(
        RESET_USER_SESSION_KEY
    )


    # =====================================================
    # NO PASSWORD RESET SESSION
    # =====================================================

    if not user_id:

        return redirect(
            "accounts:forgot_password"
        )


    user = (
        User.objects.filter(
            pk=user_id,
            is_active=True,
        )
        .first()
    )


    # =====================================================
    # USER DOES NOT EXIST
    # =====================================================

    if user is None:

        request.session.pop(
            RESET_USER_SESSION_KEY,
            None,
        )


        return redirect(
            "accounts:forgot_password"
        )


    otp = (
        PasswordResetOTP.objects
        .filter(
            user=user
        )
        .first()
    )


    # =====================================================
    # NO OTP
    # =====================================================

    if otp is None:

        return redirect(
            "accounts:forgot_password"
        )


    error = ""


    # =====================================================
    # POST REQUEST
    # =====================================================

    if request.method == "POST":

        action = request.POST.get(
            "action",
            "verify",
        )


        # =================================================
        # RESEND OTP
        # =================================================

        if action == "resend":

            cooldown = timedelta(
                seconds=(
                    OTP_RESEND_COOLDOWN_SECONDS
                )
            )


            elapsed = (
                timezone.now()
                - otp.last_sent_at
            )


            if elapsed < cooldown:

                remaining = int(
                    (
                        cooldown
                        - elapsed
                    ).total_seconds()
                ) + 1


                error = (
                    f"Please wait {remaining} "
                    "seconds before requesting "
                    "another code."
                )


            else:

                try:

                    _, code = (
                        create_password_reset_otp(
                            user
                        )
                    )


                    send_password_reset_otp_email(
                        user,
                        code,
                    )

                except Exception as email_error:

                    print(
                        "OTP resend error:",
                        repr(email_error),
                    )


                    error = (
                        "The code could not be "
                        "resent. Please check the "
                        "Gmail configuration."
                    )

                else:

                    messages.success(
                        request,
                        (
                            "A new verification "
                            "code was sent."
                        ),
                    )


                    return redirect(
                        "accounts:"
                        "verification_code"
                    )


        # =================================================
        # VERIFY OTP
        # =================================================

        else:

            form = VerificationCodeForm(
                request.POST
            )


            if not form.is_valid():

                error = first_form_error(
                    form
                )


            elif otp.is_expired:

                error = (
                    "The verification code has "
                    "expired. Request a new code."
                )


            elif (
                otp.attempt_count
                >= OTP_MAX_ATTEMPTS
            ):

                error = (
                    "Too many incorrect attempts. "
                    "Request a new code."
                )


            elif not check_password(
                form.cleaned_data[
                    "code"
                ],
                otp.code_hash,
            ):

                otp.attempt_count += 1


                otp.save(
                    update_fields=[
                        "attempt_count",
                    ]
                )


                error = (
                    "Incorrect verification code."
                )


            else:

                otp.verified_at = (
                    timezone.now()
                )


                otp.save(
                    update_fields=[
                        "verified_at",
                    ]
                )


                request.session[
                    RESET_VERIFIED_SESSION_KEY
                ] = True


                request.session.cycle_key()


                return redirect(
                    "accounts:reset_password"
                )


    return render(
        request,
        "verification_code.html",
        {
            "email": user.email,
            "error": error,
        },
    )


# =========================================================
# RESET PASSWORD
# =========================================================

def reset_password(request):

    user_id = request.session.get(
        RESET_USER_SESSION_KEY
    )


    verified = request.session.get(
        RESET_VERIFIED_SESSION_KEY,
        False,
    )


    # =====================================================
    # INVALID RESET SESSION
    # =====================================================

    if not user_id or not verified:

        return redirect(
            "accounts:forgot_password"
        )


    user = (
        User.objects.filter(
            pk=user_id,
            is_active=True,
        )
        .first()
    )


    if user is None:

        return redirect(
            "accounts:forgot_password"
        )


    otp = (
        PasswordResetOTP.objects
        .filter(
            user=user
        )
        .first()
    )


    # =====================================================
    # OTP MUST STILL BE VALID
    # =====================================================

    if (
        otp is None
        or not otp.is_verified
        or otp.is_expired
    ):

        return redirect(
            "accounts:forgot_password"
        )


    error = ""


    # =====================================================
    # POST REQUEST
    # =====================================================

    if request.method == "POST":

        form = ResetPasswordForm(
            request.POST,
            user=user,
        )


        if form.is_valid():

            user.set_password(
                form.cleaned_data[
                    "new_password"
                ]
            )


            user.save(
                update_fields=[
                    "password",
                ]
            )


            # =============================================
            # RECORD PASSWORD RESET
            # =============================================

            record_authentication_event(
                request=request,
                event_type=(
                    AuthenticationEvent
                    .EventType
                    .PASSWORD_RESET
                ),
                user=user,
                email=user.email,
            )


            # =============================================
            # DELETE USED OTP
            # =============================================

            otp.delete()


            # =============================================
            # CLEAR SESSION
            # =============================================

            request.session.pop(
                RESET_USER_SESSION_KEY,
                None,
            )


            request.session.pop(
                RESET_VERIFIED_SESSION_KEY,
                None,
            )


            request.session.cycle_key()


            return redirect(
                "accounts:"
                "password_changed"
            )


        error = first_form_error(
            form
        )


    return render(
        request,
        "reset_password.html",
        {
            "error": error,
        },
    )


# =========================================================
# PASSWORD CHANGED
# =========================================================

def password_changed(request):

    return render(
        request,
        "password_changed.html",
    )


# =========================================================
# DASHBOARD
# =========================================================

@login_required
def dashboard(request):

    return redirect_user_by_account_type(
        request.user
    )


# =========================================================
# LOGOUT
# =========================================================

def logout_view(request):

    if request.method == "POST":

        user = (
            request.user
            if request.user.is_authenticated
            else None
        )


        if user is not None:

            record_authentication_event(
                request=request,
                event_type=(
                    AuthenticationEvent
                    .EventType
                    .LOGOUT
                ),
                user=user,
                email=user.email,
            )


        logout(
            request
        )


    return redirect(
        "accounts:home"
    )