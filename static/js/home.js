// =========================================
// MOBILE NAVIGATION
// =========================================

const menuToggle = document.getElementById("menu-toggle");
const headerNavigation = document.getElementById("header-navigation");
const menuClose = document.getElementById("menu-close");
const menuBackdrop = document.getElementById("menu-backdrop");


// OPEN MENU
function openMenu() {
    headerNavigation.classList.add("active");
    menuBackdrop.classList.add("active");
    document.body.classList.add("menu-open");

    menuToggle.setAttribute("aria-expanded", "true");
    menuToggle.setAttribute("aria-label", "Close navigation menu");
}


// CLOSE MENU
function closeMenu() {
    headerNavigation.classList.remove("active");
    menuBackdrop.classList.remove("active");
    document.body.classList.remove("menu-open");

    menuToggle.setAttribute("aria-expanded", "false");
    menuToggle.setAttribute("aria-label", "Open navigation menu");
}


// TOGGLE MENU
menuToggle.addEventListener("click", function () {
    const isOpen = headerNavigation.classList.contains("active");

    if (isOpen) {
        closeMenu();
    } else {
        openMenu();
    }
});


// CLOSE USING X BUTTON
menuClose.addEventListener("click", closeMenu);


// CLOSE WHEN BACKDROP IS CLICKED
menuBackdrop.addEventListener("click", closeMenu);


// CLOSE WHEN A NAVIGATION LINK IS SELECTED
document.querySelectorAll(".main-navigation a").forEach(function (link) {
    link.addEventListener("click", closeMenu);
});


// CLOSE WHEN ESCAPE IS PRESSED
document.addEventListener("keydown", function (event) {
    if (event.key === "Escape") {
        closeMenu();
    }
});