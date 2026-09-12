document.addEventListener(
    "DOMContentLoaded",
    function () {

        /* =====================================================
           PROGRESS BAR
        ====================================================== */

        const progressFill =
            document.getElementById(
                "verificationProgressFill"
            );


        if (progressFill) {

            let progress = Number(
                progressFill.dataset.progress || 0
            );


            progress = Math.max(
                0,
                Math.min(
                    100,
                    progress
                )
            );


            progressFill.style.width =
                progress + "%";

        }


        /* =====================================================
           SUBMISSION SUCCESS POPUP
        ====================================================== */

        const submissionSuccessPopup =
            document.getElementById(
                "submissionSuccessPopup"
            );


        const closeSubmissionSuccessButton =
            document.getElementById(
                "closeSubmissionSuccess"
            );


        if (
            submissionSuccessPopup &&
            closeSubmissionSuccessButton
        ) {

            closeSubmissionSuccessButton.addEventListener(
                "click",
                function () {

                    submissionSuccessPopup.remove();

                }
            );

        }


        /* =====================================================
           EMPLOYER REVIEW STATUS POPUP
        ====================================================== */

        const employerReviewPopup =
            document.getElementById(
                "employerReviewPopup"
            );


        const closeEmployerReviewPopup =
            document.getElementById(
                "closeEmployerReviewPopup"
            );


        if (
            employerReviewPopup &&
            closeEmployerReviewPopup
        ) {

            closeEmployerReviewPopup.addEventListener(
                "click",
                function () {

                    const shouldRedirectHome =
                        employerReviewPopup
                            .dataset
                            .redirectHome === "true";


                    const homeUrl =
                        employerReviewPopup
                            .dataset
                            .homeUrl;


                    /* =========================================
                       CLOSE POPUP
                    ========================================== */

                    employerReviewPopup.remove();


                    /* =========================================
                       ACCESS ACCEPTED ONLY
                    ========================================== */

                    if (
                        shouldRedirectHome &&
                        homeUrl
                    ) {

                        window.location.href =
                            homeUrl;

                    }

                }
            );

        }


        /* =====================================================
           EMPLOYER VERIFICATION FORM
        ====================================================== */

        const verificationForm =
            document.getElementById(
                "employerVerificationForm"
            );


        const autoActionInput =
            document.getElementById(
                "verificationAutoAction"
            );


        /* =====================================================
           CHOOSE FILE BUTTONS
        ====================================================== */

        if (
            verificationForm &&
            autoActionInput
        ) {

            const chooseFileButtons =
                document.querySelectorAll(
                    ".choose-file-button[data-file-input]"
                );


            chooseFileButtons.forEach(
                function (button) {

                    const inputId =
                        button.getAttribute(
                            "data-file-input"
                        );


                    const fileInput =
                        document.getElementById(
                            inputId
                        );


                    if (!fileInput) {
                        return;
                    }


                    /* =========================================
                       OPEN FILE SELECTOR
                    ========================================== */

                    button.addEventListener(
                        "click",
                        function () {

                            fileInput.click();

                        }
                    );


                    /* =========================================
                       FILE SELECTED
                    ========================================== */

                    fileInput.addEventListener(
                        "change",
                        function () {

                            if (
                                !fileInput.files ||
                                fileInput.files.length === 0
                            ) {
                                return;
                            }


                            autoActionInput.value =
                                "auto_upload";


                            verificationForm.submit();

                        }
                    );

                }
            );

        }

    }
);