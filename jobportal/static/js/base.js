document.addEventListener("DOMContentLoaded", function () {

    /* =====================================================
       PROFILE MENU
    ====================================================== */

    const profileButton =
        document.getElementById("profileMenuButton");

    const profileDropdown =
        document.getElementById("profileDropdown");

    const profileMenuContainer =
        document.querySelector(".profile-menu-container");


    /* =====================================================
       MOBILE NAVIGATION
    ====================================================== */

    const mobileMenuButton =
        document.getElementById("mobileMenuButton");

    const mobileNavigationDropdown =
        document.getElementById("mobileNavigationDropdown");

    const mobileNavContainer =
        document.querySelector(".mobile-nav-container");


    /* =====================================================
       PROFILE FUNCTIONS
    ====================================================== */

    function openProfileDropdown() {

        if (!profileDropdown || !profileButton) {
            return;
        }

        profileDropdown.hidden = false;

        profileButton.setAttribute(
            "aria-expanded",
            "true"
        );

    }


    function closeProfileDropdown() {

        if (!profileDropdown || !profileButton) {
            return;
        }

        profileDropdown.hidden = true;

        profileButton.setAttribute(
            "aria-expanded",
            "false"
        );

    }


    function toggleProfileDropdown() {

        if (!profileDropdown) {
            return;
        }

        if (profileDropdown.hidden) {

            openProfileDropdown();

            closeMobileNavigation();

        } else {

            closeProfileDropdown();

        }

    }


    /* =====================================================
       MOBILE MENU FUNCTIONS
    ====================================================== */

    function openMobileNavigation() {

        if (
            !mobileNavigationDropdown ||
            !mobileMenuButton
        ) {
            return;
        }

        mobileNavigationDropdown.hidden = false;

        mobileMenuButton.setAttribute(
            "aria-expanded",
            "true"
        );

        mobileMenuButton.classList.add("menu-open");

    }


    function closeMobileNavigation() {

        if (
            !mobileNavigationDropdown ||
            !mobileMenuButton
        ) {
            return;
        }

        mobileNavigationDropdown.hidden = true;

        mobileMenuButton.setAttribute(
            "aria-expanded",
            "false"
        );

        mobileMenuButton.classList.remove("menu-open");

    }


    function toggleMobileNavigation() {

        if (!mobileNavigationDropdown) {
            return;
        }

        if (mobileNavigationDropdown.hidden) {

            openMobileNavigation();

            closeProfileDropdown();

        } else {

            closeMobileNavigation();

        }

    }


    /* =====================================================
       PROFILE BUTTON CLICK
    ====================================================== */

    if (profileButton) {

        profileButton.addEventListener(
            "click",
            function (event) {

                event.preventDefault();
                event.stopPropagation();

                toggleProfileDropdown();

            }
        );

    }


    /* =====================================================
       BURGER BUTTON CLICK
    ====================================================== */

    if (mobileMenuButton) {

        mobileMenuButton.addEventListener(
            "click",
            function (event) {

                event.preventDefault();
                event.stopPropagation();

                toggleMobileNavigation();

            }
        );

    }


    /* =====================================================
       CLICK OUTSIDE
    ====================================================== */

    document.addEventListener(
        "click",
        function (event) {

            if (
                profileMenuContainer &&
                !profileMenuContainer.contains(event.target)
            ) {

                closeProfileDropdown();

            }

            if (
                mobileNavContainer &&
                !mobileNavContainer.contains(event.target)
            ) {

                closeMobileNavigation();

            }

        }
    );


    /* =====================================================
       ESCAPE KEY
    ====================================================== */

    document.addEventListener(
        "keydown",
        function (event) {

            if (event.key === "Escape") {

                closeProfileDropdown();

                closeMobileNavigation();

            }

        }
    );


    /* =====================================================
       CLOSE MOBILE MENU WHEN SCREEN BECOMES LARGE AGAIN
    ====================================================== */

    window.addEventListener(
        "resize",
        function () {

            if (window.innerWidth > 800) {

                closeMobileNavigation();

            }

        }
    );

});