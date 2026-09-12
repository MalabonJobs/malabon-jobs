document.addEventListener("DOMContentLoaded", () => {

    /* =========================
       LOGIN / REGISTER ANIMATION
    ========================= */

    const accountContainer =
        document.getElementById("accountContainer");

    const registerButton =
        document.getElementById("registerButton");

    const signInButton =
        document.getElementById("signInButton");


    if (accountContainer && registerButton) {

        registerButton.addEventListener(
            "click",
            () => {

                accountContainer.classList.add(
                    "register-active"
                );

            }
        );

    }


    if (accountContainer && signInButton) {

        signInButton.addEventListener(
            "click",
            () => {

                accountContainer.classList.remove(
                    "register-active"
                );

            }
        );

    }


    /* =========================
       REGISTRATION RESULT POPUP
    ========================= */

    const registrationSuccessMessage =
        document.getElementById(
            "registrationSuccessMessage"
        );

    const registrationErrorMessage =
        document.getElementById(
            "registrationErrorMessage"
        );

    const registrationSuccessOverlay =
        document.getElementById(
            "registrationSuccessOverlay"
        );

    const registrationResultIcon =
        document.getElementById(
            "registrationResultIcon"
        );

    const registrationCheckmark =
        document.getElementById(
            "registrationCheckmark"
        );

    const registrationXmark =
        document.getElementById(
            "registrationXmark"
        );

    const registrationResultText =
        document.getElementById(
            "registrationResultText"
        );

    const registrationContinueButton =
        document.getElementById(
            "registrationContinueButton"
        );


    /* =========================
       SHOW RESULT POPUP
    ========================= */

    function showRegistrationResult(
        type,
        message
    ) {

        if (
            !registrationSuccessOverlay ||
            !registrationResultIcon ||
            !registrationCheckmark ||
            !registrationXmark ||
            !registrationResultText
        ) {
            return;
        }


        /* =========================
           ERROR RESULT
        ========================= */

        if (type === "error") {

            registrationCheckmark.hidden = true;

            registrationXmark.hidden = false;

            registrationResultText.textContent =
                message;

            registrationResultText.style.whiteSpace =
                "normal";


            const card =
                registrationSuccessOverlay.querySelector(
                    ".registration-success-card"
                );


            if (card) {

                card.setAttribute(
                    "aria-label",
                    message
                );

            }


        }

        /* =========================
           SUCCESS RESULT
        ========================= */

        else {

            registrationCheckmark.hidden = false;

            registrationXmark.hidden = true;


            registrationResultText.innerHTML =
                "Account successfully<br>created!";


            const card =
                registrationSuccessOverlay.querySelector(
                    ".registration-success-card"
                );


            if (card) {

                card.setAttribute(
                    "aria-label",
                    "Account successfully created"
                );

            }

        }


        /* SHOW POPUP */

        registrationSuccessOverlay.hidden = false;

        document.body.style.overflow = "hidden";

    }


    /* =========================
       REGISTRATION ERROR
    ========================= */

    if (
        registrationErrorMessage &&
        registrationErrorMessage.dataset.registrationError === "true"
    ) {

        showRegistrationResult(
            "error",
            registrationErrorMessage.dataset.errorMessage
        );


        /*
           Keep the registration form active
           when there is an error.
        */

        if (accountContainer) {

            accountContainer.classList.add(
                "register-active"
            );

        }

    }


    /* =========================
       REGISTRATION SUCCESS
    ========================= */

    else if (
        registrationSuccessMessage &&
        registrationSuccessOverlay &&
        registrationSuccessMessage.dataset.registrationSuccess === "true"
    ) {

        showRegistrationResult(
            "success"
        );

    }


    /* =========================
       CONTINUE BUTTON
    ========================= */

    if (
        registrationContinueButton &&
        registrationSuccessOverlay
    ) {

        registrationContinueButton.addEventListener(
            "click",
            () => {

                /*
                   Hide popup
                */

                registrationSuccessOverlay.hidden = true;

                document.body.style.overflow = "";


                /* =========================
                   ERROR
                   Return to registration form
                ========================= */

                if (
                    registrationErrorMessage &&
                    registrationErrorMessage.dataset.registrationError === "true"
                ) {

                    if (accountContainer) {

                        accountContainer.classList.add(
                            "register-active"
                        );

                    }

                    return;

                }


                /* =========================
                   SUCCESS
                   Return to normal login side
                ========================= */

                if (accountContainer) {

                    accountContainer.classList.remove(
                        "register-active"
                    );

                }

            }
        );

    }

});