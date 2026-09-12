from pathlib import Path

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from .models import EmployerVerification


User = get_user_model()


# =========================================================
# LOGIN FORM
# =========================================================

class LoginForm(forms.Form):

    email = forms.EmailField(
        max_length=254,
    )

    password = forms.CharField(
        strip=False,
        widget=forms.PasswordInput,
    )

    def clean_email(self):

        return (
            self.cleaned_data["email"]
            .strip()
            .lower()
        )


# =========================================================
# REGISTRATION FORM
# =========================================================

class RegistrationForm(forms.Form):

    first_name = forms.CharField(
        max_length=150,
        required=False,
    )

    last_name = forms.CharField(
        max_length=150,
        required=False,
    )

    email = forms.EmailField(
        max_length=254,
    )

    password = forms.CharField(
        strip=False,
        widget=forms.PasswordInput,
    )

    confirm_password = forms.CharField(
        strip=False,
        widget=forms.PasswordInput,
    )


    def clean_email(self):

        email = (
            self.cleaned_data["email"]
            .strip()
            .lower()
        )

        if User.objects.filter(
            email__iexact=email
        ).exists():

            raise forms.ValidationError(
                "Email already used, use a new one.",
                code="email_already_used",
            )

        return email


    def clean(self):

        cleaned_data = super().clean()

        password = cleaned_data.get(
            "password"
        )

        confirm_password = cleaned_data.get(
            "confirm_password"
        )


        # =================================================
        # PASSWORDS MUST MATCH
        # =================================================

        if (
            password
            and confirm_password
            and password != confirm_password
        ):

            self.add_error(
                "confirm_password",
                forms.ValidationError(
                    "Passwords do not match, please try again.",
                    code="password_mismatch",
                ),
            )


        # =================================================
        # DJANGO PASSWORD VALIDATION
        # =================================================

        if password:

            candidate = User(
                email=cleaned_data.get(
                    "email",
                    "",
                ),
                first_name=cleaned_data.get(
                    "first_name",
                    "",
                ),
                last_name=cleaned_data.get(
                    "last_name",
                    "",
                ),
            )

            try:

                validate_password(
                    password,
                    user=candidate,
                )

            except ValidationError as exc:

                self.add_error(
                    "password",
                    exc,
                )


        return cleaned_data


    def save(self):

        return User.objects.create_user(

            email=self.cleaned_data[
                "email"
            ],

            password=self.cleaned_data[
                "password"
            ],

            first_name=(
                self.cleaned_data.get(
                    "first_name",
                    "",
                ).strip()
            ),

            last_name=(
                self.cleaned_data.get(
                    "last_name",
                    "",
                ).strip()
            ),

        )


# =========================================================
# FORGOT PASSWORD FORM
# =========================================================

class ForgotPasswordForm(forms.Form):

    email = forms.EmailField(
        max_length=254,
    )


    def clean_email(self):

        return (
            self.cleaned_data["email"]
            .strip()
            .lower()
        )


# =========================================================
# VERIFICATION CODE FORM
# =========================================================

class VerificationCodeForm(forms.Form):

    digit_1 = forms.CharField(
        max_length=1,
        min_length=1,
    )

    digit_2 = forms.CharField(
        max_length=1,
        min_length=1,
    )

    digit_3 = forms.CharField(
        max_length=1,
        min_length=1,
    )

    digit_4 = forms.CharField(
        max_length=1,
        min_length=1,
    )


    def clean(self):

        cleaned_data = super().clean()


        code = "".join(

            cleaned_data.get(
                name,
                "",
            )

            for name in (

                "digit_1",
                "digit_2",
                "digit_3",
                "digit_4",

            )

        )


        if (
            len(code) != 4
            or not code.isdigit()
        ):

            raise forms.ValidationError(
                "Enter the complete 4-digit verification code."
            )


        cleaned_data[
            "code"
        ] = code


        return cleaned_data


# =========================================================
# RESET PASSWORD FORM
# =========================================================

class ResetPasswordForm(forms.Form):

    new_password = forms.CharField(
        strip=False,
        widget=forms.PasswordInput,
    )

    confirm_password = forms.CharField(
        strip=False,
        widget=forms.PasswordInput,
    )


    def __init__(
        self,
        *args,
        user=None,
        **kwargs,
    ):

        super().__init__(
            *args,
            **kwargs,
        )

        self.user = user


    def clean(self):

        cleaned_data = super().clean()


        password = cleaned_data.get(
            "new_password"
        )

        confirmation = cleaned_data.get(
            "confirm_password"
        )


        # =================================================
        # PASSWORDS MUST MATCH
        # =================================================

        if (
            password
            and confirmation
            and password != confirmation
        ):

            self.add_error(
                "confirm_password",
                "Passwords do not match.",
            )


        # =================================================
        # PASSWORD VALIDATION
        # =================================================

        if password:

            try:

                validate_password(
                    password,
                    user=self.user,
                )

            except ValidationError as exc:

                self.add_error(
                    "new_password",
                    exc,
                )


        return cleaned_data


# =========================================================
# EMPLOYER DOCUMENT SIGNATURE VALIDATION
# =========================================================

def validate_document_signature(
    uploaded_file,
):

    extension = (
        Path(
            uploaded_file.name
        )
        .suffix
        .lower()
    )


    # =====================================================
    # READ BEGINNING OF FILE
    # =====================================================

    uploaded_file.seek(0)

    header = uploaded_file.read(
        1024
    )

    uploaded_file.seek(0)


    # =====================================================
    # PDF
    # =====================================================

    if extension == ".pdf":

        if not header.startswith(
            b"%PDF-"
        ):

            raise forms.ValidationError(
                "The selected file does not appear to be a valid PDF."
            )


    # =====================================================
    # JPG / JPEG
    # =====================================================

    elif extension in (
        ".jpg",
        ".jpeg",
    ):

        if not header.startswith(
            b"\xff\xd8\xff"
        ):

            raise forms.ValidationError(
                "The selected file does not appear to be a valid JPG/JPEG image."
            )


    # =====================================================
    # PNG
    # =====================================================

    elif extension == ".png":

        if not header.startswith(
            b"\x89PNG\r\n\x1a\n"
        ):

            raise forms.ValidationError(
                "The selected file does not appear to be a valid PNG image."
            )


# =========================================================
# EMPLOYER VERIFICATION FORM
# =========================================================

class EmployerVerificationForm(
    forms.ModelForm
):

    class Meta:

        model = EmployerVerification

        fields = [

            "business_permit",

            "barangay_clearance",

            "mayors_permit",

            "cedula",

            "valid_id",

        ]


    def clean(self):

        cleaned_data = super().clean()


        # =================================================
        # VALIDATE EACH NEWLY UPLOADED FILE
        # =================================================

        for field_name in (
            EmployerVerification
            .DOCUMENT_FIELDS
        ):

            uploaded_file = (
                self.files.get(
                    field_name
                )
            )


            if uploaded_file:

                validate_document_signature(
                    uploaded_file
                )


        return cleaned_data