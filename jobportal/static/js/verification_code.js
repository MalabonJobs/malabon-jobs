document.addEventListener("DOMContentLoaded", () => {

    const codeInputs = Array.from(
        document.querySelectorAll(".code-input")
    );

    const verificationForm =
        document.querySelector(
            ".verification-form"
        );

    const sendButton =
        document.querySelector(
            ".verification-send-button"
        );


    if (
        codeInputs.length === 0 ||
        !verificationForm ||
        !sendButton
    ) {
        return;
    }


    /* =========================
       FOCUS HELPER
    ========================= */

    const focusInput = (index) => {

        if (
            index < 0 ||
            index >= codeInputs.length
        ) {
            return;
        }


        codeInputs[index].focus();

        codeInputs[index].select();

    };


    /* =========================
       FIRST INPUT AUTO-FOCUS
    ========================= */

    focusInput(0);


    /* =========================
       OTP INPUT BEHAVIOR
    ========================= */

    codeInputs.forEach(
        (input, index) => {

            /* =========================
               NUMBER INPUT
            ========================= */

            input.addEventListener(
                "input",
                (event) => {

                    const digit =
                        event.target.value
                            .replace(/\D/g, "")
                            .slice(-1);


                    event.target.value = digit;


                    if (
                        digit &&
                        index <
                            codeInputs.length - 1
                    ) {

                        focusInput(index + 1);

                    }

                }
            );


            /* =========================
               KEYBOARD BEHAVIOR
            ========================= */

            input.addEventListener(
                "keydown",
                (event) => {

                    /*
                     * ENTER
                     *
                     * Pressing Enter performs the
                     * exact same action as clicking
                     * the existing Send button.
                     */

                    if (event.key === "Enter") {

                        event.preventDefault();


                        if (
                            verificationForm
                                .checkValidity()
                        ) {

                            verificationForm
                                .requestSubmit(
                                    sendButton
                                );

                        } else {

                            verificationForm
                                .reportValidity();

                        }


                        return;
                    }


                    /*
                     * BACKSPACE
                     */

                    if (
                        event.key === "Backspace" &&
                        input.value === "" &&
                        index > 0
                    ) {

                        event.preventDefault();

                        focusInput(index - 1);

                        return;
                    }


                    /*
                     * LEFT ARROW
                     */

                    if (
                        event.key === "ArrowLeft" &&
                        index > 0
                    ) {

                        event.preventDefault();

                        focusInput(index - 1);

                        return;
                    }


                    /*
                     * RIGHT ARROW
                     */

                    if (
                        event.key === "ArrowRight" &&
                        index <
                            codeInputs.length - 1
                    ) {

                        event.preventDefault();

                        focusInput(index + 1);

                    }

                }
            );


            /* =========================
               PASTE 4-DIGIT CODE
            ========================= */

            input.addEventListener(
                "paste",
                (event) => {

                    event.preventDefault();


                    const pastedCode =
                        event.clipboardData
                            .getData("text")
                            .replace(/\D/g, "")
                            .slice(
                                0,
                                codeInputs.length
                            );


                    if (!pastedCode) {
                        return;
                    }


                    codeInputs.forEach(
                        (currentInput) => {

                            currentInput.value = "";

                        }
                    );


                    pastedCode
                        .split("")
                        .forEach(
                            (
                                digit,
                                digitIndex
                            ) => {

                                if (
                                    codeInputs[
                                        digitIndex
                                    ]
                                ) {

                                    codeInputs[
                                        digitIndex
                                    ].value = digit;

                                }

                            }
                        );


                    const nextIndex =
                        Math.min(
                            pastedCode.length,
                            codeInputs.length - 1
                        );


                    focusInput(nextIndex);

                }
            );

        }
    );

});